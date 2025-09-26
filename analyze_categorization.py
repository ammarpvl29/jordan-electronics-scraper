"""
Script to analyze categorization issues in the database
Helps identify problems and patterns for improvement
"""
import sys
import os
from collections import Counter, defaultdict

# Add src to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
sys.path.insert(0, src_dir)

from database.manager import DatabaseManager
from utils.helpers import classify_product_category

def analyze_categories():
    """Analyze current categorization in the database"""
    
    print("🔍 Analyzing Product Categorization")
    print("=" * 50)
    
    with DatabaseManager() as db:
        # Get all products
        products = list(db.products.find({}))
        
        if not products:
            print("❌ No products found in database!")
            return
        
        print(f"📊 Found {len(products)} products in database")
        print()
        
        # Analyze categories
        category_counts = Counter()
        missing_categories = []
        generic_categories = []
        product_analysis = []
        
        for product in products:
            url = product.get('url', '')
            title = product.get('title', '')
            current_category = product.get('category', '')
            
            # Count categories
            category_counts[current_category] += 1
            
            # Find issues
            if not current_category:
                missing_categories.append({
                    'url': url,
                    'title': title
                })
            elif current_category == 'Electronics':
                generic_categories.append({
                    'url': url,
                    'title': title,
                    'category': current_category
                })
            
            # Test with improved logic
            suggested_category = classify_product_category(url, title)
            
            product_analysis.append({
                'url': url,
                'title': title,
                'current_category': current_category,
                'suggested_category': suggested_category,
                'needs_change': current_category != suggested_category
            })
        
        # Print analysis results
        print("📈 Category Distribution:")
        print("-" * 30)
        for category, count in category_counts.most_common():
            category_display = category if category else "[MISSING]"
            print(f"  {category_display}: {count} products")
        print()
        
        print("⚠️ Issues Found:")
        print("-" * 20)
        print(f"  Missing categories: {len(missing_categories)} products")
        print(f"  Generic 'Electronics': {len(generic_categories)} products")
        
        changes_needed = sum(1 for p in product_analysis if p['needs_change'])
        print(f"  Products needing recategorization: {changes_needed} products")
        print()
        
        # Show specific examples
        if missing_categories:
            print("🚨 Products with Missing Categories:")
            print("-" * 40)
            for i, product in enumerate(missing_categories[:5], 1):
                print(f"  {i}. {product['title'][:60]}...")
                print(f"     URL: {product['url']}")
            if len(missing_categories) > 5:
                print(f"     ... and {len(missing_categories) - 5} more")
            print()
        
        if generic_categories:
            print("📦 Products with Generic 'Electronics' Category:")
            print("-" * 50)
            for i, product in enumerate(generic_categories[:5], 1):
                suggested = classify_product_category(product['url'], product['title'])
                print(f"  {i}. {product['title'][:50]}...")
                print(f"     Current: {product['category']}")
                print(f"     Suggested: {suggested}")
                print(f"     URL: {product['url']}")
                print()
            if len(generic_categories) > 5:
                print(f"     ... and {len(generic_categories) - 5} more")
        
        # Show categorization changes needed
        if changes_needed > 0:
            print("🔄 Suggested Categorization Changes:")
            print("-" * 40)
            changes = [p for p in product_analysis if p['needs_change']]
            for i, product in enumerate(changes[:10], 1):
                print(f"  {i}. {product['title'][:50]}...")
                print(f"     Current: {product['current_category'] or '[MISSING]'}")
                print(f"     Suggested: {product['suggested_category']}")
                print()
            if len(changes) > 10:
                print(f"     ... and {len(changes) - 10} more changes needed")
        
        # Summary
        print("📋 Summary:")
        print("-" * 15)
        print(f"  Total products: {len(products)}")
        print(f"  Unique categories: {len(category_counts)}")
        print(f"  Products with issues: {len(missing_categories) + len(generic_categories)}")
        print(f"  Improvement potential: {changes_needed} products")
        
        accuracy = ((len(products) - changes_needed) / len(products)) * 100
        print(f"  Current accuracy: {accuracy:.1f}%")

def analyze_keyword_patterns():
    """Analyze what keywords appear in titles but aren't captured"""
    
    print("\n🔍 Analyzing Keyword Patterns")
    print("=" * 40)
    
    with DatabaseManager() as db:
        products = list(db.products.find({}))
        
        # Extract common words from titles in generic categories
        generic_products = [p for p in products if p.get('category') == 'Electronics' or not p.get('category')]
        
        if not generic_products:
            print("✅ No generic categorization issues found!")
            return
        
        word_freq = Counter()
        
        for product in generic_products:
            title = product.get('title', '').lower()
            # Split into words and count
            words = title.split()
            for word in words:
                # Clean word
                clean_word = ''.join(c for c in word if c.isalnum())
                if len(clean_word) > 3:  # Only words longer than 3 chars
                    word_freq[clean_word] += 1
        
        print("🔤 Most common words in uncategorized products:")
        print("-" * 45)
        for word, count in word_freq.most_common(20):
            print(f"  {word}: {count} occurrences")

if __name__ == "__main__":
    try:
        analyze_categories()
        analyze_keyword_patterns()
        
        print("\n✅ Analysis complete!")
        print("💡 Use this information to improve the categorization logic in helpers.py")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()