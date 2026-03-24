/* Dashboard JS - QiskitML */

'use strict';

let map = null;
let disasterMarker = null;
let currentMarker = null;
let currentPrediction = null;

function setGauge(needleId, valueId, percent) {
    const angle = -90 + (percent / 100) * 180;
    const needle = document.getElementById(needleId);
    const valueEl = document.getElementById(valueId);
    if (needle) needle.style.transform = `translateX(-50%) rotate(${angle}deg)`;
    if (valueEl) valueEl.textContent = `${Math.round(percent)}%`;
}

function showToast(msg, duration = 3000) {
    const toast = document.getElementById('toast');
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add('show');
    clearTimeout(toast._timer);
    toast._timer = setTimeout(() => toast.classList.remove('show'), duration);
}

function initMap(lat = 51.5074, lon = -0.1278) {
    if (!document.getElementById('map')) return;

    if (!map) {
        map = L.map('map', { zoomControl: true, attributionControl: false }).setView([lat, lon], 11);
        L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
            maxZoom: 19
        }).addTo(map);
    } else {
        map.setView([lat, lon], 11);
    }
}

function updateMap(current, disaster, dtype) {
    if (!map) initMap(current.lat, current.lon);

    if (currentMarker) map.removeLayer(currentMarker);
    if (disasterMarker) map.removeLayer(disasterMarker);

    currentMarker = L.circleMarker([current.lat, current.lon], {
        radius: 10, fillColor: '#00d4ff', color: '#ffffff', weight: 2, fillOpacity: 1
    }).addTo(map).bindPopup('Your Location');

    const colour = getDisasterColour(dtype);
    disasterMarker = L.circleMarker([disaster.lat, disaster.lon], {
        radius: 14, fillColor: colour, color: '#ffffff', weight: 2, fillOpacity: 0.85
    }).addTo(map).bindPopup(`Disaster Zone: ${dtype}`).openPopup();

    if (map._lineLayer) map.removeLayer(map._lineLayer);
    map._lineLayer = L.polyline([[current.lat, current.lon], [disaster.lat, disaster.lon]], {
        color: colour, weight: 2, opacity: 0.5, dashArray: '6, 8'
    }).addTo(map);

    map.fitBounds([[current.lat, current.lon], [disaster.lat, disaster.lon]], { padding: [40, 40] });
}

function getDisasterColour(dtype) {
    const colours = {
        heat_wave: '#ff8a76',
        cyclone: '#7b2fff',
        flood: '#00d4ff',
        blizzard: '#a5c8ff',
        earthquake: '#ffd166',
        normal: '#00ffa3'
    };
    return colours[dtype] || '#ffffff';
}

function updateQuantumMetrics(metrics) {
    if (!metrics) return;
    
    const entropyEl = document.getElementById('entropyValue');
    const purityEl = document.getElementById('purityValue');
    const advantageEl = document.getElementById('advantageValue');
    
    if (entropyEl) entropyEl.textContent = (metrics.entropy || 0).toFixed(4);
    if (purityEl) purityEl.textContent = (metrics.purity || 0).toFixed(4);
    if (advantageEl) advantageEl.textContent = (metrics.advantage_score || 0).toFixed(4);
}

async function runPrediction() {
    const city = document.getElementById('cityInput')?.value?.trim() || 'London';
    if (!city) return;

    const overlay = document.getElementById('loadOverlay');
    if (overlay) overlay.style.display = 'flex';

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city })
        });

        if (res.status === 429) {
            showToast('Rate limit hit — wait a moment and try again.');
            return;
        }

        const data = await res.json();
        if (data.error) { showToast(`Error: ${data.error}`); return; }

        currentPrediction = data;
        updateUI(data);

        if (data.evacuation_needed) {
            await fetchRoute(data);
        } else {
            const routeCard = document.getElementById('routeCard');
            if (routeCard) routeCard.style.display = 'none';
        }

    } catch (err) {
        showToast('Connection error. Is the server running?');
    } finally {
        if (overlay) overlay.style.display = 'none';
    }
}

function updateUI(data) {
    const { risk_percentage, risk_level, disaster_type, evacuation_needed,
        current_position, disaster_location, sensor_data, timestamp, quantum_metrics } = data;

    setGauge('gaugeNeedle', 'gaugeValue', risk_percentage);

    setEl('disasterType', formatDisasterType(disaster_type));
    const evacEl = document.getElementById('evacNeeded');
    if (evacEl) {
        evacEl.textContent = evacuation_needed ? 'Required' : 'Not Required';
        evacEl.className = 'risk-block-value ' + (evacuation_needed ? 'required' : 'not-required');
    }

    if (sensor_data) {
        setEl('tempValue', `${sensor_data.temperature.toFixed(1)}°C`);
        setEl('pressureValue', `${sensor_data.pressure.toFixed(0)} hPa`);
        setEl('humidityValue', `${sensor_data.humidity.toFixed(0)}%`);
        setEl('windValue', `${sensor_data.wind_speed.toFixed(1)} m/s`);
    }

    if (quantum_metrics) {
        updateQuantumMetrics(quantum_metrics);
    }

    const quantumStatus = document.getElementById('quantumStatus');
    if (quantumStatus) {
        quantumStatus.textContent = data.quantum_enabled ? 'Active' : 'Fallback';
        quantumStatus.className = data.quantum_enabled ? 'status-pill pill-success' : 'status-pill pill-warning';
    }

    setEl('lastUpdate', formatTime(timestamp));
    const riskBadge = document.getElementById('riskLevelBadge');
    if (riskBadge) {
        riskBadge.textContent = risk_level;
        riskBadge.style.color = getRiskColour(risk_level);
    }

    initMap(current_position.lat, current_position.lon);
    updateMap(current_position, disaster_location, disaster_type);
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
        if (res.ok && !route.error) {
            const routeCard = document.getElementById('routeCard');
            if (routeCard) routeCard.style.display = 'block';
            setEl('routeDest', route.destination || '--');
            setEl('routeDist', route.distance_km ? `${route.distance_km} km` : '--');
            setEl('routeType', capitalize(route.route_type || '--'));
        }
    } catch { /* silent */ }
}

function sendAlerts() {
    if (!currentPrediction) return;
    showToast('Alert dispatched via quantum analysis pipeline.');
    const btn = document.getElementById('sendAlertsBtn');
    if (btn) {
        btn.textContent = '✓ Sent';
        btn.disabled = true;
        setTimeout(() => {
            btn.innerHTML = `<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9"/></svg> Send Alerts`;
            btn.disabled = false;
        }, 4000);
    }
}

function setEl(id, val) {
    const el = document.getElementById(id);
    if (el) el.textContent = val;
}

function formatDisasterType(t) {
    if (!t) return '--';
    return t.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
}

function getRiskColour(level) {
    const map = { LOW: '#00ffa3', MEDIUM: '#ffaa00', HIGH: '#ff8a76', CRITICAL: '#ff4466' };
    return map[level] || '#ffffff';
}

function formatTime(iso) {
    if (!iso) return '--';
    try {
        return new Date(iso).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } catch { return '--'; }
}

function capitalize(s) {
    return s ? s.charAt(0).toUpperCase() + s.slice(1) : s;
}

document.addEventListener('DOMContentLoaded', () => {
    initMap();
    runPrediction();
});
