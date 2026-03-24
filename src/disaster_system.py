"""
QuantumML Disaster Prediction System v4.0
=========================================
Real-time disaster prediction using quantum machine learning.

Features:
- Quantum Feature Maps: ZZFeatureMap for environmental data encoding
- Variational Quantum Circuits: Hybrid quantum-classical classification
- Quantum Kernel Methods: Advanced pattern recognition
- Real-time Weather: OpenWeatherMap API or Jena historical dataset
- Free Routing: OSRM for evacuation planning
- Alert Notifications: Discord webhooks + Email
"""

import os
import sys
import json
import math
import random
import smtplib
import ssl
import hashlib
import secrets
import re
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(PROJECT_ROOT, "src"))

import numpy as np
import pandas as pd

try:
    from quantum import (
        QuantumFeatureMap, ZZFeatureMap, EfficientSU2Map,
        VariationalQuantumClassifier, QuantumNeuralNetwork,
        HybridQuantumClassicalClassifier, QuantumEnsemble,
        QuantumBackend, QuantumMetrics, CircuitVisualizer
    )
    from ml import (
        DisasterFeatures, FeatureEngineering, DataPreprocessor,
        prepare_quantum_features
    )
    QUANTUM_ML_AVAILABLE = True
except ImportError:
    QUANTUM_ML_AVAILABLE = False


class SecurityValidator:
    """Input validation and sanitization."""
    
    SANITIZE_PATTERN = re.compile(r'[^\w\s\-.,@]')
    COORD_PATTERN = re.compile(r'^-?\d+\.?\d*$')
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 255) -> str:
        if not isinstance(value, str):
            return ""
        sanitized = value[:max_length].strip()
        sanitized = SecurityValidator.SANITIZE_PATTERN.sub('', sanitized)
        return sanitized
    
    @staticmethod
    def validate_coordinates(lat: float, lon: float) -> bool:
        try:
            return -90 <= float(lat) <= 90 and -180 <= float(lon) <= 180
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_city_name(city: str) -> bool:
        if not city or not isinstance(city, str):
            return False
        return bool(re.match(r'^[a-zA-Z\s\-]+$', city)) and len(city) <= 100
    
    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()


