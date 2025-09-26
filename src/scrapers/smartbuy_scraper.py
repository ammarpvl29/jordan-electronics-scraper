"""
SmartBuy Jordan scraper implementation using the hybrid architecture
Inherits from BaseScraper and focuses only on site-specific logic
"""
import sys
import os

# Add src directory to Python path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.dirname(current_dir)  # Go up one level to src/
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime

from scrapers.base_scraper import BaseScraper
from database.manager import DatabaseManager
from utils.helpers import classify_product_category, extract_currency_from_price, detect_source_website

class SmartBuyScraper(BaseScraper):
    """Scraper for SmartBuy Jordan website - inherits shared functionality from BaseScraper"""
    
    def __init__(self):
        # Initialize base scraper with SmartBuy-specific settings
        super().__init__(
            base_url="https://smartbuy-me.com",
            delay=2  # SmartBuy allows faster requests
        )
    
    def find_category_links(self):
        """Find category links from the main page - SmartBuy specific implementation"""
        self.logger.info("Looking for SmartBuy collections and categories...")
        category_links = []
        
        # Updated known categories based on actual SmartBuy website structure
        known_categories = [
            ('iPhone 12', 'https://smartbuy-me.com/collections/iphone-12'),
            ('Tablets', 'https://smartbuy-me.com/collections/tablets'),
            ('Heat Pump', 'https://smartbuy-me.com/collections/heat-pump'),
        ]
        
        # All known brands from your list
        known_brands = [
            'apple', 'samsung', 'nespresso', 'lenovo', 'dell', 'sony', 
            'asus', 'huawei', 'hp', 'xiaomi', 'beko', 'bosch', 
            'infinix', 'braun', 'canon', 'd-link'
        ]
        
        # Add brand collections
        for brand in known_brands:
            brand_name = brand.upper()
            brand_url = f"https://smartbuy-me.com/collections/{brand.lower()}"
            known_categories.append((brand_name, brand_url))
        
        # Test each known category to see if it exists and has products
        for category_name, category_url in known_categories[:10]:  # Test first 10
            self.logger.info(f"Testing category: {category_name} -> {category_url}")
            try:
                html = self.get_page(category_url)
                if html and len(html) > 2000:  # Valid page should have substantial content
                    # Quick check for product indicators
                    if ('/products/' in html or 'product' in html.lower()):
                        category_links.append((category_name, category_url))
                        self.logger.info(f"[OK] Found valid category: {category_name}")
                    else:
                        self.logger.info(f"⚠️  Category exists but may be empty: {category_name}")
                else:
                    self.logger.info(f"❌ Category not accessible: {category_name}")
            except Exception as e:
                self.logger.warning(f"Error testing category {category_name}: {e}")
        
        # Try to discover more collections from main page navigation
        try:
            html = self.get_page(self.base_url)
            if html:
                soup = self.parse_html(html)
                
                # Look for navigation menus and collection links
                nav_selectors = [
                    'nav a[href*="/collections/"]',
                    '.navigation a[href*="/collections/"]',
                    '.menu a[href*="/collections/"]',
                    'a[href*="/collections/"]'
                ]
                
                for selector in nav_selectors:
                    collection_links = soup.select(selector)
                    for link in collection_links:
                        href = link.get('href')
                        if href and '/collections/' in href:
                            full_url = self.build_absolute_url(href)
                            text = link.get_text().strip() or href.split('/')[-1].replace('-', ' ').title()
                            
                            # Skip if already have this collection
                            if (full_url not in [item[1] for item in category_links] and
                                len(text) > 2 and 
                                not any(skip in text.lower() for skip in ['home', 'about', 'contact', 'search'])):
                                
                                category_links.append((text, full_url))
                                self.logger.info(f"[COLLECTION] Discovered collection: {text} -> {full_url}")
                    
                    if len(category_links) >= 10:  # Found enough
                        break
        except Exception as e:
            self.logger.warning(f"Error discovering collections: {e}")
        
        self.logger.info(f"Total categories found: {len(category_links)}")
        # Convert list of tuples to dictionary
        category_dict = {name: url for name, url in category_links[:6]}
        return category_dict  # Return dict for compatibility
    
    def get_products_from_category(self, category_url, max_products=5):
        """Get product links from a category page - SmartBuy specific implementation"""
        self.logger.info(f"Scraping products from category: {category_url}")
        html = self.get_page(category_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
        product_links = []
        
        # SmartBuy uses /products/ URLs - look for these patterns with more specific selectors
        product_selectors = [
            'a[href*="/products/"]',  # Direct product links - most important
            '.product a[href*="/products/"]',
            '.product-item a[href*="/products/"]', 
            '.grid-item a[href*="/products/"]',
            '.collection-item a[href*="/products/"]',
            '.product-card a[href*="/products/"]',
            '.product-link[href*="/products/"]',
            '[data-product-url*="/products/"]'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            self.logger.info(f"Found {len(links)} potential product links with selector: {selector}")
            
            for link in links:
                href = link.get('href') or link.get('data-product-url')
                if href:
                    full_url = self.build_absolute_url(href)
                    
                    # Validate it's a product URL and not duplicate
                    if (self._is_product_url(full_url) and 
                        full_url not in product_links and
                        len(product_links) < max_products):
                        
                        product_links.append(full_url)
                        self.logger.info(f"[PRODUCT] Found product: {full_url}")
            
            if product_links:  # Found products with this selector, use them
                break
        
        # Enhanced fallback: Look for any links that might be products
        if not product_links:
            self.logger.info("No products found with specific selectors, trying enhanced fallback...")
            all_links = soup.find_all('a', href=True)
            
            for link in all_links:
                href = link.get('href')
                if href and len(product_links) < max_products:
                    full_url = self.build_absolute_url(href)
                    
                    # Check if it matches SmartBuy product patterns
                    if self._is_product_url(full_url) and full_url not in product_links:
                        product_links.append(full_url)
                        self.logger.info(f"🔍 Fallback found product: {full_url}")
        
        # If still no products, try to find products in page source or JavaScript
        if not product_links:
            self.logger.info("Trying to find products in page source...")
            # Look for product URLs in the HTML source directly
            import re
            product_pattern = r'https?://smartbuy-me\.com/products/[a-zA-Z0-9\-_]+'
            found_urls = re.findall(product_pattern, html)
            
            for url in found_urls[:max_products]:
                if url not in product_links:
                    product_links.append(url)
                    self.logger.info(f"� Source found product: {url}")
        
        self.logger.info(f"Total products found: {len(product_links)}")
        return product_links
    
    def _is_product_url(self, url):
        """Check if URL is a valid product URL for SmartBuy"""
        if not url or not isinstance(url, str):
            return False
            
        url_lower = url.lower().strip()
        
        # Must be SmartBuy domain
        if 'smartbuy-me.com' not in url_lower:
            return False
        
        # Must contain /products/ for individual products (main indicator)
        if '/products/' not in url_lower:
            return False
        
        # Skip obvious non-product pages even if they contain /products/
        skip_patterns = ['cart', 'checkout', 'account', 'login', 'register', 
                        'search', 'contact', 'about', 'privacy', 'terms', 
                        'shipping', 'returns', 'admin', 'api']
        
        if any(pattern in url_lower for pattern in skip_patterns):
            return False
        
        # Extract the product ID/slug from the URL
        url_parts = url_lower.split('/')
        if '/products/' in url_lower:
            try:
                product_index = url_parts.index('products')
                if product_index + 1 < len(url_parts):
                    product_id = url_parts[product_index + 1]
                    # SmartBuy product IDs should be substantial (like gts0803st0027)
                    if (len(product_id) >= 5 and 
                        product_id.replace('-', '').replace('_', '').isalnum() and
                        product_id not in ['', 'index', 'all']):
                        return True
            except ValueError:
                pass
        
        return False
    
    def test_known_product_url(self, product_url):
        """Test a known product URL to validate scraping logic"""
        self.logger.info(f"Testing known product URL: {product_url}")
        
        if not self._is_product_url(product_url):
            self.logger.error(f"❌ URL validation failed: {product_url}")
            return False
        
        product_data = self.scrape_product(product_url)
        if product_data and product_data.get('title'):
            self.logger.info(f"[SUCCESS] Successfully scraped: {product_data['title']}")
            self.logger.info(f"   Price: {product_data.get('price', 'N/A')}")
            self.logger.info(f"   Category: {product_data.get('category', 'N/A')}")
            return True
        else:
            self.logger.error(f"❌ Failed to scrape product data from: {product_url}")
            return False
    
    def scrape_product(self, product_url):
        """Scrape basic info from a product page - SmartBuy specific implementation"""
        html = self.get_page(product_url)
        if not html:
            return None
            
        soup = self.parse_html(html)
        
        # Create product data template
        product_data = self.create_product_data_template(product_url)
        
        try:
            # Title - SmartBuy specific selectors
            title_selectors = [
                'h1.product-title',
                'h1',
                '.product-name',
                '.product-title',
                '[data-product-title]',
                '.entry-title'
            ]
            product_data['title'] = self.extract_text_with_selectors(soup, title_selectors)
            
            # Price - SmartBuy specific selectors
            price_selectors = [
                '.price .amount',
                '.product-price',
                '.price',
                '.cost',
                '[data-price]',
                '.woocommerce-Price-amount'
            ]
            product_data['price'] = self.extract_text_with_selectors(soup, price_selectors)
            
            # Brand - try to extract from title or specific elements
            brand_selectors = [
                '.brand',
                '.product-brand',
                '.manufacturer',
                '[data-brand]'
            ]
            brand = self.extract_text_with_selectors(soup, brand_selectors)
            
            # If no brand found, try to extract from title
            if not brand and product_data['title']:
                # Common brand names in electronics
                brands = ['Samsung', 'Apple', 'LG', 'Sony', 'Huawei', 'Oppo', 'Xiaomi', 
                         'Dell', 'HP', 'Lenovo', 'Asus', 'Acer', 'Microsoft', 'Google']
                title_upper = product_data['title'].upper()
                for brand_name in brands:
                    if brand_name.upper() in title_upper:
                        brand = brand_name
                        break
            
            product_data['brand'] = brand
            
            # Description - SmartBuy specific selectors
            desc_selectors = [
                '.product-description',
                '.product-content',
                '.entry-content p',
                '.description',
                '.product-details'
            ]
            description = self.extract_text_with_selectors(soup, desc_selectors)
            if description:
                product_data['description'] = description[:200]  # First 200 chars
            
            # Apply dynamic field detection from base class
            product_data = self.detect_dynamic_fields(product_data, product_url)
            
            self.logger.info(f"Scraped product: {product_data['title']}")
            
        except Exception as e:
            self.logger.error(f"Error parsing product {product_url}: {e}")
        
        return product_data


def main():
    """Main function to scrape multiple products and save to database"""
    scraper = SmartBuyScraper()
    
    # Use database manager from shared module
    with DatabaseManager() as db:
        print("Starting SmartBuy scraper with database integration...")
        
        try:
            # Test known product first to validate scraping works
            print("\n[TEST] Testing known product first...")
            test_product_url = "https://smartbuy-me.com/products/gts0803st0027"
            print(f"Testing: {test_product_url}")
            
            test_product = scraper.scrape_product(test_product_url)
            if test_product and test_product.get('title'):
                print(f"[OK] Test product scraped successfully: {test_product['title']}")
                print(f"   Price: {test_product.get('price', 'N/A')}")
                print(f"   Category: {test_product.get('category', 'N/A')}")
                
                # Save test product
                if db.save_product(test_product):
                    print(f"[OK] Test product saved to database")
                else:
                    print("❌ Failed to save test product")
            else:
                print("❌ Failed to scrape test product - check selectors")
            
            # Step 1: Find categories
            print("\n1. Finding categories...")
            categories = scraper.find_category_links()
            
            if not categories:
                print("No categories found! Check the website structure.")
                # If no categories found, at least we tested the product scraping
                return
            
            print(f"Found {len(categories)} categories:")
            for name, url in categories:
                print(f"  - {name}: {url}")
            
            total_products_saved = 1 if test_product else 0  # Count test product if successful
            total_errors = 0
            
            # Step 2: Process each category (limit to avoid overwhelming)
            for category_name, category_url in categories[:2]:  # Limit to first 2 categories
                try:
                    print(f"\n2. Processing category: {category_name}")
                    
                    # Get product URLs from category
                    product_urls = scraper.get_products_from_category(category_url, max_products=3)
                    
                    if not product_urls:
                        print(f"  No products found in category: {category_name}")
                        continue
                    
                    print(f"  Found {len(product_urls)} products in {category_name}")
                    
                    # Step 3: Scrape each product and save to database
                    category_saved = 0
                    for i, product_url in enumerate(product_urls, 1):
                        try:
                            print(f"  Scraping product {i}/{len(product_urls)}...")
                            print(f"  URL: {product_url}")
                            
                            product_data = scraper.scrape_product(product_url)
                            
                            if product_data and product_data.get('title'):
                                # Save to database
                                if db.save_product(product_data):
                                    category_saved += 1
                                    total_products_saved += 1
                                    print(f"    [OK] Saved: {product_data['title'][:50]}...")
                                    print(f"    Price: {product_data.get('price', 'N/A')}")
                                    print(f"    Category: {product_data.get('category', 'N/A')}")
                                else:
                                    print(f"    ❌ Failed to save product")
                                    total_errors += 1
                            else:
                                print(f"    ❌ Failed to scrape product data")
                                total_errors += 1
                                
                        except Exception as e:
                            total_errors += 1
                            print(f"    ❌ Error with product: {e}")
                    
                    print(f"  Category {category_name}: {category_saved} products saved")
                    
                except Exception as e:
                    print(f"❌ Error processing category {category_name}: {e}")
                    total_errors += 1
            
            # Log the session
            status = "success" if total_products_saved > 0 else "failed"
            db.log_scraping_session(
                website="SmartBuy Jordan",
                status=status,
                products_count=total_products_saved,
                notes=f"Processed {len(categories[:2]) if categories else 0} categories, {total_errors} errors"
            )
            
            print(f"\n[COMPLETE] Scraping completed!")
            print(f"Total products saved: {total_products_saved}")
            print(f"Total errors: {total_errors}")
            
        except Exception as e:
            print(f"❌ Fatal error: {e}")
            db.log_scraping_session(
                website="SmartBuy Jordan",
                status="failed",
                products_count=0,
                notes=f"Fatal error: {str(e)}"
            )


if __name__ == "__main__":
    main()