"""
Quantum Feature Maps
====================
Quantum feature maps encode classical data into quantum states.

Types:
- ZZFeatureMap: Pauli-Z entangling feature map
- PauliFeatureMap: General Pauli-based feature map
- EfficientSU2Map: Hardware-efficient ansatz for feature mapping
"""

import numpy as np
from typing import Optional, Union, List
import warnings


class QuantumFeatureMap:
    """Base class for quantum feature maps."""
    
    def __init__(self, num_qubits: int, num_features: int, reps: int = 2):
        self.num_qubits = num_qubits
        self.num_features = min(num_features, num_qubits)
        self.reps = reps
        self._circuit = None
        
    def encode(self, data: np.ndarray) -> np.ndarray:
        """Normalize and prepare data for encoding."""
        data = np.array(data, dtype=np.float64)
        if data.ndim == 1:
            data = data[:self.num_features]
            if len(data) < self.num_features:
                data = np.pad(data, (0, self.num_features - len(data)))
        return self._normalize(data)
    
    def _normalize(self, data: np.ndarray) -> np.ndarray:
        """Normalize data to [0, π] range for quantum encoding."""
        min_val, max_val = data.min(), data.max()
        if max_val - min_val > 0:
            return np.pi * (data - min_val) / (max_val - min_val)
        return np.pi * np.ones_like(data) / 2
    
    def build_circuit(self, data: np.ndarray, measurements: bool = True):
        """Build the quantum circuit for this feature map."""
        raise NotImplementedError("Subclasses must implement build_circuit")
    
    def get_statevector(self, data: np.ndarray) -> np.ndarray:
        """Get the quantum statevector after encoding."""
        raise NotImplementedError("Subclasses must implement get_statevector")


class ZZFeatureMap(QuantumFeatureMap):
    """
    ZZFeatureMap: Second-order Pauli-Z entangling feature map.
    
    Creates entanglement between qubits based on feature interactions.
    Particularly effective for capturing correlations in disaster data.
    
    Circuit structure:
    - Initial layer: H gates on all qubits
    - Repeated layers: RZ rotation, ZZ entangling, RZ rotation
    
    Reference: Havlicek et al., "Supervised learning with quantum enhanced feature spaces"
    """
    
    def __init__(self, num_qubits: int, num_features: int, reps: int = 2, 
                 entanglement: str = 'linear', alpha: float = 2.0):
        super().__init__(num_qubits, num_features, reps)
        self.entanglement = entanglement
        self.alpha = alpha
        
    def build_circuit(self, data: np.ndarray, measurements: bool = True):
        """
        Build ZZFeatureMap circuit.
        
        Args:
            data: Feature vector (will be encoded)
            measurements: Whether to add measurements
            
        Returns:
            Quantum circuit with feature encoding
        """
        try:
            from qiskit import QuantumCircuit
            from qiskit.circuit.library import ZZFeatureMap as QiskitZZFeatureMap
            
            data_encoded = self.encode(data)
            
            circuit = QiskitZZFeatureMap(
                feature_dimension=len(data_encoded),
                reps=self.reps,
                entanglement=self.entanglement,
                alpha=self.alpha
            ).compose(QuantumCircuit(len(data_encoded)))
            
            if measurements:
                circuit.measure_all()
                
            return circuit
            
        except ImportError:
            return self._build_classic_circuit(data, measurements)
    
    def _build_classic_circuit(self, data: np.ndarray, measurements: bool) -> dict:
        """Fallback circuit representation without Qiskit."""
        data_encoded = self.encode(data)
        return {
            'type': 'ZZFeatureMap',
            'num_qubits': self.num_qubits,
            'reps': self.reps,
            'encoded_features': data_encoded.tolist(),
            'entanglement': self.entanglement,
            'measurements': measurements
        }
    
    def get_statevector(self, data: np.ndarray) -> np.ndarray:
        """Simulate statevector using classical approximation."""
        data_encoded = self.encode(data)
        
        num_states = 2 ** self.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        statevector[0] = 1.0
        
        for rep in range(self.reps):
            for i, angle in enumerate(data_encoded[:self.num_qubits]):
                phase = angle * self.alpha
                for state in range(num_states):
                    if (state >> i) & 1:
                        statevector[state] *= np.exp(1j * phase)
                
                if i < self.num_qubits - 1 and self.entanglement == 'linear':
                    for state in range(num_states):
                        if ((state >> i) & 1) and ((state >> (i + 1)) & 1):
                            statevector[state] *= np.exp(1j * data_encoded[i] * data_encoded[i + 1])
                            
        return statevector / np.linalg.norm(statevector)


