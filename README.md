# Jordan Electronics Scraper 🛒

A comprehensive web scraping pipeline for monitoring electronics products and prices from major Jordanian retailers. This project collects product data from SmartBuy Jordan and Leaders Center Jordan, storing it in MongoDB for analysis and tracking.

**✨ Recently refactored to hybrid architecture for better maintainability and code reuse!**

## 🎯 Project Overview

This scraping pipeline is designed to:
- Monitor electronics prices across Jordanian retailers
- Collect comprehensive product information
- Store data in a flexible MongoDB database
- Provide foundation for price tracking and market analysis

### Target Websites
- **SmartBuy Jordan**: https://smartbuy-me.com
- **Leaders Center Jordan**: https://www.leaders.jo

## 📋 Features

- ✅ **Multi-Site Scraping**: Supports SmartBuy and Leaders websites
- ✅ **Smart Field Detection**: Dynamic currency, source, and category detection
- ✅ **MongoDB Integration**: Automatic data storage with deduplication
- ✅ **Intelligent Categorization**: Auto-classifies products into specific categories
- ✅ **Respectful Scraping**: Rate limiting and robots.txt compliance
- ✅ **Comprehensive Logging**: Detailed logging for monitoring and debugging
- ✅ **Error Handling**: Robust exception handling and recovery
- ✅ **Data Validation**: URL-based uniqueness and data integrity checks
- ✅ **Currency Auto-Detection**: Supports JOD, USD, EUR with smart extraction
- 🆕 **Hybrid Architecture**: Modular design with shared base class
- 🆕 **Code Reusability**: Eliminates duplication with BaseScraper class
- 🆕 **Centralized Database**: Single DatabaseManager for all operations
- 🆕 **Easy Testing**: Multiple test runners and validation scripts
- 🆕 **Flexible Execution**: Run scrapers individually or together

## 🏗️ Architecture Overview

### Hybrid Architecture Benefits (September 2025 Refactor)

The project has been refactored from monolithic scrapers to a **hybrid architecture** that combines:

**🔄 Shared Functionality (BaseScraper)**
- HTTP request handling with rate limiting
- HTML parsing and data extraction utilities
- Error handling and logging
- Dynamic field detection (currency, category, source)
- Database integration patterns

**🎯 Site-Specific Logic (Individual Scrapers)**
- Custom category link discovery
- Site-specific product selectors
- Unique URL patterns and parsing rules
- Website-specific optimization

**🔧 Benefits Achieved:**
- **90% code reduction** in duplicate functionality
- **Consistent behavior** across all scrapers
- **Easier maintenance** with centralized updates
- **Faster development** of new site scrapers
- **Better testing** with modular components

## 🛠️ Technology Stack

- **Python 3.13**: Core programming language
- **BeautifulSoup4**: HTML parsing and data extraction
- **Requests**: HTTP client for web requests
- **MongoDB**: NoSQL database for flexible data storage
- **PyMongo**: MongoDB driver for Python

## 📁 Project Structure

**✨ Refactored to Hybrid Architecture (September 2025)**

```
jordan-electronics-scraper/
├── src/                           # Main source code directory
│   ├── scrapers/                  # Scraper implementations
│   │   ├── __init__.py
│   │   ├── base_scraper.py        # 🆕 Base class with shared functionality
│   │   ├── leaders_scraper.py     # 🔄 Leaders.jo scraper (refactored)
│   │   └── smartbuy_scraper.py    # 🔄 SmartBuy scraper (refactored)
│   ├── database/                  # Database operations
│   │   ├── __init__.py
│   │   └── manager.py             # 🆕 Centralized database manager
│   └── utils/                     # Shared utilities
│       ├── __init__.py
│       ├── logger.py              # 🆕 Logging utilities
│       └── helpers.py             # 🆕 Helper functions
├── tests/                         # Testing framework
│   ├── test_refactored_system.py  # 🆕 Import and functionality tests
│   └── simple_test.py             # 🆕 Subprocess testing
├── run_scraper.py                 # 🆕 Easy runner script
├── requirements.txt               # Python dependencies
├── README.md                      # This file (updated!)
├── Week1_Deliverables.txt        # Week 1 deliverables
├── logs/                         # Log files
│   ├── leaders_scraper.log
│   └── scraper.log
└── venv/                         # Virtual environment

# Legacy files (kept for reference)
├── leaders_scraper_old.py        # Original implementation
└── smartbuy_scraper_old.py       # Original implementation
```

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- MongoDB (local installation or MongoDB Atlas)
- Git