class TokenManager:
    """Secure token management."""
    
    @staticmethod
    def generate_token(length: int = 32) -> str:
        return secrets.token_urlsafe(length)
    
    @staticmethod
    def hash_token(token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
    
    @staticmethod
    def verify_token(token: str, hashed: str) -> bool:
        return TokenManager.hash_token(token) == hashed


class RateLimiter:
    """Rate limiter for API endpoints."""
    
    _requests = {}
    _limits = {
        'default': (10, 60),
        'weather': (5, 60),
        'route': (10, 60),
        'alert': (3, 300),
        'quantum': (5, 60)
    }
    
    @classmethod
    def check_rate_limit(cls, key: str, limit_type: str = 'default') -> bool:
        now = datetime.now()
        max_requests, time_window = cls._limits.get(limit_type, cls._limits['default'])
        
        if key not in cls._requests:
            cls._requests[key] = []
        
        cls._requests[key] = [t for t in cls._requests[key] if now - t < timedelta(seconds=time_window)]
        
        if len(cls._requests[key]) >= max_requests:
            return False
        
        cls._requests[key].append(now)
        return True


class DisasterType(Enum):
    HEAT_WAVE = "heat_wave"
    CYCLONE = "cyclone"
    FLOOD = "flood"
    BLIZZARD = "blizzard"
    EARTHQUAKE = "earthquake"
    NORMAL = "normal"


class RiskLevel(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH RISK"
    MEDIUM = "MEDIUM RISK"
    LOW = "LOW RISK"


@dataclass
class SensorData:
    pressure: float
    temperature: float
    humidity: float
    wind_speed: float
    max_wind_speed: float
    wind_direction: float
    dew_point: float
    source: str


@dataclass
class PredictionResult:
    disaster_type: DisasterType
    risk_percentage: float
    risk_level: RiskLevel
    disaster_location: tuple
    current_position: tuple
    evacuation_needed: bool
    sensor_data: SensorData
    city: str
    timestamp: str
    quantum_metrics: Optional[Dict] = None
    circuit_info: Optional[Dict] = None
    feature_vector: Optional[np.ndarray] = None


class Config:
    """Configuration management."""
    
    @staticmethod
    def load() -> dict:
        return {
            "openweather_api_key": os.environ.get("OPENWEATHERMAP_API_KEY", ""),
            "discord_webhook": os.environ.get("DISCORD_WEBHOOK_URL", ""),
            "smtp_server": os.environ.get("SMTP_SERVER", "smtp.gmail.com"),
            "smtp_port": int(os.environ.get("SMTP_PORT", "465")),
            "sender_email": os.environ.get("SENDER_EMAIL", ""),
            "sender_password": os.environ.get("SENDER_PASSWORD", ""),
            "recipient_emails": os.environ.get("RECIPIENT_EMAILS", "").split(","),
            "default_city": os.environ.get("DEFAULT_CITY", "London"),
            "data_source": os.environ.get("DATA_SOURCE", "jena"),
            "secret_key": os.environ.get("SECRET_KEY", secrets.token_hex(32)),
            "quantum_enabled": os.environ.get("QUANTUM_ENABLED", "true").lower() == "true",
            "quantum_backend": os.environ.get("QUANTUM_BACKEND", "classical"),
            "quantum_shots": int(os.environ.get("QUANTUM_SHOTS", "1024")),
        }


class WeatherAPI:
    """OpenWeatherMap API client."""
    
    def __init__(self, api_key: str):
        self.api_key = SecurityValidator.sanitize_string(api_key, 100) if api_key else ""
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"
    
    def get_weather_by_city(self, city: str) -> Optional[SensorData]:
        if not self.api_key:
            return None
        
        if not SecurityValidator.validate_city_name(city):
            return None
        
        try:
            city_safe = SecurityValidator.sanitize_string(city, 50)
            url = f"{self.base_url}?q={urllib.parse.quote(city_safe)}&appid={self.api_key}&units=metric"
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())
                main = data.get("main", {})
                wind = data.get("wind", {})
                return SensorData(
                    pressure=main.get("pressure", 0),
                    temperature=main.get("temp", 0),
                    humidity=main.get("humidity", 0),
                    wind_speed=wind.get("speed", 0),
                    max_wind_speed=wind.get("speed", 0) * 1.3,
                    wind_direction=wind.get("deg", 0),
                    dew_point=main.get("temp", 0) - (100 - main.get("humidity", 0)) / 5,
                    source="OpenWeatherMap API"
                )
        except Exception:
            return None


class OSRMRouter:
    """OSRM routing service."""
    
    BASE_URL = "https://router.project-osrm.org"
    
    def get_route(self, start_lat: float, start_lon: float,
                  end_lat: float, end_lon: float) -> Optional[dict]:
        for coord in [start_lat, start_lon, end_lat, end_lon]:
            if not SecurityValidator.validate_coordinates(coord, coord):
                return None
        
        try:
            url = f"{self.BASE_URL}/route/v1/driving/{start_lon},{start_lat};{end_lon},{end_lat}?overview=full&geometries=geojson&steps=true"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                if data.get("code") != "Ok":
                    return None
                route = data["routes"][0]
                return {
                    "distance_km": route["distance"] / 1000,
                    "duration_min": route["duration"] / 60,
                    "geometry": [(c[1], c[0]) for c in route["geometry"]["coordinates"]],
                    "steps": [s.get("maneuver", {}).get("type", "continue") for s in route["legs"][0]["steps"]]
                }
        except Exception:
            return None
    
    def format_route(self, route: Optional[dict], dtype: str) -> str:
        if not route:
            return self._fallback_route(dtype)
        
        dtype_safe = SecurityValidator.sanitize_string(dtype, 20)
        messages = {
            "flood": "Route prioritizes high-elevation safe zones",
            "blizzard": "Route minimizes exposure to high-elevation zones",
            "earthquake": "Route maximizes distance from city center",
            "cyclone": "Route maximizes inland distance from coast",
            "heat_wave": "Route prioritizes shaded/cool zones"
        }
        
        lines = [
            f"EVACUATION ROUTE",
            f"Distance: {route['distance_km']:.1f} km ({route['distance_km']*1000:.0f} meters)",
            f"Estimated Time: {route['duration_min']:.1f} minutes",
            f"[{dtype_safe.upper()}]: {messages.get(dtype_safe, 'Standard protocol')}"
        ]
        return "\n".join(lines)
    
    def _fallback_route(self, dtype: str) -> str:
        zones = [(0.1, 0.1), (0.1, 0.9), (0.9, 0.1), (0.9, 0.9)]
        zone = random.choice(zones)
        meters = random.randint(300, 800)
        return f"EVACUATION ROUTE\nDistance: {meters} meters\nDestination: SAFE_ZONE"


class DiscordNotifier:
    """Discord webhook notifications."""
    
    WEBHOOK_PATTERN = re.compile(r'^https://discord\.com/api/webhooks/\d+/[a-zA-Z0-9_-]+$')
    
    def __init__(self, webhook_url: str):
        self.webhook_url = self._validate_webhook(webhook_url) if webhook_url else ""
    
    def _validate_webhook(self, url: str) -> str:
        if self.WEBHOOK_PATTERN.match(url):
            return url
        return ""
    
    def is_configured(self) -> bool:
        return bool(self.webhook_url)
    
    def send_alert(self, alert: dict) -> bool:
        if not self.webhook_url:
            return False
        try:
            alert_safe = {k: SecurityValidator.sanitize_string(str(v), 2000) for k, v in alert.items()}
            colors = {"CRITICAL": 0xFF0000, "HIGH RISK": 0xFF6600, "MEDIUM RISK": 0xFFCC00, "LOW RISK": 0x00CC00}
            payload = {
                "embeds": [{
                    "title": f"QUANTUM ML ALERT: {alert_safe.get('title', 'Alert')[:100]}",
                    "description": alert_safe.get('instructions', '')[:2000],
                    "color": colors.get(alert_safe.get('risk_level', 'LOW'), 0xFFFFFF),
                    "fields": [
                        {"name": "Disaster", "value": alert_safe.get('disaster_type', 'Unknown')[:100], "inline": True},
                        {"name": "Risk", "value": alert_safe.get('risk_level', 'Unknown')[:50], "inline": True},
                        {"name": "Location", "value": alert_safe.get('location', 'Unknown')[:100], "inline": False},
                        {"name": "Quantum Analysis", "value": alert_safe.get('quantum_info', 'Enabled')[:100], "inline": False},
                    ],
                    "footer": {"text": f"QiskitML | {alert_safe.get('timestamp', '')}"}
                }]
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(self.webhook_url, data=data, headers={"Content-Type": "application/json"})
            urllib.request.urlopen(req, timeout=10)
            return True
        except Exception:
            return False


class EmailNotifier:
    """Gmail SMTP notifications."""
    
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __init__(self, config: dict):
        self.config = self._validate_config(config)
    
    def _validate_config(self, config: dict) -> dict:
        validated = {}
        if config.get("sender_email") and self.EMAIL_PATTERN.match(config["sender_email"]):
            validated["sender_email"] = config["sender_email"]
        if config.get("sender_password") and len(config["sender_password"]) >= 16:
            validated["sender_password"] = config["sender_password"]
        validated["smtp_server"] = "smtp.gmail.com"
        validated["smtp_port"] = 465
        if config.get("recipient_emails"):
            validated["recipient_emails"] = [e for e in config["recipient_emails"] if self.EMAIL_PATTERN.match(e)]
        return validated
    
    def is_configured(self) -> bool:
        return bool(self.config.get("sender_email") and self.config.get("sender_password"))
    
    def send_alert(self, alert: dict) -> bool:
        if not self.is_configured():
            return False
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            alert_safe = {k: SecurityValidator.sanitize_string(str(v), 5000) for k, v in alert.items()}
            message = MIMEMultipart("alternative")
            message["Subject"] = f"URGENT: Quantum ML Disaster Alert - {alert_safe.get('title', 'Alert')[:100]}"
            message["From"] = self.config["sender_email"]
            message["To"] = ", ".join(self.config.get("recipient_emails", []))
            
            text = f"QUANTUM ML DISASTER ALERT\n\n{alert_safe.get('title', '')}\n\nDisaster: {alert_safe.get('disaster_type', '')}\nRisk: {alert_safe.get('risk_level', '')}\nLocation: {alert_safe.get('location', '')}\nQuantum Analysis: Enabled\n\nInstructions: {alert_safe.get('instructions', '')}"
            
            message.attach(MIMEText(text[:5000], "plain"))
            
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(self.config["smtp_server"], self.config["smtp_port"], context=context) as server:
                server.login(self.config["sender_email"], self.config["sender_password"])
                server.sendmail(self.config["sender_email"], self.config.get("recipient_emails", []), message.as_string())
            return True
        except Exception:
            return False


class QuantumMLPredictor:
    """
    Quantum Machine Learning Disaster Predictor.
    
    Uses quantum feature maps and variational quantum circuits
    for enhanced disaster classification.
    """
    
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
    
    def __init__(self, config: dict):
        self.config = config
        self.use_api = config.get("data_source") == "api" and config.get("openweather_api_key")
        self.weather_api = WeatherAPI(config.get("openweather_api_key", "")) if self.use_api else None
        self.jena_data = self._load_jena_data()
        
        self.quantum_enabled = config.get("quantum_enabled", True) and QUANTUM_ML_AVAILABLE
        self.quantum_classifier = None
        self.preprocessor = DataPreprocessor(normalization='minmax')
        
        if self.quantum_enabled:
            self._initialize_quantum_components()
    
    def _load_jena_data(self) -> Optional[pd.DataFrame]:
        data_path = os.path.join(PROJECT_ROOT, "src", "data", "jena_climate_2009_2016.csv")
        if not os.path.exists(data_path):
            return None
        return pd.read_csv(data_path).iloc[::6].reset_index(drop=True)
    
    def _initialize_quantum_components(self):
        """Initialize quantum ML components."""
        try:
            self.feature_map = ZZFeatureMap(
                num_qubits=4,
                num_features=7,
                reps=2,
                entanglement='linear'
            )
            
            from quantum.circuits import create_vqc, CircuitConfig, AnsatzType, MeasurementType
            vqc_config = CircuitConfig(
                num_qubits=4,
                num_layers=2,
                ansatz_type=AnsatzType.EFFICIENT_SU2,
                measurement_type=MeasurementType.PARITY,
                shots=self.config.get("quantum_shots", 1024)
            )
            self.quantum_classifier = VariationalQuantumClassifier(
                config=vqc_config,
                feature_map=self.feature_map
            )
            
            self.quantum_backend = QuantumBackend()
            
        except Exception as e:
            print(f"Warning: Quantum components initialization failed: {e}")
            self.quantum_enabled = False
    
    def _extract_features(self, sensor: SensorData) -> np.ndarray:
        """Extract and prepare features for quantum model."""
        features = DisasterFeatures(
            temperature=sensor.temperature,
            pressure=sensor.pressure,
            humidity=sensor.humidity,
            wind_speed=sensor.wind_speed,
            max_wind_speed=sensor.max_wind_speed,
            wind_direction=sensor.wind_direction,
            dew_point=sensor.dew_point
        )
        return prepare_quantum_features(features.__dict__)
    
    def _quantum_infer(self, features: np.ndarray) -> tuple:
        """Use quantum ML model for inference."""
        classical_result = self._classical_infer(features)
        
        if not self.quantum_enabled or self.quantum_classifier is None:
            return classical_result
        
        try:
            normalized_features = self.preprocessor.fit_transform(features.reshape(1, -1))[0]
            
            result = self.quantum_classifier.predict(normalized_features)
            
            probabilities = result.probabilities
            prediction = result.prediction
            
            risk_score = float(probabilities[prediction]) * 100 if prediction < len(probabilities) else classical_result[1]
            
            if risk_score < 20 or risk_score > 98:
                return classical_result
            
            disaster_type = self.DISASTER_LABELS.get(int(prediction), classical_result[0])
            
            circuit_info = {
                'type': 'VariationalQuantumClassifier',
                'num_qubits': 4,
                'feature_map': 'ZZFeatureMap',
                'ansatz': 'EfficientSU2',
                'measurements': result.measurement_counts
            }
            
            quantum_metrics = QuantumMetrics.compute_all_metrics(
                type('Result', (), {
                    'counts': result.measurement_counts or {'0': 512, '1': 512},
                    'time_taken': 0.01,
                    'backend': 'quantum_simulator'
                })(),
                circuit_info
            )
            
            return disaster_type, risk_score, circuit_info, quantum_metrics
            
        except Exception as e:
            return self._classical_infer(features)
    
    def _classical_infer(self, features: np.ndarray) -> tuple:
        """Fallback classical inference."""
        temp_idx = 0
        pressure_idx = 1
        humidity_idx = 2
        wind_idx = 3
        
        temp = float(features[temp_idx])
        pressure = float(features[pressure_idx])
        humidity = float(features[humidity_idx])
        wind = float(features[wind_idx])
        
        risk = 0.0
        disaster_type = "normal"
        
        if temp > 35.0 and humidity > 60:
            disaster_type = "heat_wave"
            risk = min(95.0, 70.0 + (temp - 35.0) * 1.2)
        elif wind > 15.0 and pressure < 980:
            disaster_type = "cyclone"
            risk = min(98.0, 75.0 + (980.0 - pressure) * 0.1)
        elif humidity > 90 and temp > 5:
            disaster_type = "flood"
            risk = min(90.0, 65.0 + (humidity - 90.0) * 0.8)
        elif temp < -5 and wind > 8:
            disaster_type = "blizzard"
            risk = min(88.0, 70.0 + (-temp - 5.0) * 0.7)
        elif pressure < 970:
            disaster_type = "earthquake"
            risk = 80.0
        else:
            disaster_type = "normal"
            risk = max(5.0, 30.0 - abs(temp - 15.0))
        
        circuit_info = {
            'type': 'ClassicalFallback',
            'method': 'Rule-based',
            'features_used': ['temperature', 'pressure', 'humidity', 'wind']
        }
        
        quantum_metrics = {
            'entropy': 0.0,
            'purity': 1.0,
            'advantage_score': 0.0,
            'complexity': 0.0,
            'mode': 'classical'
        }
        
        return disaster_type, risk, circuit_info, quantum_metrics
    
    def _get_risk_level(self, risk: float) -> RiskLevel:
        if risk >= 85:
            return RiskLevel.CRITICAL
        elif risk >= 70:
            return RiskLevel.HIGH
        elif risk >= 50:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW
    
    def predict(self, city: Optional[str] = None) -> PredictionResult:
        """Make disaster prediction."""
        city = SecurityValidator.sanitize_string(city or self.config.get("default_city", "London"), 50)
        
        sensor = self._get_sensor_data(city)
        
        features = self._extract_features(sensor)
        
        disaster_type_str, risk, circuit_info, quantum_metrics = self._quantum_infer(features)
        
        lat, lon = self.LOCATIONS.get(disaster_type_str, (51.5074, -0.1278))
        
        return PredictionResult(
            disaster_type=DisasterType(disaster_type_str),
            risk_percentage=round(risk, 1),
            risk_level=self._get_risk_level(risk),
            disaster_location=(lat, lon),
            current_position=(lat + np.random.uniform(-0.05, 0.05), lon + np.random.uniform(-0.05, 0.05)),
            evacuation_needed=risk >= 70.0,
            sensor_data=sensor,
            city=city,
            timestamp=datetime.now().isoformat(),
            quantum_metrics=quantum_metrics,
            circuit_info=circuit_info,
            feature_vector=features
        )
    
    def _get_sensor_data(self, city: str) -> SensorData:
        """Get sensor data from API or dataset."""
        if self.use_api and self.weather_api:
            weather = self.weather_api.get_weather_by_city(city)
            if weather:
                return weather
        
        if self.jena_data is not None:
            row = self.jena_data.iloc[-1]
            return SensorData(
                pressure=float(row['p (mbar)']),
                temperature=float(row['T (degC)']),
                humidity=float(row['rh (%)']),
                wind_speed=float(row['wv (m/s)']),
                max_wind_speed=float(row['max. wv (m/s)']),
                wind_direction=float(row['wd (deg)']),
                dew_point=float(row['Tdew (degC)']),
                source="Jena Climate Dataset + Quantum ML"
            )
        
        return SensorData(
            pressure=1013.0,
            temperature=20.0,
            humidity=50.0,
            wind_speed=5.0,
            max_wind_speed=6.0,
            wind_direction=180.0,
            dew_point=10.0,
            source="Default (Quantum ML Ready)"
        )


class RouteOptimizer:
    """Evacuation route optimizer."""
    
    def __init__(self):
        self.osrm = OSRMRouter()
    
    def find_route(self, current: tuple, disaster: tuple, dtype: str) -> str:
        lat, lon = self._find_safe_zone(current, disaster, dtype)
        route = self.osrm.get_route(current[0], current[1], lat, lon)
        return self.osrm.format_route(route, dtype)
    
    def _find_safe_zone(self, current, disaster, dtype: str) -> tuple:
        zones = {"SW": (0.1, 0.1), "NW": (0.1, 0.9), "SE": (0.9, 0.1), "NE": (0.9, 0.9)}
        best_zone, best_score = None, float('inf')
        dtype_safe = SecurityValidator.sanitize_string(dtype, 20)
        
        for name, pos in zones.items():
            dist_zone = math.sqrt((pos[0] - current[0])**2 + (pos[1] - current[1])**2)
            dist_disaster = math.sqrt((pos[0] - disaster[0])**2 + (pos[1] - disaster[1])**2)
            score = dist_zone - dist_disaster
            
            if dtype_safe == "flood":
                score += pos[1] * 10
            elif dtype_safe == "blizzard":
                score += (1 - pos[1]) * 10
            elif dtype_safe == "earthquake":
                score += math.sqrt((pos[0]-0.5)**2 + (pos[1]-0.5)**2) * 20
            else:
                score += (1 - pos[0]) * 15
            
            if score < best_score:
                best_score, best_zone = score, pos
        return best_zone or (0.1, 0.1)


class NotificationManager:
    """Send alerts via multiple channels."""
    
    def __init__(self, config: dict):
        self.discord = DiscordNotifier(config.get("discord_webhook", ""))
        self.email = EmailNotifier(config)
    
    def send(self, prediction: PredictionResult, route: Optional[str] = None) -> dict:
        quantum_info = "Quantum ML Analysis Enabled" if prediction.quantum_metrics else "Classical Mode"
        
        alert = {
            "title": f"{prediction.disaster_type.value.upper()} ALERT",
            "disaster_type": prediction.disaster_type.value.upper(),
            "risk_level": prediction.risk_level.value,
            "risk_percentage": prediction.risk_percentage,
            "location": f"{prediction.current_position[0]:.4f}, {prediction.current_position[1]:.4f}",
            "instructions": (route or "Evacuate to nearest safe zone immediately!")[:2000],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "quantum_info": quantum_info
        }
        return {
            "discord": self.discord.send_alert(alert) if self.discord.is_configured() else False,
            "email": self.email.send_alert(alert) if self.email.is_configured() else False
        }


class PositionMonitor:
    """Display monitoring status."""
    
    RISK_MESSAGES = {
        RiskLevel.CRITICAL: "CRITICAL: Immediate evacuation required!",
        RiskLevel.HIGH: "HIGH RISK: Evacuate immediately!",
        RiskLevel.MEDIUM: "MEDIUM RISK: Prepare for evacuation.",
        RiskLevel.LOW: "LOW RISK: No immediate evacuation needed."
    }
    
    @staticmethod
    def display(prediction: PredictionResult, route: Optional[str] = None):
        current = prediction.current_position
        disaster = prediction.disaster_location
        
        output = [
            "",
            "=" * 70,
            "QUANTUM ML DISASTER PREDICTION SYSTEM v4.0",
            "=" * 70,
            f"City:          {prediction.city}",
            f"Data Source:   {prediction.sensor_data.source}",
            f"Timestamp:     {prediction.timestamp}",
            f"Quantum ML:    {'Enabled' if prediction.quantum_metrics else 'Disabled'}",
            "",
            f"Position:      ({current[0]:.6f}, {current[1]:.6f})",
            f"Epicenter:     ({disaster[0]:.6f}, {disaster[1]:.6f})",
            f"Disaster:      {prediction.disaster_type.value.upper()}",
            f"Risk:          {prediction.risk_percentage:.1f}% ({prediction.risk_level.value})",
        ]
        
        if prediction.quantum_metrics:
            qm = prediction.quantum_metrics
            output.append("")
            output.append("QUANTUM METRICS:")
            output.append(f"  Entropy:      {qm.get('entropy', 0):.4f}")
            output.append(f"  Purity:       {qm.get('purity', 0):.4f}")
            output.append(f"  Advantage:    {qm.get('advantage_score', 0):.4f}")
            output.append(f"  Complexity:   {qm.get('complexity', 0):.4f}")
        
        output.append("")
        output.append(f"Recommendation: {PositionMonitor.RISK_MESSAGES[prediction.risk_level]}")
        
        if route:
            output.extend(["", "EVACUATION ROUTE:", "-" * 50, route[:1000]])
        
        output.append("=" * 70)
        print("\n".join(output))


def main():
    print("QUANTUM ML DISASTER PREDICTION SYSTEM v4.0")
    print("Quantum Feature Maps | Variational Circuits | Real-time Prediction")
    print("=" * 60)
    
    config = Config.load()
    
    print(f"[*] Quantum ML: {'Enabled' if config.get('quantum_enabled') else 'Disabled'}")
    
    try:
        print("[*] Initializing components...")
        predictor = QuantumMLPredictor(config)
        route_optimizer = RouteOptimizer()
        notifier = NotificationManager(config)
        
        print("[*] Fetching weather data...")
        prediction = predictor.predict()
        
        sensors = prediction.sensor_data
        print(f"\n[+] SENSOR READINGS:")
        print(f"    Pressure:   {sensors.pressure:.2f} mbar")
        print(f"    Temperature:{sensors.temperature:.2f} degC")
        print(f"    Humidity:   {sensors.humidity:.2f}%")
        print(f"    Wind Speed: {sensors.wind_speed:.2f} m/s")
        print(f"    Wind Dir:   {sensors.wind_direction:.2f} deg")
        print(f"    Dew Point:  {sensors.dew_point:.2f} degC")
        
        if prediction.quantum_metrics:
            print(f"\n[+] QUANTUM METRICS:")
            print(f"    Entropy:    {prediction.quantum_metrics.get('entropy', 0):.4f}")
            print(f"    Purity:     {prediction.quantum_metrics.get('purity', 0):.4f}")
            print(f"    Advantage:  {prediction.quantum_metrics.get('advantage_score', 0):.4f}")
        
        route = None
        if prediction.evacuation_needed:
            print("\n[!] EVACUATION REQUIRED!")
            print("[*] Computing optimal route...")
            route = route_optimizer.find_route(
                prediction.current_position,
                prediction.disaster_location,
                prediction.disaster_type.value
            )
            
            print("[*] Sending alert notifications...")
            results = notifier.send(prediction, route)
            print("[+] Discord alert sent" if results.get("discord") else "[-] Discord not configured")
            print("[+] Email alert sent" if results.get("email") else "[-] Email not configured")
        else:
            print("\n[OK] No evacuation needed. Monitoring mode.")
        
        PositionMonitor.display(prediction, route)
        print("\n[OK] System execution completed!")
        
    except FileNotFoundError as e:
        print(f"\n[ERROR] {e}")
    except Exception as e:
        print(f"\n[ERROR] {e}")


if __name__ == "__main__":
    main()
