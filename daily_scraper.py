"""
Daily scraping orchestrator for Jordan Electronics Scraper
Runs both Leaders.jo and SmartBuy scrapers in sequence
Designed for GitHub Actions automation
"""

import sys
import os
import traceback
from datetime import datetime
import logging

# Add src directory to Python path for absolute imports
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir  # We're running from project root
src_dir = os.path.join(project_root, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

def setup_logging():
    """Set up logging for the daily scraping process"""
    # Ensure logs directory exists
    logs_dir = os.path.join(project_root, 'logs')
    os.makedirs(logs_dir, exist_ok=True)
    
    # Set up logging to both file and console
    log_file = os.path.join(logs_dir, f'daily_scraping_{datetime.now().strftime("%Y%m%d")}.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

def run_leaders_scraper():
    """Run the Leaders.jo scraper"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("STARTING LEADERS.JO SCRAPER")
    logger.info("=" * 50)
    
    try:
        from scrapers.leaders_scraper import LeadersScraper
        from database.manager import DatabaseManager
        
        scraper = LeadersScraper()
        products_saved = 0
        errors = 0
        
        with DatabaseManager() as db:
            logger.info("Leaders scraper initialized successfully")
            
            # Known working product URLs for reliable daily scraping
            known_products = [
                'https://leaders.jo/en/product/oppo-reno-14-five-g-512gb-12-ram/',
            ]
            
            # Try to find additional products from main page
            try:
                logger.info("Discovering additional products from main page...")
                html = scraper.get_page('https://leaders.jo/en/')
                if html:
                    soup = scraper.parse_html(html)
                    product_links = soup.select('a[href*="/product/"]')
                    
                    additional_products = []
                    for link in product_links[:3]:  # Get 3 additional products
                        href = link.get('href')
                        if href and '/product/' in href and '/product-category/' not in href:
                            product_url = scraper.build_absolute_url(href)
                            if product_url not in known_products:
                                additional_products.append(product_url)
                                logger.info(f"Found additional product: {product_url}")
                    
                    known_products.extend(additional_products)
                    
            except Exception as e:
                logger.warning(f"Error discovering additional products: {e}")
            
            logger.info(f"Total products to scrape: {len(known_products)}")
            
            # Scrape each product
            for i, product_url in enumerate(known_products, 1):
                try:
                    logger.info(f"Scraping product {i}/{len(known_products)}: {product_url}")
                    
                    product_data = scraper.scrape_product(product_url)
                    
                    if product_data and product_data.get('title'):
                        if db.save_product(product_data):
                            products_saved += 1
                            logger.info(f"✅ Saved: {product_data['title'][:50]}... | Price: {product_data.get('price', 'N/A')}")
                        else:
                            errors += 1
                            logger.error(f"❌ Failed to save product to database")
                    else:
                        errors += 1
                        logger.error(f"❌ Failed to scrape product data")
                        
                except Exception as e:
                    errors += 1
                    logger.error(f"❌ Error with product {product_url}: {e}")
            
            # Log the session
            status = "success" if products_saved > 0 else "failed"
            db.log_scraping_session(
                website="Leaders Center Jordan",
                status=status,
                products_count=products_saved,
                notes=f"Daily automated scraping: {len(known_products)} URLs, {errors} errors"
            )
            
        logger.info(f"Leaders.jo scraping completed: {products_saved} products saved, {errors} errors")
        return {"success": products_saved > 0, "products": products_saved, "errors": errors}
        
    except Exception as e:
        logger.error(f"Fatal error in Leaders scraper: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "products": 0, "errors": 1, "fatal_error": str(e)}

def run_smartbuy_scraper():
    """Run the SmartBuy Jordan scraper"""
    logger = logging.getLogger(__name__)
    logger.info("=" * 50)
    logger.info("STARTING SMARTBUY JORDAN SCRAPER")
    logger.info("=" * 50)
    
    try:
        from scrapers.smartbuy_scraper import SmartBuyScraper
        from database.manager import DatabaseManager
        
        scraper = SmartBuyScraper()
        products_saved = 0
        errors = 0
        
        with DatabaseManager() as db:
            logger.info("SmartBuy scraper initialized successfully")
            
            # Test with known working product first
            test_product_url = "https://smartbuy-me.com/products/gts0803st0027"
            logger.info(f"Testing known product: {test_product_url}")
            
            test_product = scraper.scrape_product(test_product_url)
            if test_product and test_product.get('title'):
                if db.save_product(test_product):
                    products_saved += 1
                    logger.info(f"✅ Test product saved: {test_product['title'][:50]}...")
                else:
                    errors += 1
                    logger.error("❌ Failed to save test product")
            else:
                errors += 1
                logger.error("❌ Failed to scrape test product")
            
            # Find categories and scrape products
            try:
                logger.info("Finding product categories...")
                categories = scraper.find_category_links()
                
                if categories:
                    logger.info(f"Found {len(categories)} categories")
                    
                    # Process first 2 categories to avoid overwhelming the system
                    for category_name, category_url in list(categories.items())[:2]:
                        try:
                            logger.info(f"Processing category: {category_name}")
                            
                            product_urls = scraper.get_products_from_category(category_url, max_products=2)
                            
                            if product_urls:
                                logger.info(f"Found {len(product_urls)} products in {category_name}")
                                
                                for product_url in product_urls:
                                    try:
                                        logger.info(f"Scraping: {product_url}")
                                        
                                        product_data = scraper.scrape_product(product_url)
                                        
                                        if product_data and product_data.get('title'):
                                            if db.save_product(product_data):
                                                products_saved += 1
                                                logger.info(f"✅ Saved: {product_data['title'][:50]}... | Price: {product_data.get('price', 'N/A')}")
                                            else:
                                                errors += 1
                                                logger.error("❌ Failed to save product")
                                        else:
                                            errors += 1
                                            logger.error("❌ Failed to scrape product data")
                                            
                                    except Exception as e:
                                        errors += 1
                                        logger.error(f"❌ Error with product: {e}")
                            else:
                                logger.info(f"No products found in category: {category_name}")
                                
                        except Exception as e:
                            errors += 1
                            logger.error(f"❌ Error processing category {category_name}: {e}")
                else:
                    logger.warning("No categories found")
                    
            except Exception as e:
                errors += 1
                logger.error(f"Error in category processing: {e}")
            
            # Log the session
            status = "success" if products_saved > 0 else "failed"
            db.log_scraping_session(
                website="SmartBuy Jordan",
                status=status,
                products_count=products_saved,
                notes=f"Daily automated scraping: {errors} errors"
            )
            
        logger.info(f"SmartBuy scraping completed: {products_saved} products saved, {errors} errors")
        return {"success": products_saved > 0, "products": products_saved, "errors": errors}
        
    except Exception as e:
        logger.error(f"Fatal error in SmartBuy scraper: {e}")
        logger.error(traceback.format_exc())
        return {"success": False, "products": 0, "errors": 1, "fatal_error": str(e)}

def main():
    """Main orchestrator function"""
    logger = setup_logging()
    
    logger.info("🚀 STARTING DAILY JORDAN ELECTRONICS SCRAPING")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")
    logger.info("=" * 70)
    
    # Track overall results
    total_products = 0
    total_errors = 0
    scraper_results = {}
    
    # Run Leaders.jo scraper
    try:
        leaders_result = run_leaders_scraper()
        scraper_results['leaders'] = leaders_result
        total_products += leaders_result['products']
        total_errors += leaders_result['errors']
    except Exception as e:
        logger.error(f"Failed to run Leaders scraper: {e}")
        scraper_results['leaders'] = {"success": False, "products": 0, "errors": 1}
        total_errors += 1
    
    # Run SmartBuy scraper
    try:
        smartbuy_result = run_smartbuy_scraper()
        scraper_results['smartbuy'] = smartbuy_result
        total_products += smartbuy_result['products']
        total_errors += smartbuy_result['errors']
    except Exception as e:
        logger.error(f"Failed to run SmartBuy scraper: {e}")
        scraper_results['smartbuy'] = {"success": False, "products": 0, "errors": 1}
        total_errors += 1
    
    # Final summary
    logger.info("=" * 70)
    logger.info("📊 DAILY SCRAPING SUMMARY")
    logger.info("=" * 70)
    
    for scraper_name, result in scraper_results.items():
        status = "✅ SUCCESS" if result['success'] else "❌ FAILED"
        logger.info(f"{scraper_name.upper():.<20} {status}")
        logger.info(f"{'Products saved':.<20} {result['products']}")
        logger.info(f"{'Errors':.<20} {result['errors']}")
        if 'fatal_error' in result:
            logger.info(f"{'Fatal error':.<20} {result['fatal_error']}")
        logger.info("-" * 30)
    
    logger.info(f"TOTAL PRODUCTS SAVED: {total_products}")
    logger.info(f"TOTAL ERRORS: {total_errors}")
    
    overall_success = total_products > 0
    logger.info(f"OVERALL STATUS: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")
    
    # Exit with proper code for GitHub Actions
    if not overall_success and total_errors > 0:
        logger.error("Daily scraping failed - no products saved with errors")
        sys.exit(1)
    elif not overall_success:
        logger.warning("Daily scraping completed but no new products found")
        sys.exit(0)  # Don't fail if no products, might be due to duplicates
    else:
        logger.info("Daily scraping completed successfully!")
        sys.exit(0)

if __name__ == "__main__":
    main()