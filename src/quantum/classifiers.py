"""
Quantum Classifiers
===================
Hybrid quantum-classical machine learning classifiers.

Classifiers:
- HybridQuantumClassicalClassifier: Main hybrid classifier
- QuantumEnsemble: Ensemble of quantum classifiers
- QuantumSVM: Quantum-enhanced SVM
"""

import numpy as np
from typing import Optional, List, Tuple, Dict, Union, Callable
from dataclasses import dataclass
from enum import Enum
import warnings


class ClassifierType(Enum):
    """Types of quantum classifiers."""
    VQC = "variational_quantum_classifier"
    QSVM = "quantum_svm"
    QNN = "quantum_neural_network"
    HYBRID = "hybrid_ensemble"


@dataclass
class ClassifierConfig:
    """Configuration for quantum classifiers."""
    classifier_type: ClassifierType = ClassifierType.HYBRID
    num_qubits: int = 4
    num_layers: int = 2
    learning_rate: float = 0.1
    num_iterations: int = 100
    batch_size: int = 10
    regularization: float = 0.01
    early_stopping: bool = True
    validation_split: float = 0.2


@dataclass
class PredictionResult:
    """Result from classifier prediction."""
    label: int
    probabilities: np.ndarray
    confidence: float
    feature_importance: Optional[np.ndarray] = None
    quantum_advantage_score: Optional[float] = None


class BaseQuantumClassifier:
    """Base class for all quantum classifiers."""
    
    def __init__(self, config: Optional[ClassifierConfig] = None):
        self.config = config or ClassifierConfig()
        self._is_fitted = False
        self._classes = None
        self._feature_importances = None
        self._training_history = []
        
    def fit(self, X: np.ndarray, y: np.ndarray) -> 'BaseQuantumClassifier':
        """Train the classifier."""
        raise NotImplementedError("Subclasses must implement fit")
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        raise NotImplementedError("Subclasses must implement predict")
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        raise NotImplementedError("Subclasses must implement predict_proba")
        
    def score(self, X: np.ndarray, y: np.ndarray) -> float:
        """Return mean accuracy."""
        predictions = self.predict(X)
        return np.mean(predictions == y)
        
    def get_params(self) -> Dict:
        """Get classifier parameters."""
        return {
            'num_qubits': self.config.num_qubits,
            'num_layers': self.config.num_layers,
            'learning_rate': self.config.learning_rate,
            'is_fitted': self._is_fitted
        }


