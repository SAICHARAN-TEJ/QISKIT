// Dashboard JavaScript

let map = null;
let currentPrediction = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    initMap();
    runPrediction();
});

// Initialize Leaflet map
function initMap() {
    map = L.map('map').setView([51.5074, -0.1278], 12);
    
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CartoDB',
        maxZoom: 19
    }).addTo(map);
}

// Run prediction
async function runPrediction() {
    const city = document.getElementById('cityInput').value;
    
    try {
        const response = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ city })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentPrediction = data;
            updateDashboard(data);
            updateMap(data);
        } else {
            alert(data.error || 'Prediction failed');
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Connection error');
    }
}

// Update dashboard with prediction data
function updateDashboard(data) {
    // Update gauge
    const riskPercent = data.risk_percentage;
    document.getElementById('gaugeValue').textContent = riskPercent + '%';
    
    // Rotate needle (-90deg = 0%, 90deg = 100%)
    const rotation = -90 + (riskPercent / 100) * 180;
    document.getElementById('gaugeNeedle').style.transform = `translateX(-50%) rotate(${rotation}deg)`;
    
    // Update disaster type
    const disasterType = data.disaster_type.toUpperCase().replace('_', ' ');
    document.getElementById('disasterType').textContent = disasterType;
    
    // Update evacuation status
    const evacEl = document.getElementById('evacNeeded');
    if (data.evacuation_needed) {
        evacEl.textContent = 'REQUIRED';
        evacEl.className = 'evac-value required';
    } else {
        evacEl.textContent = 'NOT REQUIRED';
        evacEl.className = 'evac-value not-required';
    }
    
    // Update sensor values
    const sensors = data.sensor_data;
    document.getElementById('tempValue').textContent = sensors.temperature.toFixed(1) + '°C';
    document.getElementById('pressureValue').textContent = sensors.pressure.toFixed(0) + ' hPa';
    document.getElementById('humidityValue').textContent = sensors.humidity.toFixed(0) + '%';
    document.getElementById('windValue').textContent = sensors.wind_speed.toFixed(1) + ' m/s';
    
    // Update timestamp
    const timestamp = new Date(data.timestamp);
    document.getElementById('lastUpdate').textContent = timestamp.toLocaleTimeString();
    
    // Show route if evacuation needed
    if (data.evacuation_needed) {
        document.getElementById('routeCard').style.display = 'block';
        getRoute(data);
    } else {
        document.getElementById('routeCard').style.display = 'none';
    }
}

// Update map markers
function updateMap(data) {
    // Clear existing markers
    map.eachLayer(function(layer) {
        if (layer instanceof L.Marker) {
            map.removeLayer(layer);
        }
    });
    
    const currentPos = data.current_position;
    const disasterPos = data.disaster_location;
    
    // Add current position marker
    const currentIcon = L.divIcon({
        className: 'custom-marker',
        html: '<div style="background: #48bb78; width: 16px; height: 16px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);"></div>',
        iconSize: [22, 22],
        iconAnchor: [11, 11]
    });
    
    L.marker([currentPos.lat, currentPos.lon], { icon: currentIcon })
        .addTo(map)
        .bindPopup('Your Location');
    
    // Add disaster location marker
    const disasterIcon = L.divIcon({
        className: 'custom-marker',
        html: '<div style="background: #f56565; width: 20px; height: 20px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 8px rgba(0,0,0,0.4);"></div>',
        iconSize: [26, 26],
        iconAnchor: [13, 13]
    });
    
    L.marker([disasterPos.lat, disasterPos.lon], { icon: disasterIcon })
        .addTo(map)
        .bindPopup(`Disaster: ${data.disaster_type.toUpperCase()}`);
    
    // Fit bounds
    const bounds = L.latLngBounds([
        [currentPos.lat, currentPos.lon],
        [disasterPos.lat, disasterPos.lon]
    ]);
    map.fitBounds(bounds, { padding: [50, 50] });
}

// Get evacuation route
async function getRoute(data) {
    try {
        const response = await fetch('/api/route', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current: data.current_position,
                disaster: data.disaster_location,
                type: data.disaster_type
            })
        });
        
        const route = await response.json();
        
        if (response.ok) {
            document.getElementById('routeDest').textContent = 'SAFE_ZONE_' + route.destination;
            document.getElementById('routeDist').textContent = route.distance_km + ' km';
            document.getElementById('routeType').textContent = route.route_type.toUpperCase();
        }
    } catch (error) {
        console.error('Route error:', error);
    }
}

// Send alerts
async function sendAlerts() {
    if (!currentPrediction) {
        alert('Run a prediction first');
        return;
    }
    
    alert('Alert notifications would be sent here.\n\nConfigure Discord webhook and email in environment variables.');
}

// Logout
async function logout() {
    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/';
    } catch (error) {
        window.location.href = '/';
    }
}

// Form submission
document.getElementById('predictForm')?.addEventListener('submit', function(e) {
    e.preventDefault();
    runPrediction();
});
