# Daily Scraping Configuration
# Adjust these settings to control the automated scraping behavior

# Scraping limits (to avoid overloading websites)
MAX_PRODUCTS_PER_CATEGORY = 2
MAX_CATEGORIES_PER_SITE = 2
LEADERS_EXTRA_PRODUCTS = 3  # Additional products to discover from main page

# Delays (seconds) - increase for production
LEADERS_DELAY = 3
SMARTBUY_DELAY = 2

# Known reliable product URLs for testing
LEADERS_TEST_PRODUCTS = [
    "https://leaders.jo/en/product/oppo-reno-14-five-g-512gb-12-ram/",
]

SMARTBUY_TEST_PRODUCTS = [
    "https://smartbuy-me.com/products/gts0803st0027",
]

# Logging settings
LOG_RETENTION_DAYS = 30
ENABLE_DETAILED_LOGGING = True

# GitHub Actions schedule (cron format)
# Current: "0 6 * * *" = 6:00 AM UTC daily (9:00 AM Jordan time)
# Format: "minute hour day_of_month month day_of_week"
# Examples:
#   "0 6 * * *"     = 6:00 AM UTC daily
#   "0 18 * * *"    = 6:00 PM UTC daily  
#   "0 6 * * 1-5"   = 6:00 AM UTC weekdays only
#   "0 6,18 * * *"  = 6:00 AM and 6:00 PM UTC daily
SCRAPING_SCHEDULE = "0 6 * * *"