"""
Test script to validate improved categorization logic
Tests various product names and URLs to ensure proper categorization
"""
import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from utils.helpers import classify_product_category

def test_categorization():
    """Test the improved categorization logic with various examples"""
    
    print("🧪 Testing Improved Categorization Logic")
    print("=" * 50)
    
    # Test cases with expected categories
    test_cases = [
        # Current database products
        ("https://leaders.jo/en/product/oppo-reno-14-five-g-512gb-12-ram/", "Oppo Reno 14 Five G 512GB 12 RAM", "Mobile Phones"),
        ("https://leaders.jo/en/product/reebok-relay-sport-smartwatch/", "Reebok Relay Sport Smartwatch", "Wearables"),
        ("https://leaders.jo/en/product/philips-multi-use-shaver-2/", "Philips Multi-Use Shaver", "Personal Care"),
        
        # Mobile phones - various brands
        ("https://store.com/samsung-galaxy-s24", "Samsung Galaxy S24", "Mobile Phones"),
        ("https://shop.com/iphone-15-pro", "Apple iPhone 15 Pro", "Mobile Phones"),
        ("https://site.com/xiaomi-redmi-note", "Xiaomi Redmi Note 13", "Mobile Phones"),
        
        # Kitchen appliances
        ("https://store.com/microwave-oven", "LG Microwave Oven 1000W", "Small Home Appliances"),
        ("https://shop.com/coffee-maker", "DeLonghi Coffee Maker", "Small Home Appliances"),
        ("https://site.com/blender", "Vitamix High-Speed Blender", "Small Home Appliances"),
        
        # Large appliances
        ("https://store.com/washing-machine", "Samsung Front Load Washing Machine", "Large Home Appliances"),
        ("https://shop.com/refrigerator", "LG Double Door Refrigerator", "Large Home Appliances"),
        
        # Air conditioning
        ("https://store.com/air-conditioner", "Midea Split Air Conditioner 1.5 Ton", "Air Conditioners & Cooling"),
        ("https://shop.com/fan", "Dyson Tower Fan", "Air Conditioners & Cooling"),
        
        # Gaming
        ("https://store.com/playstation-5", "Sony PlayStation 5 Console", "Gaming"),
        ("https://shop.com/xbox-controller", "Xbox Wireless Controller", "Gaming"),
        
        # Audio
        ("https://store.com/bluetooth-speaker", "JBL Bluetooth Speaker", "Audio & Sound"),
        ("https://shop.com/headphones", "Sony WH-1000XM5 Headphones", "Audio & Sound"),
        
        # Wearables
        ("https://store.com/apple-watch", "Apple Watch Series 9", "Wearables"),
        ("https://shop.com/fitness-tracker", "Fitbit Charge 6", "Wearables"),
        
        # Power & Networking
        ("https://store.com/power-bank", "Anker PowerCore 20000mAh", "Power & Batteries"),
        ("https://shop.com/router", "TP-Link WiFi Router", "Networking"),
        
        # Arabic titles (if any)
        ("https://store.com/mobile-phone", "هاتف ذكي سامسونج", "Mobile Phones"),
        ("https://shop.com/tv", "تلفزيون ذكي 55 بوصة", "TVs & Monitors"),
        
        # Edge cases
        ("https://store.com/unknown-product", "Generic Electronic Device", "Electronics"),
        ("https://shop.com/accessory", "Phone Case Leather", "Accessories"),
        
        # URL-based detection
        ("https://store.com/laptop/dell-inspiron", "Dell Computer", "Computers & Laptops"),
        ("https://shop.com/kitchen/rice-cooker", "Electric Rice Cooker", "Kitchen Appliances"),
    ]
    
    print("\n📊 Test Results:")
    print("-" * 30)
    
    correct = 0
    total = len(test_cases)
    
    for url, title, expected in test_cases:
        actual = classify_product_category(url, title)
        is_correct = actual == expected
        correct += is_correct
        
        status = "✅" if is_correct else "❌"
        print(f"{status} {title[:40]:<40} | Expected: {expected:<20} | Got: {actual}")
        
        if not is_correct:
            print(f"    URL: {url}")
    
    accuracy = (correct / total) * 100
    print(f"\n📈 Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    if accuracy < 90:
        print("⚠️  Consider further improvements to categorization logic")
    else:
        print("🎉 Categorization logic performing well!")

def test_existing_products():
    """Test categorization on existing products in database"""
    
    print("\n\n🔍 Testing Existing Database Products")
    print("=" * 45)
    
    try:
        from database.manager import DatabaseManager
        
        with DatabaseManager() as db:
            products = list(db.products.find({}))
            
            if not products:
                print("❌ No products found in database")
                return
            
            print(f"📊 Found {len(products)} products")
            print()
            
            for i, product in enumerate(products, 1):
                url = product.get('url', '')
                title = product.get('title', '')
                current_category = product.get('category', '')
                
                new_category = classify_product_category(url, title)
                
                status = "✅" if current_category == new_category else "🔄"
                print(f"{status} Product {i}: {title}")
                print(f"    Current: {current_category}")
                print(f"    New: {new_category}")
                if current_category != new_category:
                    print(f"    → Would be recategorized!")
                print()
                
    except Exception as e:
        print(f"❌ Error accessing database: {e}")

if __name__ == "__main__":
    test_categorization()
    test_existing_products()