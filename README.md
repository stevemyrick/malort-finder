# Malört Finder

An interactive map showing real-time Jeppson's Malört availability at Wake County ABC stores in North Carolina.

Live site: https://malort-finder.vercel.app

## Features

- **Live inventory** scraped directly from the Wake County ABC website
- **Interactive map** (OpenStreetMap via Leaflet) with all Wake County ABC store locations
- **Color-coded pins** — green (> 5 in stock), yellow (1–5), grey (out of stock)
- **Sidebar store list** sorted by distance from your location or a searched address
- **Navigation links** — one-tap directions in Google Maps or Apple Maps
- **1-hour inventory cache** so the ABC site isn't hammered on every visit

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.13 / Flask |
| Scraping | `requests` + `BeautifulSoup4` (no browser required) |
| Geocoding | Wake County ABC WP Store Locator API |
| Frontend | Vanilla JS + Leaflet.js (OpenStreetMap) |
| Deployment | Vercel (serverless, free tier) |

## Local Development

```bash
# 1. Clone and create a virtual environment
git clone https://github.com/stevemyrick/malort-finder.git
cd malort-finder
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the dev server
flask run --port 5001
```

Open http://127.0.0.1:5001 in your browser.

> **Note:** Port 5000 conflicts with macOS AirPlay Receiver. Use 5001 or disable AirPlay in System Settings → General → AirDrop & Handoff.

## Deploying to Vercel

```bash
npm i -g vercel   # install Vercel CLI once
vercel            # follow the prompts
```

`vercel.json` is already configured to route static assets through Vercel's CDN and everything else through the Flask serverless function.

## Project Structure

```
malort-finder/
├── app.py               # Flask app & API routes
├── vercel.json          # Vercel deployment config
├── requirements.txt
├── static/
│   ├── index.html
│   ├── app.js           # Map rendering, geolocation, sidebar
│   ├── style.css
│   └── malort-logo.png
└── wake_abc/
    ├── scraper.py       # HTTP scrape of wakeabc.com/search-results/
    ├── geocoder.py      # Match store addresses to lat/lng
    ├── cache.py         # In-memory TTL cache
    └── results.py       # Location / Product data classes
```

## Credits

Forked from [malort-finder](https://github.com/adamcoffee1/malort-finder) by Adam Coffee (Abstract Barista), who wrote the original Selenium-based scraper concept.
