# QuantumRes: Disaster Response AI

Real-time disaster prediction and evacuation routing powered by quantum-inspired algorithms

[Live Demo](https://qiskit-7xhj.onrender.com)
[GitHub Repository](https://github.com/SAICHARAN-TEJ/QISKIT)
[Python](https://www.python.org/)
[Qiskit](https://qiskit.org/)

## Quick Start

See QuantumRes in action: [Live Demo](https://qiskit-7xhj.onrender.com)

Run locally:
```
# Clone the repository
git clone https://github.com/SAICHARAN-TEJ/QISKIT.git
cd QISKIT

# Install dependencies
pip install -r requirements.txt

# Start the application
python webapp/app.py

# Open in browser: http://localhost:5000
```

## What QuantumRes Does

QuantumRes helps communities prepare for and respond to natural disasters by:

1. Detects your location (with permission) or lets you specify any city worldwide
2. Analyzes current conditions using real weather data and quantum-inspired ML models
3. Predicts disaster types (heat waves, cyclones, floods, blizzards, earthquakes) with risk levels
4. Calculates optimal evacuation routes using quantum-inspired optimization and real road data
5. Visualizes everything on interactive maps showing your position, danger zones, and safe paths

## How It Works

### Data Flow
Location Input 
    ↓
[Weather API] → Real-time atmospheric data 
    ↓
[Quantum ML Model] → Disaster type + risk percentage 
    ↓
[Route Optimizer] → 4 evacuation options ranked by safety 
    ↓
[Interactive Map] → Your location, threat zone, and escape routes

### Core Technologies
- Real Weather Data: OpenWeatherMap API for current conditions
- Smart Routing: OpenRouteService for actual road networks
- Quantum-Inspired ML: Variational circuits for pattern recognition
- Interactive Maps: Leaflet.js with custom visualizations
- Responsive Design: Works on mobile, tablet, and desktop

## Features

### For Residents & Communities
- Precise Location Detection: Browser geolocation or city search
- Early Warning System: Color-coded risk levels (LOW to CRITICAL)
- Evacuation Planning: Multiple route options with safety scores
- Live Map Display: See exactly where danger is and where to go
- Mobile Friendly: Works on any device with a browser

### For Emergency Planners
- Multi-Disaster Coverage: 5 major disaster types modeled
- Risk Quantification: Numerical scores for resource allocation
- Route Analysis: Comparative safety scoring of alternatives
- Simulation Mode: Test scenarios for preparedness drills

## Technical Highlights

### APIs Integrated (Securely)
- OpenWeatherMap: Real temperature, pressure, humidity, wind data
- OpenRouteService: Actual driving routes following road networks
- Keys stored as environment variables - never in code

### Quantum-Inspired Elements
- Variational Circuits: For complex pattern recognition in weather data
- Optimization Landscapes: Finding optimal evacuation directions
- Hybrid Approach: Quantum feature mapping + classical decision making

### Performance
- Sub-second predictions: From location to actionable intel
- Low bandwidth: Efficient API usage with caching
- Graceful degradation: Works fully even if external APIs unavailable

## Project Structure

```
QISKIT/
├── webapp/
│   ├── app.py              # Main Flask application
│   ├── templates/          # HTML pages (dashboard + landing)
│   └── static/             # CSS, JS, and assets
├── src/
│   ├── ml/                 # Machine learning components
│   └── quantum/            # Quantum-inspired algorithms
├── requirements.txt        # Python dependencies
├── Procfile                # For Render deployment
└── runtime.txt             # Python version specification
```

## Use Cases

### Individual Preparedness
- Check risk for your current location before traveling
- Plan evacuation routes for hurricane season
- Understand local flood risks during heavy rains

### Community Planning
- Pre-position resources based on predicted risk levels
- Design better evacuation routes using historical data
- Conduct drills with simulated disaster scenarios

### Education & Awareness
- Visualize how different weather conditions create risks
- Understand evacuation timing and route selection
- Learn about quantum computing applications in humanitarian work

## Contributing

We welcome improvements! Please:
1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-idea)
3. Make your changes
4. Submit a pull request

### Areas for Contribution
- Additional disaster types (wildfires, tsunamis, etc.)
- Enhanced routing algorithms (public transit, walking paths)
- Improved visualization layers (shelters, hospitals, etc.)
- Multi-language support
- Performance optimizations

## License

MIT License - see LICENSE for details

## Acknowledgments

- Weather Data: OpenWeatherMap API
- Routing Engine: OpenRouteService API
- Quantum Framework: IBM Qiskit and PennyLane
- Mapping: Leaflet.js and OpenStreetMap contributors
- UI Inspiration: Modern quantum computing visualization techniques


---

QuantumRes bridges cutting-edge quantum computing research with practical disaster response tools. Built with care for communities worldwide.