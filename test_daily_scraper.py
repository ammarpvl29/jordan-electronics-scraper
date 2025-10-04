"""
Manual test script for the daily scraper
Run this locally to test the automation before deploying to GitHub Actions
"""

import os
import sys
import subprocess

def test_daily_scraper():
    """Test the daily scraper locally"""
    print("🧪 Testing Daily Scraper Locally")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('daily_scraper.py'):
        print("❌ Error: daily_scraper.py not found!")
        print("Make sure you're running this from the project root directory.")
        return False
    
    if not os.path.exists('src/scrapers/'):
        print("❌ Error: src/scrapers/ directory not found!")
        return False
    
    print("✅ Project structure looks good")
    print("🚀 Running daily scraper...")
    print("-" * 50)
    
    try:
        # Run the daily scraper
        result = subprocess.run([sys.executable, 'daily_scraper.py'], 
                              capture_output=False, 
                              text=True)
        
        if result.returncode == 0:
            print("-" * 50)
            print("✅ Daily scraper completed successfully!")
            print("📁 Check the logs/ directory for detailed logs")
            return True
        else:
            print("-" * 50)
            print(f"❌ Daily scraper failed with exit code: {result.returncode}")
            return False
            
    except Exception as e:
        print(f"❌ Error running daily scraper: {e}")
        return False

def check_database():
    """Check if products were saved to database"""
    print("\n📊 Checking database contents...")
    
    try:
        # Add src to path
        sys.path.insert(0, 'src')
        from database.manager import DatabaseManager
        
        with DatabaseManager() as db:
            # Get recent products
            cursor = db.get_cursor()
            cursor.execute("""
                SELECT website, title, price, scraped_at 
                FROM products 
                ORDER BY scraped_at DESC 
                LIMIT 10
            """)
            
            products = cursor.fetchall()
            
            if products:
                print(f"✅ Found {len(products)} recent products:")
                for product in products:
                    website, title, price, scraped_at = product
                    print(f"  • {website}: {title[:40]}... | {price} | {scraped_at}")
            else:
                print("⚠️  No products found in database")
                
    except Exception as e:
        print(f"❌ Error checking database: {e}")

def main():
    """Main test function"""
    print("Jordan Electronics Scraper - Daily Automation Test")
    print("=" * 60)
    
    success = test_daily_scraper()
    
    if success:
        check_database()
        print("\n🎉 Test completed successfully!")
        print("Your daily scraper is ready for GitHub Actions deployment.")
    else:
        print("\n❌ Test failed!")
        print("Please check the errors above and fix any issues before deployment.")
    
    print("\n📝 Next steps:")
    print("1. Commit your changes to GitHub")
    print("2. The GitHub Action will run automatically at 6:00 AM UTC daily")  
    print("3. You can also trigger it manually from the GitHub Actions tab")

if __name__ == "__main__":
    main()