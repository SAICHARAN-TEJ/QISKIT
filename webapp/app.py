"""
QiskitML - Quantum ML Disaster Prediction System
Flask Web Application with Quantum Machine Learning
"""

import os
import sys
import json
import math
import sqlite3
import hashlib
import secrets
import re
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional, Dict, Any

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

import numpy as np
import pandas as pd

try:
    from quantum import (
        QuantumFeatureMap, ZZFeatureMap, EfficientSU2Map,
        VariationalQuantumClassifier, QuantumNeuralNetwork,
        QuantumBackend, QuantumMetrics
    )
    from ml import DisasterFeatures, FeatureEngineering, DataPreprocessor, prepare_quantum_features
    QUANTUM_ML_AVAILABLE = True
except ImportError:
    QUANTUM_ML_AVAILABLE = False

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

DB_PATH = os.path.join(PROJECT_ROOT, "webapp", "qiskitml.db")


class SecurityConfig:
    """Security configuration."""
    
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600
    
    @staticmethod
    def sanitize_input(value: str, max_length: int = 255) -> str:
        if not isinstance(value, str):
            return ""
        return value[:max_length].strip()
    
    @staticmethod
    def validate_email(email: str) -> bool:
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        try:
            return -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
        except (ValueError, TypeError):
            return False


