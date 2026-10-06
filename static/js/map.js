/**
 * AI Workout & Diet Plan - Interactive Nearby Gym Map Module (Leaflet.js)
 */

let map;
let userMarker;
let gymMarkersGroup;
let radiusCircle;

document.addEventListener("DOMContentLoaded", () => {
  const mapEl = document.getElementById("gym-map");
  if (!mapEl) return;

  // Default coordinate: Center of city or fallback (New York / 40.7128, -74.0060)
  const defaultLat = 40.7128;
  const defaultLng = -74.0060;

  // Initialize Leaflet Map
  map = L.map("gym-map").setView([defaultLat, defaultLng], 13);

  // High performance dark / modern OpenStreetMap tiles (CartoDB Dark Matter / OSM)
  L.tileLayer("https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png", {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: "abcd",
    maxZoom: 19
  }).addTo(map);

  gymMarkersGroup = L.layerGroup().addTo(map);

  // Try HTML5 Geolocation
  initUserLocation();

  // Search input and buttons
  const searchBtn = document.getElementById("gym-search-btn");
  const searchInput = document.getElementById("gym-query-input");
  const locateBtn = document.getElementById("locate-me-btn");

  if (searchBtn && searchInput) {
    searchBtn.addEventListener("click", () => {
      fetchAndRenderGyms(searchInput.value.trim());
    });

    searchInput.addEventListener("keypress", (e) => {
      if (e.key === "Enter") {
        fetchAndRenderGyms(searchInput.value.trim());
      }
    });
  }

  if (locateBtn) {
    locateBtn.addEventListener("click", () => {
      initUserLocation(true);
    });
  }

  // Initial fetch with default coordinates
  fetchAndRenderGyms();
});

function initUserLocation(forceCenter = false) {
  if ("geolocation" in navigator) {
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const uLat = position.coords.latitude;
        const uLng = position.coords.longitude;

        if (map) {
          map.setView([uLat, uLng], 14);

          // Remove old user marker
          if (userMarker) map.removeLayer(userMarker);
          if (radiusCircle) map.removeLayer(radiusCircle);

          // User Blue Pin
          const userIcon = L.divIcon({
            className: "user-location-pin",
            html: `<div style="background: #3b82f6; width: 18px; height: 18px; border-radius: 50%; border: 3px solid #ffffff; box-shadow: 0 0 12px rgba(59, 130, 246, 0.8);"></div>`,
            iconSize: [20, 20],
            iconAnchor: [10, 10]
          });

          userMarker = L.marker([uLat, uLng], { icon: userIcon })
            .addTo(map)
            .bindPopup("<b>You are here</b><br>Searching gyms within 5km radius.")
            .openPopup();

          radiusCircle = L.circle([uLat, uLng], {
            radius: 3000,
            color: "#10b981",
            fillColor: "#10b981",
            fillOpacity: 0.08,
            weight: 1.5
          }).addTo(map);

          // Fetch gyms around user location
          fetchAndRenderGyms("", uLat, uLng);
        }
      },
      (err) => {
        console.warn("Geolocation denied or unavailable:", err.message);
        fetchAndRenderGyms();
      }
    );
  }
}

