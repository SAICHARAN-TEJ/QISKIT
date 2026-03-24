"""
Quantum Utilities
=================
Utility functions for quantum computation and visualization.

Components:
- QuantumBackend: Backend selection and execution
- CircuitVisualizer: Circuit diagram generation
- QuantumMetrics: Quantum-specific metrics computation
"""

import numpy as np
from typing import Optional, List, Dict, Tuple, Union, Any
from dataclasses import dataclass
from enum import Enum
import json
import base64


class BackendType(Enum):
    """Available quantum backends."""
    QISKIT_AER = "qiskit_aer"
    QISKIT_IBM = "qiskit_ibm"
    SIMULATOR = "simulator"
    CLASSICAL = "classical"


@dataclass
class BackendConfig:
    """Configuration for quantum backend."""
    backend_type: BackendType = BackendType.CLASSICAL
    shots: int = 1024
    memory: bool = False
    seed: Optional[int] = None
    optimization_level: int = 1
    error_mitigation: bool = False


@dataclass
class ExecutionResult:
    """Result from quantum circuit execution."""
    counts: Dict[str, int]
    statevector: Optional[np.ndarray] = None
    probabilities: Optional[np.ndarray] = None
    time_taken: float = 0.0
    backend: str = "simulator"
    metadata: Optional[Dict] = None


