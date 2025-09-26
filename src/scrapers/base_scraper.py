"""
Base scraper class containing shared functionality for all site scrapers.
This implements the hybrid approach with common methods and utilities.
"""
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
import os

class BaseScraper:
    """Base scraper class with shared functionality for all site scrapers"""
    
    def __init__(self, base_url, delay=2):
        """
        Initialize base scraper with common settings
        
        Args:
            base_url (str): Base URL of the website to scrape
            delay (int): Delay in seconds between requests (default: 2)
        """
        self.base_url = base_url
        self.session = requests.Session()
        self.delay = delay
        self.scraped_urls = set()
        
        # Set up common headers
        self.session.headers.update({
            'User-Agent': 'Jordan Electronics Research Bot/1.0 (+research@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Set up logger for this scraper
        self.logger = self._setup_logger()
    
    def _setup_logger(self):
        """Set up logger for this scraper instance"""
        logger_name = f"{self.__class__.__name__.lower()}"
        logger = logging.getLogger(logger_name)
        
        # Avoid duplicate handlers
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            
            # Create formatter
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            
            # File handler
            os.makedirs('logs', exist_ok=True)
            file_handler = logging.FileHandler(f'logs/{logger_name}.log')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
            
            # Console handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        
        return logger
    
    def get_page(self, url):
        """
        Get a page with error handling and rate limiting
        
        Args:
            url (str): URL to fetch
            
        Returns:
            str: HTML content or None if failed
        """
        if url in self.scraped_urls:
            self.logger.info(f"Already scraped: {url}")
            return None
            
        try:
            self.logger.info(f"Fetching: {url}")
            
            # Rate limiting
            time.sleep(self.delay)
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            self.scraped_urls.add(url)
            
            # Save HTML for debugging if status is not 200
            if response.status_code != 200:
                self._save_debug_html(url, response.text)
                
            return response.text
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _save_debug_html(self, url, html_content):
        """Save HTML to disk for debugging purposes"""
        debug_dir = f'debug_html_{self.__class__.__name__.lower()}'
        os.makedirs(debug_dir, exist_ok=True)
        
        filename = f"{debug_dir}/{urlparse(url).path.replace('/', '_')}.html"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
            self.logger.info(f"Saved debug HTML: {filename}")
        except Exception as e:
            self.logger.error(f"Failed to save debug HTML: {e}")
    
    def parse_html(self, html_content):
        """
        Parse HTML content using BeautifulSoup
        
        Args:
            html_content (str): Raw HTML content
            
        Returns:
            BeautifulSoup: Parsed HTML object
        """
        return BeautifulSoup(html_content, 'html.parser')
    
    def extract_text_with_selectors(self, soup, selectors, default=''):
        """
        Try multiple selectors to extract text from soup
        
        Args:
            soup (BeautifulSoup): Parsed HTML
            selectors (list): List of CSS selectors to try
            default (str): Default value if no selector matches
            
        Returns:
            str: Extracted text or default value
        """
        for selector in selectors:
            element = soup.select_one(selector)
            if element and element.get_text().strip():
                return element.get_text().strip()
        return default
    
    def build_absolute_url(self, relative_url):
        """
        Convert relative URL to absolute URL
        
        Args:
            relative_url (str): Relative or absolute URL
            
        Returns:
            str: Absolute URL
        """
        if relative_url.startswith('http'):
            return relative_url
        return urljoin(self.base_url, relative_url)
    
    def detect_dynamic_fields(self, product_data, product_url):
        """
        Detect and populate dynamic fields (currency, source_website, category)
        
        Args:
            product_data (dict): Product data dictionary to populate
            product_url (str): Product URL for analysis
            
        Returns:
            dict: Updated product data with dynamic fields
        """
        # 1. Extract currency from price text
        if product_data.get('price'):
            price_text = product_data['price']
            if 'د.ا' in price_text or 'JOD' in price_text.upper():
                product_data['currency'] = 'JOD'
            elif '$' in price_text or 'USD' in price_text.upper():
                product_data['currency'] = 'USD'
            elif '€' in price_text or 'EUR' in price_text.upper():
                product_data['currency'] = 'EUR'
            else:
                product_data['currency'] = 'JOD'  # Default for Jordan
        
        # 2. Detect source website from URL
        if 'leaders.jo' in product_url.lower():
            product_data['source_website'] = 'Leaders Center Jordan'
        elif 'smartbuy' in product_url.lower():
            product_data['source_website'] = 'SmartBuy Jordan'
        else:
            # Extract domain name
            domain = urlparse(product_url).netloc
            product_data['source_website'] = domain
        
        # 3. Intelligent category detection
        url_lower = product_url.lower()
        title_lower = product_data.get('title', '').lower()
        
        # Category detection based on URL patterns and product titles
        if any(keyword in url_lower or keyword in title_lower for keyword in 
               ['phone', 'mobile', 'smartphone', 'iphone', 'samsung', 'oppo', 'huawei']):
            product_data['category'] = 'Mobile Phones'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['laptop', 'computer', 'pc', 'macbook', 'notebook']):
            product_data['category'] = 'Computers & Laptops'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['watch', 'smartwatch', 'fitness', 'tracker']):
            product_data['category'] = 'Wearables'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['tv', 'television', 'monitor', 'display', 'screen']):
            product_data['category'] = 'TVs & Monitors'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['audio', 'speaker', 'headphone', 'earphone', 'sound']):
            product_data['category'] = 'Audio & Sound'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['camera', 'photo', 'video', 'lens']):
            product_data['category'] = 'Cameras & Photography'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['gaming', 'game', 'console', 'playstation', 'xbox']):
            product_data['category'] = 'Gaming'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['washing', 'dryer', 'refrigerator', 'appliance', 'washer']):
            product_data['category'] = 'Home Appliances'
        elif any(keyword in url_lower or keyword in title_lower for keyword in 
                 ['shaver', 'epilator', 'grooming', 'personal care']):
            product_data['category'] = 'Personal Care'
        else:
            product_data['category'] = 'Electronics'  # Default category
        
        return product_data
    
    def create_product_data_template(self, product_url):
        """
        Create a standard product data template
        
        Args:
            product_url (str): Product URL
            
        Returns:
            dict: Product data template with default values
        """
        return {
            'url': product_url,
            'title': '',
            'price': '',
            'currency': '',
            'source_website': '',
            'category': '',
            'brand': '',
            'description': '',
            'scraped_at': datetime.now().isoformat()
        }
    
    def reset_scraped_urls(self):
        """Reset the set of scraped URLs (useful for fresh runs)"""
        self.scraped_urls.clear()
        self.logger.info("Reset scraped URLs cache")
    
    # Abstract methods that subclasses should implement
    def find_category_links(self):
        """Find category links from main page - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement find_category_links")
    
    def get_products_from_category(self, category_url, max_products=5):
        """Get product links from category page - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement get_products_from_category")
    
    def scrape_product(self, product_url):
        """Scrape individual product - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement scrape_product")