async function fetchAndRenderGyms(query = "", lat = null, lng = null) {
  const listContainer = document.getElementById("gym-results-list");
  if (listContainer) {
    listContainer.innerHTML = '<div style="color: #94a3b8; padding: 1rem; text-align: center;">Searching fitness centers...</div>';
  }

  let url = `/api/gyms/search?`;
  if (query) url += `query=${encodeURIComponent(query)}&`;
  if (lat && lng) url += `lat=${lat}&lng=${lng}&`;

  try {
    const res = await fetch(url);
    const data = await res.json();

    if (gymMarkersGroup) gymMarkersGroup.clearLayers();

    if (data.status === "success" && data.gyms && data.gyms.length > 0) {
      if (listContainer) listContainer.innerHTML = "";

      // Custom Gym Marker Icon
      const gymIcon = L.divIcon({
        className: "gym-marker-icon",
        html: `<div style="background: #10b981; color: white; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold; border: 2px solid white; box-shadow: 0 3px 10px rgba(0,0,0,0.4); font-size: 14px;">🏋️</div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 16]
      });

      data.gyms.forEach((gym, index) => {
        const lat = gym.lat || 40.7128;
        const lng = gym.lng || -74.0060;

        // Popup content
        const popupContent = `
          <div style="font-family: inherit; min-width: 200px; color: #0f172a;">
            <h4 style="margin: 0 0 4px; font-weight: 700; color: #065f46;">${gym.name}</h4>
            <p style="margin: 0 0 6px; font-size: 12px; color: #475569;">📍 ${gym.address}</p>
            <div style="display: flex; gap: 8px; font-size: 12px; margin-bottom: 8px;">
              <span style="color: #d97706; font-weight: bold;">⭐ ${gym.rating} / 5</span>
              <span>• ${gym.hours || 'Open 24/7'}</span>
            </div>
            <div style="display: flex; gap: 6px;">
              <a href="https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}" target="_blank" style="display: inline-block; background: #10b981; color: white; padding: 4px 10px; border-radius: 4px; font-size: 11px; text-decoration: none; font-weight: bold;">Get Directions</a>
              <button onclick="saveGymFavorite('${gym.name.replace(/'/g, "\\'")}', '${gym.address.replace(/'/g, "\\'")}', ${lat}, ${lng}, ${gym.rating})" style="background: #334155; color: white; border: none; padding: 4px 8px; border-radius: 4px; font-size: 11px; cursor: pointer;">⭐ Save</button>
            </div>
          </div>
        `;

        const marker = L.marker([lat, lng], { icon: gymIcon })
          .bindPopup(popupContent);
        
        gymMarkersGroup.addLayer(marker);

        // Add to side list
        if (listContainer) {
          const item = document.createElement("div");
          item.className = "gym-card";
          item.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
              <h4 style="color: #fff; font-size: 1rem; margin-bottom: 0.3rem;">${gym.name}</h4>
              <span class="badge badge-success">⭐ ${gym.rating}</span>
            </div>
            <p style="color: #94a3b8; font-size: 0.85rem; margin-bottom: 0.5rem;">📍 ${gym.address} (${gym.distance_km ? gym.distance_km + ' km away' : 'Nearby'})</p>
            <div style="display: flex; flex-wrap: wrap; gap: 0.4rem; margin-bottom: 0.75rem;">
              ${(gym.amenities || []).map(a => `<span style="font-size: 0.72rem; background: #334155; padding: 2px 6px; border-radius: 4px; color: #cbd5e1;">${a}</span>`).join("")}
            </div>
            <div style="display: flex; gap: 0.5rem;">
              <button onclick="focusGymOnMap(${lat}, ${lng}, '${gym.name}')" class="btn btn-outline btn-sm">🗺️ Show on Map</button>
              <a href="https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}" target="_blank" class="btn btn-primary btn-sm">Directions</a>
            </div>
          `;
          listContainer.appendChild(item);
        }
      });

    } else {
      if (listContainer) {
        listContainer.innerHTML = '<div style="color: #94a3b8; padding: 1.5rem; text-align: center;">No gyms found matching your query. Try a broader search.</div>';
      }
    }
  } catch (err) {
    console.error("Gym search error:", err);
  }
}

window.focusGymOnMap = (lat, lng, name) => {
  if (map) {
    map.setView([lat, lng], 16);
    // Find marker at lat, lng
    gymMarkersGroup.eachLayer(layer => {
      const pos = layer.getLatLng();
      if (Math.abs(pos.lat - lat) < 0.0001 && Math.abs(pos.lng - lng) < 0.0001) {
        layer.openPopup();
      }
    });
  }
};

window.saveGymFavorite = async (name, address, lat, lng, rating) => {
  try {
    const res = await fetch("/api/gyms/favorite", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ gym_name: name, address, latitude: lat, longitude: lng, rating })
    });
    const data = await res.json();
    alert(data.message || "Updated favorite gyms!");
    window.location.reload();
  } catch (err) {
    console.error("Favorite error:", err);
  }
};
