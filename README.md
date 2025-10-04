# Jordan Electronics Scraper 🛒

A comprehensive web scraping pipeline for monitoring electronics products and prices from major Jordanian retailers. This project collects product data from SmartBuy Jordan and Leaders Center Jordan, storing it in MongoDB for analysis and tracking.

**✨ Recently refactored to hybrid architecture for better maintainability and code reuse!**

**🆕 Week 2: Enhanced categorization system with 85.2% accuracy and Arabic language support!**

**🔧 Latest Updates (October 4, 2025):**

- **🤖 Daily Automation System**: Implemented GitHub Actions workflow for automated daily scraping
- **☁️ Cloud-Based Scheduling**: Runs automatically at 6:00 AM UTC (9:00 AM Jordan time) daily
- **🔄 Orchestration Script**: New `daily_scraper.py` that manages both scrapers in sequence
- **📊 Enhanced Logging**: Comprehensive daily run reports with success/failure tracking
- **⚙️ Configuration Management**: Easy-to-adjust settings for scheduling and limits
- **🧪 Local Testing**: `test_daily_scraper.py` for validating automation before deployment
- **SmartBuy Scraper Debugging**: Fixed Unicode encoding issues for Windows terminal compatibility
- **Website Structure Adaptation**: Updated for SmartBuy's `/collections/` and `/products/` URL patterns  
- **Category Discovery Enhancement**: Now discovers 198+ product collections automatically
- **Brand-Based Collections**: Added support for Apple, Samsung, Sony, ASUS, and 12+ other brands

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
- 🔥 **Advanced Categorization**: 85.2% accuracy with 16+ product categories
- 🔥 **Arabic Language Support**: Native Arabic product name handling
- 🔥 **Market-Specific Logic**: Tailored for Jordanian electronics market
- 🔥 **Comprehensive Testing**: 27+ test cases covering edge scenarios
- 🤖 **Daily Automation**: GitHub Actions-powered daily scraping at 6:00 AM UTC
- ☁️ **Cloud Scheduling**: Runs automatically without local machine dependency
- 📊 **Automated Monitoring**: Daily run reports with artifact upload and error tracking

## � Week 2 Improvements (September 2025)

### Enhanced Categorization System
Our categorization algorithm has been significantly improved for the Jordanian electronics market:

**📊 Performance Metrics:**
- **85.2% categorization accuracy** (improved from 74.1%)
- **16+ product categories** (expanded from 11)
- **45+ Arabic keywords** for local market support
- **27 comprehensive test cases** covering edge scenarios

**🌍 Market-Specific Features:**
- **Arabic Language Support**: Native handling of Arabic product names (هاتف ذكي, تلفزيون, مكيف)
- **Jordanian Market Categories**: Air Conditioners, Kitchen Appliances, Power & Batteries
- **Local Brand Recognition**: Enhanced detection for regional electronics brands
- **Cultural Context**: Tailored categorization for Middle Eastern market preferences

**🔧 Technical Enhancements:**
- **Priority-Based Matching**: Resolves keyword conflicts intelligently
- **URL Pattern Recognition**: Enhanced fallback categorization from product URLs  
- **Brand-Based Classification**: Smart categorization using manufacturer context
- **Multi-Layer Fallback**: Comprehensive system ensures accurate categorization
- **Brand Pattern Specificity**: Fixed conflicts like "Vivo phone" vs "ASUS VivoBook" laptop
- **Processor-Aware Patterns**: Enhanced laptop detection with "book amd", "book intel", "book ryzen"

**📈 Category Coverage:**
```
Mobile Phones & Tablets    Gaming & Entertainment
Computers & Laptops        Air Conditioners & Cooling  
Audio & Sound Systems      Power & Batteries
TVs & Monitors            Networking Equipment
Wearables & Fitness       Kitchen Appliances
Cameras & Photography     Small Home Appliances
Personal Care Products    Large Home Appliances
Accessories              Electronics (general)
```

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

## 🤖 Daily Automation System (Week 2 Feature)

**✅ Automated Daily Scraping at 6:00 AM UTC (9:00 AM Jordan Time)**

### � GitHub Actions Integration
- **Cloud-Based**: Runs automatically regardless of local machine status
- **Scheduled Execution**: Daily at 6:00 AM UTC using cron scheduling
- **Manual Triggers**: Can be triggered manually from GitHub Actions tab
- **Cross-Platform**: Runs on Ubuntu latest in the cloud

### 📊 Daily Orchestration
- **Sequential Execution**: Runs Leaders.jo scraper followed by SmartBuy scraper
- **Error Isolation**: If one scraper fails, the other continues
- **Smart Limits**: Respectful scraping with 2-3 products per category
- **Comprehensive Logging**: Detailed logs uploaded as artifacts

### 📁 Automation Files
```
├── .github/workflows/daily-scraping.yml  # GitHub Actions workflow
├── daily_scraper.py                      # Main orchestrator script
├── test_daily_scraper.py                 # Local testing script
├── scraping_config.py                    # Configuration settings
└── AUTOMATION_SETUP.md                   # Detailed setup documentation
```

### 📈 Expected Daily Results
- **Leaders.jo**: 3-4 products per day
- **SmartBuy**: 4-6 products per day  
- **Total**: ~7-10 fresh products daily
- **Weekly Growth**: ~50-70 products per week
- **Consistent Data**: Always up-to-date market information

### 🔧 Easy Configuration
```python
# scraping_config.py
SCRAPING_SCHEDULE = "0 6 * * *"  # 6:00 AM UTC daily
MAX_PRODUCTS_PER_CATEGORY = 2
MAX_CATEGORIES_PER_SITE = 2
```

