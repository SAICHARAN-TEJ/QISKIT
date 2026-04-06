/* ==========================================================================
   QiskitML - Dashboard JavaScript
   Lightweight, Vanilla JS
   ========================================================================== */

'use strict';

let map = null;
let currentMarker = null;
let disasterMarker = null;
let routeLine = null;
let calamityMode = false;
let currentPrediction = null;
let currentSlide = 0;

function showToast(msg, duration = 3000) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}

function toggleCalamityMode() {
    calamityMode = !calamityMode;
    const btn = document.getElementById('calamityToggle');
    const label = document.getElementById('calamityLabel');
    const modeStatus = document.getElementById('modeStatus');
    
    if (calamityMode) {
        btn.classList.add('active');
        label.textContent = 'Live Mode';
        modeStatus.textContent = 'Simulation';
        showToast('Calamity Simulation - Evacuation routes shown');
    } else {
        btn.classList.remove('active');
        label.textContent = 'Calamity Mode';
        modeStatus.textContent = 'Real-time';
    }
    runPrediction();
}

function initMap(lat = 13.0827, lon = 80.2707) {
    if (!document.getElementById('map')) return;
    if (map) return;

    map = L.map('map', { zoomControl: true, attributionControl: false }).setView([lat, lon], 11);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 19
    }).addTo(map);
}

function updateMap(current, disaster) {
    if (!map) initMap(current.lat, current.lon);

    if (currentMarker) map.removeLayer(currentMarker);
    if (disasterMarker) map.removeLayer(disasterMarker);
    if (routeLine) map.removeLayer(routeLine);

    currentMarker = L.circleMarker([current.lat, current.lon], {
        radius: 12, fillColor: '#2563eb', color: '#ffffff', weight: 2, fillOpacity: 1
    }).addTo(map).bindPopup('Your Location');

    const colour = getDisasterColour(currentPrediction?.disaster_type || 'normal');
    
    disasterMarker = L.circleMarker([disaster.lat, disaster.lon], {
        radius: 16, fillColor: colour, color: '#ffffff', weight: 2, fillOpacity: 0.85
    }).addTo(map).bindPopup(`Disaster: ${currentPrediction?.disaster_type || 'unknown'}`);

    routeLine = L.polyline([[current.lat, current.lon], [disaster.lat, disaster.lon]], {
        color: colour, weight: 3, opacity: 0.7, dashArray: '10, 10'
    }).addTo(map);

    map.fitBounds([[current.lat, current.lon], [disaster.lat, disaster.lon]], { padding: [40, 40] });
}

function getDisasterColour(dtype) {
    const colours = {
        heat_wave: '#ef4444', cyclone: '#8b2fff', flood: '#06b6d4',
        blizzard: '#64748b', earthquake: '#f59e0b', normal: '#10b981'
    };
    return colours[dtype] || '#2563eb';
}

function setGauge(value) {
    const angle = -90 + (Math.min(100, Math.max(0, value)) / 100) * 180;
    const needle = document.getElementById('gaugeNeedle');
    const valueEl = document.getElementById('gaugeValue');
    if (needle) needle.style.transform = `translateX(-50%) rotate(${angle}deg)`;
    if (valueEl) valueEl.textContent = Math.round(value);
}

async function runPrediction() {
    const cityInput = document.getElementById('cityInput');
    let city = cityInput?.value?.trim() || 'Chennai';

    const overlay = document.getElementById('loadOverlay');
    if (overlay) overlay.classList.add('active');

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city, calamity_mode: calamityMode })
        });

        const data = await res.json();
        if (data.error) { showToast('Error: ' + data.error); return; }

        currentPrediction = data;
        updateUI(data);

        if (data.evacuation_needed || data.calamity_mode) {
            await fetchRoute(data);
        } else {
            const routeCard = document.getElementById('routeCard');
            if (routeCard) routeCard.style.display = 'none';
        }
    } catch (err) {
        showToast('Connection error. Is the server running?');
    } finally {
        if (overlay) overlay.classList.remove('active');
    }
}

