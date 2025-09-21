"""
Simple web scraper for SmartBuy Jordan
Respects robots.txt and follows best practices
"""
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import logging
from datetime import datetime
from pymongo import MongoClient
import os

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DatabaseManager:
    """Simple database manager for saving products"""
    
    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['jordan_electronics']
        self.products = self.db['products']
        self.logs = self.db['scraping_logs']
    
    def save_product(self, product_data):
        """Save product to database"""
        try:
            # Use upsert to avoid duplicates based on URL
            result = self.products.update_one(
                {'url': product_data['url']},  # Filter
                {'$set': product_data},        # Update
                upsert=True                    # Insert if not exists
            )
            
            if result.upserted_id:
                logger.info(f"✅ New product saved: {product_data['title']}")
                return True
            else:
                logger.info(f"✅ Product updated: {product_data['title']}")
                return True
                
        except Exception as e:
            logger.error(f"❌ Failed to save product: {e}")
            return False
    
    def log_scraping_session(self, website, status, products_count, notes=""):
        """Log scraping session"""
        try:
            log_entry = {
                'website': website,
                'status': status,
                'products_scraped': products_count,
                'timestamp': datetime.now(),
                'notes': notes
            }
            
            self.logs.insert_one(log_entry)
            logger.info(f"✅ Logged scraping session for {website}")
            
        except Exception as e:
            logger.error(f"❌ Failed to log session: {e}")
    
    def close(self):
        """Close database connection"""
        self.client.close()

