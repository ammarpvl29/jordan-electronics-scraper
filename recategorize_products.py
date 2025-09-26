"""
Script to recategorize existing products in database with improved logic
This will update any products that might be better categorized with the new algorithm
"""
import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from database.manager import DatabaseManager
from utils.helpers import classify_product_category

def recategorize_products():
    """Update categories of existing products with improved logic"""
    
    print("🔄 Recategorizing Existing Products")
    print("=" * 40)
    
    with DatabaseManager() as db:
        products = list(db.products.find({}))
        
        if not products:
            print("❌ No products found in database!")
            return
        
        print(f"📊 Found {len(products)} products")
        print()
        
        updated_count = 0
        
        for i, product in enumerate(products, 1):
            url = product.get('url', '')
            title = product.get('title', '')
            current_category = product.get('category', '')
            
            # Get new category with improved logic
            new_category = classify_product_category(url, title)
            
            if current_category != new_category:
                print(f"🔄 Product {i}: {title}")
                print(f"    Current: {current_category}")
                print(f"    New: {new_category}")
                
                # Update in database
                try:
                    result = db.products.update_one(
                        {'url': url},
                        {'$set': {'category': new_category}}
                    )
                    
                    if result.modified_count > 0:
                        updated_count += 1
                        print(f"    ✅ Updated successfully")
                    else:
                        print(f"    ❌ Update failed")
                        
                except Exception as e:
                    print(f"    ❌ Error updating: {e}")
                print()
            else:
                print(f"✅ Product {i}: {title} - Category unchanged ({current_category})")
        
        print("\n📋 Recategorization Summary:")
        print(f"  Total products: {len(products)}")
        print(f"  Products updated: {updated_count}")
        print(f"  Products unchanged: {len(products) - updated_count}")
        
        if updated_count > 0:
            print("\n🎉 Database updated with improved categorization!")
        else:
            print("\n✅ All products already have optimal categories!")

if __name__ == "__main__":
    try:
        recategorize_products()
    except Exception as e:
        print(f"❌ Error during recategorization: {e}")
        import traceback
        traceback.print_exc()