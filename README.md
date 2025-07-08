#  Product Price Aggregator 

This Aggregator tool compares prices for products across different websites using SerpAPI and scraping.

## API Use

### Post /compare-prices
  
  **Request Body**
    *JSON* :
    

 {
  "country": "string",
  "query": "string"
}



##  Run Instructions

###  Docker


docker build -t price-aggregator .
docker run -p 8000:8000 --env-file .env price-aggregator


###  Test using curl
## Example:


curl -X POST https://product-price-aggregator.onrender.com/docs \
  -H "Content-Type: application/json" \
  -d '{"country": "US", "query": "iPhone 16 Pro, 128GB"}'





##  .env Example


SERPAPI_KEY="key string"

## Deploy
*https://product-price-aggregator.onrender.com*


# video demo

*https://drive.google.com/file/d/12OgFZBWilQ9zLMzpM6D3pIVwSU_gDDIW/view?usp=sharing*

