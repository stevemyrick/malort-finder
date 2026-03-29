// Default location: CackalackyCon (DoubleTree by Hilton RTP)
const DEFAULT_LAT = 35.8843;
const DEFAULT_LNG = -78.8645;

let map;
let userMarker;
let userLat = DEFAULT_LAT;
let userLng = DEFAULT_LNG;
let storeMarkers = [];
let locations = [];

// --- Map Setup ---

function initMap() {
    map = L.map("map").setView([userLat, userLng], 11);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 18,
    }).addTo(map);

    userMarker = L.circleMarker([userLat, userLng], {
        radius: 8,
        color: "#2563eb",
        fillColor: "#3b82f6",
        fillOpacity: 0.9,
        weight: 2,
    }).addTo(map).bindPopup("Your location");
}

// --- Geolocation ---

function requestUserLocation() {
    if (!navigator.geolocation) return;
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            userLat = pos.coords.latitude;
            userLng = pos.coords.longitude;
            updateUserPosition();
        },
        () => {
            // Permission denied or error — keep default
        }
    );
}

function updateUserPosition() {
    userMarker.setLatLng([userLat, userLng]);
    map.setView([userLat, userLng], 11);
    if (locations.length > 0) {
        renderStoreList();
    }
}

// --- Geocode address via Nominatim ---

async function geocodeAddress(address) {
    const url = `https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(address)}&format=json&limit=1&countrycodes=us`;
    const resp = await fetch(url, {
        headers: { "User-Agent": "MalortFinder/1.0" },
    });
    const results = await resp.json();
    if (results.length > 0) {
        return { lat: parseFloat(results[0].lat), lng: parseFloat(results[0].lon) };
    }
    return null;
}

// --- Haversine Distance (miles) ---

function haversine(lat1, lon1, lat2, lon2) {
    const R = 3959;
    const toRad = (d) => (d * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLon = toRad(lon2 - lon1);
    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * Math.sin(dLon / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// --- Custom Markers ---

function stockColor(count) {
    if (count > 5)  return { fill: "#22c55e", border: "#16a34a" }; // green
    if (count >= 1) return { fill: "#f5c518", border: "#8b6914" }; // yellow
    return { fill: "#aaa", border: "#777" };                        // grey
}

function createIcon(stockCount) {
    const { fill, border } = stockColor(stockCount);
    return L.divIcon({
        className: "custom-marker",
        html: `<div style="
            width: 14px; height: 14px;
            background: ${fill};
            border: 2px solid ${border};
            border-radius: 50%;
            box-shadow: 0 1px 4px rgba(0,0,0,0.3);
        "></div>`,
        iconSize: [14, 14],
        iconAnchor: [7, 7],
        popupAnchor: [0, -10],
    });
}

// --- Render Map Markers ---

function renderMarkers() {
    storeMarkers.forEach((m) => map.removeLayer(m));
    storeMarkers = [];

    for (const loc of locations) {
        if (loc.lat == null || loc.lng == null) continue;

        const marker = L.marker([loc.lat, loc.lng], {
            icon: createIcon(loc.stock_count),
        }).addTo(map);

        const stockText = loc.has_stock
            ? `<span class="stock in-stock">${loc.stock_count} in stock</span>`
            : `<span class="stock no-stock">Out of stock</span>`;

        const navLinks = `
            <div class="nav-links">
                <a href="https://www.google.com/maps/dir/?api=1&destination=${loc.lat},${loc.lng}" target="_blank">Google Maps</a>
                <a href="http://maps.apple.com/?daddr=${loc.lat},${loc.lng}" target="_blank">Apple Maps</a>
            </div>`;

        marker.bindPopup(`
            <div class="popup-content">
                <h3>${loc.address}</h3>
                ${stockText}
                ${navLinks}
            </div>
        `);

        storeMarkers.push(marker);
    }
}

// --- Render Sidebar Store List ---

function renderStoreList() {
    const listEl = document.getElementById("store-list");

    // Sort by distance
    const sorted = [...locations].filter((l) => l.lat != null).map((loc) => ({
        ...loc,
        distance: haversine(userLat, userLng, loc.lat, loc.lng),
    }));
    sorted.sort((a, b) => a.distance - b.distance);

    listEl.innerHTML = "";
    for (const loc of sorted) {
        const card = document.createElement("div");
        card.className = `store-card${loc.has_stock ? "" : " out-of-stock"}`;

        const stockClass = loc.has_stock ? "in-stock" : "no-stock";
        const stockLabel = loc.has_stock ? `${loc.stock_count} in stock` : "Out of stock";

        card.innerHTML = `
            <div class="store-address">${loc.address}</div>
            <div class="store-stock ${stockClass}">${stockLabel}</div>
            <div class="store-distance">${loc.distance.toFixed(1)} mi away</div>
        `;

        card.addEventListener("click", () => {
            map.setView([loc.lat, loc.lng], 14);
            const marker = storeMarkers.find(
                (m) => m.getLatLng().lat === loc.lat && m.getLatLng().lng === loc.lng
            );
            if (marker) marker.openPopup();
        });

        listEl.appendChild(card);
    }
}

// --- Fetch Inventory ---

async function fetchInventory() {
    const loading = document.getElementById("loading");
    loading.style.display = "flex";

    try {
        const resp = await fetch("/api/inventory");
        const data = await resp.json();

        if (data.error) {
            loading.querySelector("p").textContent = `Error: ${data.error}`;
            loading.querySelector(".spinner").style.display = "none";
            return;
        }

        // Show product info
        if (data.product) {
            const infoEl = document.getElementById("product-info");
            infoEl.textContent = `PLU ${data.product.plu} · $${data.product.price.toFixed(2)} · ${data.product.volume}L`;
            infoEl.classList.remove("hidden");
        }

        locations = data.locations;
        renderMarkers();
        renderStoreList();
    } catch (err) {
        const loading = document.getElementById("loading");
        loading.querySelector("p").textContent = "Failed to load inventory. Is the server running?";
        loading.querySelector(".spinner").style.display = "none";
    }
}

// --- Event Listeners ---

document.getElementById("locate-btn").addEventListener("click", () => {
    if (!navigator.geolocation) {
        alert("Geolocation is not supported by your browser.");
        return;
    }
    navigator.geolocation.getCurrentPosition(
        (pos) => {
            userLat = pos.coords.latitude;
            userLng = pos.coords.longitude;
            updateUserPosition();
        },
        () => alert("Unable to get your location.")
    );
});

document.getElementById("search-btn").addEventListener("click", async () => {
    const input = document.getElementById("address-input").value.trim();
    if (!input) return;

    const result = await geocodeAddress(input);
    if (result) {
        userLat = result.lat;
        userLng = result.lng;
        updateUserPosition();
    } else {
        alert("Could not find that address. Try being more specific.");
    }
});

document.getElementById("address-input").addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
        document.getElementById("search-btn").click();
    }
});

// --- Init ---

initMap();
requestUserLocation();
fetchInventory();
