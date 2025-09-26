"""
Script to examine current products in detail to understand categorization patterns
"""
import sys
import os

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from database.manager import DatabaseManager

def examine_products():
    """Examine current products in detail"""
    
    print("🔍 Examining Current Products")
    print("=" * 40)
    
    with DatabaseManager() as db:
        products = list(db.products.find({}))
        
        for i, product in enumerate(products, 1):
            print(f"\n📱 Product {i}:")
            print(f"  Title: {product.get('title', 'N/A')}")
            print(f"  Category: {product.get('category', 'N/A')}")
            print(f"  Price: {product.get('price', 'N/A')}")
            print(f"  Source: {product.get('source_website', 'N/A')}")
            print(f"  URL: {product.get('url', 'N/A')}")

if __name__ == "__main__":
    examine_products()