class PauliFeatureMap(QuantumFeatureMap):
    """
    PauliFeatureMap: General Pauli-based feature map.
    
    Uses arbitrary Pauli strings for encoding, allowing
    exploration of different feature correlations.
    """
    
    def __init__(self, num_qubits: int, num_features: int, reps: int = 2,
                 paulis: Optional[List[str]] = None):
        super().__init__(num_qubits, num_features, reps)
        self.paulis = paulis or ['Z', 'ZZ']
        
    def build_circuit(self, data: np.ndarray, measurements: bool = True):
        """Build Pauli feature map circuit."""
        try:
            from qiskit import QuantumCircuit
            from qiskit.circuit.library import PauliFeatureMap as QiskitPauliFeatureMap
            
            data_encoded = self.encode(data)
            
            circuit = QiskitPauliFeatureMap(
                feature_dimension=len(data_encoded),
                reps=self.reps,
                paulis=self.paulis
            ).compose(QuantumCircuit(len(data_encoded)))
            
            if measurements:
                circuit.measure_all()
                
            return circuit
            
        except ImportError:
            return self._build_classic_circuit(data, measurements)
    
    def _build_classic_circuit(self, data: np.ndarray, measurements: bool) -> dict:
        """Fallback circuit representation."""
        data_encoded = self.encode(data)
        return {
            'type': 'PauliFeatureMap',
            'num_qubits': self.num_qubits,
            'reps': self.reps,
            'encoded_features': data_encoded.tolist(),
            'paulis': self.paulis,
            'measurements': measurements
        }
    
    def get_statevector(self, data: np.ndarray) -> np.ndarray:
        """Simulate Pauli-based encoding."""
        data_encoded = self.encode(data)
        
        num_states = 2 ** self.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        statevector[0] = 1.0
        
        for rep in range(self.reps):
            for i, angle in enumerate(data_encoded[:self.num_qubits]):
                for state in range(num_states):
                    if 'Z' in self.paulis:
                        if (state >> i) & 1:
                            statevector[state] *= np.exp(1j * angle)
                            
                if 'ZZ' in self.paulis and i < self.num_qubits - 1:
                    for state in range(num_states):
                        if ((state >> i) & 1) and ((state >> (i + 1)) & 1):
                            statevector[state] *= np.exp(1j * angle * data_encoded[i + 1])
                            
        return statevector / np.linalg.norm(statevector)


class EfficientSU2Map(QuantumFeatureMap):
    """
    EfficientSU2Map: Hardware-efficient ansatz for feature mapping.
    
    Uses only RY and RZ rotations with CNOT entanglement,
    optimized for execution on real quantum hardware.
    """
    
    def __init__(self, num_qubits: int, num_features: int, reps: int = 2,
                 su2_gates: str = 'ryrz'):
        super().__init__(num_qubits, num_features, reps)
        self.su2_gates = su2_gates
        
    def build_circuit(self, data: np.ndarray, measurements: bool = True):
        """Build EfficientSU2 feature map circuit."""
        try:
            from qiskit import QuantumCircuit
            from qiskit.circuit.library import EfficientSU2
            
            data_encoded = self.encode(data)
            
            circuit = EfficientSU2(
                num_qubits=self.num_qubits,
                reps=self.reps,
                su2_gates=self.su2_gates
            ).compose(QuantumCircuit(self.num_qubits))
            
            param_count = circuit.num_parameters
            if param_count > 0:
                params = np.concatenate([data_encoded, np.zeros(max(0, param_count - len(data_encoded)))])
                params = params[:param_count]
                circuit = circuit.assign_parameters(params)
            
            if measurements:
                circuit.measure_all()
                
            return circuit
            
        except ImportError:
            return self._build_classic_circuit(data, measurements)
    
    def _build_classic_circuit(self, data: np.ndarray, measurements: bool) -> dict:
        """Fallback circuit representation."""
        data_encoded = self.encode(data)
        return {
            'type': 'EfficientSU2',
            'num_qubits': self.num_qubits,
            'reps': self.reps,
            'encoded_features': data_encoded.tolist(),
            'su2_gates': self.su2_gates,
            'measurements': measurements
        }
    
    def get_statevector(self, data: np.ndarray) -> np.ndarray:
        """Simulate EfficientSU2 encoding."""
        data_encoded = self.encode(data)
        
        num_states = 2 ** self.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        statevector[0] = 1.0
        
        for rep in range(self.reps):
            for i in range(self.num_qubits):
                idx = (rep * self.num_qubits + i) % len(data_encoded)
                angle = data_encoded[idx]
                
                for state in range(num_states):
                    if (state >> i) & 1:
                        statevector[state] *= np.exp(1j * angle)
                    else:
                        statevector[state] *= np.cos(angle / 2)
                        
                if i < self.num_qubits - 1:
                    for state in range(num_states):
                        if ((state >> i) & 1) != ((state >> (i + 1)) & 1):
                            statevector[state] *= 1j / np.sqrt(2)
                            
        return statevector / np.linalg.norm(statevector)


