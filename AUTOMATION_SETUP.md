# Daily Automation Setup 🤖

This document explains the automated daily scraping system implemented for Week 2 Deliverable #2.

## 🎯 Overview

The system automatically runs both scrapers (Leaders.jo and SmartBuy Jordan) daily at **6:00 AM UTC** (9:00 AM Jordan time) using **GitHub Actions**.

## 📁 Files Added

- **`.github/workflows/daily-scraping.yml`** - GitHub Actions workflow configuration
- **`daily_scraper.py`** - Main orchestrator script that runs both scrapers
- **`scraping_config.py`** - Configuration file for easy adjustments
- **`test_daily_scraper.py`** - Local testing script
- **`AUTOMATION_SETUP.md`** - This documentation file

## 🚀 How It Works

### 1. **GitHub Actions Workflow**
```yaml
# Runs at 6:00 AM UTC daily
schedule:
  - cron: '0 6 * * *'
```

### 2. **Daily Orchestrator**
The `daily_scraper.py` script:
- ✅ Runs Leaders.jo scraper (discovers 3-4 products)
- ✅ Runs SmartBuy scraper (tests known product + discovers more)
- ✅ Saves all products to database
- ✅ Generates detailed logs
- ✅ Handles errors gracefully

### 3. **Smart Limits**
To be respectful to websites:
- **Max 2 categories** per site
- **Max 2-3 products** per category  
- **3-second delays** between requests
- **Error recovery** - continues if one scraper fails

## 🧪 Testing Locally

Before the automation goes live, test it locally:

```bash
# Test the daily scraper
python test_daily_scraper.py

# Or run directly
python daily_scraper.py
```

## 📊 Monitoring

### **Logs**
- Detailed logs saved in `logs/daily_scraping_YYYYMMDD.log`
- GitHub Actions logs available in the Actions tab
- Logs include timestamps, success/failure status, product counts

### **GitHub Actions Dashboard**
1. Go to your repository on GitHub
2. Click **Actions** tab
3. See daily runs under "Daily Electronics Scraping"
4. Download log artifacts if needed

### **Database Monitoring**
Check recent products:
```python
from src.database.manager import DatabaseManager

with DatabaseManager() as db:
    cursor = db.get_cursor()
    cursor.execute("SELECT * FROM products ORDER BY scraped_at DESC LIMIT 10")
    recent_products = cursor.fetchall()
    for product in recent_products:
        print(product)
```

## ⚙️ Configuration

Edit `scraping_config.py` to adjust:

```python
# Change scraping limits
MAX_PRODUCTS_PER_CATEGORY = 2
MAX_CATEGORIES_PER_SITE = 2

# Change schedule (edit .github/workflows/daily-scraping.yml)
SCRAPING_SCHEDULE = "0 6 * * *"  # 6 AM UTC daily

# Add more test products
LEADERS_TEST_PRODUCTS = [
    "https://leaders.jo/en/product/your-product-here/",
]
```

## 📅 Schedule Examples

Edit the `cron` schedule in `.github/workflows/daily-scraping.yml`:

```yaml
# Daily at 6 AM UTC (9 AM Jordan)
- cron: '0 6 * * *'

# Twice daily (6 AM and 6 PM UTC)  
- cron: '0 6,18 * * *'

# Weekdays only at 6 AM UTC
- cron: '0 6 * * 1-5'

# Every 6 hours
- cron: '0 */6 * * *'
```

## 🔧 Manual Triggers

You can manually trigger the scraping:

1. **GitHub Web Interface:**
   - Go to Actions tab → Daily Electronics Scraping
   - Click "Run workflow" button

2. **Local Testing:**
   ```bash
   python daily_scraper.py
   ```

## 📈 Expected Results

**Daily Output:**
- **Leaders.jo**: 3-4 products per day
- **SmartBuy**: 4-6 products per day  
- **Total**: ~7-10 products per day
- **Logs**: Detailed success/failure reports

**Weekly Results:**
- **~50-70 products** added to database
- **Consistent data refresh** 
- **Market trend tracking**

## 🛠️ Troubleshooting

### **Common Issues:**

1. **"No products found"**
   - Websites might have changed structure
   - Check individual scraper logs
   - Test specific product URLs manually

2. **"Import errors"**  
   - Normal in IDE, works fine in GitHub Actions
   - Test with `python daily_scraper.py` locally

3. **"Database connection failed"**
   - Check if database file exists
   - Verify file permissions

### **Debug Steps:**
1. Run `python test_daily_scraper.py` locally
2. Check `logs/` directory for detailed error messages
3. Test individual scrapers: `python src/scrapers/leaders_scraper.py`

## ✅ Deployment Checklist

- [x] **GitHub Actions workflow** created
- [x] **Daily orchestrator script** implemented  
- [x] **Configuration system** set up
- [x] **Local testing script** available
- [x] **Error handling** and logging
- [x] **Documentation** complete

## 🎯 Week 2 Deliverable Status

✅ **COMPLETED**: Live Extraction with Daily Refresh
- **Automated Process**: GitHub Actions runs daily at 6:00 AM UTC
- **Data Refresh**: Both websites scraped automatically  
- **Scheduling**: Configurable cron-based timing
- **Monitoring**: Comprehensive logging and error handling
- **Simple Setup**: No overengineering, reliable cloud-based solution

## 🚀 Next Steps

1. **Commit and push** all automation files to GitHub
2. **Verify first run** in GitHub Actions (will run at next scheduled time)
3. **Monitor logs** for the first few days
4. **Adjust limits** if needed based on performance

The automation is now ready to provide **daily fresh electronics data** from Jordan's major retailers! 🎉