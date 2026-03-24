# Architecture

**Analysis Date:** 2026-03-24

## Pattern Overview

**Overall:** Hybrid Quantum-Classical Machine Learning Pipeline

**Key Characteristics:**
- Quantum feature encoding using ZZFeatureMap for environmental data
- Variational Quantum Circuits (VQC) for disaster classification
- Classical fallback for when quantum components unavailable
- Hybrid pipeline: Quantum ML → Classical Post-processing → Disaster Prediction

## Layers

**Quantum Layer:**
- Purpose: Encode features into quantum states and perform quantum classification
- Location: `src/quantum/`
- Contains: Feature maps, variational circuits, classifiers, quantum utilities
- Depends on: Qiskit, NumPy
- Used by: `disaster_system.py`, `webapp/app.py`

**Classical ML Layer:**
- Purpose: Feature engineering and preprocessing for quantum models
- Location: `src/ml/preprocessing.py`
- Contains: DisasterFeatures dataclass, FeatureEngineering, DataPreprocessor
- Depends on: NumPy, Pandas
- Used by: Quantum layer, Main CLI

**Application Layer:**
- Purpose: CLI and web interface for disaster prediction
- Location: `src/disaster_system.py`, `webapp/app.py`
- Contains: QuantumMLPredictor, routing, notifications, Flask endpoints
- Depends on: Flask, all above layers

**Presentation Layer:**
- Purpose: Quantum-themed web UI
- Location: `webapp/templates/`, `webapp/static/`
- Contains: HTML templates, CSS/JS for dashboard

## Data Flow

**Prediction Flow:**

1. **Input**: Sensor data (temperature, pressure, humidity, wind) from Jena dataset or OpenWeatherMap API
2. **Preprocessing**: `DataPreprocessor` normalizes features → `FeatureEngineering` computes derived features
3. **Quantum Encoding**: `ZZFeatureMap` encodes 7 features into 4-qubit quantum state
4. **Variational Circuit**: `VariationalQuantumClassifier` applies parameterized ansatz (EfficientSU2)
5. **Measurement**: Parity measurement on qubits produces classification
6. **Post-processing**: `QuantumMetrics` computes entropy, purity, advantage score
7. **Risk Assessment**: `RiskLevel` enum maps confidence to disaster type

**State Management:**
- Session-based for Flask webapp (SQLite for persistence)
- In-memory `RateLimiter` for API throttling
- Quantum backend selection via `QuantumBackend` singleton

## Key Abstractions

**QuantumFeatureMap (Abstract):**
- Purpose: Encode classical data into quantum states
- Examples: `src/quantum/feature_maps.py` - ZZFeatureMap, PauliFeatureMap, EfficientSU2Map
- Pattern: Base class with `encode()`, `build_circuit()`, `get_statevector()` methods

**VariationalQuantumClassifier:**
- Purpose: Hybrid quantum-classical classification
- Examples: `src/quantum/circuits.py` - CircuitConfig, AnsatzType enum
- Pattern: Config-driven circuit builder with `predict()` returning VQCResult

**QuantumMLPredictor:**
- Purpose: Main prediction orchestrator
- Examples: `src/disaster_system.py` lines 381-596, `webapp/app.py` lines 175-344
- Pattern: Initializes quantum/classical components, exposes `predict()` method

**PredictionResult (Dataclass):**
- Purpose: Structured output from prediction
- Contains: disaster_type, risk_percentage, risk_level, quantum_metrics, circuit_info

## Entry Points

**CLI Entry:**
- Location: `src/disaster_system.py` (main function lines 741-801)
- Triggers: `python src/disaster_system.py`
- Responsibilities: Load config, initialize predictor, display prediction, send alerts

**Web Entry:**
- Location: `webapp/app.py` (lines 476-479)
- Triggers: `python webapp/app.py` or `flask run`
- Responsibilities: Initialize Flask, SQLite DB, route handlers

**API Endpoint:**
- Location: `/api/predict` POST in `webapp/app.py` (lines 404-417)
- Triggers: HTTP POST with JSON body containing city name
- Responsibilities: Validate input, call predictor, return JSON prediction

## Error Handling

**Strategy:** Graceful degradation with quantum fallback to classical

**Patterns:**
- `QUANTUM_ML_AVAILABLE` flag: If quantum imports fail, uses rule-based classification
- Try-except in `_quantum_infer`: Falls back to `_classical_infer` on quantum errors
- `SecurityValidator`: Input sanitization prevents injection attacks
- Rate limiting: `RateLimiter` class prevents API abuse

## Cross-Cutting Concerns

**Logging:** Print-based for CLI, no structured logging framework

**Validation:**
- `SecurityValidator.sanitize_string()` for all user inputs
- `SecurityValidator.validate_coordinates()` for lat/lon
- `SecurityValidator.validate_city_name()` for city strings
- Regex patterns for email, webhook URLs

**Authentication:**
- Flask session-based with secure cookie settings
- `DatabaseManager.hash_password()` using PBKDF2-HMAC-SHA256
- Token generation via `secrets.token_urlsafe()`

**Rate Limiting:**
- Flask-Limiter for web endpoints
- Custom `RateLimiter` class for CLI (10 req/60s default)

---

*Architecture analysis: 2026-03-24*
