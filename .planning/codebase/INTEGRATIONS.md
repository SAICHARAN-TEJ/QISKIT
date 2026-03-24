# External Integrations

**Analysis Date:** 2026-03-24

## APIs & External Services

**Weather Data:**
- OpenWeatherMap API - Real-time weather data
  - SDK/Client: Direct HTTP via `urllib.request` in `WeatherAPI` class (`src/disaster_system.py` lines 197-229)
  - Auth: `OPENWEATHERMAP_API_KEY` environment variable
  - Endpoint: `https://api.openweathermap.org/data/2.5/weather`

**Routing:**
- OSRM (Open Source Routing Machine) - Evacuation route planning
  - SDK/Client: Direct HTTP via `urllib.request` in `OSRMRouter` class (`src/disaster_system.py` lines 232-286)
  - Auth: None required (public API)
  - Endpoint: `https://router.project-osrm.org/route/v1/driving/...`

**Quantum Computing:**
- Qiskit Aer - Local quantum simulator (when quantum enabled)
  - Backend: `qiskit-aer` library
  - Fallback: Classical simulation in `VariationalQuantumClassifier._simulate_circuit()`
- IBM Quantum (optional) - Cloud quantum access
  - SDK: `qiskit-ibm-runtime`
  - Auth: IBM Quantum token (via `量子_BACKEND` config)

## Data Storage

**Database:**
- SQLite
  - Location: `webapp/qiskitml.db`
  - Client: Python built-in `sqlite3`
  - Tables: users, predictions, alerts, audit_log
  - Connection: Via `DatabaseManager` class in `webapp/app.py`

**File Storage:**
- Local filesystem only
  - Climate data: `src/data/jena_climate_2009_2016.csv`
  - Templates: `webapp/templates/`
  - Static assets: `webapp/static/`

**Caching:**
- None detected (no Redis, Memcached, or in-memory caching)

## Authentication & Identity

**Auth Provider:**
- Custom session-based authentication
  - Implementation: Flask sessions with secure cookies (`webapp/app.py` lines 51-74)
  - Password hashing: PBKDF2-HMAC-SHA256 via `hashlib.pbkdf2_hmac()` (100000 iterations)
  - Session management: Flask-Limiter with 1-hour session lifetime
  - Token generation: `secrets.token_urlsafe()`

## Monitoring & Observability

**Error Tracking:**
- None detected (no Sentry, Rollbar, etc.)

**Logs:**
- Print-based logging for CLI
- No structured logging framework
- Flask request logs (default)

## CI/CD & Deployment

**Hosting:**
- Heroku (via `Procfile`)

**CI Pipeline:**
- Not detected (no GitHub Actions, CircleCI, etc.)

## Environment Configuration

**Required env vars:**
- `OPENWEATHERMAP_API_KEY` - Weather API access
- `DISCORD_WEBHOOK_URL` - Discord alerts
- `SENDER_EMAIL` - Email notifications
- `SENDER_PASSWORD` - Email password (app-specific password)
- `SMTP_SERVER` - Email relay (default: smtp.gmail.com)
- `SMTP_PORT` - Email port (default: 465)
- `RECIPIENT_EMAILS` - Alert recipients (comma-separated)
- `SECRET_KEY` - Flask session secret
- `QUANTUM_ENABLED` - Enable/disable quantum (default: true)
- `QUANTUM_BACKEND` - Quantum backend choice
- `QUANTUM_SHOTS` - Measurement shots (default: 1024)
- `DATA_SOURCE` - 'api' or 'jena' (default: jena)
- `DEFAULT_CITY` - Default prediction city

**Secrets location:**
- Environment variables (production)
- Not hardcoded anywhere in source

## Webhooks & Callbacks

**Incoming:**
- None (no webhook endpoints for external services)

**Outgoing:**
- Discord webhook - Alert notifications
  - URL validation via regex in `DiscordNotifier.WEBHOOK_PATTERN`
  - Format: Embed with disaster info, risk level, quantum metrics

---

*Integration audit: 2026-03-24*
