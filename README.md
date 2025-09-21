# Jordan Electronics Scraper 🛒

A comprehensive web scraping pipeline for monitoring electronics products and prices from major Jordanian retailers. This project collects product data from SmartBuy Jordan and Leaders Center Jordan, storing it in MongoDB for analysis and tracking.

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
- ✅ **MongoDB Integration**: Automatic data storage with deduplication
- ✅ **Respectful Scraping**: Rate limiting and robots.txt compliance
- ✅ **Comprehensive Logging**: Detailed logging for monitoring and debugging
- ✅ **Error Handling**: Robust exception handling and recovery
- ✅ **Data Validation**: URL-based uniqueness and data integrity checks

## 🛠️ Technology Stack

- **Python 3.13**: Core programming language
- **BeautifulSoup4**: HTML parsing and data extraction
- **Requests**: HTTP client for web requests
- **MongoDB**: NoSQL database for flexible data storage
- **PyMongo**: MongoDB driver for Python

## 📁 Project Structure

```
jordan-electronics-scraper/
├── leaders_scraper.py      # Leaders.jo scraper implementation
├── smartbuy_scraper.py     # SmartBuy Jordan scraper implementation
├── requirements.txt        # Python dependencies
├── WEEK1_DOCUMENTED_PLAN.md # Technical decisions and roadmap
├── README.md              # This file
├── logs/                  # Log files
│   ├── leaders_scraper.log
│   └── scraper.log
└── venv/                  # Virtual environment
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

**SmartBuy Scraper:**
```powershell
python smartbuy_scraper.py
```

**Leaders Scraper:**
```powershell
python leaders_scraper.py
```

## 📊 Data Collection

### Collected Product Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `url` | String | Product page URL (unique) | "https://smartbuy-me.com/product/..." |
| `title` | String | Product name | "Samsung WW70T3020BS 7KG Washer" |
| `price` | String | Price as displayed | "439.000 JOD" |
| `currency` | String | Currency code | "JOD" |
| `source_website` | String | Source identifier | "smartbuy" or "leaders" |
| `category` | String | Product category | "washing-machines" |
| `scraped_at` | DateTime | Collection timestamp | "2025-09-21T10:30:00Z" |

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

Current test files (development phase):
- Basic functionality validation
- Database connection testing
- Individual scraper testing

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

See `WEEK1_DOCUMENTED_PLAN.md` for detailed technical roadmap including:
- **Phase 1**: Project restructuring and data enhancement
- **Phase 2**: Automation and additional websites
- **Phase 3**: Analytics and machine learning features

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

*Last Updated: September 21, 2025*  
*Version: 1.0.0 (Week 1 Prototype)*