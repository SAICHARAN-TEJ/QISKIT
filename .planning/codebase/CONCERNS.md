# Codebase Concerns

**Analysis Date:** 2026-03-24

## Tech Debt

**No Test Suite:**
- Issue: Zero unit tests, integration tests, or E2E tests
- Files: All source files in `src/`, `webapp/`
- Impact: Cannot verify correctness of quantum classifiers, ML preprocessing, or API endpoints
- Fix approach: Add pytest configuration and write tests for core functionality

**No Type Hints:**
- Issue: Inconsistent type annotations throughout codebase
- Files: Multiple files have partial or missing type hints
- Impact: Reduced code maintainability, potential runtime errors
- Fix approach: Add mypy or pyright for type checking, add comprehensive type hints

**No Linting/Formatting:**
- Issue: No ESLint equivalent, Black, or Ruff configured
- Files: All Python files
- Impact: Inconsistent code style, potential bugs from formatting issues
- Fix approach: Add pre-commit hooks with Ruff for linting/formatting

**Code Duplication:**
- Issue: `QuantumMLPredictor` class duplicated in `src/disaster_system.py` and `webapp/app.py`
- Files: `src/disaster_system.py` (lines 381-627), `webapp/app.py` (lines 175-344)
- Impact: Maintenance burden, potential inconsistencies
- Fix approach: Extract to shared module in `src/`

## Known Bugs

**Rule-Based Classification May Be Incorrect:**
- Symptoms: Hardcoded thresholds in `_classical_infer()` may not accurately predict disasters
- Files: `src/disaster_system.py` (lines 512-560), `webapp/app.py` (lines 272-289)
- Trigger: Using system without trained quantum model
- Workaround: Always ensure quantum model is trained and enabled

## Security Considerations

**Environment Variables for Secrets:**
- Risk: No `.env` file template provided, secrets could be committed
- Files: No `.env.example` file
- Current mitigation: `.gitignore` should exclude `.env` files
- Recommendations: Add `.env.example` with placeholder values

**Input Validation:**
- Current: Comprehensive sanitization in `SecurityValidator` class
- Strengths: Coordinate validation, city name validation, string sanitization
- Gaps: None significant detected

**Password Storage:**
- Current: PBKDF2-HMAC-SHA256 with 100000 iterations (acceptable)
- Files: `webapp/app.py` lines 164-172
- Recommendations: Consider Argon2 as alternative

**Rate Limiting:**
- Current: Flask-Limiter configured, custom CLI rate limiter
- Files: `webapp/app.py`, `src/disaster_system.py` (lines 102-128)

## Performance Bottlenecks

**Jena Climate Dataset Loading:**
- Problem: Full dataset loaded into memory on each run
- Files: `src/disaster_system.py` line 411-424
- Cause: `pd.read_csv()` loads entire 420k+ row dataset
- Improvement path: Stream or sample dataset, cache last row

**Quantum Simulation:**
- Problem: Classical quantum simulation in `_simulate_circuit()` is O(2^n) complexity
- Files: `src/quantum/circuits.py` lines 248-309
- Cause: Statevector simulation scales exponentially with qubit count
- Improvement path: Limit to 4-6 qubits, use sampling for larger circuits

## Fragile Areas

**Quantum Import Fallback:**
- Why fragile: Silent failures if Qiskit unavailable
- Files: `src/quantum/feature_maps.py`, `src/quantum/circuits.py`, `src/quantum/classifiers.py`
- Safe modification: Always test with and without Qiskit installed
- Test coverage: None (no tests exist)

**Weather API Integration:**
- Why fragile: No retry logic, timeout handling minimal
- Files: `src/disaster_system.py` lines 197-229
- Safe modification: Add exponential backoff, circuit breaker pattern

## Scaling Limits

**SQLite Database:**
- Current capacity: Single user ~1000 requests/day
- Limit: SQLite locks on write, not suitable for concurrent access
- Scaling path: Migrate to PostgreSQL for production

**In-Memory Rate Limiter:**
- Current capacity: Per-process state
- Limit: Not shared across multiple workers
- Scaling path: Use Redis-backed rate limiter

## Dependencies at Risk

**Qiskit Version Compatibility:**
- Risk: Qiskit 1.0+ introduced breaking changes from 0.x
- Impact: `qiskit-machine-learning` and `qiskit-aer` must match
- Migration plan: Test all quantum components with target versions

## Missing Critical Features

**User Authentication:**
- Problem: Database schema exists but no login/register endpoints
- Blocks: Personalization, history tracking per user

**Model Training Pipeline:**
- Problem: No training script, only inference
- Blocks: Improving model accuracy, using new data

**Alert History:**
- Problem: Alerts sent but not stored for history
- Blocks: Audit trail, user notification preferences

## Test Coverage Gaps

**Untested Areas:**
- All quantum feature maps (ZZFeatureMap, PauliFeatureMap, EfficientSU2Map)
- All classifiers (HybridQuantumClassicalClassifier, QuantumEnsemble, QuantumSVM)
- All ML preprocessing (FeatureEngineering, DataPreprocessor)
- All Flask API endpoints
- Security validation functions

**Risk:** Quantum components may have bugs causing incorrect predictions
**Priority:** HIGH - Critical for production reliability

---

*Concerns audit: 2026-03-24*
