"""
Machine Learning Module
======================
Classical ML components for disaster prediction.

Components:
- FeatureEngineering: Feature extraction and transformation
- DataPreprocessor: Data cleaning and normalization
- ModelEvaluator: Model performance evaluation
"""

import numpy as np
from typing import Optional, List, Dict, Tuple, Union
from dataclasses import dataclass
import warnings


@dataclass
class DisasterFeatures:
    """Container for disaster prediction features."""
    temperature: float
    pressure: float
    humidity: float
    wind_speed: float
    max_wind_speed: float
    wind_direction: float
    dew_point: float
    
    def to_array(self) -> np.ndarray:
        """Convert to numpy array."""
        return np.array([
            self.temperature,
            self.pressure,
            self.humidity,
            self.wind_speed,
            self.max_wind_speed,
            self.wind_direction,
            self.dew_point
        ])
    
    @classmethod
    def from_sensor_data(cls, data: dict) -> 'DisasterFeatures':
        """Create from sensor data dictionary."""
        return cls(
            temperature=float(data.get('temperature', 0)),
            pressure=float(data.get('pressure', 1013)),
            humidity=float(data.get('humidity', 50)),
            wind_speed=float(data.get('wind_speed', 0)),
            max_wind_speed=float(data.get('max_wind_speed', 0)),
            wind_direction=float(data.get('wind_direction', 0)),
            dew_point=float(data.get('dew_point', 0))
        )


class FeatureEngineering:
    """
    Feature Engineering for Disaster Prediction.
    
    Creates derived features from raw sensor data to improve
    prediction accuracy.
    """
    
    @staticmethod
    def compute_derived_features(features: DisasterFeatures) -> np.ndarray:
        """
        Compute derived features for quantum ML model.
        
        Args:
            features: Raw disaster features
            
        Returns:
            Feature vector with derived features
        """
        raw = features.to_array()
        
        temp, pressure, humidity, wind, max_wind, wind_dir, dew_point = raw
        
        derived = [
            temp ** 2,
            pressure ** 2,
            temp * humidity,
            wind * pressure,
            humidity / (temp + 0.1),
            (temp - dew_point) ** 2,
            wind ** 2,
            abs(wind_dir),
            max_wind - wind,
            (humidity * pressure) / (temp + 273.15),
            np.sin(np.radians(wind_dir)),
            np.cos(np.radians(wind_dir)),
            temp / (pressure + 1),
            (wind ** 2) / (pressure + 1),
            humidity * np.sin(np.radians(wind_dir)),
        ]
        
        return np.array([temp, pressure, humidity, wind, max_wind, wind_dir, dew_point] + derived)
    
    @staticmethod
    def compute_risk_indicators(features: DisasterFeatures) -> Dict[str, float]:
        """
        Compute risk indicators for each disaster type.
        
        Returns:
            Dict with risk scores for each disaster type
        """
        temp = features.temperature
        pressure = features.pressure
        humidity = features.humidity
        wind = features.wind_speed
        max_wind = features.max_wind_speed
        
        indicators = {}
        
        indicators['heat_wave'] = (
            0.4 * max(0, min(1, (temp - 30) / 10)) +
            0.3 * max(0, min(1, (humidity - 50) / 30)) +
            0.3 * max(0, min(1, (temp - features.dew_point) / 15))
        )
        
        indicators['cyclone'] = (
            0.4 * max(0, min(1, wind / 20)) +
            0.4 * max(0, min(1, (1013 - pressure) / 50)) +
            0.2 * max(0, min(1, (max_wind - wind) / 10))
        )
        
        indicators['flood'] = (
            0.5 * max(0, min(1, (humidity - 70) / 25)) +
            0.3 * max(0, min(1, (pressure - 980) / 50)) +
            0.2 * max(0, min(1, temp / 30))
        )
        
        indicators['blizzard'] = (
            0.5 * max(0, min(1, (25 - temp) / 25)) +
            0.3 * max(0, min(1, wind / 15)) +
            0.2 * max(0, min(1, humidity / 80))
        )
        
        indicators['earthquake'] = (
            0.7 * max(0, min(1, (1013 - pressure) / 50)) +
            0.3 * max(0, min(1, (25 - temp) / 20))
        )
        
        return indicators
    
    @staticmethod
    def compute_interaction_features(features: np.ndarray) -> np.ndarray:
        """
        Compute second-order interaction features.
        
        Args:
            features: Feature vector
            
        Returns:
            Feature vector with interactions
        """
        interactions = []
        for i in range(len(features)):
            for j in range(i + 1, len(features)):
                interactions.append(features[i] * features[j])
                
        return np.concatenate([features, interactions])


