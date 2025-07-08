import requests
from bs4 import BeautifulSoup
from fastapi import FastAPI
from pydantic import BaseModel
import os
from typing import List, Dict
import re
from dotenv import load_dotenv
import random
import time

load_dotenv()
app = FastAPI()

class PriceQuery(BaseModel):
    country: str
    query: str

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:108.0) Gecko/20100101 Firefox/108.0",
]

def get_ecommerce_sites(query: str, country: str) -> List[str]:
    from serpapi import GoogleSearch
    api_key = os.getenv("SERPAPI_KEY")
    if not api_key:
        raise ValueError("SERPAPI_KEY environment key variable is not set")

    country_domains = {
        "US": "google.com",
        "IN": "google.co.in",
        "UK": "google.co.uk",
        "CA": "google.ca",
        "AU": "google.com.au",
    }
    google_domain = country_domains.get(country, "google.com")

    params = {
        "q": f"{query} site:*.{country.lower()} buy",
        "google_domain": google_domain,
        "api_key": api_key,
        "num": 10
    }

    try:
        search = GoogleSearch(params)
        results = search.get_dict().get("organic_results", [])
        return [result["link"] for result in results if "link" in result]
    except Exception as e:
        print(f"[!] Error fetching sites: {e}")
        return []

def scrape_product(url: str, query: str, country: str) -> Dict:
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "lxml")

        product_name = None
        for tag in ["h1", "h2", "title"]:
            element = soup.find(tag)
            if element:
                product_name = element.get_text(strip=True)
                break
        if not product_name:
            product_name = "Unknown Product"

        price = None
        country_currencies = {
            "US": "USD", "IN": "INR", "UK": "GBP", "CA": "CAD", "AU": "AUD"
        }
        currency = country_currencies.get(country, "USD")

        price_patterns = [
            {"class": re.compile(r"price|amount|cost|a-price-whole|product-price|sale-price", re.I)},
            {"id": re.compile(r"price|amount|cost", re.I)},
            {"data-price": True}
        ]

        for pattern in price_patterns:
            element = soup.find(attrs=pattern)
            if element:
                price_text = element.get_text(strip=True)
                price_match = re.search(r"[\d,.]+", price_text)
                if price_match:
                    price = price_match.group()
                    currency_match = re.search(r"[€$£₹]", price_text)
                    if currency_match:
                        currency = currency_match.group()
                    break

        if not price:
            return None

        query_terms = set(query.lower().split())
        product_terms = set(product_name.lower().split())
        if not query_terms.intersection(product_terms):
            return None

        return {
            "link": url,
            "price": price,
            "currency": currency,
            "productName": product_name
        }

    except Exception as e:
        print(f"[!] Error scraping {url}: {e}")
        return None

@app.post("/compare-prices", response_model=List[Dict])
async def compare_prices(query: PriceQuery):
    sites = get_ecommerce_sites(query.query, query.country)
    results = []

    for url in sites:
        result = scrape_product(url, query.query, query.country)
        if result:
            results.append(result)

    def clean_price(price: str) -> float:
        try:
            return float(price.replace(",", "").replace("₹", "").replace("$", ""))
        except:
            return float("inf")

    results = sorted(results, key=lambda x: clean_price(x["price"]))
    return results

@app.get("/")
async def root():
    return {"message": "Product Price Comparison Tool"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
