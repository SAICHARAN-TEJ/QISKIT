"""
Quantum Circuits
================
Variational quantum circuits for classification and learning.

Components:
- VariationalQuantumClassifier: VQC for disaster classification
- QuantumNeuralNetwork: QNN architecture for feature extraction
- QuantumKernelCircuit: Quantum kernel computation
"""

import numpy as np
from typing import Optional, List, Tuple, Union, Dict, Callable
from dataclasses import dataclass
from enum import Enum
import warnings


class AnsatzType(Enum):
    """Types of variational ansatz circuits."""
    REAL_AMPLITUDE = "real_amplitude"
    EFFICIENT_SU2 = "efficient_su2"
    TWO_LOCAL = "two_local"
    NAR = "nlocal_real_amplitudes"
    CUSTOM = "custom"


class MeasurementType(Enum):
    """Types of measurements for quantum circuits."""
    PARITY = "parity"
    EXPECTATION = "expectation"
    SAMPLING = "sampling"
    STATEVECTOR = "statevector"


@dataclass
class CircuitConfig:
    """Configuration for quantum circuit construction."""
    num_qubits: int = 4
    num_layers: int = 2
    ansatz_type: AnsatzType = AnsatzType.EFFICIENT_SU2
    measurement_type: MeasurementType = MeasurementType.PARITY
    include_interaction: bool = True
    barrier: bool = False
    shots: int = 1024
    

@dataclass 
class VQCResult:
    """Result from VQC execution."""
    probabilities: np.ndarray
    prediction: int
    confidence: float
    statevector: Optional[np.ndarray] = None
    measurement_counts: Optional[Dict] = None
    circuit_depth: int = 0
    num_gates: int = 0