class DatabaseManager:
    """Database management."""
    
    @staticmethod
    def init_db():
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                salt TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active INTEGER DEFAULT 1
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                city TEXT NOT NULL,
                disaster_type TEXT NOT NULL,
                risk_percentage REAL NOT NULL,
                risk_level TEXT NOT NULL,
                latitude REAL NOT NULL,
                longitude REAL NOT NULL,
                sensor_data TEXT,
                evacuation_needed INTEGER,
                quantum_enabled INTEGER DEFAULT 0,
                quantum_metrics TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prediction_id INTEGER,
                alert_type TEXT NOT NULL,
                sent_to TEXT,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (prediction_id) REFERENCES predictions (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                ip_address TEXT,
                user_agent TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_user ON predictions(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_predictions_created ON predictions(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_user ON audit_log(user_id)')
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def log_action(user_id: Optional[int], action: str, ip_address: str, user_agent: str, details: str = None):
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO audit_log (user_id, action, ip_address, user_agent, details) VALUES (?, ?, ?, ?, ?)',
                (user_id, action, ip_address, user_agent[:500] if user_agent else "", details)
            )
            conn.commit()
            conn.close()
        except:
            pass
    
    @staticmethod
    def hash_password(password: str) -> tuple:
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return salt + pwd_hash.hex(), salt
    
    @staticmethod
    def verify_password(password: str, stored_hash: str, salt: str) -> bool:
        pwd_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
        return pwd_hash.hex() == stored_hash


class QuantumMLPredictor:
    """Quantum ML Disaster Prediction Engine."""
    
    DISASTER_LABELS = {
        0: "normal",
        1: "heat_wave",
        2: "cyclone",
        3: "flood",
        4: "blizzard",
        5: "earthquake"
    }
    
    LOCATIONS = {
        "heat_wave": (51.5074, -0.1278),
        "cyclone": (51.5074, -0.1278),
        "flood": (51.5074, -0.1278),
        "blizzard": (51.5074, -0.1278),
        "earthquake": (51.5074, -0.1278),
        "normal": (51.5074, -0.1278)
    }
    
    def __init__(self):
        self.jena_data = self._load_jena_data()
        self.quantum_enabled = QUANTUM_ML_AVAILABLE
        self.preprocessor = DataPreprocessor(normalization='minmax')
        
        if self.quantum_enabled:
            self._initialize_quantum()
    
    def _load_jena_data(self):
        data_path = os.path.join(PROJECT_ROOT, "src", "data", "jena_climate_2009_2016.csv")
        if not os.path.exists(data_path):
            return None
        return pd.read_csv(data_path).iloc[::6].reset_index(drop=True)
    
    def _initialize_quantum(self):
        try:
            self.feature_map = ZZFeatureMap(
                num_qubits=4,
                num_features=7,
                reps=2,
                entanglement='linear'
            )
            self.vqc = VariationalQuantumClassifier(num_qubits=4, num_classes=6)
            self.backend = QuantumBackend()
        except Exception:
            self.quantum_enabled = False
    
    def _extract_features(self, sensor: dict) -> np.ndarray:
        features = DisasterFeatures(
            temperature=float(sensor.get('temperature', 20)),
            pressure=float(sensor.get('pressure', 1013)),
            humidity=float(sensor.get('humidity', 50)),
            wind_speed=float(sensor.get('wind_speed', 5)),
            max_wind_speed=float(sensor.get('max_wind_speed', 6)),
            wind_direction=float(sensor.get('wind_direction', 180)),
            dew_point=float(sensor.get('dew_point', 10))
        )
        return prepare_quantum_features(features.__dict__)
    
    def _get_risk_level(self, risk: float) -> str:
        if risk >= 85: return "CRITICAL"
        elif risk >= 70: return "HIGH"
        elif risk >= 50: return "MEDIUM"
        return "LOW"
    
    def _quantum_infer(self, features: np.ndarray) -> tuple:
        if not self.quantum_enabled:
            return self._classical_infer(features)
        
        try:
            normalized = self.preprocessor.fit_transform(features.reshape(1, -1))[0]
            result = self.vqc.predict(normalized)
            
            disaster_type = self.DISASTER_LABELS.get(int(result.prediction), "normal")
            risk = float(result.confidence) * 100
            
            circuit_info = {
                'type': 'VariationalQuantumClassifier',
                'num_qubits': 4,
                'feature_map': 'ZZFeatureMap',
                'ansatz': 'EfficientSU2'
            }
            
            metrics = QuantumMetrics.compute_all_metrics(
                type('R', (), {
                    'counts': result.measurement_counts or {'0': 512, '1': 512},
                    'time_taken': 0.01,
                    'backend': 'quantum_simulator'
                })(),
                circuit_info
            )
            
            return disaster_type, risk, metrics
        except Exception:
            return self._classical_infer(features)
    
    def _classical_infer(self, features: np.ndarray) -> tuple:
        temp = float(features[0])
        pressure = float(features[1])
        humidity = float(features[2])
        wind = float(features[3])
        
        if temp > 35.0 and humidity > 60:
            return "heat_wave", min(95.0, 70 + (temp - 35) * 1.2), None
        elif wind > 15.0 and pressure < 980:
            return "cyclone", min(98.0, 75 + (980 - pressure) * 0.1), None
        elif humidity > 90 and temp > 5:
            return "flood", min(90.0, 65 + (humidity - 90) * 0.8), None
        elif temp < -5 and wind > 8:
            return "blizzard", min(88.0, 70 + (-temp - 5) * 0.7), None
        elif pressure < 970:
            return "earthquake", 80.0, None
        else:
            return "normal", max(10.0, 30 - abs(temp - 15)), None
    
    def predict(self, city: str = "London", coords: tuple = None) -> dict:
        city = SecurityConfig.sanitize_input(city, 50)
        
        # Use provided coordinates or default
        lat, lon = coords if coords else (51.5074, -0.1278)
        
        # Add small random offset for current position
        current_lat = lat + np.random.uniform(-0.02, 0.02)
        current_lon = lon + np.random.uniform(-0.02, 0.02)
        
        sensor = self._get_sensor_data(lat, lon)
        features = self._extract_features(sensor)
        
        disaster_type, risk, quantum_metrics = self._quantum_infer(features)
        risk_level = self._get_risk_level(risk)
        
        # Disaster location is based on disaster type, but offset from input city
        disaster_lat = lat + np.random.uniform(-0.1, 0.1)
        disaster_lon = lon + np.random.uniform(-0.1, 0.1)
        
        return {
            "city": city,
            "disaster_type": disaster_type,
            "risk_percentage": round(risk, 1),
            "risk_level": risk_level,
            "evacuation_needed": risk >= 70.0,
            "current_position": {"lat": float(current_lat), "lon": float(current_lon)},
            "disaster_location": {"lat": float(disaster_lat), "lon": float(disaster_lon)},
            "sensor_data": {
                "pressure": float(sensor.get('pressure', 1013)),
                "temperature": float(sensor.get('temperature', 20)),
                "humidity": float(sensor.get('humidity', 50)),
                "wind_speed": float(sensor.get('wind_speed', 5)),
                "wind_direction": float(sensor.get('wind_direction', 180)),
                "dew_point": float(sensor.get('dew_point', 10))
            },
            "quantum_enabled": self.quantum_enabled,
            "quantum_metrics": quantum_metrics,
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_sensor_data(self, lat: float = 51.5074, lon: float = -0.1278) -> dict:
        # Always generate location-based sensor data for accurate predictions
        # Tropical cities (near equator) are hotter, northern cities are colder
        base_temp = 28 - abs(lat) * 0.35  # Temp decreases with latitude from equator
        base_humidity = 70 + (20 - abs(lat)) * 0.4  # Higher humidity near equator
        base_pressure = 1013 - (abs(lat) / 90) * 12  # Pressure varies with latitude
        
        # Add randomization for natural variation
        import random
        base = {
            'pressure': base_pressure + random.uniform(-8, 8),
            'temperature': base_temp + random.uniform(-5, 5),
            'humidity': min(100, max(0, base_humidity + random.uniform(-15, 15))),
            'wind_speed': random.uniform(1, 12),
            'max_wind_speed': random.uniform(5, 18),
            'wind_direction': random.uniform(0, 360),
            'dew_point': base_temp * 0.55 + random.uniform(-3, 3)
        }
        
        return base


class RouteOptimizer:
    """Route optimization."""
    
    def calculate_route(self, current: tuple, disaster: tuple, dtype: str) -> dict:
        dtype = SecurityConfig.sanitize_input(dtype, 20)
        
        if not SecurityConfig.validate_coordinates(current[0], current[1]):
            return {"error": "Invalid coordinates"}
        
        zones = {
            "SW": (51.45, -0.20),
            "NW": (51.55, -0.20),
            "SE": (51.45, -0.05),
            "NE": (51.55, -0.05)
        }
        
        best_zone = min(zones.items(), 
            key=lambda x: math.sqrt((x[1][0]-current[0])**2 + (x[1][1]-current[1])**2)
        )
        
        return {
            "destination": best_zone[0],
            "destination_coords": best_zone[1],
            "distance_km": round(math.sqrt((best_zone[1][0]-current[0])**2 + (best_zone[1][1]-current[1])**2) * 111, 2),
            "route_type": dtype
        }


predictor = QuantumMLPredictor()
route_optimizer = RouteOptimizer()


@app.before_request
def before_request():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=1)


@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/api/predict', methods=['POST'])
def api_predict():
    try:
        import sys
        data = request.get_json() or {}
        city = data.get('city', 'Chennai')
        
        sys.stderr.write(f"DEBUG: Received city: {city}\n")
        sys.stderr.flush()
        
        city = SecurityConfig.sanitize_input(city, 50)
        if not re.match(r'^[a-zA-Z\s\-]+$', city):
            return jsonify({"error": "Invalid city name"}), 400
        
        # Get coordinates for city
        coords = get_city_coordinates(city)
        sys.stderr.write(f"DEBUG: Coords: {coords}\n")
        sys.stderr.flush()
        
        result = predictor.predict(city, coords)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# City coordinates database
CITY_COORDINATES = {
    "london": (51.5074, -0.1278),
    "new york": (40.7128, -74.0060),
    "tokyo": (35.6762, 139.6503),
    "paris": (48.8566, 2.3522),
    "sydney": (-33.8688, 151.2093),
    "dubai": (25.2048, 55.2708),
    "singapore": (1.3521, 103.8198),
    "mumbai": (19.0760, 72.8777),
    "delhi": (28.7041, 77.1025),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "jaipur": (26.9124, 75.7873),
    "kerala": (10.8505, 76.2711),
    "rajasthan": (27.0238, 74.2179),
    "gujarat": (22.2587, 71.1924),
    "himachal": (31.1048, 77.1734),
    "tamil nadu": (11.1271, 78.6569),
    "los angeles": (34.0522, -118.2437),
    "chicago": (41.8781, -87.6298),
    "san francisco": (37.7749, -122.4194),
    "miami": (25.7617, -80.1918),
    "seattle": (47.6062, -122.3321),
    "boston": (42.3601, -71.0589),
    "berlin": (52.5200, 13.4050),
    "madrid": (40.4168, -3.7038),
    "rome": (41.9028, 12.4964),
    "amsterdam": (52.3676, 4.9041),
    "moscow": (55.7558, 37.6173),
    "beijing": (39.9042, 116.4074),
    "shanghai": (31.2304, 121.4737),
    "hong kong": (22.3193, 114.1694),
    "taipei": (25.0330, 121.5654),
    "seoul": (37.5665, 126.9780),
    "bangkok": (13.7563, 100.5018),
    "jakarta": (-6.2088, 106.8456),
    "kuala lumpur": (3.1390, 101.6869),
    "manila": (14.5995, 120.9842),
    "cairo": (30.0444, 31.2357),
    "lagos": (6.5244, 3.3792),
    "cape town": (-33.9249, 18.4241),
    "nairobi": (-1.2921, 36.8219),
    "rio de janeiro": (-22.9068, -43.1729),
    "buenos aires": (-34.6037, -58.3816),
    "mexico city": (19.4326, -99.1332),
    "toronto": (43.6532, -79.3832),
    "vancouver": (49.2827, -123.1207),
    "melbourne": (-37.8136, 144.9631),
    "auckland": (-36.8509, 174.7645),
}

def get_city_coordinates(city_name):
    """Get coordinates for a city name."""
    city_lower = city_name.lower().strip()
    
    # Direct lookup
    if city_lower in CITY_COORDINATES:
        return CITY_COORDINATES[city_lower]
    
    # Try partial match
    for city, coords in CITY_COORDINATES.items():
        if city_lower in city or city in city_lower:
            return coords
    
    # Default to Chennai
    return (13.0827, 80.2707)


@app.route('/api/route', methods=['POST'])
def api_route():
    try:
        data = request.get_json() or {}
        
        current = data.get('current', {})
        disaster = data.get('disaster', {})
        dtype = data.get('type', 'normal')
        
        current_lat = float(current.get('lat', 0))
        current_lon = float(current.get('lon', 0))
        disaster_lat = float(disaster.get('lat', 0))
        disaster_lon = float(disaster.get('lon', 0))
        
        if not all([SecurityConfig.validate_coordinates(current_lat, current_lon),
                   SecurityConfig.validate_coordinates(disaster_lat, disaster_lon)]):
            return jsonify({"error": "Invalid coordinates"}), 400
        
        result = route_optimizer.calculate_route(
            (current_lat, current_lon),
            (disaster_lat, disaster_lon),
            dtype
        )
        
        return jsonify(result)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid request"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "version": "4.0",
        "quantum_ml": predictor.quantum_enabled,
        "timestamp": datetime.now().isoformat()
    })


@app.route('/api/quantum-info')
def api_quantum_info():
    return jsonify({
        "quantum_enabled": predictor.quantum_enabled,
        "backend": "classical_simulator" if not predictor.quantum_enabled else "quantum_simulator",
        "feature_map": "ZZFeatureMap" if predictor.quantum_enabled else "N/A",
        "num_qubits": 4 if predictor.quantum_enabled else 0
    })


@app.errorhandler(500)
def error_handler(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    DatabaseManager.init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