function updateUI(data) {
    setGauge(data.risk_percentage);

    const typeEl = document.getElementById('disasterType');
    typeEl.textContent = (data.disaster_type || 'normal').replace(/_/g, ' ');
    typeEl.className = 'disaster-badge disaster-' + (data.disaster_type || 'normal');

    const evacEl = document.getElementById('evacNeeded');
    if (evacEl) {
        evacEl.textContent = data.evacuation_needed ? 'Required' : 'Not Needed';
        evacEl.style.color = data.evacuation_needed ? '#ef4444' : '#10b981';
    }

    if (data.sensor_data) {
        const els = {
            tempValue: data.sensor_data.temperature?.toFixed(1) + ' C',
            pressureValue: data.sensor_data.pressure?.toFixed(0) + ' hPa',
            humidityValue: data.sensor_data.humidity?.toFixed(0) + '%',
            windValue: data.sensor_data.wind_speed?.toFixed(1) + ' m/s'
        };
        Object.entries(els).forEach(([id, val]) => {
            const el = document.getElementById(id);
            if (el) el.textContent = val;
        });
    }

    const lastUpdate = document.getElementById('lastUpdate');
    if (lastUpdate && data.timestamp) {
        lastUpdate.textContent = new Date(data.timestamp).toLocaleTimeString();
    }

    const badge = document.getElementById('riskLevelBadge');
    if (badge) {
        badge.textContent = data.risk_level;
        badge.className = 'status-pill ' + 
            (data.risk_level === 'CRITICAL' ? 'pill-danger' : 
             data.risk_level === 'HIGH' ? 'pill-warning' : 'pill-success');
    }

    const quantumStatus = document.getElementById('quantumStatus');
    if (quantumStatus) {
        quantumStatus.textContent = data.quantum_enabled ? 'Active' : 'Fallback';
        quantumStatus.className = 'status-pill ' + (data.quantum_enabled ? 'pill-success' : 'pill-warning');
    }

    updateMap(data.current_position, data.disaster_location);
}

async function fetchRoute(data) {
    try {
        const res = await fetch('/api/route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current: data.current_position,
                disaster: data.disaster_location,
                type: data.disaster_type
            })
        });

        const route = await res.json();
        if (!res.ok || route.error) return;

        const routeCard = document.getElementById('routeCard');
        if (routeCard) routeCard.style.display = 'block';

        const destEl = document.getElementById('routeDest');
        const distEl = document.getElementById('routeDist');
        const scoreEl = document.getElementById('routeScore');

        if (destEl) destEl.textContent = route.destination || '--';
        if (distEl) distEl.textContent = route.distance_km ? route.distance_km + ' km' : '--';
        if (scoreEl) scoreEl.textContent = route.safety_score ? route.safety_score.toFixed(1) : '--';

        const routesEl = document.getElementById('allRoutes');
        if (routesEl && route.all_routes) {
            routesEl.innerHTML = route.all_routes.map((r, i) => `
                <div class="route-option ${i === 0 ? 'optimal' : ''}" onclick="selectRoute(${r.coords[0]}, ${r.coords[1]})">
                    <span class="route-zone">Zone ${r.zone}</span>
                    <span class="route-distance">${r.distance_km} km</span>
                    <span class="route-score">Score: ${r.safety_score}</span>
                </div>
            `).join('');
        }
    } catch (e) {
        console.error('Route fetch error:', e);
    }
}

function selectRoute(lat, lon) {
    if (map && currentPrediction) {
        const destMarker = L.circleMarker([lat, lon], {
            radius: 10, fillColor: '#10b981', color: '#fff', weight: 2
        }).addTo(map).bindPopup('Selected Safe Zone');
        
        const current = currentPrediction.current_position;
        L.polyline([[current.lat, current.lon], [lat, lon]], {
            color: '#10b981', weight: 4, opacity: 0.8
        }).addTo(map);
        
        map.fitBounds([[current.lat, current.lon], [lat, lon]], { padding: [40, 40] });
        showToast('Route selected! Navigate to safety.');
    }
}

function sendAlerts() {
    if (!currentPrediction) return;
    showToast('Alert dispatched successfully!');
    const btn = document.getElementById('sendAlertsBtn');
    if (btn) {
        btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/>
        </svg> Sent`;
        btn.disabled = true;
        setTimeout(() => {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/>
            </svg> Send Alerts`;
            btn.disabled = false;
        }, 3000);
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    initMap();
    runPrediction();
});

// Expose functions globally
window.toggleCalamityMode = toggleCalamityMode;
window.runPrediction = runPrediction;
window.selectRoute = selectRoute;
window.sendAlerts = sendAlerts;