class DataPreprocessor:
    """
    Data Preprocessing for Quantum ML.
    
    Handles normalization, handling of missing values,
    and data augmentation.
    """
    
    def __init__(self, normalization: str = 'minmax'):
        self.normalization = normalization
        self._feature_min = None
        self._feature_max = None
        self._feature_mean = None
        self._feature_std = None
        self._is_fitted = False
        
    def fit(self, X: np.ndarray) -> 'DataPreprocessor':
        """
        Fit preprocessor to training data.
        
        Args:
            X: Training features
            
        Returns:
            Self
        """
        X = np.array(X, dtype=np.float64)
        
        if self.normalization == 'minmax':
            self._feature_min = X.min(axis=0)
            self._feature_max = X.max(axis=0)
        elif self.normalization == 'standard':
            self._feature_mean = X.mean(axis=0)
            self._feature_std = X.std(axis=0) + 1e-8
            
        self._is_fitted = True
        return self
        
    def transform(self, X: np.ndarray) -> np.ndarray:
        """
        Transform data using fitted parameters.
        
        Args:
            X: Features to transform
            
        Returns:
            Normalized features
        """
        X = np.array(X, dtype=np.float64)
        
        if not self._is_fitted:
            raise ValueError("Preprocessor must be fitted before transform")
            
        if self.normalization == 'minmax':
            range_vals = self._feature_max - self._feature_min
            range_vals[range_vals == 0] = 1
            return (X - self._feature_min) / range_vals
            
        elif self.normalization == 'standard':
            return (X - self._feature_mean) / self._feature_std
            
        return X
        
    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        """Fit and transform in one step."""
        return self.fit(X).transform(X)
    
    def inverse_transform(self, X: np.ndarray) -> np.ndarray:
        """Reverse normalization."""
        X = np.array(X, dtype=np.float64)
        
        if self.normalization == 'minmax':
            range_vals = self._feature_max - self._feature_min
            return X * range_vals + self._feature_min
        elif self.normalization == 'standard':
            return X * self._feature_std + self._feature_mean
            
        return X
        
    def handle_missing(self, X: np.ndarray, strategy: str = 'mean') -> np.ndarray:
        """
        Handle missing values.
        
        Args:
            X: Input data
            strategy: 'mean', 'median', or 'zero'
            
        Returns:
            Data with missing values filled
        """
        X = np.array(X, dtype=np.float64).copy()
        
        if strategy == 'mean':
            fill_values = np.nanmean(X, axis=0)
        elif strategy == 'median':
            fill_values = np.nanmedian(X, axis=0)
        elif strategy == 'zero':
            fill_values = np.zeros(X.shape[1])
        else:
            raise ValueError(f"Unknown strategy: {strategy}")
            
        nan_mask = np.isnan(X)
        for j in range(X.shape[1]):
            X[nan_mask[:, j], j] = fill_values[j]
            
        return X


