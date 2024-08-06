import time
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from elasticsearch import Elasticsearch
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class NewsCrawler(ABC):
    def __init__(self, base_url, es_host='localhost', es_port=9200):
        self.base_url = base_url
        self.data = []
        
        # Check if Elasticsearch is running
        self.es = None
        self.es_available = self.check_elasticsearch(es_host, es_port)
        if self.es_available:
            self.es = Elasticsearch([f'http://{es_host}:{es_port}'])
        else:
            logging.warning("Elasticsearch is not available. Data will not be saved to Elasticsearch.")
        
        # Set up Selenium
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            logging.error(f"Failed to initialize Selenium WebDriver: {e}")
            self.driver = None
        
        ## Intialization of beautifulsoup
        self.soup = None
    
    def init_beautifulsoup(self, html_content):
        self.soup = BeautifulSoup(html_content, 'html.parser')
    
    def check_elasticsearch(self, host, port):
        try:
            response = requests.get(f'http://{host}:{port}', timeout=2)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def get_data(self):
        return self.data
    
    def fetch_page(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            logging.error(f"Error fetching page {url}: {e}")
            return None
    
    def fetch_page_with_js(self, url):
        if self.driver is None:
            logging.error("Selenium WebDriver is not initialized")
            return None
        try:
            self.driver.get(url)
            time.sleep(2)  # Wait for JavaScript to load
            return BeautifulSoup(self.driver.page_source, 'html.parser')
        except Exception as e:
            logging.error(f"Error fetching page with JavaScript {url}: {e}")
            return None
    
    @abstractmethod
    def parse_article(self, article_url):
        pass
    
    @abstractmethod
    def get_article_urls(self, date):
        pass
    
    def save_to_elasticsearch(self, article):
        if not self.es_available:
            logging.warning("Elasticsearch is not available. Cannot save article.")
            logging.info("To save articles, ensure Elasticsearch is running and modify the code to connect.")
            return

        try:
            self.es.index(index='news_articles', body=article)
            logging.info("Article saved to Elasticsearch")
        except Exception as e:
            logging.error(f"Error saving article to Elasticsearch: {e}")
    
    def get_all_articles_of_today(self):
        today = datetime.now().date()
        return self.get_all_articles_of_date(today)
    
    def get_all_articles_of_date(self, date):
        article_urls = self.get_article_urls(date)
        articles = []
        for url in article_urls:
            article = self.parse_article(url)
            if article:
                articles.append(article)
                self.save_to_elasticsearch(article)
        return articles    
    
    def __del__(self):
        if self.driver:
            self.driver.quit()

def main():
    logging.info("News Crawler Service is running")
    while True:
        # Add any periodic tasks here
        time.sleep(3600)  # Sleep for an hour

if __name__ == "__main__":
    main()