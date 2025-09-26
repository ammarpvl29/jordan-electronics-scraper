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
        html = self.get_page(self.base_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
        category_links = []
        
        # SmartBuy-specific selectors for categories
        category_selectors = [
            '.categories a',
            '.category-menu a',
            '.product-categories a',
            'nav .menu-item a',
            '.main-navigation a'
        ]
        
        for selector in category_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and text and len(text) > 2:  # Meaningful text
                    full_url = self.build_absolute_url(href)
                    
                    # Filter for electronics-related categories
                    if (not any(skip in text.lower() for skip in ['home', 'about', 'contact', 'cart', 'account']) and
                        full_url not in [item[1] for item in category_links]):
                        
                        category_links.append((text, full_url))
                        self.logger.info(f"Found category: {text} -> {full_url}")
            
            if category_links:  # Found categories, use them
                break
        
        # Fallback: Look for any product-containing links
        if not category_links:
            self.logger.info("No categories found, looking for product-containing pages...")
            all_links = soup.find_all('a', href=True)
            for link in all_links[:20]:  # Check first 20 links
                href = link.get('href')
                text = link.get_text().strip()
                
                if href and 'product' in href.lower():
                    full_url = self.build_absolute_url(href)
                    category_name = text or "Products"
                    
                    if full_url not in [item[1] for item in category_links]:
                        category_links.append((category_name, full_url))
                        self.logger.info(f"Found product page: {category_name} -> {full_url}")
        
        return category_links[:5]  # Limit to 5 categories for testing
    
    def get_products_from_category(self, category_url, max_products=5):
        """Get product links from a category page - SmartBuy specific implementation"""
        html = self.get_page(category_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
        product_links = []
        
        # SmartBuy-specific selectors for products
        product_selectors = [
            '.product a[href*="product"]',
            '.product-item a',
            '.woocommerce-LoopProduct-link',
            'a[href*="/product/"]',
            '.product-card a',
            '.item-product a'
        ]
        
        for selector in product_selectors:
            links = soup.select(selector)
            for link in links[:max_products]:
                href = link.get('href')
                if href:
                    full_url = self.build_absolute_url(href)
                    
                    # Validate it's a product URL and not duplicate
                    if (self._is_product_url(full_url) and 
                        full_url not in product_links):
                        product_links.append(full_url)
                        self.logger.info(f"Found product: {full_url}")
            
            if product_links:  # Found products, use them
                break
        
        return product_links
    
    def _is_product_url(self, url):
        """Check if URL is a valid product URL for SmartBuy"""
        url_lower = url.lower()
        return (
            'smartbuy' in url_lower and
            ('product' in url_lower or '/p/' in url_lower) and
            not any(skip in url_lower for skip in ['cart', 'checkout', 'account', 'category'])
        )
    
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
                        print(f"  No products found in category: {category_name}")
                        continue
                    
                    print(f"  Found {len(product_urls)} products in {category_name}")
                    
                    # Step 3: Scrape each product and save to database
                    category_saved = 0
                    for i, product_url in enumerate(product_urls, 1):
                        try:
                            print(f"  Scraping product {i}/{len(product_urls)}...")
                            product_data = scraper.scrape_product(product_url)
                            
                            if product_data and product_data.get('title'):
                                # If category wasn't detected dynamically, use the category name from URL
                                if not product_data.get('category') or product_data['category'] == 'Electronics':
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
                    
                    print(f"  Saved {category_saved} products from {category_name}")
                    
                except Exception as e:
                    total_errors += 1
                    print(f"❌ Error processing category {category_name}: {e}")
            
            # Log the session
            status = "success" if total_products_saved > 0 else "failed"
            db.log_scraping_session(
                website="SmartBuy Jordan",
                status=status,
                products_count=total_products_saved,
                notes=f"Processed {len(categories[:2])} categories, {total_errors} errors"
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


if __name__ == "__main__":
    main()