class VariationalQuantumClassifier:
    """
    Variational Quantum Classifier (VQC).
    
    Implements a parameterized quantum circuit for classification
    combined with classical post-processing. Uses feature maps
    for data encoding and ansatz for learning.
    
    Architecture:
    1. Data Encoding Layer (Feature Map)
    2. Variational Ansatz (Parameterized Layers)
    3. Measurement (Classification Output)
    
    For disaster prediction:
    - Input: Environmental features (temp, pressure, humidity, wind)
    - Output: Disaster type classification with confidence
    """
    
    def __init__(self, config: Optional[CircuitConfig] = None,
                 feature_map: Optional[object] = None,
                 ansatz_params: Optional[np.ndarray] = None,
                 num_qubits: int = 4,
                 num_classes: int = 2,
                 num_layers: int = 2):
        if config is None:
            config = CircuitConfig(
                num_qubits=num_qubits,
                num_layers=num_layers
            )
        self.config = config
        self.feature_map = feature_map
        self._num_parameters = self._calculate_num_parameters()
        
        if ansatz_params is None:
            self.ansatz_params = self._initialize_parameters()
        else:
            self.ansatz_params = ansatz_params
            
        self._circuit = None
        self._is_fitted = False
        self._classes = None
        
    def _calculate_num_parameters(self) -> int:
        """Calculate number of trainable parameters."""
        if self.config.ansatz_type == AnsatzType.EFFICIENT_SU2:
            return self.config.num_qubits * self.config.num_layers * 3
        elif self.config.ansatz_type == AnsatzType.REAL_AMPLITUDE:
            return self.config.num_qubits * self.config.num_layers
        elif self.config.ansatz_type == AnsatzType.TWO_LOCAL:
            return self.config.num_qubits * self.config.num_layers * 2
        else:
            return self.config.num_qubits * self.config.num_layers * 3
            
    def _initialize_parameters(self, seed: Optional[int] = None) -> np.ndarray:
        """Initialize parameters with random values."""
        rng = np.random.default_rng(seed)
            
        if self.config.measurement_type == MeasurementType.PARITY:
            return rng.uniform(0, 2 * np.pi, self._num_parameters)
        else:
            return rng.uniform(-np.pi, np.pi, self._num_parameters)
            
    def build_circuit(self, data: np.ndarray, build_ansatz: bool = True) -> dict:
        """
        Build the complete VQC circuit.
        
        Args:
            data: Input features to encode
            build_ansatz: Whether to include variational ansatz
            
        Returns:
            Circuit representation (dict if no Qiskit, else QuantumCircuit)
        """
        circuit = {
            'type': 'VariationalQuantumClassifier',
            'config': {
                'num_qubits': self.config.num_qubits,
                'num_layers': self.config.num_layers,
                'ansatz': self.config.ansatz_type.value,
                'measurement': self.config.measurement_type.value
            },
            'layers': []
        }
        
        circuit['layers'].append({
            'layer_type': 'feature_encoding',
            'data': data.tolist() if isinstance(data, np.ndarray) else data
        })
        
        if build_ansatz:
            ansatz_layer = {
                'layer_type': 'variational_ansatz',
                'num_parameters': len(self.ansatz_params),
                'parameters': self.ansatz_params.tolist()
            }
            
            if self.config.ansatz_type == AnsatzType.EFFICIENT_SU2:
                ansatz_layer['gates'] = self._build_efficient_su2_layer()
            elif self.config.ansatz_type == AnsatzType.REAL_AMPLITUDE:
                ansatz_layer['gates'] = self._build_real_amplitude_layer()
            else:
                ansatz_layer['gates'] = self._build_two_local_layer()
                
            circuit['layers'].append(ansatz_layer)
            
        if self.config.measurement_type == MeasurementType.PARITY:
            circuit['measurement'] = {
                'type': 'parity',
                'qubits': list(range(self.config.num_qubits)),
                'classical_bits': [0]
            }
            
        return circuit
        
    def _build_efficient_su2_layer(self) -> List[Dict]:
        """Build EfficientSU2 ansatz layer."""
        gates = []
        for layer in range(self.config.num_layers):
            layer_gates = {'ry_rotations': [], 'rz_rotations': [], 'cx_entanglements': []}
            
            for qubit in range(self.config.num_qubits):
                idx = (layer * self.config.num_qubits + qubit) * 2
                layer_gates['ry_rotations'].append({
                    'qubit': qubit,
                    'parameter_idx': idx % len(self.ansatz_params)
                })
                layer_gates['rz_rotations'].append({
                    'qubit': qubit,
                    'parameter_idx': (idx + 1) % len(self.ansatz_params)
                })
                
            if self.config.include_interaction:
                for qubit in range(self.config.num_qubits - 1):
                    layer_gates['cx_entanglements'].append({
                        'control': qubit,
                        'target': qubit + 1
                    })
                    
            gates.append(layer_gates)
            
        return gates
        
    def _build_real_amplitude_layer(self) -> List[Dict]:
        """Build RealAmplitude ansatz layer."""
        gates = []
        for layer in range(self.config.num_layers):
            layer_gates = {'ry_rotations': [], 'cx_entanglements': []}
            
            for qubit in range(self.config.num_qubits):
                idx = layer * self.config.num_qubits + qubit
                layer_gates['ry_rotations'].append({
                    'qubit': qubit,
                    'parameter_idx': idx % len(self.ansatz_params)
                })
                
            if self.config.include_interaction:
                for qubit in range(0, self.config.num_qubits - 1, 2):
                    layer_gates['cx_entanglements'].append({
                        'control': qubit,
                        'target': qubit + 1
                    })
                    
            gates.append(layer_gates)
            
        return gates
        
    def _build_two_local_layer(self) -> List[Dict]:
        """Build TwoLocal ansatz layer."""
        gates = []
        for layer in range(self.config.num_layers):
            layer_gates = {'rz_rotations': [], 'ry_rotations': [], 'cx_entanglements': []}
            
            for qubit in range(self.config.num_qubits):
                idx1 = (layer * self.config.num_qubits + qubit) * 2
                idx2 = idx1 + 1
                layer_gates['rz_rotations'].append({
                    'qubit': qubit,
                    'parameter_idx': idx1 % len(self.ansatz_params)
                })
                layer_gates['ry_rotations'].append({
                    'qubit': qubit,
                    'parameter_idx': idx2 % len(self.ansatz_params)
                })
                
            if self.config.include_interaction:
                for qubit in range(self.config.num_qubits - 1):
                    layer_gates['cx_entanglements'].append({
                        'control': qubit,
                        'target': qubit + 1
                    })
                    
            gates.append(layer_gates)
            
        return gates
        
    def _simulate_circuit(self, data: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """
        Simulate circuit execution classically.
        
        Returns:
            Tuple of (probabilities, measurement_counts)
        """
        num_states = 2 ** self.config.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        statevector[0] = 1.0
        
        data_normalized = data / (np.linalg.norm(data) + 1e-8)
        
        for i, feature in enumerate(data_normalized[:self.config.num_qubits]):
            angle = np.arccos(min(1.0, abs(feature))) if abs(feature) > 1e-6 else 0
            for state in range(num_states):
                if (state >> i) & 1:
                    statevector[state] *= np.exp(1j * angle)
                else:
                    statevector[state] *= np.cos(angle)
                    
        for param_idx, param in enumerate(self.ansatz_params):
            layer = param_idx // self.config.num_qubits
            qubit = param_idx % self.config.num_qubits
            
            if self.config.ansatz_type == AnsatzType.EFFICIENT_SU2:
                gate_type = (param_idx // self.config.num_qubits) % 2
                for state in range(num_states):
                    if (state >> qubit) & 1:
                        statevector[state] *= np.exp(1j * param)
                        
            elif self.config.ansatz_type == AnsatzType.REAL_AMPLITUDE:
                for state in range(num_states):
                    if (state >> qubit) & 1:
                        statevector[state] *= np.cos(param / 2)
                    else:
                        statevector[state] *= np.sin(param / 2)
                        
        for layer in range(self.config.num_layers):
            for qubit in range(self.config.num_qubits - 1):
                for state in range(num_states):
                    if ((state >> qubit) & 1) != ((state >> (qubit + 1)) & 1):
                        statevector[state] *= 1 / np.sqrt(2)
                        if ((state >> qubit) & 1):
                            statevector[state] *= 1j
                            
        statevector = statevector / np.linalg.norm(statevector)
        probabilities = np.abs(statevector) ** 2
        
        if self.config.measurement_type == MeasurementType.PARITY:
            measurement_counts = {}
            for state, prob in enumerate(probabilities):
                parity = bin(state).count('1') % 2
                if parity not in measurement_counts:
                    measurement_counts[parity] = 0
                measurement_counts[parity] += prob * self.config.shots
                
        else:
            measurement_counts = {state: int(prob * self.config.shots) 
                               for state, prob in enumerate(probabilities)}
            
        return probabilities, measurement_counts
        
    def predict(self, data: np.ndarray) -> VQCResult:
        """
        Make prediction on input data.
        
        Args:
            data: Input feature vector
            
        Returns:
            VQCResult with prediction and confidence
        """
        probabilities, counts = self._simulate_circuit(data)
        
        if self.config.measurement_type == MeasurementType.PARITY:
            sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
            pred_key = sorted_counts[0][0] if sorted_counts else 0
            prediction = int(pred_key) if isinstance(pred_key, str) else pred_key
            confidence = sorted_counts[0][1] / self.config.shots if sorted_counts else 0.0
        else:
            max_idx = np.argmax(probabilities)
            prediction = max_idx % 2
            confidence = probabilities[max_idx]
            
        return VQCResult(
            probabilities=probabilities,
            prediction=prediction,
            confidence=float(confidence),
            measurement_counts=counts,
            circuit_depth=self.config.num_layers * 2,
            num_gates=self.config.num_qubits * self.config.num_layers * 3
        )
        
    def fit(self, X: np.ndarray, y: np.ndarray, 
            optimizer: Optional[Callable] = None) -> 'VariationalQuantumClassifier':
        """
        Fit the VQC to training data.
        
        Args:
            X: Training features
            y: Training labels
            optimizer: Classical optimizer function
            
        Returns:
            Self
        """
        self._classes = np.unique(y)
        self._is_fitted = True
        
        if optimizer is None:
            optimizer = self._gradient_descent
            
        best_loss = float('inf')
        best_params = self.ansatz_params.copy()
        
        for iteration in range(100):
            loss = self._compute_loss(X, y, self.ansatz_params)
            
            if loss < best_loss:
                best_loss = loss
                best_params = self.ansatz_params.copy()
                
            self.ansatz_params = optimizer(X, y, self.ansatz_params, loss)
            
        self.ansatz_params = best_params
        return self
        
    def _compute_loss(self, X: np.ndarray, y: np.ndarray, 
                     params: np.ndarray) -> float:
        """Compute cross-entropy loss."""
        old_params = self.ansatz_params.copy()
        self.ansatz_params = params
        
        total_loss = 0.0
        for i, (x, label) in enumerate(zip(X, y)):
            result = self.predict(x)
            probs = result.probabilities
            
            if self.config.measurement_type == MeasurementType.PARITY:
                counts = result.measurement_counts or {}
                class_0_prob = sum(c for k, c in counts.items() if str(k) == '0') / self.config.shots
                class_1_prob = sum(c for k, c in counts.items() if str(k) == '1') / self.config.shots
                pred_prob = class_1_prob if label == 1 else class_0_prob
            else:
                pred_prob = probs[label % len(probs)]
                
            pred_prob = max(pred_prob, 1e-10)
            total_loss -= np.log(pred_prob)
            
        self.ansatz_params = old_params
        return float(total_loss / len(X))
        
    def _gradient_descent(self, X: np.ndarray, y: np.ndarray,
                         params: np.ndarray, loss: float,
                         lr: float = 0.1) -> np.ndarray:
        """Simple gradient descent optimizer."""
        epsilon = 1e-5
        gradients = np.zeros_like(params)
        
        for i in range(len(params)):
            params_plus = params.copy()
            params_plus[i] += epsilon
            loss_plus = self._compute_loss(X, y, params_plus)
            gradients[i] = (loss_plus - loss) / epsilon
            
        return params - lr * gradients


class QuantumNeuralNetwork:
    """
    Quantum Neural Network for feature extraction and transformation.
    
    Provides a quantum analogue to classical neural network layers,
    enabling non-linear feature transformations in Hilbert space.
    """
    
    def __init__(self, num_qubits: int, num_layers: int,
                 encoding_type: str = 'amplitude'):
        self.num_qubits = num_qubits
        self.num_layers = num_layers
        self.encoding_type = encoding_type
        self.weights = self._initialize_weights()
        
    def _initialize_weights(self, seed: Optional[int] = None) -> np.ndarray:
        """Initialize network weights."""
        rng = np.random.default_rng(seed)
        return rng.standard_normal((self.num_layers, self.num_qubits)) * 0.1
        
    def forward(self, data: np.ndarray) -> np.ndarray:
        """
        Forward pass through QNN.
        
        Args:
            data: Input feature vector
            
        Returns:
            Transformed feature vector
        """
        data = np.array(data, dtype=np.float64)
        if data.ndim == 1:
            data = data.reshape(1, -1)
            
        num_samples = data.shape[0]
        outputs = np.zeros((num_samples, 2 ** self.num_qubits))
        
        for i, sample in enumerate(data):
            statevector = self._encode_sample(sample)
            
            for layer in range(self.num_layers):
                statevector = self._apply_layer(statevector, self.weights[layer])
                
            outputs[i] = np.abs(statevector) ** 2
            
        return outputs
        
    def _encode_sample(self, sample: np.ndarray) -> np.ndarray:
        """Encode sample into quantum state."""
        num_states = 2 ** self.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        
        sample_norm = sample / (np.linalg.norm(sample) + 1e-8)
        
        if self.encoding_type == 'amplitude':
            for i, feature in enumerate(sample_norm):
                idx = min(i, num_states - 1)
                statevector[idx] = complex(feature, 0)
                
        elif self.encoding_type == 'angle':
            for i, feature in enumerate(sample_norm):
                if i < self.num_qubits:
                    angle = np.pi * (feature - sample_norm.min()) / (sample_norm.max() - sample_norm.min() + 1e-8)
                    for state in range(num_states):
                        if (state >> i) & 1:
                            statevector[state] *= np.exp(1j * angle)
                            
        elif self.encoding_type == 'basis':
            idx = int(np.argmax(np.abs(sample_norm)) % num_states)
            statevector[idx] = 1.0
            
        return statevector / np.linalg.norm(statevector)
        
    def _apply_layer(self, statevector: np.ndarray, weights: np.ndarray) -> np.ndarray:
        """Apply single QNN layer transformation."""
        num_states = len(statevector)
        new_state = np.zeros_like(statevector)
        
        for state in range(num_states):
            amplitude = statevector[state]
            
            for qubit in range(min(self.num_qubits, len(weights))):
                weight = weights[qubit]
                bit_value = (state >> qubit) & 1
                
                if bit_value:
                    rotation = np.exp(1j * weight)
                    new_state[state] += amplitude * rotation
                else:
                    new_state[state] += amplitude * np.cos(weight / 2)
                    flipped = state | (1 << qubit)
                    new_state[flipped] += amplitude * np.sin(weight / 2) * 1j
                    
        return new_state / np.linalg.norm(new_state)
        
    def get_circuit_diagram(self) -> Dict:
        """Get visual representation of QNN circuit."""
        diagram = {
            'type': 'QuantumNeuralNetwork',
            'num_qubits': self.num_qubits,
            'num_layers': self.num_layers,
            'encoding': self.encoding_type,
            'layers': []
        }
        
        diagram['layers'].append({
            'name': 'Data Encoding',
            'type': self.encoding_type,
            'qubits': list(range(self.num_qubits))
        })
        
        for layer_idx in range(self.num_layers):
            layer_desc = {
                'name': f'Layer {layer_idx + 1}',
                'rotations': [
                    {'qubit': q, 'type': 'ry', 'weight_idx': layer_idx * self.num_qubits + q}
                    for q in range(self.num_qubits)
                ],
                'entanglements': [
                    {'control': q, 'target': q + 1}
                    for q in range(self.num_qubits - 1)
                ]
            }
            diagram['layers'].append(layer_desc)
            
        return diagram


class QuantumKernelCircuit:
    """
    Quantum Kernel Circuit for computing kernel matrices.
    
    Computes quantum kernel K(x,y) = |<0|U(x)^dagger U(y)|0>|^2
    which measures the overlap between quantum states.
    """
    
    def __init__(self, num_qubits: int, feature_map_type: str = 'zz'):
        self.num_qubits = num_qubits
        self.feature_map_type = feature_map_type
        self._kernel_matrix = None
        
    def compute_kernel(self, X: np.ndarray, Y: Optional[np.ndarray] = None) -> np.ndarray:
        """
        Compute quantum kernel matrix.
        
        Args:
            X: First set of samples
            Y: Second set of samples (if None, computes K(X,X))
            
        Returns:
            Kernel matrix K[i,j] = quantum_kernel(X[i], Y[j])
        """
        if Y is None:
            Y = X
            
        n_x, n_y = len(X), len(Y)
        kernel_matrix = np.zeros((n_x, n_y))
        
        for i in range(n_x):
            for j in range(n_y):
                kernel_matrix[i, j] = self._compute_overlap(X[i], Y[j])
                
        self._kernel_matrix = kernel_matrix
        return kernel_matrix
        
    def _compute_overlap(self, x: np.ndarray, y: np.ndarray) -> float:
        """Compute overlap between two quantum states."""
        state_x = self._encode_state(x)
        state_y = self._encode_state(y)
        
        overlap = np.vdot(state_x, state_y)
        return np.abs(overlap) ** 2
        
    def _encode_state(self, data: np.ndarray) -> np.ndarray:
        """Encode classical data into quantum state."""
        num_states = 2 ** self.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        
        data_norm = data / (np.linalg.norm(data) + 1e-8)
        
        if self.feature_map_type == 'zz':
            for i, feature in enumerate(data_norm[:self.num_qubits]):
                angle = np.pi * feature
                for state in range(num_states):
                    if (state >> i) & 1:
                        statevector[state] *= np.exp(1j * angle)
                        
        elif self.feature_map_type == 'amplitude':
            for i, feature in enumerate(data_norm):
                if i < num_states:
                    statevector[i] = complex(feature, 0)
                    
        return statevector / np.linalg.norm(statevector)
        
    def get_kernel_properties(self) -> Dict:
        """Get properties of the computed kernel."""
        if self._kernel_matrix is None:
            return {'error': 'Kernel not yet computed'}
            
        eigenvalues = np.linalg.eigvalsh(self._kernel_matrix)
        
        return {
            'shape': self._kernel_matrix.shape,
            'min_eigenvalue': float(eigenvalues.min()),
            'max_eigenvalue': float(eigenvalues.max()),
            'condition_number': float(eigenvalues.max() / eigenvalues.min()) if eigenvalues.min() > 0 else float('inf'),
            'is_positive_semi_definite': bool(np.all(eigenvalues >= -1e-10)),
            'feature_map': self.feature_map_type
        }


def create_vqc(num_qubits: int = 4, num_classes: int = 2,
               ansatz_type: str = 'efficient_su2',
               measurement: str = 'parity') -> VariationalQuantumClassifier:
    """
    Factory function to create VQC instances.
    
    Args:
        num_qubits: Number of qubits
        num_classes: Number of classification classes
        ansatz_type: Type of variational ansatz
        measurement: Measurement strategy
        
    Returns:
        Configured VariationalQuantumClassifier
    """
    ansatz_map = {
        'efficient_su2': AnsatzType.EFFICIENT_SU2,
        'real_amplitude': AnsatzType.REAL_AMPLITUDE,
        'two_local': AnsatzType.TWO_LOCAL,
    }
    
    measurement_map = {
        'parity': MeasurementType.PARITY,
        'expectation': MeasurementType.EXPECTATION,
        'sampling': MeasurementType.SAMPLING,
    }
    
    config = CircuitConfig(
        num_qubits=num_qubits,
        ansatz_type=ansatz_map.get(ansatz_type, AnsatzType.EFFICIENT_SU2),
        measurement_type=measurement_map.get(measurement, MeasurementType.PARITY),
        num_layers=2
    )
    
    return VariationalQuantumClassifier(config=config)
