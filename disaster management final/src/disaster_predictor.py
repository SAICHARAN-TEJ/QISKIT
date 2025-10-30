# disaster_predictor.py
import pandas as pd
import numpy as np
import os

class DisasterPredictor:
    def __init__(self):
        self.csv_path = os.path.join("data", "jena_climate_2009_2016.csv")
        if not os.path.exists(self.csv_path):
            raise FileNotFoundError(f"Dataset not found: {os.path.abspath(self.csv_path)}")
        
        print("⏳ Loading Jena Climate Dataset (2009–2016)...")
        raw_data = pd.read_csv(self.csv_path)
        self.data = raw_data.iloc[::6].reset_index(drop=True)  # Hourly samples
        print(f"✅ Loaded {len(self.data)} climate records")

    def _infer_disaster(self, row):
        temp = row['T (degC)']
        pressure = row['p (mbar)']
        rh = row['rh (%)']
        wind = row['wv (m/s)']

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
        else:
            return "normal", max(10.0, 30 - abs(temp - 15))

    def predict_from_weather_data(self):
        row = self.data.iloc[-1]
        pressure = float(row['p (mbar)'])
        temperature = float(row['T (degC)'])
        humidity = float(row['rh (%)'])
        wind_speed = float(row['wv (m/s)'])
        dew_point = float(row['Tdew (degC)'])
        wind_direction = float(row.get('wd (deg)', 180.0))

        disaster_type, risk = self._infer_disaster(row)
        risk_percentage = float(risk)

        locations = {
            "cyclone": (0.85, 0.25),
            "flood": (0.55, 0.15),
            "heat_wave": (0.4, 0.6),
            "blizzard": (0.45, 0.85),
            "earthquake": (0.5, 0.5),
            "normal": (0.5, 0.5)
        }
        disaster_location = locations.get(disaster_type, (0.5, 0.5))
        current_position = (
            np.clip(disaster_location[0] + np.random.uniform(-0.15, 0.15), 0, 1),
            np.clip(disaster_location[1] + np.random.uniform(-0.15, 0.15), 0, 1)
        )

        return {
            'disaster_type': disaster_type,
            'risk_percentage': round(risk_percentage, 1),
            'disaster_location': disaster_location,
            'current_position': current_position,
            'evacuation_needed': risk_percentage >= 70.0,
            'sensor_data': {
                'pressure': pressure,
                'temperature': temperature,
                'humidity': humidity,
                'wind_speed': wind_speed,
                'max_wind_speed': wind_speed,
                'wind_direction': wind_direction,
                'dew_point': dew_point
            }
        }