class CustomFeatureMap(QuantumFeatureMap):
    """
    CustomFeatureMap: User-defined feature map for specific use cases.
    
    Allows custom encoding strategies for disaster prediction
    with domain-specific feature interactions.
    """
    
    def __init__(self, num_qubits: int, num_features: int, reps: int = 2,
                 interaction_pattern: Optional[str] = None,
                 rotation_gates: Optional[List[str]] = None):
        super().__init__(num_qubits, num_features, reps)
        self.interaction_pattern = interaction_pattern or 'full'
        self.rotation_gates = rotation_gates or ['rx', 'ry', 'rz']
        
    def build_circuit(self, data: np.ndarray, measurements: bool = True) -> dict:
        """Build custom feature map based on specification."""
        data_encoded = self.encode(data)
        
        circuit_desc = {
            'type': 'CustomFeatureMap',
            'num_qubits': self.num_qubits,
            'num_features': self.num_features,
            'reps': self.reps,
            'encoded_features': data_encoded.tolist(),
            'interaction_pattern': self.interaction_pattern,
            'rotation_gates': self.rotation_gates,
            'layers': []
        }
        
        for rep in range(self.reps):
            layer = {'rotation_layer': [], 'entanglement_layer': []}
            
            for i in range(self.num_qubits):
                idx = (rep * self.num_qubits + i) % len(data_encoded)
                layer['rotation_layer'].append({
                    'qubit': i,
                    'gates': [{g: float(data_encoded[idx] * np.random.rand())} 
                             for g in self.rotation_gates]
                })
                
            for i in range(self.num_qubits - 1):
                if self.interaction_pattern == 'linear':
                    layer['entanglement_layer'].append({
                        'type': 'cx',
                        'control': i,
                        'target': i + 1
                    })
                elif self.interaction_pattern == 'full':
                    for j in range(i + 1, self.num_qubits):
                        layer['entanglement_layer'].append({
                            'type': 'cx',
                            'control': i,
                            'target': j
                        })
                        
            circuit_desc['layers'].append(layer)
            
        if measurements:
            circuit_desc['measurements'] = list(range(self.num_qubits))
            
        return circuit_desc
    
    def get_statevector(self, data: np.ndarray) -> np.ndarray:
        """Simulate custom feature encoding."""
        data_encoded = self.encode(data)
        
        num_states = 2 ** self.num_qubits
        statevector = np.zeros(num_states, dtype=complex)
        statevector[0] = 1.0
        
        for rep in range(self.reps):
            for i in range(self.num_qubits):
                idx = (rep * self.num_qubits + i) % len(data_encoded)
                angle = data_encoded[idx]
                
                for state in range(num_states):
                    y_weight = ((state >> i) & 1)
                    statevector[state] *= np.exp(1j * angle * y_weight)
                    
            if self.interaction_pattern == 'linear':
                for i in range(self.num_qubits - 1):
                    for state in range(num_states):
                        if ((state >> i) & 1) and ((state >> (i + 1)) & 1):
                            statevector[state] *= np.exp(1j * 0.1)
                            
        return statevector / np.linalg.norm(statevector)


def create_feature_map(map_type: str, num_qubits: int, num_features: int, 
                       **kwargs) -> QuantumFeatureMap:
    """
    Factory function to create feature maps.
    
    Args:
        map_type: Type of feature map ('zz', 'pauli', 'efficient_su2', 'custom')
        num_qubits: Number of qubits
        num_features: Number of features
        **kwargs: Additional parameters for the feature map
        
    Returns:
        QuantumFeatureMap instance
    """
    map_type = map_type.lower().replace('-', '_').replace(' ', '_')
    
    if map_type in ['zz', 'zzfeaturemap']:
        return ZZFeatureMap(num_qubits, num_features, **kwargs)
    elif map_type in ['pauli', 'paulifeaturemap']:
        return PauliFeatureMap(num_qubits, num_features, **kwargs)
    elif map_type in ['efficient_su2', 'efficient_su2_map']:
        return EfficientSU2Map(num_qubits, num_features, **kwargs)
    elif map_type in ['custom', 'custom_feature_map']:
        return CustomFeatureMap(num_qubits, num_features, **kwargs)
    else:
        warnings.warn(f"Unknown feature map type '{map_type}', defaulting to ZZFeatureMap")
        return ZZFeatureMap(num_qubits, num_features, **kwargs)
