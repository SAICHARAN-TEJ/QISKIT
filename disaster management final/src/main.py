# main.py
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from disaster_predictor import DisasterPredictor
from quantum_route_optimizer import QuantumRouteOptimizer
from position_monitor import PositionMonitor

def main():
    print("🌪️  QUANTUM DISASTER RESPONSE SYSTEM v2.0")
    print("🚀 Powered by Jena Climate Dataset (2009–2016)")
    print("=" * 60)
    
    try:
        print("🔍 Initializing disaster prediction system...")
        predictor = DisasterPredictor()
        
        print("🗺️  Initializing quantum route optimization...")
        route_optimizer = QuantumRouteOptimizer()
        
        print("📍 Initializing real-time position monitoring...")
        position_monitor = PositionMonitor()
        
        print(f"\n⚡ ANALYZING LATEST CLIMATE RECORD...")
        prediction = predictor.predict_from_weather_data()
        
        sensors = prediction['sensor_data']
        print(f"\n📊 REAL-TIME SENSOR READINGS:")
        print(f"   Atmospheric Pressure: {sensors['pressure']:.2f} mbar")
        print(f"   Temperature: {sensors['temperature']:.2f}°C")
        print(f"   Relative Humidity: {sensors['humidity']:.2f}%")
        print(f"   Wind Velocity: {sensors['wind_speed']:.2f} m/s ({sensors['wind_speed']*3.6:.2f} km/h)")
        print(f"   Wind Direction: {sensors['wind_direction']:.2f}°")
        print(f"   Dew Point Temperature: {sensors['dew_point']:.2f}°C")
        
        evacuation_route = None
        if prediction['evacuation_needed']:
            print("\n🧠 QUANTUM ROUTE OPTIMIZATION IN PROGRESS...")
            evacuation_route = route_optimizer.find_optimal_route(
                prediction['current_position'],
                prediction['disaster_location'],
                prediction['disaster_type']
            )
        else:
            print("\n✅ No evacuation needed. System in monitoring mode.")
        
        position_monitor.display_live_status(
            current_position=prediction['current_position'],
            disaster_location=prediction['disaster_location'],
            disaster_type=prediction['disaster_type'],
            risk_percentage=prediction['risk_percentage'],
            evacuation_route=evacuation_route
        )
        
        print("\n✅ Quantum disaster response system completed successfully!")
        
    except FileNotFoundError as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        print("👉 Please download the Jena Climate Dataset from:")
        print("   https://storage.googleapis.com/tensorflow/tf-keras-datasets/jena_climate_2009_2016.csv.zip")
        print("   and place it at:")
        print(f"   {os.path.abspath('data/jena_climate_2009_2016.csv')}")
        
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise

if __name__ == "__main__":
    main()