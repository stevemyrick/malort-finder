"""Scrape Wake ABC inventory using plain HTTP requests + BeautifulSoup.

The Wake ABC site renders results server-side: POST productSearch to
/search-results/ and parse the returned HTML — no browser required.
"""

import requests
from bs4 import BeautifulSoup

from .results import Location, Product
from . import cache

SEARCH_URL = "https://wakeabc.com/search-results/"
CACHE_KEY_PREFIX = "inventory:"

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def _search_inventory(product_name: str) -> dict:
    cache_key = CACHE_KEY_PREFIX + product_name.lower()
    cached = cache.get(cache_key, ttl=cache.INVENTORY_TTL)
    if cached:
        locations = [Location(l["address"], l["stock_count"]) for l in cached["locations"]]
        p = cached["product"]
        product = Product(p["plu"], p["price"], p["volume"])
        return {Location: locations, Product: product}

    resp = requests.post(
        SEARCH_URL,
        data={"productSearch": product_name},
        headers=_HEADERS,
        timeout=9,   # Stay under Vercel's 10 s free-tier limit
        allow_redirects=True,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    results_container = soup.find("div", id="productSearchResults")

    if not results_container:
        raise RuntimeError("Could not find #productSearchResults in the Wake ABC response.")

    product_row = results_container.find("div", class_="product-row")
    if not product_row:
        raise RuntimeError(f"No results found for '{product_name}'.")

    wake_product = product_row.find("div", class_="wake-product")

    # --- Product details ---
    plu = ""
    small = wake_product.find("small") if wake_product else None
    if small:
        plu = small.get_text(strip=True).replace("PLU:", "").strip()

    price = 0.0
    price_span = wake_product.find("span", class_="price") if wake_product else None
    if price_span:
        try:
            price = float(price_span.get_text(strip=True).split()[0])
        except (ValueError, IndexError):
            pass

    volume = 0.0
    size_span = wake_product.find("span", class_="size") if wake_product else None
    if size_span:
        try:
            volume = float(size_span.get_text(strip=True).replace("L", ""))
        except (ValueError, IndexError):
            pass

    product = Product(plu, price, volume)

    # --- Store locations ---
    locations: list[Location] = []
    ul = wake_product.find("ul") if wake_product else None
    if ul:
        for li in ul.find_all("li"):
            addr_span = li.find("span", class_="address")
            qty_span = li.find("span", class_="quantity")
            if not addr_span or not qty_span:
                continue
            address = addr_span.get_text(separator=" ", strip=True)
            try:
                count = int(qty_span.get_text(strip=True).split()[0])
            except (ValueError, IndexError):
                count = 0
            locations.append(Location(address, count))

    cache.set(cache_key, {
        "locations": [{"address": l.address, "stock_count": l.stock_count} for l in locations],
        "product": product.to_dict(),
    })

    return {Location: locations, Product: product}


def get_inventory(product_name: str) -> list[Location]:
    return _search_inventory(product_name)[Location]


def get_product(product_name: str) -> Product:
    return _search_inventory(product_name)[Product]


def clear_cache() -> None:
    cache.clear()