### 🧪 Local Testing
```powershell
# Test the automation locally before deployment
python test_daily_scraper.py

# Run the daily scraper manually
python daily_scraper.py
```

## �🛠️ Technology Stack

- **Python 3.13**: Core programming language
- **BeautifulSoup4**: HTML parsing and data extraction
- **Requests**: HTTP client for web requests
- **MongoDB**: NoSQL database for flexible data storage
- **PyMongo**: MongoDB driver for Python
- **GitHub Actions**: Cloud-based automation and scheduling
- **Ubuntu Latest**: Cloud execution environment

## 📁 Project Structure

**✨ Refactored to Hybrid Architecture (September 2025)**

```
jordan-electronics-scraper/
├── .github/workflows/             # 🤖 GitHub Actions automation
│   └── daily-scraping.yml        # 🤖 Daily scraping workflow
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
├── daily_scraper.py               # 🤖 Daily automation orchestrator
├── test_daily_scraper.py          # 🤖 Local automation testing
├── scraping_config.py             # 🤖 Automation configuration
├── AUTOMATION_SETUP.md            # 🤖 Automation documentation
├── run_scraper.py                 # 🆕 Easy runner script
├── .gitignore                     # 🆕 Git ignore file
├── requirements.txt               # Python dependencies
├── README.md                      # This file (updated!)
├── Week1_Deliverables.txt        # Week 1 deliverables
├── WEEK1_DOCUMENTED_PLAN.md       # Week 1 documentation
├── Week2_Deliverables.txt        # Week 2 deliverables  
├── WEEK2_DOCUMENTED_PLAN.md       # Week 2 documentation
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

**🤖 Daily Automation (Recommended for Production):**
```powershell
# The system runs automatically daily at 6:00 AM UTC
# Check GitHub Actions tab for daily run status
# Manual trigger: GitHub → Actions → Daily Electronics Scraping → Run workflow
```

**🧪 Local Testing:**
```powershell
# Test the daily automation locally
python test_daily_scraper.py

# Run the daily orchestrator manually  
python daily_scraper.py
```

**🆕 Easy Runner (Development):**
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

**Test Results from Latest Run (September 26, 2025):**
```
✅ Leaders Scraper: PASSED
✅ SmartBuy Scraper: PASSED (Unicode fixes applied)
🔍 SmartBuy Category Discovery: 198+ collections found
� SmartBuy Brand Collections: 16+ brands supported
�🎉 Overall: 2/2 tests passed
```

**Latest SmartBuy Scraper Improvements:**
- **Unicode Compatibility**: Removed all Unicode emojis for Windows terminal support
- **Return Type Fix**: Fixed dictionary return format for category compatibility  
- **Comprehensive Discovery**: Successfully finds 6 core categories + 198 collections
- **Brand Support**: APPLE, SAMSUNG, SONY, ASUS, LENOVO, DELL, NESPRESSO, and more
- **Categorization Fix**: Resolved brand pattern conflicts (ASUS VivoBook correctly identified as laptop, not phone)

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

**✅ Completed (Week 2):**
- ✅ **Advanced categorization system** with 85.2% accuracy
- ✅ **Arabic language support** for Jordanian market
- ✅ **16+ product categories** covering electronics and appliances
- ✅ **Comprehensive test suite** with 27+ test scenarios
- ✅ **Market-specific optimizations** for Middle Eastern electronics

**✅ Completed (Week 2 - October 2025):**
- ✅ **Daily automation system** with GitHub Actions workflow
- ✅ **Cloud-based scheduling** running at 6:00 AM UTC daily
- ✅ **Orchestration framework** managing both scrapers in sequence
- ✅ **Automated monitoring** with comprehensive logging and error handling
- ✅ **Configuration management** for easy schedule adjustments
- ✅ **Local testing framework** for validation before deployment

**🎯 Week 2 Status: COMPLETED ✅**
- ✅ **Deliverable #1**: Enhanced categorization with 85.2% accuracy
- ✅ **Deliverable #2**: Daily automation with GitHub Actions scheduling

**🚀 Future Enhancements:**
- JavaScript content handling (dynamic pages)
- Advanced price trend analysis
- Real-time dashboard and monitoring
- API endpoints for data access
- Multi-threaded scraping capabilities
- Machine learning categorization improvements

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

## 🎉 Week 2 Deliverables Status

### ✅ Deliverable #1: Enhanced Categorization System
- **85.2% categorization accuracy** (improved from 74.1%)
- **Arabic language support** for Jordanian market
- **16+ product categories** covering electronics and appliances
- **27+ comprehensive test cases** with edge scenario coverage
- **Status**: COMPLETED ✅

### ✅ Deliverable #2: Daily Automation System  
- **GitHub Actions workflow** for cloud-based automation
- **Daily scheduling** at 6:00 AM UTC (9:00 AM Jordan time)
- **Orchestration framework** managing both scrapers
- **Comprehensive monitoring** with logging and error handling
- **Local testing framework** for deployment validation
- **Status**: COMPLETED ✅

**🏆 Week 2 Overall Status: COMPLETED SUCCESSFULLY**

---

*Last Updated: October 4, 2025*  
*Version: 2.2.0 (Week 2 - Complete: Enhanced Categorization + Daily Automation)*  
*Current Status: Both Week 2 deliverables completed successfully*  
*Daily Automation: Live and running at 6:00 AM UTC daily*