#!/usr/bin/env python3
"""
Model Drift Detector - Runtime Control #5

Detects model performance degradation over time using statistical methods.
Triggers retraining alerts when accuracy drops significantly.

Aligned to: Framework quality assurance, NIST SI-4 (System Monitoring)
"""

import statistics
import logging
from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict
from datetime import datetime
from collections import deque
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Single prediction record"""
    prediction: str
    ground_truth: Optional[str]
    confidence: float
    timestamp: datetime
    metadata: Dict = None


@dataclass
class DriftReport:
    """Model drift detection report"""
    drift_detected: bool
    baseline_accuracy: float
    current_accuracy: float
    accuracy_drop: float
    sample_size: int
    confidence_calibration: float  # How well-calibrated are confidence scores
    timestamp: datetime


class ModelDriftDetector:
    """
    Detect model performance drift using statistical methods.
    
    Methods:
    - Accuracy tracking (sliding window)
    - Confidence calibration analysis
    - Distribution shift detection
    """
    
    def __init__(
        self,
        agent_id: str,
        baseline_accuracy: float,
        drift_threshold: float = 0.05,
        window_size: int = 100,
        min_samples: int = 20
    ):
        self.agent_id = agent_id
        self.baseline_accuracy = baseline_accuracy
        self.drift_threshold = drift_threshold
        self.window_size = window_size
        self.min_samples = min_samples
        
        # Sliding window of predictions
        self.predictions = deque(maxlen=window_size)
        
        logger.info(f"Initialized drift detector for {agent_id}")
        logger.info(f"  Baseline accuracy: {baseline_accuracy:.2%}")
        logger.info(f"  Drift threshold: {drift_threshold:.2%}")
        logger.info(f"  Window size: {window_size}")
    
    def record_prediction(
        self,
        prediction: str,
        ground_truth: Optional[str],
        confidence: float,
        metadata: Optional[Dict] = None
    ):
        """Record a prediction for drift analysis"""
        pred = Prediction(
            prediction=prediction,
            ground_truth=ground_truth,
            confidence=confidence,
            timestamp=datetime.now(),
            metadata=metadata or {}
        )
        
        self.predictions.append(pred)
        
        logger.debug(
            f"Recorded prediction: {prediction} "
            f"(confidence: {confidence:.2f}, ground_truth: {ground_truth})"
        )
    
    def calculate_current_accuracy(self) -> Optional[float]:
        """Calculate accuracy over recent predictions"""
        # Filter predictions with ground truth
        labeled_predictions = [
            p for p in self.predictions
            if p.ground_truth is not None
        ]
        
        if len(labeled_predictions) < self.min_samples:
            logger.debug(
                f"Insufficient labeled samples: {len(labeled_predictions)} < {self.min_samples}"
            )
            return None
        
        correct = sum(
            1 for p in labeled_predictions
            if p.prediction == p.ground_truth
        )
        
        return correct / len(labeled_predictions)
    
    def calculate_confidence_calibration(self) -> Optional[float]:
        """
        Calculate confidence calibration score.
        
        Well-calibrated model: predictions with 90% confidence should be correct 90% of the time.
        
        Returns:
            Calibration error (lower is better, 0.0 = perfect calibration)
        """
        labeled_predictions = [
            p for p in self.predictions
            if p.ground_truth is not None
        ]
        
        if len(labeled_predictions) < self.min_samples:
            return None
        
        # Group predictions by confidence bins
        bins = {
            "0.0-0.2": [],
            "0.2-0.4": [],
            "0.4-0.6": [],
            "0.6-0.8": [],
            "0.8-1.0": []
        }
        
        for pred in labeled_predictions:
            if pred.confidence < 0.2:
                bins["0.0-0.2"].append(pred)
            elif pred.confidence < 0.4:
                bins["0.2-0.4"].append(pred)
            elif pred.confidence < 0.6:
                bins["0.4-0.6"].append(pred)
            elif pred.confidence < 0.8:
                bins["0.6-0.8"].append(pred)
            else:
                bins["0.8-1.0"].append(pred)
        
        # Calculate calibration error
        total_error = 0.0
        total_samples = 0
        
        for bin_name, preds in bins.items():
            if not preds:
                continue
            
            # Average confidence in this bin
            avg_confidence = statistics.mean(p.confidence for p in preds)
            
            # Actual accuracy in this bin
            accuracy = sum(1 for p in preds if p.prediction == p.ground_truth) / len(preds)
            
            # Calibration error = |confidence - accuracy|
            error = abs(avg_confidence - accuracy)
            total_error += error * len(preds)
            total_samples += len(preds)
        
        return total_error / total_samples if total_samples > 0 else None
    
    def detect_distribution_shift(self) -> Tuple[bool, str]:
        """
        Detect if prediction distribution has shifted.
        
        Example: Model used to predict 50% class A, 50% class B
        Now predicting 90% class A, 10% class B
        """
        if len(self.predictions) < self.min_samples:
            return False, ""
        
        # Count prediction distribution
        prediction_counts = {}
        for pred in self.predictions:
            prediction_counts[pred.prediction] = prediction_counts.get(pred.prediction, 0) + 1
        
        # Calculate entropy of distribution
        import math
        total = len(self.predictions)
        entropy = 0.0
        
        for count in prediction_counts.values():
            prob = count / total
            entropy -= prob * math.log2(prob)
        
        # Low entropy = predictions concentrated in few classes (possible shift)
        # High entropy = predictions spread across many classes
        
        # For binary classification, max entropy = 1.0
        # For 10 classes, max entropy = 3.32
        
        num_classes = len(prediction_counts)
        max_entropy = math.log2(num_classes) if num_classes > 1 else 1.0
        
        # If entropy is <50% of max, distribution is skewed
        if entropy < (max_entropy * 0.5):
            most_common = max(prediction_counts.items(), key=lambda x: x[1])
            return True, (
                f"Distribution shift detected: {most_common[1]/total:.1%} predictions "
                f"are '{most_common[0]}' (entropy: {entropy:.2f}/{max_entropy:.2f})"
            )
        
        return False, ""
    
    def detect_drift(self) -> DriftReport:
        """
        Detect if model has drifted from baseline.
        
        Returns:
            DriftReport with drift status and metrics
        """
        current_accuracy = self.calculate_current_accuracy()
        
        if current_accuracy is None:
            # Not enough data
            return DriftReport(
                drift_detected=False,
                baseline_accuracy=self.baseline_accuracy,
                current_accuracy=0.0,
                accuracy_drop=0.0,
                sample_size=len([p for p in self.predictions if p.ground_truth]),
                confidence_calibration=0.0,
                timestamp=datetime.now()
            )
        
        accuracy_drop = self.baseline_accuracy - current_accuracy
        drift_detected = accuracy_drop > self.drift_threshold
        
        calibration = self.calculate_confidence_calibration() or 0.0
        
        report = DriftReport(
            drift_detected=drift_detected,
            baseline_accuracy=self.baseline_accuracy,
            current_accuracy=current_accuracy,
            accuracy_drop=accuracy_drop,
            sample_size=len([p for p in self.predictions if p.ground_truth]),
            confidence_calibration=calibration,
            timestamp=datetime.now()
        )
        
        if drift_detected:
            logger.warning(f"🚨 MODEL DRIFT DETECTED: {self.agent_id}")
            logger.warning(f"  Baseline accuracy: {self.baseline_accuracy:.2%}")
            logger.warning(f"  Current accuracy: {current_accuracy:.2%}")
            logger.warning(f"  Drop: {accuracy_drop:.2%} (threshold: {self.drift_threshold:.2%})")
            logger.warning(f"  Sample size: {report.sample_size}")
        
        return report
    
    def trigger_retraining_alert(self, report: DriftReport):
        """Emit alert that model needs retraining"""
        alert = {
            "event_type": "model_drift_detected",
            "agent_id": self.agent_id,
            "baseline_accuracy": report.baseline_accuracy,
            "current_accuracy": report.current_accuracy,
            "accuracy_drop": report.accuracy_drop,
            "sample_size": report.sample_size,
            "confidence_calibration": report.confidence_calibration,
            "timestamp": report.timestamp.isoformat(),
            "action_required": "model_retraining"
        }
        
        print(json.dumps(alert))
        
        # In production, this would:
        # 1. Create Jira ticket for ML team
        # 2. Send Slack notification
        # 3. Update agent status to "needs_retraining"
        # 4. Optionally pause agent


# Example usage
if __name__ == "__main__":
    # Create detector for security agent
    detector = ModelDriftDetector(
        agent_id="security-agent",
        baseline_accuracy=0.95,  # 95% accuracy baseline
        drift_threshold=0.05,    # Alert if drops >5%
        window_size=100,
        min_samples=20
    )
    
    print("\n" + "="*80)
    print("MODEL DRIFT DETECTOR - TEST SUITE")
    print("="*80 + "\n")
    
    # Simulate normal performance
    print("Phase 1: Normal performance (95% accuracy)")
    for i in range(50):
        # 95% correct predictions
        is_correct = i % 20 != 0  # 19/20 = 95%
        detector.record_prediction(
            prediction="vulnerability_found" if is_correct else "no_vulnerability",
            ground_truth="vulnerability_found",
            confidence=0.92
        )
    
    report = detector.detect_drift()
    print(f"Drift detected: {report.drift_detected}")
    print(f"Current accuracy: {report.current_accuracy:.2%}")
    print(f"Accuracy drop: {report.accuracy_drop:.2%}")
    print()
    
    # Simulate performance degradation
    print("Phase 2: Performance degradation (85% accuracy)")
    for i in range(50):
        # 85% correct predictions
        is_correct = i % 7 < 6  # 6/7 ≈ 85%
        detector.record_prediction(
            prediction="vulnerability_found" if is_correct else "no_vulnerability",
            ground_truth="vulnerability_found",
            confidence=0.88
        )
    
    report = detector.detect_drift()
    print(f"Drift detected: {report.drift_detected}")
    print(f"Current accuracy: {report.current_accuracy:.2%}")
    print(f"Accuracy drop: {report.accuracy_drop:.2%}")
    print(f"Calibration error: {report.confidence_calibration:.3f}")
    
    if report.drift_detected:
        print("\n🚨 Triggering retraining alert...")
        detector.trigger_retraining_alert(report)
    
    print("\n" + "="*80)
    print("Test completed")
    print("="*80)
