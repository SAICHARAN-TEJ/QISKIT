"""
QuantumML - Quantum Machine Learning Module
==========================================
Quantum computing integration for disaster prediction.

Components:
- Feature Maps: Quantum encoding of classical data
- Circuits: Variational quantum circuits for classification
- Classifiers: Quantum-enhanced ML classifiers
- Utils: Quantum computation utilities
"""

from .feature_maps import QuantumFeatureMap, ZZFeatureMap, PauliFeatureMap, EfficientSU2Map
from .circuits import VariationalQuantumClassifier, QuantumNeuralNetwork, QuantumKernelCircuit
from .classifiers import HybridQuantumClassicalClassifier, QuantumEnsemble, QuantumSVM
from .utils import QuantumBackend, CircuitVisualizer, QuantumMetrics

__all__ = [
    'QuantumFeatureMap',
    'ZZFeatureMap',
    'PauliFeatureMap',
    'EfficientSU2Map',
    'VariationalQuantumClassifier',
    'QuantumNeuralNetwork',
    'QuantumKernelCircuit',
    'HybridQuantumClassicalClassifier',
    'QuantumEnsemble',
    'QuantumSVM',
    'QuantumBackend',
    'CircuitVisualizer',
    'QuantumMetrics',
]
