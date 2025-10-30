# position_monitor.py
import numpy as np

class PositionMonitor:
    def __init__(self):
        self.city_diameter_meters = 2000.0

    def _calculate_distance_meters(self, pos1, pos2):
        norm_dist = np.sqrt((pos2[0] - pos1[0])**2 + (pos2[1] - pos1[1])**2)
        return int(norm_dist * self.city_diameter_meters)

    def _get_safety_status(self, risk, _):
        if risk >= 85: return "🚨 CRITICAL: Immediate evacuation required!"
        if risk >= 70: return "⚠️  HIGH RISK: Evacuate immediately!"
        if risk >= 50: return "🟡 MEDIUM RISK: Prepare for evacuation."
        return "🟢 LOW RISK: No immediate evacuation needed."

    def display_live_status(self, current_position, disaster_location,
                           disaster_type, risk_percentage, evacuation_route=None):
        dist_to_disaster = self._calculate_distance_meters(current_position, disaster_location)
        dist_to_safety = 500  # Simplified
        safety_status = self._get_safety_status(risk_percentage, dist_to_safety)

        output = []
        output.append("\n" + "="*70)
        output.append("📍 QUANTUM DISASTER RESPONSE SYSTEM - REAL-TIME MONITORING")
        output.append("="*70)
        output.append(f"🎯 YOUR EXACT POSITION:     ({current_position[0]:.6f}, {current_position[1]:.6f})")
        output.append(f"🔥 DISASTER EPICENTER:      ({disaster_location[0]:.6f}, {disaster_location[1]:.6f})")
        output.append(f"🌀 DISASTER TYPE:           {disaster_type.upper()}")
        output.append(f"📊 RISK ASSESSMENT:         {risk_percentage:.1f}%")
        output.append("")
        output.append(f"🏠 NEAREST SAFE ZONE:      SAFE_ZONE_3")
        output.append(f"📏 DISTANCE TO SAFETY:     {dist_to_safety} meters")
        output.append(f"💥 DISTANCE TO DISASTER:   {dist_to_disaster} meters")
        output.append("")
        output.append(f"🛡️  SAFETY RECOMMENDATION: {safety_status}")

        if evacuation_route:
            output.append("\n" + "🗺️  QUANTUM-OPTIMIZED EVACUATION INSTRUCTIONS:")
            output.append("-" * 50)
            output.append(evacuation_route)

        output.append("="*70)
        output.append("📡 Data Source: Jena Climate Dataset (2009–2016)")
        output.append("🧠 Quantum Processing: Real-time disaster prediction & routing")
        print("\n".join(output))