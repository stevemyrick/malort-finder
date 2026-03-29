"""Flask application for Malört Finder."""

import logging
from flask import Flask, jsonify, send_from_directory
from pathlib import Path

from wake_abc.scraper import get_inventory, get_product
from wake_abc.geocoder import build_full_store_list

PRODUCT_NAME = "Malort"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder=str(Path(__file__).parent / "static"))
app.config["JSON_SORT_KEYS"] = False


# ---------------------------------------------------------------------------
# Security headers
# ---------------------------------------------------------------------------

ALLOWED_FRAME_ORIGINS = "https://www.stevemyrick.com https://stevemyrick.com"

@app.after_request
def add_security_headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    # Allow embedding from stevemyrick.com only; DENY for everyone else.
    # X-Frame-Options can only express one origin, so we use CSP frame-ancestors
    # which supersedes it in modern browsers.
    response.headers["Content-Security-Policy"] = (
        f"frame-ancestors {ALLOWED_FRAME_ORIGINS}"
    )
    response.headers["X-Frame-Options"] = "SAMEORIGIN"  # legacy fallback
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    # Restrict the API to same-origin fetches only
    if response.content_type == "application/json":
        response.headers["Access-Control-Allow-Origin"] = ""
    return response


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/inventory")
def inventory():
    try:
        inv = get_inventory(PRODUCT_NAME)
        product = get_product(PRODUCT_NAME)
        all_locations = build_full_store_list(inv)

        return jsonify({
            "product": product.to_dict(),
            "locations": [loc.to_dict() for loc in all_locations],
        })
    except Exception:
        logger.exception("Error fetching inventory")
        return jsonify({"error": "Unable to fetch inventory. Please try again later."}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5001)