class ModelEvaluator:
    """
    Model Evaluation Metrics.
    
    Provides comprehensive evaluation of disaster prediction models.
    """
    
    @staticmethod
    def accuracy(y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Calculate accuracy."""
        return np.mean(y_true == y_pred)
    
    @staticmethod
    def precision(y_true: np.ndarray, y_pred: np.ndarray, 
                 pos_label: int = 1) -> float:
        """Calculate precision."""
        true_positives = np.sum((y_true == pos_label) & (y_pred == pos_label))
        predicted_positives = np.sum(y_pred == pos_label)
        
        if predicted_positives == 0:
            return 0.0
        return true_positives / predicted_positives
    
    @staticmethod
    def recall(y_true: np.ndarray, y_pred: np.ndarray,
             pos_label: int = 1) -> float:
        """Calculate recall."""
        true_positives = np.sum((y_true == pos_label) & (y_pred == pos_label))
        actual_positives = np.sum(y_true == pos_label)
        
        if actual_positives == 0:
            return 0.0
        return true_positives / actual_positives
    
    @staticmethod
    def f1_score(y_true: np.ndarray, y_pred: np.ndarray,
                pos_label: int = 1) -> float:
        """Calculate F1 score."""
        prec = ModelEvaluator.precision(y_true, y_pred, pos_label)
        rec = ModelEvaluator.recall(y_true, y_pred, pos_label)
        
        if prec + rec == 0:
            return 0.0
        return 2 * (prec * rec) / (prec + rec)
    
    @staticmethod
    def confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray) -> np.ndarray:
        """Generate confusion matrix."""
        classes = np.unique(np.concatenate([y_true, y_pred]))
        n_classes = len(classes)
        cm = np.zeros((n_classes, n_classes), dtype=int)
        
        class_to_idx = {c: i for i, c in enumerate(classes)}
        
        for true, pred in zip(y_true, y_pred):
            cm[class_to_idx[true], class_to_idx[pred]] += 1
            
        return cm
    
    @staticmethod
    def classification_report(y_true: np.ndarray, y_pred: np.ndarray,
                            class_names: Optional[List[str]] = None) -> Dict:
        """Generate comprehensive classification report."""
        classes = np.unique(y_true)
        
        if class_names is None:
            class_names = [f"Class {c}" for c in classes]
            
        report = {
            'per_class': {},
            'macro': {},
            'weighted': {},
            'overall': {}
        }
        
        all_true = []
        all_pred = []
        
        for i, cls in enumerate(classes):
            mask = y_true == cls
            cls_true = y_true[mask]
            cls_pred = y_pred[mask]
            
            all_true.extend(cls_true.tolist())
            all_pred.extend(cls_pred.tolist())
            
            prec = ModelEvaluator.precision(y_true, y_pred, cls)
            rec = ModelEvaluator.recall(y_true, y_pred, cls)
            f1 = ModelEvaluator.f1_score(y_true, y_pred, cls)
            
            report['per_class'][class_names[i]] = {
                'precision': float(prec),
                'recall': float(rec),
                'f1-score': float(f1),
                'support': int(np.sum(mask))
            }
            
        report['overall']['accuracy'] = float(ModelEvaluator.accuracy(y_true, y_pred))
        
        macro_prec = np.mean([report['per_class'][n]['precision'] for n in class_names])
        macro_rec = np.mean([report['per_class'][n]['recall'] for n in class_names])
        macro_f1 = np.mean([report['per_class'][n]['f1-score'] for n in class_names])
        
        report['macro'] = {
            'precision': float(macro_prec),
            'recall': float(macro_rec),
            'f1-score': float(macro_f1)
        }
        
        supports = [report['per_class'][n]['support'] for n in class_names]
        total_support = sum(supports)
        weights = [s / total_support for s in supports]
        
        report['weighted'] = {
            'precision': float(np.average(
                [report['per_class'][n]['precision'] for n in class_names],
                weights=weights
            )),
            'recall': float(np.average(
                [report['per_class'][n]['recall'] for n in class_names],
                weights=weights
            )),
            'f1-score': float(np.average(
                [report['per_class'][n]['f1-score'] for n in class_names],
                weights=weights
            ))
        }
        
        return report


def prepare_quantum_features(sensor_data: Dict) -> np.ndarray:
    """
    Prepare features for quantum ML model from sensor data.
    
    Args:
        sensor_data: Dictionary with sensor readings
        
    Returns:
        Prepared feature vector
    """
    features = DisasterFeatures.from_sensor_data(sensor_data)
    
    derived = FeatureEngineering.compute_derived_features(features)
    
    interactions = FeatureEngineering.compute_interaction_features(derived)
    
    return interactions