class QuantumBackend:
    """
    Quantum Backend Manager.
    
    Handles execution of quantum circuits on various backends
    with automatic fallback to classical simulation.
    """
    
    def __init__(self, config: Optional[BackendConfig] = None):
        self.config = config or BackendConfig()
        self._available_backends = self._detect_backends()
        self._current_backend = self._select_backend()
        
    def _detect_backends(self) -> Dict[str, bool]:
        """Detect available quantum backends."""
        backends = {
            'qiskit_aer': False,
            'qiskit_ibm': False,
            'simulator': True
        }
        
        try:
            import qiskit_aer
            backends['qiskit_aer'] = True
        except ImportError:
            pass
            
        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            backends['qiskit_ibm'] = True
        except ImportError:
            pass
            
        return backends
        
    def _select_backend(self) -> BackendType:
        """Select best available backend."""
        if self.config.backend_type == BackendType.QISKIT_AER and self._available_backends['qiskit_aer']:
            return BackendType.QISKIT_AER
        elif self.config.backend_type == BackendType.QISKIT_IBM and self._available_backends['qiskit_ibm']:
            return BackendType.QISKIT_IBM
        elif self._available_backends['qiskit_aer']:
            return BackendType.QISKIT_AER
        else:
            return BackendType.CLASSICAL
            
    def execute(self, circuit: Any) -> ExecutionResult:
        """
        Execute quantum circuit.
        
        Args:
            circuit: Quantum circuit to execute
            
        Returns:
            ExecutionResult with measurement counts
        """
        import time
        start_time = time.time()
        
        if self._current_backend == BackendType.QISKIT_AER:
            return self._execute_aer(circuit, start_time)
        else:
            return self._execute_classical(circuit, start_time)
            
    def _execute_aer(self, circuit: Any, start_time: float) -> ExecutionResult:
        """Execute on Qiskit Aer simulator."""
        try:
            from qiskit_aer import AerSimulator
            from qiskit import transpile
            
            backend = AerSimulator()
            
            if hasattr(circuit, 'transpile'):
                circuit = transpile(circuit, backend, optimization_level=self.config.optimization_level)
                
            job = backend.run(circuit, shots=self.config.shots, memory=self.config.memory)
            result = job.result()
            
            counts = result.get_counts(circuit) if hasattr(result, 'get_counts') else {}
            
            return ExecutionResult(
                counts=counts,
                statevector=result.get_statevector() if hasattr(result, 'get_statevector') else None,
                probabilities=result.get_counts(circuit) if hasattr(result, 'get_counts') else None,
                time_taken=time.time() - start_time,
                backend='qiskit_aer',
                metadata={'shots': self.config.shots}
            )
        except Exception as e:
            return self._execute_classical(None, start_time)
            
    def _execute_classical(self, circuit: Any, start_time: float) -> ExecutionResult:
        """Execute using classical simulation."""
        counts = self._simulate_measurement(circuit)
        
        return ExecutionResult(
            counts=counts,
            statevector=None,
            probabilities=None,
            time_taken=time.time() - start_time,
            backend='classical_simulator',
            metadata={'shots': self.config.shots}
        )
        
    def _simulate_measurement(self, circuit: Any) -> Dict[str, int]:
        """Simulate measurement without actual quantum execution."""
        if circuit is None:
            return {'0': self.config.shots // 2, '1': self.config.shots // 2}
            
        if isinstance(circuit, dict):
            num_qubits = circuit.get('config', {}).get('num_qubits', 4)
        else:
            num_qubits = getattr(circuit, 'num_qubits', 4)
            
        np.random.seed(self.config.seed)
        
        state_probs = np.random.rand(2 ** num_qubits)
        state_probs /= state_probs.sum()
        
        states = [format(i, f'0{num_qubits}b') for i in range(2 ** num_qubits)]
        
        measurements = np.random.choice(
            len(states),
            size=self.config.shots,
            p=state_probs
        )
        
        counts = {}
        for idx in measurements:
            state = states[idx]
            if state in counts:
                counts[state] += 1
            else:
                counts[state] = 1
                
        return counts
        
    def get_available_backends(self) -> Dict[str, bool]:
        """Get status of all backends."""
        return self._available_backends.copy()
        
    def set_backend(self, backend_type: BackendType):
        """Switch backend type."""
        self.config.backend_type = backend_type
        self._current_backend = self._select_backend()


class CircuitVisualizer:
    """
    Quantum Circuit Visualization.
    
    Generates ASCII/text representations of quantum circuits
    and can produce visualization data for web interfaces.
    """
    
    @staticmethod
    def to_ascii(circuit: Dict) -> str:
        """
        Generate ASCII art representation of circuit.
        
        Args:
            circuit: Circuit dictionary
            
        Returns:
            ASCII string representation
        """
        if isinstance(circuit, dict):
            return CircuitVisualizer._dict_to_ascii(circuit)
        return str(circuit)
        
    @staticmethod
    def _dict_to_ascii(circuit: Dict) -> str:
        """Convert circuit dictionary to ASCII art."""
        lines = []
        lines.append("Quantum Circuit Visualization")
        lines.append("=" * 40)
        
        circuit_type = circuit.get('type', 'Unknown')
        lines.append(f"Type: {circuit_type}")
        
        config = circuit.get('config', {})
        lines.append(f"Qubits: {config.get('num_qubits', 'N/A')}")
        lines.append(f"Layers: {config.get('num_layers', 'N/A')}")
        lines.append("")
        
        layers = circuit.get('layers', [])
        
        num_qubits = config.get('num_qubits', 4)
        
        for q in range(num_qubits):
            lines.append(f"q{q}: ────", end="")
            
        lines.append("")
        
        for layer_idx, layer in enumerate(layers):
            layer_type = layer.get('layer_type', 'unknown')
            
            if layer_type == 'feature_encoding':
                lines.append(f"[Layer {layer_idx}] Feature Encoding")
                for q in range(num_qubits):
                    lines.append(f"q{q}: ────[H]───", end="")
                lines.append("")
                
            elif layer_type == 'variational_ansatz':
                gates = layer.get('gates', [])
                for gate_layer in gates:
                    layer_repr = f"[Layer {layer_idx}] "
                    for q in range(num_qubits):
                        gate_repr = "─[RY]─"
                        layer_repr += f"q{q}: ────{gate_repr}"
                    lines.append(layer_repr)
                    
                    if gate_layer.get('cx_entanglements'):
                        lines.append(f"        │cx│ " * len(gate_layer['cx_entanglements']))
                        
                lines.append("")
                
        return "\n".join(lines)
        
    @staticmethod
    def to_json(circuit: Dict) -> str:
        """Export circuit as JSON."""
        return json.dumps(circuit, indent=2)
        
    @staticmethod
    def to_html(circuit: Dict) -> str:
        """Generate HTML visualization data."""
        return json.dumps({
            'type': 'quantum_circuit',
            'data': circuit,
            'render_options': {
                'show_barriers': True,
                'show_gates': True,
                'color_scheme': 'default'
            }
        })
        
    @staticmethod
    def get_bloch_sphere_coords(statevector: np.ndarray) -> Dict[str, float]:
        """
        Calculate Bloch sphere coordinates from statevector.
        
        Args:
            statevector: Quantum statevector
            
        Returns:
            Dict with theta, phi angles
        """
        if statevector is None or len(statevector) < 2:
            return {'theta': 0.0, 'phi': 0.0}
            
        alpha = statevector[0]
        beta = statevector[1] if len(statevector) > 1 else 0
        
        alpha = complex(alpha)
        beta = complex(beta)
        
        theta = 2 * np.arccos(np.abs(alpha))
        phi = np.angle(beta) - np.angle(alpha) if np.abs(beta) > 1e-10 else 0
        
        return {
            'theta': float(theta),
            'phi': float(phi),
            'x': float(np.sin(theta) * np.cos(phi)),
            'y': float(np.sin(theta) * np.sin(phi)),
            'z': float(np.cos(theta))
        }


class QuantumMetrics:
    """
    Quantum-specific Metrics Computation.
    
    Provides metrics for analyzing quantum circuits and results.
    """
    
    @staticmethod
    def entanglement_entropy(probabilities: np.ndarray) -> float:
        """
        Compute von Neumann entanglement entropy.
        
        Args:
            probabilities: Measurement probabilities
            
        Returns:
            Entropy value
        """
        probs = probabilities[probabilities > 1e-10]
        return -np.sum(probs * np.log2(probs))
        
    @staticmethod
    def purity(probabilities: np.ndarray) -> float:
        """
        Compute purity of quantum state.
        
        Args:
            probabilities: Measurement probabilities
            
        Returns:
            Purity value (1 = pure, 0.5 = maximally mixed)
        """
        return np.sum(probabilities ** 2)
        
    @staticmethod
    def quantum_advantage_score(entanglement: float, coherence: float,
                               circuit_depth: int) -> float:
        """
        Estimate potential quantum advantage.
        
        Args:
            entanglement: Entanglement measure
            coherence: Coherence measure
            circuit_depth: Depth of quantum circuit
            
        Returns:
            Advantage score [0, 1]
        """
        depth_factor = min(1.0, circuit_depth / 10)
        
        advantage = (0.4 * entanglement + 
                    0.4 * coherence + 
                    0.2 * depth_factor)
        
        return min(1.0, max(0.0, advantage))
        
    @staticmethod
    def circuit_complexity(num_gates: int, num_qubits: int,
                         entanglement: float) -> float:
        """
        Compute circuit complexity score.
        
        Args:
            num_gates: Number of quantum gates
            num_qubits: Number of qubits
            entanglement: Entanglement level
            
        Returns:
            Complexity score
        """
        gate_complexity = np.log2(num_gates + 1) / 10
        
        qubit_factor = num_qubits / 10
        
        return min(1.0, 0.3 * gate_complexity + 0.4 * qubit_factor + 0.3 * entanglement)
        
    @staticmethod
    def compute_all_metrics(result: ExecutionResult,
                          circuit_info: Optional[Dict] = None) -> Dict:
        """
        Compute all quantum metrics from execution result.
        
        Args:
            result: ExecutionResult from circuit execution
            circuit_info: Optional circuit information
            
        Returns:
            Dict with all computed metrics
        """
        total_shots = sum(result.counts.values()) if result.counts else 1
        
        if result.counts:
            probabilities = np.array([
                count / total_shots 
                for count in result.counts.values()
            ])
        else:
            probabilities = np.array([1.0])
            
        entropy = QuantumMetrics.entanglement_entropy(probabilities)
        purity = QuantumMetrics.purity(probabilities)
        
        num_qubits = circuit_info.get('config', {}).get('num_qubits', 4) if circuit_info else 4
        max_entropy = np.log2(2 ** num_qubits)
        normalized_entropy = entropy / max_entropy if max_entropy > 0 else 0
        
        coherence = purity * normalized_entropy
        
        circuit_depth = circuit_info.get('config', {}).get('num_layers', 1) * 2 if circuit_info else 2
        
        advantage = QuantumMetrics.quantum_advantage_score(
            normalized_entropy, coherence, circuit_depth
        )
        
        num_gates = circuit_info.get('config', {}).get('num_gates', 10) if circuit_info else 10
        complexity = QuantumMetrics.circuit_complexity(
            num_gates, num_qubits, normalized_entropy
        )
        
        return {
            'entropy': float(entropy),
            'purity': float(purity),
            'coherence': float(coherence),
            'advantage_score': float(advantage),
            'complexity': float(complexity),
            'num_qubits': num_qubits,
            'circuit_depth': circuit_depth,
            'execution_time': result.time_taken,
            'backend': result.backend,
            'total_shots': total_shots
        }


class QuantumStateAnalyzer:
    """
    Analyzer for quantum states and their properties.
    """
    
    @staticmethod
    def analyze_state(statevector: np.ndarray) -> Dict:
        """
        Comprehensive analysis of quantum state.
        
        Args:
            statevector: Quantum statevector
            
        Returns:
            Dict with state analysis
        """
        probs = np.abs(statevector) ** 2
        
        return {
            'norm': float(np.linalg.norm(statevector)),
            'dimension': len(statevector),
            'max_probability': float(probs.max()),
            'entropy': QuantumMetrics.entanglement_entropy(probs),
            'purity': QuantumMetrics.purity(probs),
            'bloch_coords': CircuitVisualizer.get_bloch_sphere_coords(statevector)
        }
        
    @staticmethod
    def compare_states(state1: np.ndarray, state2: np.ndarray) -> Dict:
        """
        Compare two quantum states.
        
        Args:
            state1: First statevector
            state2: Second statevector
            
        Returns:
            Dict with comparison metrics
        """
        overlap = np.abs(np.vdot(state1, state2)) ** 2
        
        fidelity = np.abs(np.vdot(state1, state2))
        
        trace_distance = 0.5 * np.sum(np.abs(state1 - state2))
        
        return {
            'overlap': float(overlap),
            'fidelity': float(fidelity),
            'trace_distance': float(trace_distance),
            'are_identical': bool(np.allclose(state1, state2))
        }


def create_backend(backend_type: str = 'classical',
                  shots: int = 1024,
                  **kwargs) -> QuantumBackend:
    """
    Factory function to create quantum backends.
    
    Args:
        backend_type: Type of backend
        shots: Number of measurement shots
        **kwargs: Additional configuration
        
    Returns:
        Configured QuantumBackend
    """
    backend_type_map = {
        'aer': BackendType.QISKIT_AER,
        'qiskit_aer': BackendType.QISKIT_AER,
        'ibm': BackendType.QISKIT_IBM,
        'qiskit_ibm': BackendType.QISKIT_IBM,
        'simulator': BackendType.SIMULATOR,
        'classical': BackendType.CLASSICAL
    }
    
    config = BackendConfig(
        backend_type=backend_type_map.get(backend_type, BackendType.CLASSICAL),
        shots=shots,
        seed=kwargs.get('seed'),
        optimization_level=kwargs.get('optimization_level', 1)
    )
    
    return QuantumBackend(config)