class SmartBuyScraper:
    def __init__(self):
        self.base_url = "https://smartbuy-me.com"
        self.session = requests.Session()
        
        # Respectful headers
        self.session.headers.update({
            'User-Agent': 'Jordan Electronics Research Bot/1.0 (+your-email@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Track scraped URLs to avoid duplicates
        self.scraped_urls = set()
        
        # Rate limiting - be respectful
        self.delay = 2  # seconds between requests
        
    def get_page(self, url):
        """Get a page with error handling and rate limiting"""
        if url in self.scraped_urls:
            logger.info(f"Already scraped: {url}")
            return None
            
        try:
            logger.info(f"Fetching: {url}")
            
            # Rate limiting
            time.sleep(self.delay)
            
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            self.scraped_urls.add(url)
            
            # Save HTML for debugging if needed
            if response.status_code != 200:
                self.save_debug_html(url, response.text)
                
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def save_debug_html(self, url, html_content):
        """Save HTML to disk for debugging"""
        os.makedirs('debug_html', exist_ok=True)
        filename = f"debug_html/{urlparse(url).path.replace('/', '_')}.html"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        logger.info(f"Saved debug HTML: {filename}")
    
    def find_category_links(self):
        """Find category links from the main page"""
        html = self.get_page(self.base_url)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        category_links = []
        
        # Look for navigation menu links
        # Common selectors for category links
        nav_selectors = [
            'nav a[href*="/collections/"]',
            '.navigation a[href*="/collections/"]',
            '.menu a[href*="/collections/"]',
            'a[href*="/collections/"]'
        ]
        
        for selector in nav_selectors:
            links = soup.select(selector)
            for link in links[:5]:  # Limit to first 5 for testing
                href = link.get('href')
                if href and '/collections/' in href:
                    full_url = urljoin(self.base_url, href)
                    text = link.get_text().strip()
                    if text and full_url not in [item[1] for item in category_links]:
                        category_links.append((text, full_url))
                        logger.info(f"Found category: {text} -> {full_url}")
            
            if category_links:  # If we found some, use them
                break
        
        return category_links
    
    def get_products_from_category(self, category_url, max_products=5):
        """Get product links from a category page"""
        html = self.get_page(category_url)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        product_links = []
        
        # Common selectors for product links
        product_selectors = [
            'a[href*="/products/"]',
            '.product-item a',
            '.product-card a',
            '.product a'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            for link in links[:max_products]:
                href = link.get('href')
                if href and '/products/' in href:
                    full_url = urljoin(self.base_url, href)
                    if full_url not in product_links:
                        product_links.append(full_url)
                        logger.info(f"Found product: {full_url}")
            
            if product_links:  # If we found some, use them
                break
        
        return product_links
    
    def scrape_product(self, product_url):
        """Scrape basic info from a product page"""
        html = self.get_page(product_url)
        if not html:
            return None
            
        soup = BeautifulSoup(html, 'html.parser')
        
        product_data = {
            'url': product_url,
            'title': '',
            'price': '',
            'brand': '',
            'description': '',
            'scraped_at': datetime.now().isoformat()
        }
        
        try:
            # Title - common selectors
            title_selectors = ['h1', '.product-title', '.product-name', '[data-product-title]']
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    product_data['title'] = title_elem.get_text().strip()
                    break
            
            # Price - common selectors  
            price_selectors = ['.price', '.product-price', '[data-price]', '.money']
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem:
                    product_data['price'] = price_elem.get_text().strip()
                    break
            
            # Description - first paragraph or description div
            desc_selectors = ['.product-description', '.description', '.product-info p']
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    product_data['description'] = desc_elem.get_text().strip()[:200]  # First 200 chars
                    break
            
            logger.info(f"Scraped product: {product_data['title']}")
            
        except Exception as e:
            logger.error(f"Error parsing product {product_url}: {e}")
        
        return product_data

def main():
    """Main function to scrape multiple products and save to database"""
    scraper = SmartBuyScraper()
    db = DatabaseManager()
    
    print("Starting SmartBuy scraper with database integration...")
    
    try:
        # Step 1: Find categories
        print("\n1. Finding categories...")
        categories = scraper.find_category_links()
        
        if not categories:
            print("No categories found! Check the website structure.")
            return
        
        print(f"Found {len(categories)} categories:")
        for name, url in categories:
            print(f"  - {name}: {url}")
        
        total_products_saved = 0
        total_errors = 0
        
        # Step 2: Process each category
        for category_name, category_url in categories[:2]:  # Limit to first 2 categories
            try:
                print(f"\n2. Processing category: {category_name}")
                
                # Get product URLs from category
                product_urls = scraper.get_products_from_category(category_url, max_products=5)
                
                if not product_urls:
                    print(f"No products found in category: {category_name}")
                    continue
                    
                print(f"Found {len(product_urls)} products in {category_name}")
                
                # Step 3: Scrape each product and save to database
                category_saved = 0
                for i, product_url in enumerate(product_urls, 1):
                    try:
                        print(f"  Scraping product {i}/{len(product_urls)}...")
                        product_data = scraper.scrape_product(product_url)
                        
                        if product_data and product_data.get('title'):
                            product_data['category'] = category_name
                            
                            # Save to database
                            if db.save_product(product_data):
                                category_saved += 1
                                total_products_saved += 1
                                print(f"  ✅ Saved: {product_data['title'][:50]}...")
                            else:
                                total_errors += 1
                                print(f"  ❌ Failed to save product")
                        else:
                            total_errors += 1
                            print(f"  ❌ Failed to scrape product: {product_url}")
                            
                    except Exception as e:
                        total_errors += 1
                        print(f"  ❌ Error with product {product_url}: {e}")
                
                print(f"Category {category_name}: {category_saved} products saved")
                
            except Exception as e:
                total_errors += 1
                print(f"❌ Error processing category {category_name}: {e}")
        
        # Log the session
        status = "success" if total_products_saved > 0 else "failed"
        db.log_scraping_session(
            website="SmartBuy Jordan",
            status=status,
            products_count=total_products_saved,
            notes=f"Scraped {len(categories[:2])} categories, {total_errors} errors"
        )
        
        print(f"\n✅ Scraping completed!")
        print(f"Total products saved: {total_products_saved}")
        print(f"Total errors: {total_errors}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        db.log_scraping_session(
            website="SmartBuy Jordan",
            status="failed",
            products_count=total_products_saved,
            notes=f"Fatal error: {str(e)}"
        )
    
    finally:
        db.close()

if __name__ == "__main__":
    main()