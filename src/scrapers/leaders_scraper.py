"""
Leaders.jo scraper implementation using the hybrid architecture
Inherits from BaseScraper and focuses only on site-specific logic
"""
import sys
import os

# Set up proper encoding for Windows console output
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

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

class LeadersScraper(BaseScraper):
    """Scraper for Leaders.jo website - inherits shared functionality from BaseScraper"""
    
    def __init__(self):
        # Initialize base scraper with Leaders-specific settings
        # Use shorter delay for testing, can be increased for production
        super().__init__(
            base_url="https://leaders.jo/en/",
            delay=3  # Reduced delay for testing - increase to 10 for production
        )
    
    def find_category_links(self):
        """Find category links from the main page - Leaders.jo specific implementation"""
        html = self.get_page(self.base_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
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
                    full_url = self.build_absolute_url(href)
                    
                    # Filter for category-like links (electronics related)
                    electronics_keywords = ['laptop', 'computer', 'mobile', 'phone', 'tablet', 
                                          'electronics', 'gaming', 'audio', 'camera', 'tv',
                                          'monitor', 'printer', 'accessories', 'apple', 'samsung']
                    
                    if (any(keyword in text.lower() for keyword in electronics_keywords) or
                        any(keyword in href.lower() for keyword in electronics_keywords)):
                        
                        if full_url not in [item[1] for item in category_links]:
                            category_links.append((text, full_url))
                            self.logger.info(f"Found category: {text} -> {full_url}")
            
            if category_links:  # If we found some, break
                break
        
        # If no specific categories found, try to find any product-containing pages
        if not category_links:
            self.logger.info("No specific categories found, looking for any product pages...")
            product_links = soup.select('a[href*="product"]')
            for link in product_links[:3]:
                href = link.get('href')
                text = link.get_text().strip() or "Product Page"
                if href:
                    full_url = self.build_absolute_url(href)
                    category_links.append((text, full_url))
                    self.logger.info(f"Found product page: {text} -> {full_url}")
        
        return category_links
    
    def get_products_from_category(self, category_url, max_products=5):
        """Get product links from a category page - Leaders.jo specific implementation"""
        html = self.get_page(category_url)
        if not html:
            return []
            
        soup = self.parse_html(html)
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
                    full_url = self.build_absolute_url(href)
                    
                    # Avoid category pages and ensure it's an actual product
                    if '/product-category/' not in full_url and full_url not in product_links:
                        product_links.append(full_url)
                        self.logger.info(f"Found product: {full_url}")
            
            if product_links:  # If we found some, use them
                break
        
        # If no products found with /product/ pattern, try to find them on the main products page
        if not product_links:
            self.logger.info("No products found in category, trying main products page...")
            main_products_url = "https://leaders.jo/en/products/"
            main_html = self.get_page(main_products_url)
            if main_html:
                main_soup = self.parse_html(main_html)
                main_links = main_soup.select('a[href*="/product/"]')
                for link in main_links[:max_products]:
                    href = link.get('href')
                    if href and '/product/' in href:
                        full_url = self.build_absolute_url(href)
                        if '/product-category/' not in full_url:
                            product_links.append(full_url)
                            self.logger.info(f"Found product from main page: {full_url}")
        
        return product_links
    
    def scrape_product(self, product_url):
        """Scrape basic info from a product page - Leaders.jo specific implementation"""
        html = self.get_page(product_url)
        if not html:
            return None
            
        soup = self.parse_html(html)
        
        # Create product data template
        product_data = self.create_product_data_template(product_url)
        
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
            product_data['title'] = self.extract_text_with_selectors(soup, title_selectors)
            
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
            product_data['price'] = self.extract_text_with_selectors(soup, price_selectors)
            
            # Brand - try to find brand info
            brand_selectors = [
                '.brand',
                '.manufacturer',
                '.product-brand',
                '[data-brand]'
            ]
            product_data['brand'] = self.extract_text_with_selectors(soup, brand_selectors)
            
            # Description - first paragraph or description div
            desc_selectors = [
                '.product-description',
                '.description',
                '.product-info p',
                '.details',
                '.product-details p'
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
    scraper = LeadersScraper()
    
    # Use database manager from shared module
    with DatabaseManager() as db:
        print("Starting Leaders.jo scraper with database integration...")
        
        try:
            # Known working product URLs for reliable testing
            known_products = [
                'https://leaders.jo/en/product/oppo-reno-14-five-g-512gb-12-ram/',
                # Only test with 1 product to avoid timeout during development
                # 'https://leaders.jo/en/product/reebok-relay-sport-smartwatch/',
            ]
            
            total_products_saved = 0
            total_errors = 0
            
            # Step 1: Try to find more products from main page
            print("\n1. Finding additional products from main page...")
            try:
                additional_products = []
                html = scraper.get_page('https://leaders.jo/en/')
                if html:
                    soup = scraper.parse_html(html)
                    product_links = soup.select('a[href*="/product/"]')
                    
                    for link in product_links[:1]:  # Get only 1 additional for testing
                        href = link.get('href')
                        if href and '/product/' in href and '/product-category/' not in href:
                            product_url = scraper.build_absolute_url(href)
                            
                            if product_url not in known_products:
                                additional_products.append(product_url)
                                scraper.logger.info(f"Found additional product: {product_url}")
                
                # Combine known products with discovered ones
                all_products = known_products + additional_products
                
            except Exception as e:
                scraper.logger.warning(f"Error finding additional products: {e}")
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
                            # Handle encoding issues for console output
                            title = str(product_data['title'])[:50]
                            price = str(product_data.get('price', 'N/A'))
                            try:
                                print(f"   Saved: {title}...")
                                print(f"   Price: {price}")
                            except UnicodeEncodeError:
                                print(f"   Saved: [Product with special characters]...")
                                print(f"   Price: {price}")
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


if __name__ == "__main__":
    main()