"""
Simple web scraper for Leaders.jo (English version)
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
        logging.FileHandler('leaders_scraper.log'),
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

class LeadersScraper:
    def __init__(self):
        self.base_url = "https://leaders.jo/en/"  # English version
        self.session = requests.Session()
        
        # Respectful headers
        self.session.headers.update({
            'User-Agent': 'Jordan Electronics Research Bot/1.0 (+research@example.com)',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
        # Track scraped URLs to avoid duplicates
        self.scraped_urls = set()
        
        # Rate limiting - respect robots.txt crawl delay of 10 seconds
        self.delay = 10  # seconds between requests as per robots.txt
        
    def get_page(self, url):
        """Get a page with error handling and rate limiting"""
        if url in self.scraped_urls:
            logger.info(f"Already scraped: {url}")
            return None
            
        try:
            logger.info(f"Fetching: {url}")
            
            # Rate limiting - respect robots.txt crawl delay
            time.sleep(self.delay)
            
            response = self.session.get(url, timeout=15)
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
        os.makedirs('debug_html_leaders', exist_ok=True)
        filename = f"debug_html_leaders/{urlparse(url).path.replace('/', '_')}.html"
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
        
        # Look for navigation menu links - try various selectors
        nav_selectors = [
            'nav a',
            '.navigation a',
            '.menu a',
            '.navbar a',
            '.main-menu a',
            '.category-menu a',
            'header a'
        ]
        
        for selector in nav_selectors:
            links = soup.select(selector)
            for link in links[:10]:  # Limit to first 10 for testing
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and text:
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = urljoin(self.base_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # Filter for category-like links (electronics related)
                    electronics_keywords = ['laptop', 'computer', 'mobile', 'phone', 'tablet', 
                                          'electronics', 'gaming', 'audio', 'camera', 'tv',
                                          'monitor', 'printer', 'accessories', 'apple', 'samsung']
                    
                    if (any(keyword in text.lower() for keyword in electronics_keywords) or
                        any(keyword in href.lower() for keyword in electronics_keywords)):
                        
                        if full_url not in [item[1] for item in category_links]:
                            category_links.append((text, full_url))
                            logger.info(f"Found category: {text} -> {full_url}")
            
            if category_links:  # If we found some, break
                break
        
        # If no specific categories found, try to find any product-containing pages
        if not category_links:
            logger.info("No specific categories found, looking for any product pages...")
            product_links = soup.select('a[href*="product"]')
            for link in product_links[:3]:
                href = link.get('href')
                text = link.get_text().strip() or "Product Page"
                if href:
                    full_url = urljoin(self.base_url, href)
                    category_links.append((text, full_url))
                    logger.info(f"Found product page: {text} -> {full_url}")
        
        return category_links
    
    def get_products_from_category(self, category_url, max_products=5):
        """Get product links from a category page"""
        html = self.get_page(category_url)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        product_links = []
        
        # Look specifically for actual product links with /product/ pattern
        product_selectors = [
            'a[href*="/product/"]',  # Actual product pages
            '.product a[href*="/product/"]',
            '.product-item a[href*="/product/"]',
            '.product-card a[href*="/product/"]'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            for link in links[:max_products]:
                href = link.get('href')
                if href and '/product/' in href:  # Must contain /product/
                    # Convert relative URLs to absolute
                    if href.startswith('/'):
                        full_url = urljoin(self.base_url, href)
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        continue
                    
                    # Avoid category pages and ensure it's an actual product
                    if '/product-category/' not in full_url and full_url not in product_links:
                        product_links.append(full_url)
                        logger.info(f"Found product: {full_url}")
            
            if product_links:  # If we found some, use them
                break
        
        # If no products found with /product/ pattern, try to find them on the main products page
        if not product_links:
            logger.info("No products found in category, trying main products page...")
            main_products_url = "https://leaders.jo/en/products/"
            main_html = self.get_page(main_products_url)
            if main_html:
                main_soup = BeautifulSoup(main_html, 'html.parser')
                main_links = main_soup.select('a[href*="/product/"]')
                for link in main_links[:max_products]:
                    href = link.get('href')
                    if href and '/product/' in href:
                        full_url = urljoin(self.base_url, href)
                        if '/product-category/' not in full_url:
                            product_links.append(full_url)
                            logger.info(f"Found product from main page: {full_url}")
        
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
            # Title - try multiple selectors
            title_selectors = [
                'h1',
                '.product-title',
                '.product-name', 
                '.title',
                '[data-product-title]',
                '.product-info h1',
                '.product-details h1'
            ]
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem and title_elem.get_text().strip():
                    product_data['title'] = title_elem.get_text().strip()
                    break
            
            # Price - try multiple selectors
            price_selectors = [
                '.price',
                '.product-price',
                '.cost',
                '.amount',
                '[data-price]',
                '.money',
                '.price-current',
                '.sale-price'
            ]
            for selector in price_selectors:
                price_elem = soup.select_one(selector)
                if price_elem and price_elem.get_text().strip():
                    product_data['price'] = price_elem.get_text().strip()
                    break
            
            # Brand - try to find brand info
            brand_selectors = [
                '.brand',
                '.manufacturer',
                '.product-brand',
                '[data-brand]'
            ]
            for selector in brand_selectors:
                brand_elem = soup.select_one(selector)
                if brand_elem and brand_elem.get_text().strip():
                    product_data['brand'] = brand_elem.get_text().strip()
                    break
            
            # Description - first paragraph or description div
            desc_selectors = [
                '.product-description',
                '.description',
                '.product-info p',
                '.details',
                '.product-details p'
            ]
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem and desc_elem.get_text().strip():
                    product_data['description'] = desc_elem.get_text().strip()[:200]  # First 200 chars
                    break
            
            logger.info(f"Scraped product: {product_data['title']}")
            
        except Exception as e:
            logger.error(f"Error parsing product {product_url}: {e}")
        
        return product_data

def main():
    """Main function to scrape multiple products and save to database"""
    scraper = LeadersScraper()
    db = DatabaseManager()
    
    print("Starting Leaders.jo scraper with database integration...")
    
    try:
        # Known working product URLs for reliable testing
        known_products = [
            'https://leaders.jo/en/product/oppo-reno-14-five-g-512gb-12-ram/',
            'https://leaders.jo/en/product/reebok-relay-sport-smartwatch/',
        ]
        
        total_products_saved = 0
        total_errors = 0
        
        # Step 1: Try to find more products from main page
        print("\n1. Finding additional products from main page...")
        try:
            additional_products = []
            html = scraper.get_page('https://leaders.jo/en/')
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                product_links = soup.select('a[href*="/product/"]')
                
                for link in product_links[:3]:  # Get first 3 found
                    href = link.get('href')
                    if href and '/product/' in href and '/product-category/' not in href:
                        if href.startswith('/'):
                            product_url = 'https://leaders.jo' + href
                        else:
                            product_url = href
                        
                        if product_url not in known_products:
                            additional_products.append(product_url)
                            logger.info(f"Found additional product: {product_url}")
            
            # Combine known products with discovered ones
            all_products = known_products + additional_products
            
        except Exception as e:
            logger.warning(f"Error finding additional products: {e}")
            all_products = known_products
        
        print(f"Total products to scrape: {len(all_products)}")
        
        # Step 2: Scrape each product
        for i, product_url in enumerate(all_products, 1):
            try:
                print(f"\n2. Scraping product {i}/{len(all_products)}...")
                print(f"   URL: {product_url}")
                
                product_data = scraper.scrape_product(product_url)
                
                if product_data and product_data.get('title'):
                    # Save to database
                    if db.save_product(product_data):
                        total_products_saved += 1
                        print(f"   ✅ Saved: {product_data['title'][:50]}...")
                        print(f"   Price: {product_data.get('price', 'N/A')}")
                    else:
                        total_errors += 1
                        print(f"   ❌ Failed to save product")
                else:
                    total_errors += 1
                    print(f"   ❌ Failed to scrape product data")
                    
            except Exception as e:
                total_errors += 1
                print(f"   ❌ Error with product {product_url}: {e}")
        
        # Log the session
        status = "success" if total_products_saved > 0 else "failed"
        db.log_scraping_session(
            website="Leaders Center Jordan",
            status=status,
            products_count=total_products_saved,
            notes=f"Scraped {len(all_products)} product URLs, {total_errors} errors"
        )
        
        print(f"\n✅ Scraping completed!")
        print(f"Total products saved: {total_products_saved}")
        print(f"Total errors: {total_errors}")
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        db.log_scraping_session(
            website="Leaders Center Jordan",
            status="failed",
            products_count=total_products_saved,
            notes=f"Fatal error: {str(e)}"
        )
    
    finally:
        db.close()

if __name__ == "__main__":
    main()