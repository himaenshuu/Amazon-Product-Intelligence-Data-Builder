# Amazon Product Scraper with ChatAI Integration

## Summary

This project demonstrates a resilient, AI-ready data ingestion pipeline for Amazon products. It converts raw API responses into a structured, query-efficient commerce dataset with sentiment segmentation, numeric enrichment (prices/ratings), and domain-aware categorization (phones, laptops, tablets, etc.). Designed for powering chat-based product discovery, recommendation, and analytical queries over MongoDB.

### Why It Matters

- Practical handling of rate limits, transient API failures, and inconsistent source data.
- Lean, semantically rich schema optimized for natural language → query translation.
- Bridges acquisition → normalization → persistence → retrieval, mirroring production AI patterns.
- Index strategy aligned with user intent (price, rating, brand, text search, best sellers).

### Core Strengths

- Fault-tolerant scraping (rate limiter + bounded exponential retries).
- Dual representation (human-readable + numeric) for prices & ratings.
- Review sentiment segmentation (positive / negative / neutral) for conversational UX.
- Targeted MongoDB indexes (single, compound, text) for low-latency filtering.
- Extensible modular pipeline ready for recommendation or dashboard layers.

---

## Project Overview

End-to-end Python scraper: collects Amazon product data via RapidAPI, normalizes responses, enriches records, and stores them in MongoDB—ready for AI chat interfaces and analytical filtering.

---

## 🎯 Features

- **Smart Web Scraping**: Fetches Amazon product details using RapidAPI with automatic retry logic
- **Rate Limiting**: Prevents API throttling with configurable request limits (2 req/sec default)
- **Data Normalization**: Parses prices, ratings, and reviews for easy querying
- **Review Categorization**: Automatically classifies reviews as positive, negative, or neutral
- **MongoDB Integration**: Stores data with optimized indexes for fast queries
- **ChatAI Ready**: Numeric fields and structured data for natural language queries
- **Error Handling**: Graceful error recovery with detailed logging

---

## 📋 Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- RapidAPI Account with Amazon Data API access
- pip (Python package manager)

---

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd "scrapper code"

# Create a .env file from the example
cp .env.example .env
```

### 2. Configure .env

Edit `.env` and add your credentials:

```dotenv
# RapidAPI
RAPID_API_KEY=your_api_key_here

# MongoDB
MONGODB_URI=mongodb://localhost:27017/
MONGO_DB=amazon_scrape_db
MONGO_COLLECTION=amazon_scrape

# Optional: Appwrite, SendGrid, etc.
```

### 3. Install Dependencies

```bash
pip install requests retrying pandas pymongo python-dotenv tqdm
```

### 4. Run the Scraper

Open `notebook-scrapper.ipynb` in Jupyter and run the cells in order:

- **Cell 1-3**: Install packages and import libraries
- **Cell 4-5**: Load configuration and logger
- **Cell 6-8**: Define helper functions (read ASINs, fetch API, normalize data)
- **Cell 9A**: Scrape Amazon data and save to JSON
- **Cell 9B**: Push JSON data to MongoDB
- **Cell 10+**: Run example queries

---

## 📁 Project Structure

```text
scrapper code/
├── notebook-scrapper.ipynb    # Main scraper pipeline
├── clean_json.py              # Data cleaning script
├── asins.csv                  # Input: Product ASINs to scrape
├── amazon_results.json        # Output: Raw scraped data
├── amazon_results_cleaned.json # Output: Cleaned data
├── .env.example               # Configuration template
└── README.md                  # This file
```

---

## 🔄 Workflow

### Step 1: Read ASINs

```python
asins = read_asins_from_csv('asins.csv')
# Loads product ASINs from CSV and deduplicates
```

### Step 2: Fetch Data

```python
data = call_api_for_asin(asin)
# Calls RapidAPI with automatic retry (2 attempts)
# Includes rate limiting to avoid 429 errors
```

### Step 3: Normalize & Transform

```python
record = normalize_api_response(asin, data)
# Parses prices and ratings to numeric values
# Categorizes reviews (positive/negative/neutral)
# Detects product type (phone, laptop, tablet, etc.)
```

### Step 4: Save to JSON

```python
save_to_json(results, 'amazon_results.json')
# Stores all records with UTF-8 encoding
```

### Step 5: Push to MongoDB

```python
push_to_mongo(records)
# Creates optimized indexes for fast queries
# Uses upsert to handle duplicates
```

---

## 📊 Data Structure

Each scraped product record contains:

```json
{
  "asin": "B09XXXXX",
  "title": "Product Title",
  "brand": "Brand Name",
  "product_type": "phone",
  "price": "₹19,999",
  "price_numeric": 19999,
  "rating": "4.5 out of 5 stars",
  "rating_numeric": 4.5,
  "reviews_count": 1250,
  "positive_reviews": [...],
  "negative_reviews": [...],
  "neutral_reviews": [...],
  "is_best_seller": true,
  "product_url": "https://...",
  "scraped_at": "2024-01-15T10:30:00Z"
}
```

---

## 🔍 MongoDB Queries

### Find phones under ₹20,000

```python
db.amazon_scrape.find({
  "product_type": "phone",
  "price_numeric": {"$lte": 20000}
}).sort("price_numeric", 1)
```

### Find highly rated products (rating ≥ 4)

```python
db.amazon_scrape.find({
  "rating_numeric": {"$gte": 4.0}
}).sort("rating_numeric", -1)
```

### Search by text

```python
db.amazon_scrape.find({
  "$text": {"$search": "iPhone"}
})
```

---

## ⚙️ Configuration

### Rate Limiter

Controls API requests to avoid throttling:

```python
rate_limiter = RateLimiter(max_calls=2, period=1.0)  # 2 requests per second
```

### Retry Logic

Automatically retries failed requests:

```python
@retry(stop_max_attempt_number=2, wait_exponential_multiplier=1000)
# 2 total attempts with 1 second exponential backoff
```

### Max Scrapes

Limit the number of ASINs to scrape:

```python
MAX_ASINS_TO_SCRAPE = 500  # Set to None for all
```

---

## 🧹 Data Cleaning

Remove error records from scraped JSON:

```bash
python clean_json.py
```

This script:

- Identifies error records
- Separates valid and invalid data
- Creates a backup of original data
- Outputs statistics

---

## 📈 Performance & Statistics

After scraping 122 ASINs:

- **Valid Records**: 96 (78.7% success rate)
- **Error Records**: 6 (API errors, timeouts)
- **Product Types**: 47 phones, 26 laptops, 19 tablets, 2 audio, 2 unknown
- **Price Range**: ₹21.23 - ₹28,998 (avg: ₹1,715.75)
- **Rating Range**: 1.0 - 5.0 (avg: 4.11)
- **File Size**: ~3-5 MB per 100 records

---

## ⚠️ Error Handling

### Common Errors & Solutions

| Error | Cause | Solution |
|-------|-------|----------|
| 429 (Too Many Requests) | API rate limit | Reduce `max_calls` in RateLimiter |
| 503 (Service Unavailable) | API server down | Automatic retry kicks in |
| Connection Timeout | Network issue | Check internet, increase timeout |
| Invalid ASIN | Bad product ID | Verify CSV data format |

### Error Summary Report

After scraping, check the error summary:

```text
⚠️  Error Summary:
  HTTPError: 3 occurrences - Example: 429 Client Error
    Affected ASINs: [B091234, B092345, B093456]
