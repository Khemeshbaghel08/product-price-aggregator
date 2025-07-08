#  Product Price Aggregator 

This Aggregator tool compares prices for products across different websites using SerpAPI and scraping.

## API Use

### Post /compare-prices
  
  **Request Body**
    *JSON* :
    
```bash
 {
  "country": "string",
  "query": "string"
}



##  Run Instructions

###  Docker

```bash
docker build -t price-aggregator .
docker run -p 8000:8000 --env-file .env price-aggregator


###  Test using curl
## Example:
```bash

curl -X POST https://price-compare-api.onrender.com/compare-prices \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'




##  .env Example

```
SERPAPI_KEY="key string"
```
