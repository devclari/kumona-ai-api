"""
Utilitários para integração com MLFlow
"""

import mlflow
import mlflow.tensorflow
import numpy as np
from typing import Dict, Any, Optional, List
import logging
import time
from datetime import datetime
import json
from functools import wraps

from mlflow_config import mlflow_manager

logger = logging.getLogger(__name__)

class MLFlowTracker:
    """Classe para tracking de predições e métricas"""
    
    def __init__(self):
        self.prediction_count = 0
        self.total_inference_time = 0.0
        self.confidence_scores = []
        self.class_predictions = []
    
    def track_prediction(self, 
                        predicted_class: str, 
                        confidence: float, 
                        inference_time: float,
                        all_predictions: Dict[str, float],
                        image_metadata: Optional[Dict[str, Any]] = None):
        """Tracka uma predição individual"""
        
        self.prediction_count += 1
        self.total_inference_time += inference_time
        self.confidence_scores.append(confidence)
        self.class_predictions.append(predicted_class)
        
        # Log métricas da predição
        metrics = {
            "inference_time_ms": inference_time * 1000,
            "confidence_score": confidence,
            "prediction_count": self.prediction_count
        }
        
        # Adicionar distribuição de classes
        for class_name, prob in all_predictions.items():
            metrics[f"prob_{class_name}"] = prob
        
        mlflow_manager.log_metrics(metrics)
        
        # Log parâmetros se fornecidos
        if image_metadata:
            mlflow_manager.log_params({
                f"image_{k}": v for k, v in image_metadata.items()
            })
        
        logger.info(f"📊 Predição trackada: {predicted_class} ({confidence:.2f}%)")
    
    def get_session_metrics(self) -> Dict[str, float]:
        """Obtém métricas da sessão atual"""
        if self.prediction_count == 0:
            return {}
        
        avg_inference_time = self.total_inference_time / self.prediction_count
        avg_confidence = np.mean(self.confidence_scores)
        
        # Distribuição de classes
        class_distribution = {}
        for class_name in set(self.class_predictions):
            count = self.class_predictions.count(class_name)
            class_distribution[f"class_dist_{class_name}"] = count / self.prediction_count
        
        metrics = {
            "session_total_predictions": self.prediction_count,
            "session_avg_inference_time_ms": avg_inference_time * 1000,
            "session_avg_confidence": avg_confidence,
            **class_distribution
        }
        
        return metrics
    
    def log_session_summary(self):
        """Loga resumo da sessão"""
        session_metrics = self.get_session_metrics()
        if session_metrics:
            mlflow_manager.log_metrics(session_metrics)
            logger.info(f"📈 Resumo da sessão logado: {self.prediction_count} predições")

# Instância global do tracker
mlflow_tracker = MLFlowTracker()

def mlflow_track_prediction(func):
    """Decorator para tracking automático de predições"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            # Executar função original
            result = await func(*args, **kwargs)
            
            # Calcular tempo de inferência
            inference_time = time.time() - start_time
            
            # Extrair dados da predição
            if hasattr(result, 'predicted_class') and hasattr(result, 'confidence'):
                predicted_class = result.predicted_class
                confidence = result.confidence
                all_predictions = getattr(result, 'all_predictions', {})
                
                # Trackar predição
                mlflow_tracker.track_prediction(
                    predicted_class=predicted_class,
                    confidence=confidence,
                    inference_time=inference_time,
                    all_predictions=all_predictions
                )
            
            return result
            
        except Exception as e:
            # Log erro
            mlflow_manager.log_metrics({
                "error_count": 1,
                "error_inference_time_ms": (time.time() - start_time) * 1000
            })
            
            mlflow_manager.log_params({
                "error_message": str(e),
                "error_timestamp": datetime.utcnow().isoformat()
            })
            
            raise
    
    return wrapper

def mlflow_track_health_check(func):
    """Decorator para tracking de health checks"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            
            # Log métricas de health check
            response_time = time.time() - start_time
            
            metrics = {
                "health_check_response_time_ms": response_time * 1000,
                "health_check_count": 1
            }
            
            if hasattr(result, 'model_loaded'):
                metrics["model_loaded"] = 1 if result.model_loaded else 0
            
            mlflow_manager.log_metrics(metrics)
            
            return result
            
        except Exception as e:
            mlflow_manager.log_metrics({
                "health_check_error_count": 1
            })
            raise
    
    return wrapper