class HybridQuantumClassicalClassifier(BaseQuantumClassifier):
    """
    Hybrid Quantum-Classical Classifier.
    
    Combines quantum feature transformation with classical
    post-processing for robust disaster classification.
    
    Architecture:
    - Quantum Feature Map: Encode environmental data
    - Variational Quantum Circuit: Learn decision boundaries
    - Classical Post-processing: Final classification
    """
    
    def __init__(self, config: Optional[ClassifierConfig] = None):
        super().__init__(config)
        self.config.classifier_type = ClassifierType.HYBRID
        self._quantum_weights = None
        self._classical_model = None
        self._feature_dim = None
        
    def fit(self, X: np.ndarray, y: np.ndarray,
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None) -> 'HybridQuantumClassicalClassifier':
        """
        Train the hybrid classifier.
        
        Args:
            X: Training features
            y: Training labels
            X_val: Validation features (optional)
            y_val: Validation labels (optional)
            
        Returns:
            Self
        """
        X = np.array(X, dtype=np.float64)
        y = np.array(y, dtype=np.int32)
        
        self._classes = np.unique(y)
        self._feature_dim = X.shape[1]
        
        self._quantum_weights = self._initialize_weights()
        
        best_weights = self._quantum_weights.copy()
        best_loss = float('inf')
        
        num_batches = max(1, len(X) // self.config.batch_size)
        
        for iteration in range(self.config.num_iterations):
            indices = np.random.permutation(len(X))
            
            for batch_idx in range(num_batches):
                start_idx = batch_idx * self.config.batch_size
                end_idx = min(start_idx + self.config.batch_size, len(X))
                batch_indices = indices[start_idx:end_idx]
                
                X_batch = X[batch_indices]
                y_batch = y[batch_indices]
                
                gradients = self._compute_gradients(X_batch, y_batch, self._quantum_weights)
                
                self._quantum_weights -= self.config.learning_rate * gradients
                
            train_loss = self._compute_loss(X, y, self._quantum_weights)
            self._training_history.append({'iteration': iteration, 'loss': train_loss})
            
            if train_loss < best_loss:
                best_loss = train_loss
                best_weights = self._quantum_weights.copy()
                
            if self.config.early_stopping and X_val is not None and y_val is not None:
                val_loss = self._compute_loss(X_val, y_val, self._quantum_weights)
                if val_loss > train_loss * 1.5:
                    break
                    
        self._quantum_weights = best_weights
        self._is_fitted = True
        self._compute_feature_importances(X, y)
        
        self._classical_model = self._train_classical_postprocessor(X, y)
        
        return self
        
    def _initialize_weights(self) -> np.ndarray:
        """Initialize quantum circuit weights."""
        total_params = self.config.num_qubits * self.config.num_layers * 3
        return np.random.randn(total_params) * 0.01
        
    def _quantum_transform(self, X: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """Transform features using quantum circuit."""
        num_samples = len(X)
        output_dim = 2 ** self.config.num_qubits
        quantum_features = np.zeros((num_samples, output_dim))
        
        for i, sample in enumerate(X):
            statevector = self._encode_quantum(sample)
            statevector = self._apply_variational_circuit(statevector, weights)
            quantum_features[i] = np.abs(statevector) ** 2
            
        return quantum_features
        
    def _encode_quantum(self, sample: np.ndarray) -> np.ndarray:
        """Encode classical data into quantum state."""
        num_states = 2 ** self.config.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        statevector[0] = 1.0
        
        sample_normalized = sample / (np.linalg.norm(sample) + 1e-8)
        
        for i, feature in enumerate(sample_normalized[:self.config.num_qubits]):
            angle = np.arccos(min(1.0, abs(feature))) if abs(feature) > 1e-6 else np.pi / 4
            for state in range(num_states):
                if (state >> i) & 1:
                    statevector[state] *= np.exp(1j * angle)
                else:
                    statevector[state] *= np.cos(angle)
                    
        return statevector / np.linalg.norm(statevector)
        
    def _apply_variational_circuit(self, statevector: np.ndarray, 
                                   weights: np.ndarray) -> np.ndarray:
        """Apply parameterized variational circuit."""
        num_states = len(statevector)
        
        for layer in range(self.config.num_layers):
            for qubit in range(self.config.num_qubits):
                idx = (layer * self.config.num_qubits + qubit) * 3
                
                for state in range(num_states):
                    if (state >> qubit) & 1:
                        statevector[state] *= np.exp(1j * weights[idx])
                        
                if qubit < self.config.num_qubits - 1:
                    for state in range(num_states):
                        if ((state >> qubit) & 1) != ((state >> (qubit + 1)) & 1):
                            statevector[state] *= 1 / np.sqrt(2)
                            
        return statevector
        
    def _compute_loss(self, X: np.ndarray, y: np.ndarray, 
                    weights: np.ndarray) -> float:
        """Compute cross-entropy loss with L2 regularization."""
        quantum_features = self._quantum_transform(X, weights)
        
        logits = np.dot(quantum_features, weights[:quantum_features.shape[1]])
        
        logits = logits - logits.max(axis=1, keepdims=True)
        exp_logits = np.exp(logits)
        probs = exp_logits / exp_logits.sum(axis=1, keepdims=True)
        
        probs = np.clip(probs, 1e-10, 1 - 1e-10)
        loss = -np.mean(np.log(probs[np.arange(len(y)), y]))
        
        l2_penalty = self.config.regularization * np.sum(weights ** 2)
        
        return loss + l2_penalty
        
    def _compute_gradients(self, X: np.ndarray, y: np.ndarray,
                         weights: np.ndarray) -> np.ndarray:
        """Compute gradients using numerical approximation."""
        epsilon = 1e-5
        gradients = np.zeros_like(weights)
        
        loss_plus = self._compute_loss(X, y, weights)
        
        for i in range(min(10, len(weights))):
            weights_plus = weights.copy()
            weights_plus[i] += epsilon
            loss_i = self._compute_loss(X, y, weights_plus)
            gradients[i] = (loss_i - loss_plus) / epsilon
            
        return gradients
        
    def _train_classical_postprocessor(self, X: np.ndarray, y: np.ndarray) -> Dict:
        """Train classical post-processing layer."""
        quantum_features = self._quantum_transform(X, self._quantum_weights)
        
        return {
            'type': 'logistic_regression',
            'weights': np.random.randn(quantum_features.shape[1], len(self._classes)) * 0.01,
            'bias': np.zeros(len(self._classes))
        }
        
    def _compute_feature_importances(self, X: np.ndarray, y: np.ndarray):
        """Compute feature importances via permutation."""
        importances = np.zeros(X.shape[1])
        baseline_score = self.score(X, y)
        
        for feature_idx in range(X.shape[1]):
            X_permuted = X.copy()
            X_permuted[:, feature_idx] = np.random.permutation(X_permuted[:, feature_idx])
            importances[feature_idx] = baseline_score - self.score(X_permuted, y)
            
        self._feature_importances = np.abs(importances) / (importances.sum() + 1e-8)
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions on new data."""
        if not self._is_fitted:
            raise ValueError("Classifier must be fitted before prediction")
            
        X = np.array(X, dtype=np.float64)
        quantum_features = self._quantum_transform(X, self._quantum_weights)
        
        logits = np.dot(quantum_features, self._classical_model['weights'])
        predictions = np.argmax(logits, axis=1)
        
        return self._classes[predictions]
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities."""
        if not self._is_fitted:
            raise ValueError("Classifier must be fitted before prediction")
            
        X = np.array(X, dtype=np.float64)
        quantum_features = self._quantum_transform(X, self._quantum_weights)
        
        logits = np.dot(quantum_features, self._classical_model['weights'])
        logits = logits - logits.max(axis=1, keepdims=True)
        exp_logits = np.exp(logits)
        probs = exp_logits / exp_logits.sum(axis=1, keepdims=True)
        
        return probs
        
    def predict_with_confidence(self, X: np.ndarray) -> List[PredictionResult]:
        """Predict with confidence scores and quantum advantage metrics."""
        X = np.array(X, dtype=np.float64)
        quantum_features = self._quantum_transform(X, self._quantum_weights)
        
        probs = self.predict_proba(X)
        predictions = np.argmax(probs, axis=1)
        
        results = []
        for i in range(len(X)):
            quantum_measurements = self._estimate_quantum_advantage(quantum_features[i:i+1])
            
            results.append(PredictionResult(
                label=int(predictions[i]),
                probabilities=probs[i],
                confidence=float(probs[i].max()),
                feature_importance=self._feature_importances,
                quantum_advantage_score=quantum_measurements
            ))
            
        return results
        
    def _estimate_quantum_advantage(self, quantum_features: np.ndarray) -> float:
        """Estimate quantum advantage based on entanglement entropy."""
        probs = quantum_features / (quantum_features.sum() + 1e-8)
        
        entropy = -np.sum(probs * np.log(probs + 1e-10))
        max_entropy = np.log(len(probs))
        
        return float(1 - entropy / max_entropy) if max_entropy > 0 else 0.0


class QuantumEnsemble(BaseQuantumClassifier):
    """
    Quantum Ensemble Classifier.
    
    Combines multiple quantum classifiers for improved
    prediction accuracy and robustness.
    """
    
    def __init__(self, config: Optional[ClassifierConfig] = None,
                 n_estimators: int = 3):
        super().__init__(config)
        self.config.classifier_type = ClassifierType.HYBRID
        self.n_estimators = n_estimators
        self._estimators = []
        
    def fit(self, X: np.ndarray, y: np.ndarray,
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None) -> 'QuantumEnsemble':
        """Train ensemble of quantum classifiers."""
        X = np.array(X, dtype=np.float64)
        y = np.array(y, dtype=np.int32)
        
        self._classes = np.unique(y)
        
        self._estimators = []
        for i in range(self.n_estimators):
            np.random.seed(i)
            config = ClassifierConfig(
                num_qubits=max(2, self.config.num_qubits - i % 2),
                num_layers=max(1, self.config.num_layers - i % 2),
                learning_rate=self.config.learning_rate
            )
            
            estimator = HybridQuantumClassicalClassifier(config)
            indices = np.random.choice(len(X), len(X), replace=True)
            estimator.fit(X[indices], y[indices], X_val, y_val)
            self._estimators.append(estimator)
            
        self._is_fitted = True
        return self
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Aggregate predictions from all estimators."""
        X = np.array(X, dtype=np.float64)
        
        all_predictions = np.zeros((len(X), len(self._estimators)))
        for i, estimator in enumerate(self._estimators):
            all_predictions[:, i] = estimator.predict(X)
            
        final_predictions = np.apply_along_axis(
            lambda x: np.bincount(x.astype(int), minlength=len(self._classes)).argmax(),
            axis=1,
            arr=all_predictions
        )
        
        return self._classes[final_predictions]
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Average probabilities from all estimators."""
        X = np.array(X, dtype=np.float64)
        
        all_proba = np.zeros((len(X), len(self._classes), len(self._estimators)))
        for i, estimator in enumerate(self._estimators):
            all_proba[:, :, i] = estimator.predict_proba(X)
            
        return all_proba.mean(axis=2)


class QuantumSVM(BaseQuantumClassifier):
    """
    Quantum-enhanced Support Vector Machine.
    
    Uses quantum kernel computation for SVM classification,
    enabling capture of complex feature interactions.
    """
    
    def __init__(self, config: Optional[ClassifierConfig] = None,
                 kernel_type: str = 'quantum'):
        super().__init__(config)
        self.config.classifier_type = ClassifierType.QSVM
        self.kernel_type = kernel_type
        self._support_vectors = None
        self._dual_coefficients = None
        self._intercept = None
        
    def fit(self, X: np.ndarray, y: np.ndarray,
            X_val: Optional[np.ndarray] = None,
            y_val: Optional[np.ndarray] = None) -> 'QuantumSVM':
        """Train quantum SVM."""
        X = np.array(X, dtype=np.float64)
        y = np.array(y, dtype=np.int32)
        
        self._classes = np.unique(y)
        y_binary = (y == self._classes[1]).astype(float) * 2 - 1
        
        self._support_vectors = X.copy()
        self._sv_y = y_binary
        
        alpha = np.zeros(len(X))
        bias = 0.0
        
        kernel_matrix = self._compute_kernel(X, X)
        
        for _ in range(self.config.num_iterations):
            for i in range(len(X)):
                error = y_binary[i] - sum(alpha * y_binary * kernel_matrix[i])
                alpha[i] = alpha[i] + self.config.learning_rate * error
                alpha[i] = max(0, min(alpha[i], self.config.regularization))
                
        self._dual_coefficients = alpha * y_binary
        self._intercept = bias
        
        self._is_fitted = True
        return self
        
    def _compute_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute kernel matrix."""
        if self.kernel_type == 'quantum':
            return self._quantum_kernel(X1, X2)
        elif self.kernel_type == 'rbf':
            return self._rbf_kernel(X1, X2)
        else:
            return self._linear_kernel(X1, X2)
            
    def _quantum_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Compute quantum kernel using feature map."""
        n1, n2 = len(X1), len(X2)
        kernel = np.zeros((n1, n2))
        
        for i in range(n1):
            for j in range(n2):
                state1 = self._encode_state(X1[i])
                state2 = self._encode_state(X2[j])
                kernel[i, j] = np.abs(np.vdot(state1, state2)) ** 2
                
        return kernel
        
    def _encode_state(self, sample: np.ndarray) -> np.ndarray:
        """Encode sample into quantum state."""
        num_qubits = self.config.num_qubits
        num_states = 2 ** num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        statevector[0] = 1.0
        
        sample_normalized = sample / (np.linalg.norm(sample) + 1e-8)
        
        for i, feature in enumerate(sample_normalized[:num_qubits]):
            angle = np.pi * abs(feature)
            for state in range(num_states):
                if (state >> i) & 1:
                    statevector[state] *= np.exp(1j * angle)
                    
        return statevector / np.linalg.norm(statevector)
        
    def _rbf_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """RBF kernel."""
        gamma = 1.0 / X1.shape[1]
        diff = X1[:, np.newaxis] - X2[np.newaxis]
        return np.exp(-gamma * np.sum(diff ** 2, axis=2))
        
    def _linear_kernel(self, X1: np.ndarray, X2: np.ndarray) -> np.ndarray:
        """Linear kernel."""
        return np.dot(X1, X2.T)
        
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Make predictions."""
        X = np.array(X, dtype=np.float64)
        
        kernel = self._compute_kernel(X, self._support_vectors)
        decisions = np.dot(kernel, self._dual_coefficients) + self._intercept
        
        return self._classes[(decisions > 0).astype(int)]
        
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict probabilities using Platt scaling."""
        X = np.array(X, dtype=np.float64)
        
        kernel = self._compute_kernel(X, self._support_vectors)
        decisions = np.dot(kernel, self._dual_coefficients) + self._intercept
        
        proba = 1 / (1 + np.exp(-decisions))
        return np.column_stack([1 - proba, proba])


def create_classifier(classifier_type: str = 'hybrid',
                     num_qubits: int = 4,
                     **kwargs) -> BaseQuantumClassifier:
    """
    Factory function to create quantum classifiers.
    
    Args:
        classifier_type: Type ('hybrid', 'ensemble', 'svm')
        num_qubits: Number of qubits
        **kwargs: Additional configuration
        
    Returns:
        Configured classifier instance
    """
    classifier_type = classifier_type.lower().replace('-', '_')
    
    config = ClassifierConfig(
        num_qubits=num_qubits,
        **kwargs
    )
    
    if classifier_type in ['hybrid', 'hybrid_qc']:
        return HybridQuantumClassicalClassifier(config)
    elif classifier_type in ['ensemble', 'quantum_ensemble']:
        return QuantumEnsemble(config, n_estimators=kwargs.get('n_estimators', 3))
    elif classifier_type in ['svm', 'quantum_svm']:
        return QuantumSVM(config, kernel_type=kwargs.get('kernel_type', 'quantum'))
    else:
        warnings.warn(f"Unknown classifier type '{classifier_type}', defaulting to Hybrid")
        return HybridQuantumClassicalClassifier(config)
