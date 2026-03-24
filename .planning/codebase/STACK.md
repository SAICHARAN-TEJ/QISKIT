# Technology Stack

**Analysis Date:** 2026-03-24

## Languages

**Primary:**
- Python 3.11+ - Main implementation language for quantum ML, CLI, and webapp

**Secondary:**
- HTML5 - Web UI templates
- CSS3 - Styling for quantum-themed dark UI
- JavaScript - Frontend interactivity

## Runtime

**Environment:**
- Python 3.11+ (specified in `runtime.txt`)

**Package Manager:**
- pip (via `requirements.txt`)
- Lockfile: Not present (requirements.txt without hash verification)

## Frameworks

**Core Quantum ML:**
- Qiskit 1.0.0+ - Quantum computing framework
- qiskit-algorithms 0.3.0 - Quantum algorithms
- qiskit-machine-learning 0.8.0 - Quantum ML implementations
- qiskit-nature 0.7.0 - Quantum nature/physics applications
- qiskit-aer 0.14.0 - Quantum simulator backend
- qiskit-ibm-runtime 0.25.0 - IBM Quantum access

**Classical ML:**
- scikit-learn 1.4.0+ - Classical ML preprocessing
- pandas 2.0.0+ - Data manipulation
- numpy 1.24.0+ - Numerical computing
- matplotlib 3.8.0+ - Visualization
- seaborn 0.13.0+ - Statistical visualization

**Web Framework:**
- Flask 3.0.0+ - Web application framework
- flask-limiter 3.5.0+ - Rate limiting
- gunicorn 21.0.0+ - WSGI server

**Data:**
- SQLite (built-in) - User data, predictions, alerts storage

## Key Dependencies

**Quantum Computing:**
- `qiskit>=1.0.0` - Core quantum framework
- `qiskit-machine-learning>=0.8.0` - VQC, quantum kernels
- `qiskit-aer>=0.14.0` - Local quantum simulator

**Data Processing:**
- `pandas>=2.0.0` - Climate data handling
- `numpy>=1.24.0` - Array operations for quantum statevectors

**Web:**
- `flask>=3.0.0` - REST API and web UI
- `flask-limiter>=3.5.0` - API rate limiting

## Configuration

**Environment:**
- Environment variables loaded via `os.environ.get()`
- Key configs: `OPENWEATHERMAP_API_KEY`, `DISCORD_WEBHOOK_URL`, `SMTP_SERVER`, `SMTP_PORT`, `SENDER_EMAIL`, `SENDER_PASSWORD`, `RECIPIENT_EMAILS`, `SECRET_KEY`, `QUANTUM_ENABLED`, `QUANTUM_BACKEND`, `QUANTUM_SHOTS`, `DATA_SOURCE`, `DEFAULT_CITY`
- `Config.load()` method in `src/disaster_system.py` (lines 175-194)

**Build:**
- `requirements.txt` - pip dependencies
- `runtime.txt` - Python version (e.g., python-3.11.x)
- `Procfile` - Heroku deployment

## Platform Requirements

**Development:**
- Python 3.11+
- pip for package installation
- Local SQLite for development database

**Production:**
- Heroku or similar PaaS
- Environment variables for secrets
- Gunicorn WSGI server

---

*Stack analysis: 2026-03-24*
