import sys
import os
from datetime import datetime, timedelta
import logging
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from selenium.common.exceptions import NoSuchElementException

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from news_crawler import NewsCrawler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ProthomAloCrawler(NewsCrawler):
    def __init__(self, es_host='localhost', es_port=9200):
        super().__init__('https://www.prothomalo.com', es_host, es_port) # Initialize the Selenium WebDriver
        logging.info("ProthomAloCrawler initialized with ES host: %s, port: %d", es_host, es_port)

    def get_article_urls(self, date):
        logging.info("Fetching article URLs for date: %s", date)
        # Convert date to timestamp (milliseconds)
        date_timestamp = int(datetime.combine(date, datetime.min.time()).timestamp() * 1000)
        next_day_timestamp = int(datetime.combine(date + timedelta(days=1), datetime.min.time()).timestamp() * 1000)
        
        search_url = f'{self.base_url}/search?published-before={next_day_timestamp}&published-after={date_timestamp}'
        logging.info("Navigating to search URL: %s", search_url)
        self.driver.get(search_url)
        time.sleep(7)  # Wait for page to load
        while True:
            try:
                logging.info('Getting Load more button')
                load_more_button = self.driver.find_element(By.CSS_SELECTOR, '.load-more-content')
                logging.info('Load more button found')
                if load_more_button:
                    page_source_before = self.driver.page_source
                    ActionChains(self.driver).move_to_element(load_more_button).click(load_more_button).perform()
                    logging.info("Clicked 'Load More' button")
                    time.sleep(2)  # Wait for new content to load
                    
                    # Scroll a little bit
                    self.driver.execute_script("window.scrollBy(0, 500);")
                    time.sleep(2)  # Wait for the page to scroll
                    
                    page_source_after = self.driver.page_source
                    if page_source_before == page_source_after:
                        logging.info("No new content loaded. Exiting loop.")
                        break
            except NoSuchElementException:
                logging.error("No 'Load More' button found. Exiting loop.")
                break
            except Exception as e:
                logging.error("An error occurred: %s", e)
                break

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        links = soup.select('.headline-title a')
        article_urls = [link.get('href') for link in links]
        logging.info("Found %d articles after scrolling", len(article_urls))
        return article_urls

    def parse_article(self, article_url):
        logging.info("Parsing article: %s", article_url)
        self.driver.get(article_url)
        soup = self.fetch_page(article_url)
        if soup is None:
            logging.error("Failed to fetch article page: %s", article_url)
            return None

        try:
            if '/video/' in article_url:
                headline = soup.select_one('h1').text if soup.select_one('h1') else ''
                category = 'video'
                article = {
                    'url': article_url,
                    'headline': headline,
                    'category': category
                }
                logging.info("Parsed video article: %s", article_url)
                return article

            headline = soup.select_one('h1').text if soup.select_one('h1') else ''
            publication_date = soup.select_one('time span').text.replace('প্রকাশ:', '').strip() if soup.select_one('time span') else ''
            article_descriptions = soup.select('.story-element-text p')
            content = ' '.join([article_description.text for article_description in article_descriptions])
            category = soup.select_one('.print-tags span').text if soup.select_one('.print-tags span') else ''
            topics = [topic.text for topic in soup.select('.tag-list li a')]
            suggested_article_titles = [article.text for article in self.driver.find_elements(By.CSS_SELECTOR, '.card-with-image-zoom h3')]
            suggested_article_links = [article.get_attribute('href') for article in self.driver.find_elements(By.CSS_SELECTOR, '.card-with-image-zoom a')]
            article = {
                'url': article_url,
                'headline': headline,
                'content': content,
                'publication_date': publication_date,
                'topics': topics,
                'suggested_articles_title': suggested_article_titles,
                'suggested_articles_link': suggested_article_links,
                'category': category
            }
            logging.info("Parsed article: %s", article_url)
            return article

        except Exception as e:
            logging.error("Error parsing article %s: %s", article_url, e)
            return None

    def __del__(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
            logging.info("Web driver quit")
        super().__del__()

def main():
    crawler = ProthomAloCrawler()
    today = datetime.now().date()
    logging.info("Starting to crawl articles for date: %s", today)
    articles = crawler.get_all_articles_of_date(today)
    logging.info("Crawled %d articles from Prothom Alo for %s", len(articles), today)

    if not crawler.es_available:
        logging.warning("Elasticsearch is not available. Articles were not saved to the database.")
        logging.info("To save articles, ensure Elasticsearch is running and modify the code to connect.")

if __name__ == "__main__":
    main()