class ModelPerformanceMonitor:
    """Monitor de performance do modelo"""
    
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.recent_predictions = []
        self.recent_confidences = []
        self.recent_times = []
    
    def add_prediction(self, predicted_class: str, confidence: float, inference_time: float):
        """Adiciona uma predição ao monitor"""
        self.recent_predictions.append(predicted_class)
        self.recent_confidences.append(confidence)
        self.recent_times.append(inference_time)
        
        # Manter apenas as últimas N predições
        if len(self.recent_predictions) > self.window_size:
            self.recent_predictions.pop(0)
            self.recent_confidences.pop(0)
            self.recent_times.pop(0)
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Calcula métricas de performance"""
        if not self.recent_predictions:
            return {}
        
        # Métricas básicas
        avg_confidence = np.mean(self.recent_confidences)
        avg_inference_time = np.mean(self.recent_times)
        std_confidence = np.std(self.recent_confidences)
        std_inference_time = np.std(self.recent_times)
        
        # Distribuição de classes
        class_counts = {}
        for pred in self.recent_predictions:
            class_counts[pred] = class_counts.get(pred, 0) + 1
        
        total_preds = len(self.recent_predictions)
        class_distribution = {
            f"recent_class_ratio_{k}": v / total_preds 
            for k, v in class_counts.items()
        }
        
        # Detectar possível drift (confiança muito baixa)
        low_confidence_ratio = sum(1 for c in self.recent_confidences if c < 70) / total_preds
        
        metrics = {
            "recent_avg_confidence": avg_confidence,
            "recent_avg_inference_time_ms": avg_inference_time * 1000,
            "recent_std_confidence": std_confidence,
            "recent_std_inference_time_ms": std_inference_time * 1000,
            "recent_low_confidence_ratio": low_confidence_ratio,
            "recent_prediction_count": total_preds,
            **class_distribution
        }
        
        return metrics
    
    def check_model_drift(self) -> Dict[str, Any]:
        """Verifica possível drift do modelo"""
        if len(self.recent_predictions) < self.window_size // 2:
            return {"drift_detected": False, "reason": "insufficient_data"}
        
        metrics = self.get_performance_metrics()
        
        # Critérios para detecção de drift
        drift_indicators = []
        
        # 1. Confiança média muito baixa
        if metrics.get("recent_avg_confidence", 100) < 60:
            drift_indicators.append("low_average_confidence")
        
        # 2. Muitas predições com baixa confiança
        if metrics.get("recent_low_confidence_ratio", 0) > 0.3:
            drift_indicators.append("high_low_confidence_ratio")
        
        # 3. Tempo de inferência muito alto (possível problema de performance)
        if metrics.get("recent_avg_inference_time_ms", 0) > 5000:  # 5 segundos
            drift_indicators.append("high_inference_time")
        
        # 4. Distribuição de classes muito desbalanceada
        class_ratios = [v for k, v in metrics.items() if k.startswith("recent_class_ratio_")]
        if class_ratios and max(class_ratios) > 0.8:
            drift_indicators.append("imbalanced_class_distribution")
        
        drift_detected = len(drift_indicators) > 0
        
        result = {
            "drift_detected": drift_detected,
            "indicators": drift_indicators,
            "metrics": metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Log resultado no MLFlow
        mlflow_manager.log_metrics({
            "drift_detected": 1 if drift_detected else 0,
            "drift_indicator_count": len(drift_indicators)
        })
        
        if drift_detected:
            mlflow_manager.log_params({
                "drift_indicators": json.dumps(drift_indicators),
                "drift_timestamp": result["timestamp"]
            })
            
            logger.warning(f"🚨 Possível drift detectado: {drift_indicators}")
        
        return result

# Instância global do monitor
performance_monitor = ModelPerformanceMonitor()

def setup_mlflow_for_api():
    """Configura MLFlow para a API"""
    try:
        # Iniciar run para a sessão da API
        run_tags = {
            "api_session": "true",
            "start_time": datetime.utcnow().isoformat()
        }
        
        mlflow_manager.start_run(
            run_name=f"api_session_{int(time.time())}",
            tags=run_tags
        )
        
        logger.info("✅ MLFlow configurado para API")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao configurar MLFlow para API: {str(e)}")
        return False

def cleanup_mlflow_for_api():
    """Limpa recursos do MLFlow ao encerrar API"""
    try:
        # Log resumo final da sessão
        mlflow_tracker.log_session_summary()
        
        # Log métricas finais de performance
        final_metrics = performance_monitor.get_performance_metrics()
        if final_metrics:
            mlflow_manager.log_metrics(final_metrics)
        
        # Finalizar run
        mlflow_manager.end_run()
        
        logger.info("✅ MLFlow cleanup concluído")
        
    except Exception as e:
        logger.error(f"❌ Erro no cleanup do MLFlow: {str(e)}")
