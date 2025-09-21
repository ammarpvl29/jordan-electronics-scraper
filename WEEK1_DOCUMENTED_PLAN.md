# Week 1 Documented Plan: Jordan Electronics Scraping Pipeline

## Project Overview
This document outlines the technical decisions, data collection strategy, and next steps for the Jordan Electronics scraping pipeline targeting SmartBuy Jordan and Leaders Center Jordan websites.

## Database Choice: MongoDB

### Selected Database: MongoDB
**Rationale:**
1. **Company Alignment**: MongoDB is already used by our company's technology stack, ensuring consistency and leveraging existing team expertise.
2. **Schema Flexibility**: Electronics products have varying attributes (different brands, categories, specifications). MongoDB's document-based structure allows us to store products with different fields without rigid schema constraints.
3. **Scalability**: As we expand to more websites and product categories, MongoDB can handle increasing data volumes and diverse product structures efficiently.
4. **JSON-Native**: Web scraping naturally produces JSON-like data structures, making MongoDB a natural fit for storing scraped product information.
5. **Indexing Capabilities**: MongoDB's indexing features support efficient querying by price ranges, categories, brands, and other product attributes.

### Database Structure
- **Database Name**: `jordan_electronics`
- **Collections**: 
  - `products`: Main product data storage
  - `scraping_logs`: Audit trail and monitoring data

## Product Fields Collection Strategy

### Core Product Fields
The following fields are being collected for each product:

| Field Name | Data Type | Description | Example |
|------------|-----------|-------------|---------|
| `url` | String | Product page URL (unique identifier) | "https://smartbuy-me.com/product/..." |
| `title` | String | Product name/title | "Samsung WW70T3020BS 7KG Washer" |
| `price` | String | Product price as displayed | "439.000 JOD" |
| `currency` | String | **Auto-detected** from price text | "JOD", "USD", "EUR" |
| `source_website` | String | **Auto-detected** from URL | "SmartBuy Jordan", "Leaders Center Jordan" |
| `category` | String | **Smart-detected** from content | "Home Appliances", "Mobile Phones" |
| `brand` | String | Product manufacturer | "Samsung", "Apple", "Oppo" |
| `description` | String | Product description (truncated) | "Samsung front-loading washer..." |
| `scraped_at` | DateTime | Timestamp of data collection | "2025-09-21T10:30:00Z" |

### 🤖 Smart Field Detection Implementation

#### Dynamic Currency Detection
- **Method**: Pattern matching on price text using regular expressions
- **Supported**: JOD (د.ا), USD ($), EUR (€)
- **Logic**: Scans price string for currency symbols and codes
- **Fallback**: Defaults to "JOD" for Jordan-based websites

#### Automatic Source Website Detection
- **Method**: URL domain analysis
- **Implementation**: Extracts website identity from product URL
- **Mapping**: 
  - `smartbuy` domain → "SmartBuy Jordan"
  - `leaders.jo` domain → "Leaders Center Jordan"
  - Unknown domains → Domain name extraction

#### Intelligent Category Classification
- **Method**: Keyword analysis of URLs and product titles
- **Categories Detected**:
  - Mobile Phones (phone, smartphone, iphone, samsung, oppo)
  - Computers & Laptops (laptop, computer, pc, macbook)
  - Wearables (watch, smartwatch, fitness, tracker)
  - Home Appliances (washing, dryer, refrigerator, washer)
  - Audio & Sound (speaker, headphone, audio, sound)
  - Personal Care (shaver, epilator, grooming)
  - Gaming (console, playstation, xbox, gaming)
  - TVs & Monitors (tv, monitor, display, screen)
  - Cameras & Photography (camera, photo, video)
- **Fallback Strategy**: Uses URL structure category if no specific match found

### Enhanced Data Collection Fields
- `brand`: String - Product manufacturer (extracted from page content)
- `description`: String - Product description (first 200 characters)

