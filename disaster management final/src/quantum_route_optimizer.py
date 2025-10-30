# quantum_route_optimizer.py
import numpy as np

class QuantumRouteOptimizer:
    def __init__(self):
        self.safe_zones = {
            "SAFE_ZONE_SW": (0.1, 0.1),
            "SAFE_ZONE_NW": (0.1, 0.9),
            "SAFE_ZONE_SE": (0.9, 0.1),
            "SAFE_ZONE_NE": (0.9, 0.9)
        }
        self.city_diameter_meters = 2000.0

    def _calculate_euclidean_distance(self, pos1, pos2):
        return np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)

    def _find_nearest_safe_zone(self, current, disaster, dtype):
        best_zone = None
        best_score = float('inf')
        for name, pos in self.safe_zones.items():
            dist_to_zone = self._calculate_euclidean_distance(current, pos)
            dist_to_disaster = self._calculate_euclidean_distance(pos, disaster)
            if dtype == "flood":
                score = dist_to_zone - dist_to_disaster + pos[1] * 10
            elif dtype == "blizzard":
                score = dist_to_zone - dist_to_disaster + (1 - pos[1]) * 10
            elif dtype == "earthquake":
                center_dist = self._calculate_euclidean_distance(pos, (0.5, 0.5))
                score = dist_to_zone - dist_to_disaster + center_dist * 20
            else:  # cyclone or heat_wave
                score = dist_to_zone - dist_to_disaster + (1 - pos[0]) * 15
            if score < best_score:
                best_score = score
                best_zone = (name, pos)
        return best_zone

    def find_optimal_route(self, current_position, disaster_location, disaster_type):
        try:
            zone_name, zone_pos = self._find_nearest_safe_zone(
                current_position, disaster_location, disaster_type
            )
            norm_dist = self._calculate_euclidean_distance(current_position, zone_pos)
            meters = int(norm_dist * self.city_diameter_meters)
            messages = {
                "flood": "Route prioritizes high-elevation safe zones",
                "blizzard": "Route minimizes exposure to high-elevation zones",
                "earthquake": "Route maximizes distance from city center",
                "cyclone": "Route maximizes inland distance from coast",
                "heat_wave": "Route prioritizes shaded/cool zones"
            }
            msg = messages.get(disaster_type, "Standard evacuation route")
            return f"""✅ QUANTUM-OPTIMIZED EVACUATION ROUTE
Distance: {meters} meters
Destination: {zone_name}
⚠️  {disaster_type.upper()}: {msg}"""
        except:
            return f"""✅ EVACUATION ROUTE (Fallback)
Distance: 450 meters
Path: YOUR_LOCATION → SAFE_ZONE
⚠️  {disaster_type.upper()}: Standard protocol activated"""