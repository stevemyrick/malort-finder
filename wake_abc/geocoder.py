"""Fetch Wake ABC store locations and match scraped addresses to coordinates."""

import re

import requests

from . import cache
from .results import Location

STORE_LOCATOR_URL = "https://wakeabc.com/wp-admin/admin-ajax.php"
STORE_CACHE_KEY = "store_locations"


def _fetch_store_locations() -> list[dict]:
    """Fetch all Wake ABC store locations with lat/lng from the WP Store Locator."""
    cached = cache.get(STORE_CACHE_KEY, ttl=cache.STORE_LOCATIONS_TTL)
    if cached:
        return cached

    resp = requests.get(STORE_LOCATOR_URL, params={
        "action": "store_search",
        "lat": "35.7796",
        "lng": "-78.6382",
        "max_results": "50",
        "search_radius": "50",
    }, timeout=10)
    resp.raise_for_status()
    stores = resp.json()

    cache.set(STORE_CACHE_KEY, stores)
    return stores


def _normalize(text: str) -> str:
    """Normalize an address for fuzzy matching."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_street_number_and_name(address: str) -> str:
    """Extract the street number and first word of street name for matching."""
    parts = _normalize(address).split()
    if len(parts) >= 2:
        return parts[0] + " " + parts[1]
    return _normalize(address)


def get_all_stores() -> list[dict]:
    """Return all Wake ABC stores with their coordinates."""
    return _fetch_store_locations()


def enrich_locations(inventory_locations: list[Location]) -> list[Location]:
    """Match scraped inventory locations to store coordinates."""
    stores = _fetch_store_locations()

    for location in inventory_locations:
        inv_key = _extract_street_number_and_name(location.address)
        for store in stores:
            store_addr = f"{store.get('address', '')} {store.get('address2', '')}"
            store_key = _extract_street_number_and_name(store_addr)
            if inv_key == store_key:
                location.lat = float(store["lat"])
                location.lng = float(store["lng"])
                break

    return inventory_locations


def build_full_store_list(inventory_locations: list[Location]) -> list[Location]:
    """Build a complete list of all stores, with stock counts for those that have inventory."""
    stores = _fetch_store_locations()
    enriched_inventory = enrich_locations(inventory_locations)

    # Index inventory by street key for quick lookup
    inv_by_key = {}
    for loc in enriched_inventory:
        key = _extract_street_number_and_name(loc.address)
        inv_by_key[key] = loc

    all_locations = []
    matched_keys = set()

    for store in stores:
        store_addr = f"{store.get('address', '')} {store.get('address2', '')}".strip()
        city = store.get("city", "")
        state = store.get("state", "")
        zip_code = store.get("zip", "")
        full_address = f"{store_addr} {city}, {state} {zip_code}".strip()
        store_key = _extract_street_number_and_name(store_addr)
        lat = float(store["lat"])
        lng = float(store["lng"])

        if store_key in inv_by_key:
            loc = inv_by_key[store_key]
            loc.lat = lat
            loc.lng = lng
            all_locations.append(loc)
            matched_keys.add(store_key)
        else:
            all_locations.append(Location(full_address, 0, lat, lng))

    # Include any inventory locations that didn't match a store
    for loc in enriched_inventory:
        key = _extract_street_number_and_name(loc.address)
        if key not in matched_keys:
            all_locations.append(loc)

    return all_locations
