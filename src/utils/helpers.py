"""
Helper utilities and common functions
"""
import re
from urllib.parse import urlparse, urljoin
from datetime import datetime

def extract_currency_from_price(price_text):
    """
    Extract currency from price text
    
    Args:
        price_text (str): Price text to analyze
        
    Returns:
        str: Currency code (JOD, USD, EUR) or default JOD
    """
    if not price_text:
        return 'JOD'  # Default for Jordan
    
    price_upper = price_text.upper()
    
    if 'د.ا' in price_text or 'JOD' in price_upper:
        return 'JOD'
    elif '$' in price_text or 'USD' in price_upper:
        return 'USD'
    elif '€' in price_text or 'EUR' in price_upper:
        return 'EUR'
    else:
        return 'JOD'  # Default for Jordan

def detect_source_website(url):
    """
    Detect source website from URL
    
    Args:
        url (str): Product URL
        
    Returns:
        str: Human-readable website name
    """
    url_lower = url.lower()
    
    if 'leaders.jo' in url_lower:
        return 'Leaders Center Jordan'
    elif 'smartbuy' in url_lower:
        return 'SmartBuy Jordan'
    else:
        # Extract domain name as fallback
        domain = urlparse(url).netloc
        return domain

def classify_product_category(url, title):
    """
    Classify product into category based on URL and title
    
    Args:
        url (str): Product URL
        title (str): Product title
        
    Returns:
        str: Product category
    """
    url_lower = url.lower()
    title_lower = title.lower() if title else ''
    
    # Define category keywords
    categories = {
        'Mobile Phones': ['phone', 'mobile', 'smartphone', 'iphone', 'samsung', 'oppo', 'huawei', 'xiaomi', 'oneplus'],
        'Computers & Laptops': ['laptop', 'computer', 'pc', 'macbook', 'notebook', 'desktop'],
        'Wearables': ['watch', 'smartwatch', 'fitness', 'tracker', 'band', 'wearable'],
        'TVs & Monitors': ['tv', 'television', 'monitor', 'display', 'screen', 'smart tv'],
        'Audio & Sound': ['audio', 'speaker', 'headphone', 'earphone', 'sound', 'bluetooth', 'headset', 'earbuds'],
        'Cameras & Photography': ['camera', 'photo', 'video', 'lens', 'dslr', 'mirrorless'],
        'Gaming': ['gaming', 'game', 'console', 'playstation', 'xbox', 'nintendo', 'ps5', 'ps4'],
        'Home Appliances': ['washing', 'dryer', 'refrigerator', 'appliance', 'washer', 'fridge', 'microwave', 'oven'],
        'Personal Care': ['shaver', 'epilator', 'grooming', 'personal care', 'trimmer', 'hair dryer'],
        'Tablets': ['tablet', 'ipad', 'tab'],
        'Accessories': ['case', 'cover', 'charger', 'cable', 'adapter', 'accessory', 'power bank']
    }
    
    # Check each category
    for category, keywords in categories.items():
        if any(keyword in url_lower or keyword in title_lower for keyword in keywords):
            return category
    
    # Default category
    return 'Electronics'

def clean_text(text):
    """
    Clean and normalize text
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    if not text:
        return ''
    
    # Remove extra whitespace and normalize
    cleaned = ' '.join(text.split())
    
    # Remove special characters but keep basic punctuation
    cleaned = re.sub(r'[^\w\s\-.,€$د.ا]', '', cleaned)
    
    return cleaned.strip()

def extract_price_number(price_text):
    """
    Extract numeric value from price text
    
    Args:
        price_text (str): Price text like "439.000 JOD"
        
    Returns:
        float or None: Numeric price value
    """
    if not price_text:
        return None
    
    # Remove currency symbols and letters
    price_clean = re.sub(r'[^\d.,]', '', price_text)
    
    # Handle different decimal separators
    if ',' in price_clean and '.' in price_clean:
        # Assume format like "1,234.56"
        price_clean = price_clean.replace(',', '')
    elif ',' in price_clean:
        # Could be either thousands separator or decimal
        parts = price_clean.split(',')
        if len(parts) == 2 and len(parts[1]) <= 2:
            # Decimal separator
            price_clean = price_clean.replace(',', '.')
        else:
            # Thousands separator
            price_clean = price_clean.replace(',', '')
    
    try:
        return float(price_clean)
    except ValueError:
        return None

def is_valid_product_url(url, base_domain):
    """
    Check if URL is a valid product URL for the domain
    
    Args:
        url (str): URL to check
        base_domain (str): Expected domain
        
    Returns:
        bool: True if valid product URL
    """
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        
        # Check domain
        if base_domain not in parsed.netloc:
            return False
        
        # Check for product-like paths
        path_lower = parsed.path.lower()
        if '/product/' in path_lower:
            return True
        if '/item/' in path_lower:
            return True
        if '/p/' in path_lower:
            return True
        
        return False
    except:
        return False

def normalize_url(url, base_url):
    """
    Convert relative URL to absolute URL and normalize
    
    Args:
        url (str): URL to normalize
        base_url (str): Base URL for relative URLs
        
    Returns:
        str: Normalized absolute URL
    """
    if not url:
        return ''
    
    # Convert to absolute URL
    if url.startswith('http'):
        absolute_url = url
    else:
        absolute_url = urljoin(base_url, url)
    
    # Remove fragments and normalize
    parsed = urlparse(absolute_url)
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    
    if parsed.query:
        normalized += f"?{parsed.query}"
    
    return normalized

def create_product_template(url):
    """
    Create a standard product data template
    
    Args:
        url (str): Product URL
        
    Returns:
        dict: Product template with default values
    """
    return {
        'url': url,
        'title': '',
        'price': '',
        'currency': '',
        'source_website': '',
        'category': '',
        'brand': '',
        'description': '',
        'scraped_at': datetime.now().isoformat(),
        'last_updated': datetime.now().isoformat()
    }

def merge_product_data(existing_data, new_data):
    """
    Merge existing product data with new data
    
    Args:
        existing_data (dict): Existing product data
        new_data (dict): New product data to merge
        
    Returns:
        dict: Merged product data
    """
    merged = existing_data.copy()
    
    # Update with new data
    for key, value in new_data.items():
        if value:  # Only update if new value is not empty
            merged[key] = value
    
    # Always update timestamp
    merged['last_updated'] = datetime.now().isoformat()
    
    return merged

def validate_product_data(product_data):
    """
    Validate product data before saving
    
    Args:
        product_data (dict): Product data to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['url', 'title']
    
    for field in required_fields:
        if not product_data.get(field):
            return False, f"Missing required field: {field}"
    
    # Validate URL format
    if not is_valid_url(product_data['url']):
        return False, "Invalid URL format"
    
    return True, "Valid"

def is_valid_url(url):
    """
    Check if string is a valid URL
    
    Args:
        url (str): URL to validate
        
    Returns:
        bool: True if valid URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False