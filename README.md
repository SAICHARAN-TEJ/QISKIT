# QiskitML - Quantum Machine Learning Disaster Prediction System

![Quantum ML](https://img.shields.io/badge/Quantum-ML-00d4ff?style=for-the-badge)
![Qiskit](https://img.shields.io/badge/Powered_by-Qiskit-6929c8?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.11+-3776ab?style=for-the-badge)

## 🔗 Live Demo

**🌐 https://qiskit-7xhj.onrender.com**

Real-time disaster prediction using **Quantum Machine Learning** powered by **IBM Qiskit**. This project leverages variational quantum circuits, quantum feature maps, and quantum kernel methods for enhanced disaster classification.

## Quantum Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Feature Encoding** | ZZFeatureMap | Quantum encoding of environmental features |
| **Classification** | Variational Quantum Circuit (VQC) | Hybrid quantum-classical learning |
| **Kernels** | Quantum Kernel Estimation | High-dimensional Hilbert space similarity |
| **Backend** | Qiskit Aer / IBM Quantum | Circuit execution |
| **Classical ML** | Scikit-learn | Pre/Post processing |

## Features

- **Quantum Feature Maps**: ZZFeatureMap for encoding environmental data (temperature, pressure, humidity, wind)
- **Variational Quantum Classifier**: Parameterized quantum circuits for disaster type classification
- **Quantum Metrics**: Entropy, purity, and quantum advantage scoring
- **Multi-Disaster Detection**: Heat Waves, Cyclones, Floods, Blizzards, Earthquakes
- **Real-time Alerts**: Discord webhooks + Email notifications
- **Free Routing**: OSRM for evacuation planning
- **Modern Web Interface**: Quantum-themed dashboard

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    QUANTUM ML PIPELINE                          │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌──────────────────┐    ┌───────────────┐  │
│  │   Sensor    │───▶│ Feature Engineering│───▶│  ZZFeatureMap │  │
│  │   Data      │    │    + Preprocessing│    │   Encoding    │  │
│  └─────────────┘    └──────────────────┘    └───────┬───────┘  │
│                                                        │         │
│                                                        ▼         │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              VARIATIONAL QUANTUM CIRCUIT                     ││
│  │  ┌─────┐   ┌─────┐   ┌─────┐   ┌─────┐                   ││
│  │  │  H  │──▶│ RY  │──▶│ CNOT│──▶│ RY  │──▶ Measurement   ││
│  │  └─────┘   └─────┘   └─────┘   └─────┘                   ││
│  │    Q0────────Q1────────Q2────────Q3                       ││
│  └─────────────────────────────────────────────────────────────┘│
│                           │                                     │
│                           ▼                                     │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │  Classical  │◀───│   Quantum    │───▶│    Disaster     │    │
│  │ Post-Process│    │    Metrics    │    │   Prediction    │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone the repository
git clone https://github.com/SAICHARAN-TEJ/QISKIT.git
cd QISKIT

# Create virtual environment
python -m venv qenv
source qenv/bin/activate  # On Windows: qenv\Scripts\activate

# Install quantum ML dependencies
pip install -r requirements.txt

# Install Qiskit (if not in requirements)
pip install qiskit qiskit-algorithms qiskit-machine-learning qiskit-aer
```

## Configuration

```bash
# Weather API (optional - uses Jena dataset by default)
set OPENWEATHERMAP_API_KEY=your_key

# Discord alerts (optional)
set DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...

# Email alerts (optional)
set SENDER_EMAIL=your_email@gmail.com
set SENDER_PASSWORD=your_app_password

# Quantum ML settings
set QUANTUM_ENABLED=true
set QUANTUM_BACKEND=classical  # or 'aer', 'ibm'
set QUANTUM_SHOTS=1024
```

## Running the Application

### Web Application

```bash
cd webapp
python app.py
```

Visit `http://localhost:5000`

### CLI System

```bash
python src/disaster_system.py
```

### With Quantum Backend

```bash
# Set quantum backend
set QUANTUM_ENABLED=true
set QUANTUM_BACKEND=aer

# Run
python src/disaster_system.py
```

## Quantum ML Components

### Feature Maps (`src/quantum/feature_maps.py`)

- `ZZFeatureMap`: Second-order Pauli-Z entangling feature map
- `PauliFeatureMap`: General Pauli-based encoding
- `EfficientSU2Map`: Hardware-efficient ansatz

### Circuits (`src/quantum/circuits.py`)

- `VariationalQuantumClassifier`: Main VQC implementation
- `QuantumNeuralNetwork`: Quantum feature transformation
- `QuantumKernelCircuit`: Kernel matrix computation

### Classifiers (`src/quantum/classifiers.py`)

- `HybridQuantumClassicalClassifier`: Full hybrid pipeline
- `QuantumEnsemble`: Ensemble of quantum classifiers
- `QuantumSVM`: Quantum-enhanced SVM

### Utilities (`src/quantum/utils.py`)

- `QuantumBackend`: Backend selection and execution
- `CircuitVisualizer`: Circuit diagram generation
- `QuantumMetrics`: Entropy, purity, advantage scoring

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Landing page |
| `/dashboard` | GET | Quantum ML dashboard |
| `/api/predict` | POST | Quantum ML disaster prediction |
| `/api/route` | POST | Evacuation routing |
| `/api/status` | GET | System status |
| `/api/quantum-info` | GET | Quantum backend info |

## Quantum Metrics

The system computes and displays:

- **Entropy**: Von Neumann entanglement entropy
- **Purity**: State purity (1 = pure, 0.5 = maximally mixed)
- **Advantage Score**: Estimated quantum advantage potential
- **Circuit Complexity**: Gate count and depth

## Project Structure

```
QISKIT/
├── src/
│   ├── disaster_system.py       # Main CLI system with quantum ML
│   ├── quantum/
│   │   ├── __init__.py
│   │   ├── feature_maps.py     # ZZFeatureMap, Pauli, EfficientSU2
│   │   ├── circuits.py         # VQC, QNN, Quantum Kernel
│   │   ├── classifiers.py      # Hybrid classifiers, Ensemble, SVM
│   │   └── utils.py           # Backend, Metrics, Visualization
│   ├── ml/
│   │   ├── __init__.py
│   │   └── preprocessing.py    # Feature engineering, preprocessing
│   └── data/
│       └── jena_climate_2009_2016.csv
├── webapp/
│   ├── app.py                 # Flask app with quantum endpoints
│   ├── templates/
│   │   ├── index.html         # Landing page
│   │   └── dashboard.html     # Quantum ML dashboard
│   ├── static/
│   │   ├── css/              # Quantum-themed styling
│   │   └── js/               # Dashboard JavaScript
│   └── qiskitml.db
├── README.md
├── requirements.txt
├── Procfile
└── runtime.txt
```

## Disaster Detection

| Disaster | Conditions | Risk Range |
|----------|-----------|-------------|
| Heat Wave | Temp > 35°C, Humidity > 60% | 70-95% |
| Cyclone | Wind > 15 m/s, P < 980 | 75-98% |
| Flood | Humidity > 90%, Temp > 5°C | 65-90% |
| Blizzard | Temp < -5°C, Wind > 8 m/s | 70-88% |
| Earthquake | Pressure < 970 mbar | 80% |

## Risk Levels

- **CRITICAL (>=85%)**: Immediate evacuation required
- **HIGH (>=70%)**: Evacuate immediately
- **MEDIUM (>=50%)**: Prepare for evacuation
- **LOW (<50%)**: No action needed

## Technologies

- **Quantum Computing**: IBM Qiskit, Qiskit Aer, Qiskit Machine Learning
- **Machine Learning**: NumPy, Pandas, Scikit-learn
- **Web Framework**: Flask, Flask-Limiter
- **Visualization**: Leaflet.js, GSAP
- **Styling**: Custom CSS with quantum theme

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add quantum ML improvements
4. Submit a pull request

## License

MIT License

## References

- [Qiskit Documentation](https://qiskit.org/documentation/)
- [Quantum Machine Learning](https://qiskit.org/documentation/machine-learning/)
- [Havlicek et al. - Supervised learning with quantum enhanced feature spaces](https://arxiv.org/abs/1804.11326)
