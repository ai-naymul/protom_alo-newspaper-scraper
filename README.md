# Prothom Alo News Crawler 📰

![Prothom Alo Logo](https://dwg-office.com/wp-content/uploads/2020/05/Prothom-Alo-logo-300x175.jpg)

## Overview

The **Prothom Alo News Crawler** is a Python-based web scraping tool designed to fetch and parse news articles from the Prothom Alo website. It uses Selenium for dynamic content loading, BeautifulSoup for HTML parsing, and Elasticsearch for storing the scraped data.

## Features

- **Dynamic Content Loading**: Utilizes Selenium to handle JavaScript-rendered content.
- **HTML Parsing**: Uses BeautifulSoup to parse and extract data from HTML.
- **Elasticsearch Integration**: Stores the scraped articles in an Elasticsearch database.
- **Error Handling**: Robust error handling and logging mechanisms.

## Requirements

- Python 3.x
- Docker (for running Elasticsearch)
- The following Python packages (listed in `requirements.txt`):
  - selenium
  - beautifulsoup4
  - requests
  - elasticsearch

## Setup

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/prothom-alo-crawler.git
cd prothom-alo-crawler
```
### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Elasticsearch with Docker

Ensure Docker is installed on your system. Then, run the following command to start Elasticsearch:

```bash
docker-compose up -d
```


This will start an Elasticsearch instance on `localhost:9200`.

### 4. Run the Crawler

Execute the main script to start crawling:

```bash
python protom_alo_crawler.py
```



### Key Files

- **`protom_alo_crawler.py`**: Contains the `ProthomAloCrawler` class which extends the `NewsCrawler` class to implement site-specific crawling logic.
- **`generalized_news_crawler.py`**: Defines the `NewsCrawler` abstract base class, providing common functionality for web scraping and Elasticsearch integration.
- **`docker_compose.yml`**: Docker Compose configuration for setting up Elasticsearch.
- **`requirements.txt`**: Lists the Python dependencies required for the project.

## How It Works

### Crawling Articles

1. **Initialization**: The `ProthomAloCrawler` class is initialized with the base URL and Elasticsearch host/port.
2. **Fetching URLs**: The `get_article_urls` method fetches article URLs for a given date by navigating to the search page and clicking the "Load More" button until all articles are loaded.
3. **Parsing Articles**: The `parse_article` method extracts details like headline, publication date, content, category, and suggested articles from each article page.
4. **Saving to Elasticsearch**: Parsed articles are saved to Elasticsearch for easy querying and analysis.


## Contributing

Feel free to fork this repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License.

---

Happy Crawling! 🚀