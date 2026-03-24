# Codebase Structure

**Analysis Date:** 2026-03-24

## Directory Layout

```
QISKIT/
├── .git/                        # Git repository
├── .gitignore                   # Git ignore rules
├── README.md                    # Project documentation
├── requirements.txt             # Python dependencies
├── runtime.txt                  # Python version
├── Procfile                     # Heroku deployment config
├── src/
│   ├── disaster_system.py       # Main CLI entry point
│   ├── quantum/
│   │   ├── __init__.py          # Quantum module exports
│   │   ├── feature_maps.py      # Quantum feature encoding
│   │   ├── circuits.py          # Variational quantum circuits
│   │   ├── classifiers.py       # Hybrid quantum-classical classifiers
│   │   └── utils.py             # Backend, metrics, visualization
│   ├── ml/
│   │   ├── __init__.py          # ML module exports
│   │   └── preprocessing.py    # Feature engineering, preprocessor
│   └── data/
│       └── jena_climate_2009_2016.csv  # Climate dataset
└── webapp/
    ├── app.py                   # Flask application
    ├── qiskitml.db              # SQLite database
    ├── templates/
    │   ├── index.html           # Landing page
    │   └── dashboard.html       # Quantum ML dashboard
    └── static/
        ├── css/
        │   ├── design.css       # Core styles
        │   ├── dashboard.css    # Dashboard styles
        │   └── landing.css      # Landing page styles
        └── js/
            ├── dashboard.js     # Dashboard JavaScript
            └── landing.js       # Landing page JavaScript
```

## Directory Purposes

**`src/`:**
- Purpose: Core application source code
- Contains: CLI system, quantum ML modules, classical ML preprocessing

**`src/quantum/`:**
- Purpose: Quantum machine learning components
- Contains: Feature maps, circuits, classifiers, utilities
- Key files: `feature_maps.py` (403 lines), `circuits.py` (664 lines), `classifiers.py` (556 lines)

**`src/ml/`:**
- Purpose: Classical machine learning preprocessing
- Contains: Feature engineering, data preprocessing, model evaluation
- Key files: `preprocessing.py` (419 lines)

**`webapp/`:**
- Purpose: Flask web application
- Contains: Web server, templates, static assets, database

**`webapp/templates/`:**
- Purpose: HTML templates for web UI
- Contains: Quantum-themed landing page and dashboard

**`webapp/static/`:**
- Purpose: CSS and JavaScript assets
- Contains: Custom quantum-themed styling and interactive JS

## Key File Locations

**Entry Points:**
- `src/disaster_system.py`: CLI application (lines 741-801 main function)
- `webapp/app.py`: Flask web server (lines 476-479 run block)

**Configuration:**
- `requirements.txt`: Python package dependencies
- `runtime.txt`: Python version specification (3.11+)
- `Procfile`: Heroku deployment command

**Core Logic:**
- `src/quantum/feature_maps.py`: ZZFeatureMap, PauliFeatureMap, EfficientSU2Map implementations
- `src/quantum/circuits.py`: VariationalQuantumClassifier, QuantumNeuralNetwork, QuantumKernelCircuit
- `src/quantum/classifiers.py`: HybridQuantumClassicalClassifier, QuantumEnsemble, QuantumSVM
- `src/ml/preprocessing.py`: DisasterFeatures, FeatureEngineering, DataPreprocessor

**Testing:**
- No test files detected (no `*test*.py`, `*_test.py`, or `tests/` directory)

## Naming Conventions

**Files:**
- Snake_case: `feature_maps.py`, `disaster_system.py`, `preprocessing.py`
- All lowercase module names: `utils.py`, `circuits.py`

**Directories:**
- Snake_case: `quantum/`, `ml/`, `static/`, `css/`, `js/`

**Classes:**
- PascalCase: `QuantumFeatureMap`, `VariationalQuantumClassifier`, `HybridQuantumClassicalClassifier`
- Enum values: `AnsatzType.EFFICIENT_SU2`, `MeasurementType.PARITY`

**Functions:**
- snake_case: `build_circuit()`, `predict()`, `compute_derived_features()`
- Private methods: `_initialize_quantum_components()`, `_quantum_infer()`

**Dataclasses:**
- PascalCase: `CircuitConfig`, `PredictionResult`, `SensorData`, `DisasterFeatures`

## Where to Add New Code

**New Feature (CLI):**
- Primary code: `src/disaster_system.py` - Add new method to `QuantumMLPredictor` class
- Configuration: Update `Config.load()` method

**New Quantum Component:**
- Implementation: `src/quantum/feature_maps.py` or `src/quantum/circuits.py`
- Export: Update `src/quantum/__init__.py` with new class
- Example: Add new feature map class inheriting from `QuantumFeatureMap`

**New ML Component:**
- Implementation: `src/ml/preprocessing.py`
- Export: Update `src/ml/__init__.py`

**New Web API Endpoint:**
- Implementation: `webapp/app.py` - Add new route handler
- Example: `@app.route('/api/new-endpoint', methods=['GET'])`

**New Web Page:**
- Template: `webapp/templates/new_page.html`
- Static: `webapp/static/css/new_page.css`, `webapp/static/js/new_page.js`
- Route: Add route in `webapp/app.py`

**New Notification Channel:**
- Implementation: Add new notifier class in `src/disaster_system.py`
- Usage: Update `NotificationManager` to include new channel

## Special Directories

**`.git/`:**
- Purpose: Git version control metadata
- Generated: Yes
- Committed: No (git internal)

**`src/data/`:**
- Purpose: Climate dataset for predictions
- Generated: No (external Jena dataset)
- Committed: Yes

**`webapp/qiskitml.db`:**
- Purpose: SQLite database for user accounts, predictions, alerts
- Generated: Yes (created on first run)
- Committed: Yes (initial empty state)

---

*Structure analysis: 2026-03-24*
