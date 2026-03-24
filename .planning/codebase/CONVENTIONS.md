# Coding Conventions

**Analysis Date:** 2026-03-24

## Naming Patterns

**Files:**
- snake_case: `feature_maps.py`, `disaster_system.py`, `preprocessing.py`
- Module files: all lowercase (`utils.py`, `circuits.py`)

**Functions:**
- snake_case: `build_circuit()`, `predict()`, `compute_derived_features()`
- Private functions: leading underscore `_quantum_infer()`, `_initialize_parameters()`

**Variables:**
- snake_case: `quantum_enabled`, `disaster_type`, `risk_percentage`
- Constants: SCREAMING_SNAKE_CASE in some files (e.g., `RISK_MESSAGES`)

**Types:**
- PascalCase: `QuantumFeatureMap`, `VariationalQuantumClassifier`, `DisasterFeatures`
- Enum values: `AnsatzType.EFFICIENT_SU2`, `DisasterType.HEAT_WAVE`
- Dataclasses: `CircuitConfig`, `PredictionResult`, `SensorData`

## Code Style

**Formatting:**
- 4 spaces indentation
- Line length: No explicit limit (varies 80-200+ characters)
- No automated formatter detected (no pre-commit hooks, no pyproject.toml formatting config)

**Linting:**
- No explicit linting configuration
- Type hints present in some functions but not comprehensive

**Docstrings:**
- Triple-quote docstrings for modules and major classes
- Google-style docstring format in some files:
  ```python
  """
  Args:
      param_name: Description
  Returns:
      Description
  """
  ```

## Import Organization

**Order:**
1. Standard library imports (`os`, `sys`, `json`, `datetime`)
2. Third-party imports (`numpy`, `pandas`, `flask`)
3. Local imports (quantum, ml modules)

**Example from `src/disaster_system.py`:**
```python
import os
import sys
import json
import math
import random
import smtplib
import ssl
import hashlib
import secrets
import re
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from enum import Enum

import numpy as np
import pandas as pd

from quantum import (...)
from ml import (...)
```

## Error Handling

**Patterns:**
- Try-except blocks for graceful degradation
- `QUANTUM_ML_AVAILABLE` flag for optional dependencies
- Silent failures with fallback (e.g., `except Exception: return None`)

**Example (src/disaster_system.py line 509):**
```python
except Exception as e:
    return self._classical_infer(features)
```

## Logging

**Framework:** Print-based (no logging module)

**Patterns:**
- CLI status messages with brackets: `print("[*] Initializing...")`
- Success/Error prefixes: `print("[+] Email alert sent")`, `print("[-] Discord not configured")`
- No structured logging

## Comments

**When to Comment:**
- Module-level docstrings explaining purpose
- Complex algorithms (quantum circuits, feature maps)
- Configuration defaults

**Style:**
- Inline comments for tricky code sections
- No consistent comment style enforcement

## Function Design

**Size:**
- Large monolithic methods (e.g., `QuantumMLPredictor.predict()` is 25+ lines)
- Mixed approach: some small utility functions, some large orchestrators

**Parameters:**
- Type hints in some places: `def predict(self, city: Optional[str] = None) -> PredictionResult`
- Missing type hints in other places

**Return Values:**
- Dataclasses for structured returns: `PredictionResult`, `VQCResult`
- Dictionaries for web API responses

## Module Design

**Exports:**
- `__init__.py` files define `__all__` lists
- Explicit imports in consuming modules

**Barrel Files:**
- `src/quantum/__init__.py` exports all quantum classes
- `src/ml/__init__.py` exports ML components

---

*Convention analysis: 2026-03-24*
