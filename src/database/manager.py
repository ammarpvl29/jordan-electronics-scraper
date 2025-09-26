"""
Database manager for handling MongoDB operations
Shared across all scrapers to eliminate code duplication
"""
import logging
from datetime import datetime, timedelta
from pymongo import MongoClient

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Manages MongoDB operations for product data and scraping logs"""
    
    def __init__(self, connection_string='mongodb://localhost:27017/', database_name='jordan_electronics'):
        """
        Initialize database connection
        
        Args:
            connection_string (str): MongoDB connection string
            database_name (str): Database name to use
        """
        self.connection_string = connection_string
        self.database_name = database_name
        
        # Initialize connection
        self.client = MongoClient(connection_string)
        self.db = self.client[database_name]
        self.products = self.db['products']
        self.logs = self.db['scraping_logs']
        
        # Create indexes for better performance
        self._create_indexes()
        
        logger.info(f"Connected to MongoDB database: {database_name}")
    
    def _create_indexes(self):
        """Create database indexes for better performance"""
        try:
            # Create unique index on URL for products
            self.products.create_index('url', unique=True)
            
            # Create index on scraped_at for time-based queries
            self.products.create_index('scraped_at')
            
            # Create index on category for filtering
            self.products.create_index('category')
            
            # Create index on source_website
            self.products.create_index('source_website')
            
            logger.info("Database indexes created successfully")
        except Exception as e:
            logger.warning(f"Index creation warning (might already exist): {e}")
    
    def save_product(self, product_data):
        """
        Save or update product in database
        
        Args:
            product_data (dict): Product information to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate required fields
            if not product_data.get('url') or not product_data.get('title'):
                logger.error("Product data missing required fields (url or title)")
                return False
            
            # Use upsert to avoid duplicates based on URL
            result = self.products.update_one(
                {'url': product_data['url']},  # Filter
                {'$set': product_data},        # Update
                upsert=True                    # Insert if not exists
            )
            
            if result.upserted_id:
                logger.info(f"New product saved: {product_data['title']}")
                return True
            else:
                logger.info(f"Product updated: {product_data['title']}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to save product: {e}")
            return False
    
    def get_product_by_url(self, url):
        """
        Get product by URL
        
        Args:
            url (str): Product URL to search for
            
        Returns:
            dict or None: Product data if found, None otherwise
        """
        try:
            return self.products.find_one({'url': url})
        except Exception as e:
            logger.error(f"Failed to get product by URL: {e}")
            return None
    
    def get_products_by_category(self, category):
        """
        Get all products in a specific category
        
        Args:
            category (str): Category to filter by
            
        Returns:
            list: List of products in the category
        """
        try:
            return list(self.products.find({'category': category}))
        except Exception as e:
            logger.error(f"Failed to get products by category: {e}")
            return []
    
    def get_products_by_website(self, website):
        """
        Get all products from a specific website
        
        Args:
            website (str): Source website to filter by
            
        Returns:
            list: List of products from the website
        """
        try:
            return list(self.products.find({'source_website': website}))
        except Exception as e:
            logger.error(f"Failed to get products by website: {e}")
            return []
    
    def get_all_products(self, limit=None):
        """
        Get all products from database
        
        Args:
            limit (int, optional): Maximum number of products to return
            
        Returns:
            list: List of all products
        """
        try:
            cursor = self.products.find()
            if limit:
                cursor = cursor.limit(limit)
            return list(cursor)
        except Exception as e:
            logger.error(f"Failed to get all products: {e}")
            return []
    
    def count_products(self, filter_dict=None):
        """
        Count products in database
        
        Args:
            filter_dict (dict, optional): Filter criteria
            
        Returns:
            int: Number of products matching criteria
        """
        try:
            if filter_dict:
                return self.products.count_documents(filter_dict)
            return self.products.count_documents({})
        except Exception as e:
            logger.error(f"Failed to count products: {e}")
            return 0
    
    def delete_product_by_url(self, url):
        """
        Delete product by URL
        
        Args:
            url (str): Product URL to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            result = self.products.delete_one({'url': url})
            if result.deleted_count > 0:
                logger.info(f"Product deleted: {url}")
                return True
            else:
                logger.warning(f"No product found to delete: {url}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete product: {e}")
            return False
    
    def log_scraping_session(self, website, status, products_count, notes=""):
        """
        Log a scraping session for monitoring purposes
        
        Args:
            website (str): Website that was scraped
            status (str): Status of the scraping session (success/failed/partial)
            products_count (int): Number of products scraped
            notes (str): Additional notes about the session
            
        Returns:
            bool: True if logged successfully, False otherwise
        """
        try:
            log_entry = {
                'website': website,
                'status': status,
                'products_scraped': products_count,
                'timestamp': datetime.now(),
                'notes': notes,
                'scraper_version': '2.0'  # Track version for future compatibility
            }
            
            self.logs.insert_one(log_entry)
            logger.info(f"Logged scraping session for {website}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to log session: {e}")
            return False
    
    def get_scraping_logs(self, website=None, limit=10):
        """
        Get recent scraping logs
        
        Args:
            website (str, optional): Filter logs by website
            limit (int): Maximum number of logs to return
            
        Returns:
            list: List of log entries
        """
        try:
            filter_dict = {'website': website} if website else {}
            return list(self.logs.find(filter_dict).sort('timestamp', -1).limit(limit))
        except Exception as e:
            logger.error(f"Failed to get scraping logs: {e}")
            return []
    
    def cleanup_old_logs(self, days_to_keep=30):
        """
        Remove old scraping logs to keep database clean
        
        Args:
            days_to_keep (int): Number of days of logs to retain
            
        Returns:
            int: Number of logs deleted
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            result = self.logs.delete_many({'timestamp': {'$lt': cutoff_date}})
            logger.info(f"Cleaned up {result.deleted_count} old log entries")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
            return 0
    
    def get_database_stats(self):
        """
        Get database statistics
        
        Returns:
            dict: Database statistics
        """
        try:
            stats = {
                'total_products': self.count_products(),
                'products_by_category': {},
                'products_by_website': {},
                'total_logs': self.logs.count_documents({})
            }
            
            # Get category breakdown
            pipeline = [{'$group': {'_id': '$category', 'count': {'$sum': 1}}}]
            for result in self.products.aggregate(pipeline):
                stats['products_by_category'][result['_id']] = result['count']
            
            # Get website breakdown
            pipeline = [{'$group': {'_id': '$source_website', 'count': {'$sum': 1}}}]
            for result in self.products.aggregate(pipeline):
                stats['products_by_website'][result['_id']] = result['count']
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get database stats: {e}")
            return {}
    
    def close(self):
        """Close database connection"""
        try:
            self.client.close()
            logger.info("Database connection closed")
        except Exception as e:
            logger.error(f"Error closing database connection: {e}")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()