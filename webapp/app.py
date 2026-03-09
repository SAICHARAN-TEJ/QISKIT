"""
ResQbit - Quantum Disaster Response System
Flask Web Application with Complete Security
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
from typing import Optional

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

import numpy as np
import pandas as pd

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

DB_PATH = os.path.join(PROJECT_ROOT, "webapp", "resqbit.db")


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
    """Secure database management."""
    
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
                (user_id, action, ip_address, user_agent[:500], details)
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


class DisasterPredictor:
    """Disaster prediction engine."""

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

    def _load_jena_data(self):
        data_path = os.path.join(PROJECT_ROOT, "src", "data", "jena_climate_2009_2016.csv")
        if not os.path.exists(data_path):
            return None
        return pd.read_csv(data_path).iloc[::6].reset_index(drop=True)

    def _infer_disaster(self, temp: float, pressure: float, rh: float, wind: float) -> tuple:
        if temp > 35.0 and rh > 60:
            return "heat_wave", min(95.0, 70 + (temp - 35) * 1.2)
        elif wind > 15.0 and pressure < 980:
            return "cyclone", min(98.0, 75 + (980 - pressure) * 0.1)
        elif rh > 90 and temp > 5:
            return "flood", min(90.0, 65 + (rh - 90) * 0.8)
        elif temp < -5 and wind > 8:
            return "blizzard", min(88.0, 70 + (-temp - 5) * 0.7)
        elif pressure < 970:
            return "earthquake", 80.0
        return "normal", max(10.0, 30 - abs(temp - 15))

    def _get_risk_level(self, risk: float) -> str:
        if risk >= 85: return "CRITICAL"
        elif risk >= 70: return "HIGH"
        elif risk >= 50: return "MEDIUM"
        return "LOW"

    def predict(self, city: str = "London") -> dict:
        city = SecurityConfig.sanitize_input(city, 50)
        
        if self.jena_data is None:
            return {"error": "Dataset not found"}

        row = self.jena_data.iloc[-1]
        temp = float(row['T (degC)'])
        pressure = float(row['p (mbar)'])
        rh = float(row['rh (%)'])
        wind = float(row['wv (m/s)'])

        disaster_type, risk = self._infer_disaster(temp, pressure, rh, wind)
        risk_level = self._get_risk_level(risk)
        lat, lon = self.LOCATIONS.get(disaster_type, (51.5074, -0.1278))
        current_lat = lat + np.random.uniform(-0.05, 0.05)
        current_lon = lon + np.random.uniform(-0.05, 0.05)

        return {
            "city": city,
            "disaster_type": disaster_type,
            "risk_percentage": round(risk, 1),
            "risk_level": risk_level,
            "evacuation_needed": risk >= 70.0,
            "current_position": {"lat": current_lat, "lon": current_lon},
            "disaster_location": {"lat": lat, "lon": lon},
            "sensor_data": {
                "pressure": float(row['p (mbar)']),
                "temperature": float(row['T (degC)']),
                "humidity": float(row['rh (%)']),
                "wind_speed": float(row['wv (m/s)']),
                "wind_direction": float(row['wd (deg)']),
                "dew_point": float(row['Tdew (degC)'])
            },
            "timestamp": datetime.now().isoformat()
        }


class RouteOptimizer:
    """Route optimization with safe zone calculation."""

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


predictor = DisasterPredictor()
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
        data = request.get_json() or {}
        city = data.get('city', 'London')
        
        city = SecurityConfig.sanitize_input(city, 50)
        if not re.match(r'^[a-zA-Z\s\-]+$', city):
            return jsonify({"error": "Invalid city name"}), 400
        
        result = predictor.predict(city)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
        return jsonify({"error": "Invalid request"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "online",
        "version": "3.0",
        "security": "enabled",
        "timestamp": datetime.now().isoformat()
    })

@app.errorhandler(500)
def error_handler(e):
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    DatabaseManager.init_db()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