### Future Enhancement Fields (Planned)
- `model`: String - Specific product model
- `specifications`: Object - Technical specifications
- `availability`: String - Stock status
- `images`: Array - Product image URLs
- `rating`: Number - Customer rating
- `reviews_count`: Integer - Number of reviews

## Implementation Status

### ✅ Completed Deliverables
1. **Environment Setup**: Python 3.13, virtual environment, required libraries (requests, beautifulsoup4, pymongo)
2. **Repository Creation**: GitHub repository "jordan-electronics-scraper" by ammarpvl29
3. **Working Links Identified**:
   - SmartBuy: Washing machines category, Samsung product
   - Leaders: English site products, Oppo Reno 14, Reebok smartwatch
4. **Database Implementation**: MongoDB with local instance and MongoDB Compass
5. **Working Prototype**: Both scrapers operational with database integration

### 🔧 Current Technical Architecture
- **Web Scraping**: BeautifulSoup4 + Requests (chosen over Selenium for simplicity)
- **Smart Data Detection**: Dynamic currency, source website, and category identification
- **Intelligent Classification**: Keyword-based product categorization system
- **Rate Limiting**: Respectful crawling with delays (10 seconds for Leaders.jo)
- **Error Handling**: Robust exception handling and logging
- **Data Deduplication**: URL-based uniqueness constraints
- **Comprehensive Logging**: Monitoring and debugging with Unicode-safe log output
- **Multi-Currency Support**: Auto-detection of JOD, USD, EUR currencies

## Next Steps

### Phase 1: Immediate Improvements (Week 2)
1. **Project Restructuring**:
   - Implement proper folder structure (src/, config/, tests/, logs/)
   - Create modular architecture with base scraper class
   - Separate database operations into dedicated modules

2. **Data Enhancement**:
   - Extract additional fields (brand, model, specifications)
   - Implement data validation and cleaning
   - Add price parsing for numerical analysis

3. **Monitoring & Reliability**:
   - Implement comprehensive logging system
   - Add health checks and error notifications
   - Create data quality validation rules

## Technical Considerations

### Challenges Identified
1. **Website Structure Variations**: Different HTML structures between sites
2. **Rate Limiting**: Respecting website policies and avoiding blocking
3. **Data Consistency**: Standardizing product information across sites
4. **Dynamic Content**: Some products may require JavaScript rendering

### Risk Mitigation
1. **Robust Selectors**: Multiple fallback strategies for data extraction
2. **Respectful Scraping**: User-Agent headers, delays, robots.txt compliance
3. **Error Recovery**: Graceful handling of failed requests and retries
4. **Data Validation**: Schema validation before database insertion

## Success Metrics

### Week 1 Goals ✅
- [x] Environment setup complete
- [x] GitHub repository created
- [x] Working links identified from both sites
- [x] MongoDB database chosen and configured
- [x] Functional prototype with data storage
- [x] Documented plan created

### Ongoing Metrics
- **Data Collection Rate**: Products scraped per hour/day
- **Data Quality**: Percentage of complete product records
- **System Reliability**: Uptime and error rates
- **Coverage**: Number of categories and products monitored

## Conclusion

The Week 1 deliverables have been successfully completed with a solid foundation for the Jordan Electronics scraping pipeline. MongoDB was chosen for its alignment with company technology stack and flexibility for handling diverse product data. 

**Key Technical Achievements:**
- **Smart Field Detection**: Implemented dynamic currency, source website, and category detection
- **Intelligent Classification**: Products are automatically categorized based on content analysis
- **Robust Data Collection**: Enhanced schema with dynamic field population
- **Unicode-Safe Logging**: Resolved encoding issues for reliable monitoring

The current implementation provides a robust base for expansion and enhancement in subsequent weeks, with intelligent data processing capabilities that reduce manual configuration and improve data quality.

The next phase will focus on code organization, data enhancement, and building towards a production-ready automated pipeline that can scale to monitor the entire Jordan electronics market effectively.

---
*Document created: September 21, 2025*  
*Project: Jordan Electronics Scraping Pipeline*  
*Week: 1 Deliverables Documentation*