### Installation

1. **Clone the repository**
   ```powershell
   git clone https://github.com/ammarpvl29/jordan-electronics-scraper.git
   cd jordan-electronics-scraper
   ```

2. **Create and activate virtual environment**
   ```powershell
   python -m venv venv
   venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Ensure MongoDB is running on `localhost:27017`
   - The scrapers will automatically create the `jordan_electronics` database

### Running the Scrapers

**🆕 Easy Runner (Recommended):**
```powershell
# Run individual scrapers
python run_scraper.py leaders    # Leaders scraper only
python run_scraper.py smartbuy   # SmartBuy scraper only
python run_scraper.py both       # Both scrapers

# Examples
python run_scraper.py leaders
python run_scraper.py both
```

**Direct Execution:**
```powershell
# Navigate to scraper directory first
cd src/scrapers

# Run individual scrapers
python leaders_scraper.py
python smartbuy_scraper.py
```

**🧪 Testing the System:**
```powershell
# Test all scrapers with timeout handling
python simple_test.py

# Test import system and functionality  
python test_refactored_system.py
```

## 📊 Data Collection

### Collected Product Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `url` | String | Product page URL (unique identifier) | "https://smartbuy-me.com/product/..." |
| `title` | String | Product name/title | "Samsung WW70T3020BS 7KG Washer" |
| `price` | String | Price as displayed on website | "439.000 JOD" |
| `currency` | String | **Auto-detected** from price text | "JOD", "USD", "EUR" |
| `source_website` | String | **Auto-detected** from URL | "SmartBuy Jordan", "Leaders Center Jordan" |
| `category` | String | **Smart-detected** from content/URL | "Home Appliances", "Mobile Phones", "Wearables" |
| `brand` | String | Product manufacturer | "Samsung", "Apple", "Oppo" |
| `description` | String | Product description (first 200 chars) | "Samsung front-loading washer..." |
| `scraped_at` | DateTime | Data collection timestamp | "2025-09-21T10:30:00Z" |

### 🤖 Smart Field Detection

#### Currency Detection
- **Automatic extraction** from price text using pattern matching
- **Supported currencies**: JOD (د.ا), USD ($), EUR (€)
- **Default fallback**: JOD (Jordan's currency)

#### Source Website Detection
- **URL-based identification**: Automatically detects website from product URL
- **Supported sites**: SmartBuy Jordan, Leaders Center Jordan
- **Extensible**: Automatically handles new domains

#### Category Classification
- **Intelligent categorization** based on URL patterns and product titles
- **Categories include**:
  - Mobile Phones (phone, smartphone, iphone, samsung, oppo)
  - Computers & Laptops (laptop, computer, pc, macbook)
  - Wearables (watch, smartwatch, fitness tracker)
  - Home Appliances (washing, dryer, refrigerator)
  - Audio & Sound (speaker, headphone, audio)
  - Personal Care (shaver, epilator, grooming)
  - Gaming (console, playstation, xbox)
  - TVs & Monitors (tv, monitor, display)
  - Cameras & Photography (camera, photo, video)
- **Fallback system**: Uses category from URL structure if specific detection fails

### Database Structure

- **Database**: `jordan_electronics`
- **Collections**:
  - `products`: Main product data
  - `scraping_logs`: Audit trail and monitoring

## 🔧 Configuration

### MongoDB Configuration
- **Host**: `localhost:27017`
- **Database**: `jordan_electronics`
- **Authentication**: None (local development)

### Scraping Settings
- **User-Agent**: Custom headers to identify as legitimate browser
- **Rate Limiting**: 10-second delays for Leaders.jo
- **Timeout**: 30 seconds per request
- **Retries**: Automatic retry on failed requests

## 📝 Logging

Each scraper generates detailed logs:
- **File Locations**: `./logs/` directory
- **Log Levels**: INFO, ERROR, WARNING
- **Content**: Requests, responses, errors, data collection metrics

## 🧪 Testing

**🆕 Comprehensive Testing Framework:**

- **`simple_test.py`**: Subprocess-based testing with timeout handling
  - Tests both scrapers independently
  - 60-second timeout per scraper
  - Captures output and return codes
  - Provides detailed success/failure reporting

- **`test_refactored_system.py`**: Import and functionality testing
  - Validates Python imports work correctly
  - Tests database connectivity
  - Verifies scraper instantiation
  - Checks shared functionality inheritance

- **`run_scraper.py`**: Manual testing and execution
  - Easy individual scraper testing
  - Combined scraper execution
  - Production and development modes

**Test Results from Latest Run:**
```
✅ Leaders Scraper: PASSED
✅ SmartBuy Scraper: PASSED  
🎉 Overall: 2/2 tests passed
```

## 📈 Monitoring

### Success Metrics
- **Products Scraped**: Number of products collected per run
- **Success Rate**: Percentage of successful requests
- **Data Quality**: Completeness of product information
- **Error Rate**: Failed requests and parsing errors

### Health Checks
- Database connectivity
- Website accessibility
- Data validation
- Log file monitoring

## 🔒 Ethical Scraping Practices

This project follows responsible web scraping guidelines:
- **Rate Limiting**: Respectful delays between requests
- **robots.txt Compliance**: Checking and following robots.txt rules
- **User-Agent Headers**: Proper identification
- **No Overloading**: Minimal server impact
- **Legal Compliance**: Following terms of service

## 🚧 Known Limitations

1. **JavaScript Content**: Currently handles static HTML only
2. **Site Changes**: Scraper updates needed if website structures change
3. **Rate Limits**: Manual delay management (no automatic adjustment)
4. **Error Recovery**: Basic retry logic implemented

## 📋 Roadmap

**✅ Completed (Week 1 + Refactoring):**
- ✅ Basic scraping functionality for 2 major Jordanian retailers
- ✅ MongoDB integration with comprehensive data storage
- ✅ Smart field detection (currency, category, source)
- ✅ **Hybrid architecture refactoring** (September 2025)
- ✅ **BaseScraper base class** with shared functionality
- ✅ **Centralized DatabaseManager** eliminating code duplication
- ✅ **Comprehensive testing framework** with multiple test approaches
- ✅ **Modular project structure** for better maintainability

**🎯 Week 2 Deliverables (Due: October 3, 2025):**
- 🔄 Fix categorization improvements
- 🔄 Daily automation implementation
- 🔄 Scheduling system for regular scraping

**🚀 Future Enhancements:**
- JavaScript content handling (dynamic pages)
- Automatic rate limit detection
- Advanced error recovery mechanisms
- Performance monitoring dashboard
- Multi-threaded scraping capabilities

## 📄 License

This project is for educational and research purposes. Please respect website terms of service and robots.txt files.

## 🆘 Troubleshooting

### Common Issues

**MongoDB Connection Error:**
```
pymongo.errors.ServerSelectionTimeoutError
```
**Solution**: Ensure MongoDB is running on localhost:27017

**Import Errors:**
```
ModuleNotFoundError: No module named 'requests'
```
**Solution**: Activate virtual environment and install requirements

**Scraping Failures:**
```
RequestException or parsing errors
```
**Solution**: Check internet connection and website accessibility

### Getting Help

1. Check log files in `./logs/` directory
2. Verify MongoDB connection
3. Ensure all dependencies are installed
4. Review error messages for specific issues

---

*Last Updated: September 26, 2025*  
*Version: 2.0.0 (Hybrid Architecture + Week 1 Complete)*  
*Next Milestone: Week 2 Deliverables (Due: October 3, 2025)*