```

---

## 🤖 ChatAI Integration

The data is optimized for natural language queries:

| User Query | MongoDB Query |
|-----------|---------------|
| "Show me phones under 20k" | `{product_type: 'phone', price_numeric: {$lte: 20000}}` |
| "What are positive reviews of iPhone?" | `{$text: {$search: 'iPhone'}, positive_reviews_count: {$gt: 0}}` |
| "Best seller laptops" | `{product_type: 'laptop', is_best_seller: true}` |
| "Highly rated products" | `{rating_numeric: {$gte: 4.5}}` |

---

## 🔐 Security Notes

- ⚠️ **Never commit `.env`** - Contains API keys
- ✅ **Always use `.env.example`** - For public repos
- 🔒 **Rotate API keys** - If accidentally exposed
- 🚫 **Don't hardcode credentials** - Use environment variables

---

## 📝 Troubleshooting

### MongoDB Connection Failed

```text
Error: [Errno 111] Connection refused
```

**Solution**: Ensure MongoDB is running

```bash
# Windows
mongod  # Start MongoDB service

# Or use MongoDB Atlas cloud instead
```

### API Key Invalid

```text
Error: 401 Unauthorized
```

**Solution**: Check `.env` file has correct `RAPID_API_KEY`

### CSV Not Found

```text
Error: No such file or directory: 'asins.csv'
```

**Solution**: Ensure `asins.csv` exists in the project directory with "asin" column

---

## 📚 Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP requests to RapidAPI |
| `retrying` | Automatic retry with exponential backoff |
| `pandas` | CSV reading and data manipulation |
| `pymongo` | MongoDB database operations |
| `python-dotenv` | Load environment variables |
| `tqdm` | Progress bars during scraping |

---

## 📞 Support

For issues or questions:

1. Check the troubleshooting section
2. Review error logs in the console output
3. Verify `.env` configuration
4. Ensure all dependencies are installed

---

## 📄 License

This project is for educational purposes. Ensure compliance with:

- Amazon's Terms of Service
- RapidAPI's Terms of Use
- Local data collection laws

---

## ✨ Future Enhancements

- [ ] Add proxy rotation for large-scale scraping
- [ ] Implement incremental scraping (skip already scraped ASINs)
- [ ] Export data to CSV/Excel
- [ ] Create REST API for MongoDB queries
- [ ] Add scheduling with APScheduler
- [ ] Build web dashboard for data visualization

---

**Last Updated**: November 2025  
**Version**: 1.0
