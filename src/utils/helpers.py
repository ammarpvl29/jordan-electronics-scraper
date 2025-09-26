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
    Enhanced version with better patterns, Arabic support, and more categories
    
    Args:
        url (str): Product URL
        title (str): Product title
        
    Returns:
        str: Product category
    """
    url_lower = url.lower()
    title_lower = title.lower() if title else ''
    combined_text = f"{url_lower} {title_lower}"
    
    # Enhanced category keywords with Arabic support and more specific categories
    # Order matters: more specific keywords first
    categories = {
        # Specific appliances first (to avoid conflicts)
        'Small Home Appliances': [
            'microwave', 'blender', 'mixer', 'toaster', 'coffee maker', 'kettle',
            'iron', 'vacuum', 'cleaner', 'air fryer', 'juicer', 'food processor',
            'rice cooker', 'slow cooker', 'pressure cooker',
            'مايكروويف', 'خلاط', 'محمصة', 'مكواة', 'مكنسة'
        ],
        'Kitchen Appliances': [
            'kitchen appliance', 'cooking appliance', 'baking', 'chef', 'culinary', 'food prep',
            'مطبخ', 'طبخ'
        ],
        'Large Home Appliances': [
            'washing machine', 'washer', 'dryer', 'refrigerator', 'fridge', 'dishwasher',
            'oven', 'stove', 'range', 'freezer', 'غسالة', 'ثلاجة', 'مجمد'
        ],
        'Air Conditioners & Cooling': [
            'air conditioner', 'ac', 'cooling', 'fan', 'heater', 'humidifier',
            'dehumidifier', 'air purifier', 'مكيف', 'تكييف', 'مروحة', 'تبريد'
        ],
        
        # Personal Care
        'Personal Care': [
            'shaver', 'epilator', 'grooming', 'personal care', 'trimmer', 'hair dryer',
            'straightener', 'curler', 'electric toothbrush', 'ماكينة حلاقة', 'تشذيب'
        ],
        
        # Power & Connectivity (specific terms first)
        'Power & Batteries': [
            'power bank', 'powerbank', 'powercore', 'battery pack', 'portable battery', 'battery charger',
            'ups', 'uninterruptible power supply', 'power supply', 'generator',
            'solar panel', 'بطارية', 'طاقة'
        ],
        'Networking': [
            'router', 'wifi router', 'wireless router', 'modem', 'network', 'ethernet', 
            'switch', 'access point', 'range extender', 'راوتر', 'مودم', 'شبكة'
        ],
        
        # Gaming
        'Gaming': [
            'gaming', 'game console', 'console', 'playstation', 'xbox', 'nintendo', 'ps5', 'ps4',
            'controller', 'joystick', 'gaming chair', 'gaming mouse', 'gaming keyboard',
            'ألعاب', 'بلايستيشن'
        ],
        
        # Audio & Entertainment
        'Audio & Sound': [
            'speaker', 'bluetooth speaker', 'wireless speaker', 'soundbar', 'subwoofer', 
            'headphone', 'headphones', 'earphone', 'earphones', 'headset', 'earbuds',
            'amplifier', 'microphone', 'audio system', 'sound system',
            'سماعة', 'صوت', 'مكبر'
        ],
        'TVs & Monitors': [
            'television', 'smart tv', 'led tv', 'oled', 'qled', 'lcd tv', '4k tv', '8k tv',
            'monitor', 'display', 'screen', 'computer monitor', 'gaming monitor',
            'تلفزيون', 'تلفاز', 'شاشة', 'مونيتر'
        ],
        
        # Computing
        'Computers & Laptops': [
            'laptop', 'notebook', 'ultrabook', 'chromebook', 'macbook', 'vivobook',
            'computer', 'desktop', 'pc', 'workstation', 'gaming pc', 'all-in-one pc',
            'book amd', 'book intel', 'book ryzen',  # Specific laptop patterns
            'كمبيوتر', 'لابتوب', 'حاسوب'
        ],
        'Tablets': [
            'tablet', 'ipad', 'android tablet', 'windows tablet', 'kindle', 'surface tablet',
            'تابلت', 'لوح'
        ],
        
        # Mobile & Communication (check exact patterns first)
        'Mobile Phones': [
            'smartphone', 'mobile phone', 'cell phone', 'iphone', 'android phone',
            'galaxy phone', 'galaxy s', 'galaxy note', 'pixel phone', 'nokia phone',
            'samsung phone', 'oppo phone', 'huawei phone', 'xiaomi phone',
            'phone'  # Keep generic 'phone' last to avoid conflicts
        ],
        
        # Wearables & Health
        'Wearables': [
            'smartwatch', 'smart watch', 'fitness tracker', 'fitness band', 'activity tracker',
            'sports watch', 'running watch', 'apple watch', 'galaxy watch', 'fitbit',
            'fitness band', 'wearable device', 'health tracker', 'charge 6', 'charge 5',
            'ساعة ذكية', 'ساعة رياضية'
        ],
        
        # Cameras & Photography
        'Cameras & Photography': [
            'camera', 'digital camera', 'dslr', 'mirrorless camera', 'action camera',
            'camcorder', 'video camera', 'gopro', 'photo', 'photography',
            'كاميرا', 'تصوير'
        ],
        
        # Accessories (most general, check last)
        'Accessories': [
            'phone case', 'case', 'tablet case', 'laptop case', 'screen protector',
            'phone charger', 'charger', 'cable', 'adapter', 'mount', 'stand', 'holder',
            'car charger', 'wireless charger', 'protector', 'cover',
            'كفر', 'حامل'
        ]
    }
    
    # Check each category for exact keyword matches
    for category, keywords in categories.items():
        for keyword in keywords:
            if keyword in combined_text:
                return category
    
    # Brand-based categorization for ambiguous cases
    brand_patterns = {
        'Computers & Laptops': [
            'asus laptop', 'asus notebook', 'asus vivobook', 'asus zenbook', 'asus gaming',
            'dell laptop', 'dell inspiron', 'dell xps', 'hp laptop', 'hp pavilion',
            'lenovo laptop', 'lenovo thinkpad', 'lenovo ideapad'
        ],
        'Mobile Phones': [
            'oppo', 'huawei', 'xiaomi', 'oneplus', 'realme', 'vivo phone', 'vivo smartphone', 
            'nokia phone', 'motorola phone'
        ],
        'Gaming': [
            'razer gaming', 'logitech gaming', 'corsair gaming', 'asus gaming', 'msi gaming'
        ],
        'Audio & Sound': [
            'bose', 'jbl', 'beats', 'sennheiser', 'sony audio', 'harman kardon'
        ],
        'Cameras & Photography': [
            'canon camera', 'nikon camera', 'sony camera', 'fujifilm', 'olympus camera'
        ],
        'Personal Care': [
            'braun grooming', 'gillette', 'panasonic grooming', 'remington'
        ],
        'Kitchen Appliances': [
            'kitchenaid', 'cuisinart', 'hamilton beach', 'ninja kitchen'
        ]
    }
    
    # Check brand patterns
    for category, brands in brand_patterns.items():
        for brand in brands:
            if brand in combined_text:
                return category
    
    # URL pattern matching for additional context (more specific patterns first)
    url_patterns = {
        'Power & Batteries': ['/power-bank/', '/battery/', '/ups/', '/power/'],
        'Wearables': ['/fitness-tracker/', '/smartwatch/', '/watch/', '/fitness/', '/wearable/', '/tracker/'],
        'Computers & Laptops': ['/laptop/', '/computer/', '/pc/', '/notebook/', '/macbook/'],
        'Accessories': ['/accessory/', '/case/', '/cover/'],
        'Kitchen Appliances': ['/kitchen/', '/cooking/', '/microwave/'],
        'Mobile Phones': ['/mobile/', '/phone/', '/smartphone/', '/iphone/', '/galaxy/'],
        'TVs & Monitors': ['/tv/', '/television/', '/monitor/', '/display/'],
        'Audio & Sound': ['/audio/', '/speaker/', '/headphone/', '/sound/', '/headset/'],
        'Gaming': ['/gaming/', '/console/', '/game/', '/playstation/', '/xbox/'],
        'Large Home Appliances': ['/appliance/', '/washing/', '/refrigerator/', '/washer/'],
        'Personal Care': ['/grooming/', '/personal-care/', '/shaver/'],
        'Networking': ['/network/', '/router/', '/wifi/']
    }
    
    for category, patterns in url_patterns.items():
        if any(pattern in url_lower for pattern in patterns):
            return category
    
    # Final fallback: check for common electronics terms
    electronics_keywords = ['electronic', 'digital', 'smart', 'tech', 'device']
    if any(keyword in combined_text for keyword in electronics_keywords):
        return 'Electronics'
    
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