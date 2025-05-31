"""
Módulo de monitoramento e métricas para a API
"""

import time
import logging
from functools import wraps
from typing import Dict, Any
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class APIMetrics:
    """Classe para coletar métricas da API"""
    
    def __init__(self):
        self.request_count = 0
        self.prediction_count = 0
        self.error_count = 0
        self.total_response_time = 0.0
        self.start_time = time.time()
        
    def increment_requests(self):
        """Incrementa contador de requests"""
        self.request_count += 1
        
    def increment_predictions(self):
        """Incrementa contador de predições"""
        self.prediction_count += 1
        
    def increment_errors(self):
        """Incrementa contador de erros"""
        self.error_count += 1
        
    def add_response_time(self, response_time: float):
        """Adiciona tempo de resposta"""
        self.total_response_time += response_time
        
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas atuais"""
        uptime = time.time() - self.start_time
        avg_response_time = (
            self.total_response_time / self.request_count 
            if self.request_count > 0 else 0
        )
        
        return {
            "uptime_seconds": round(uptime, 2),
            "total_requests": self.request_count,
            "total_predictions": self.prediction_count,
            "total_errors": self.error_count,
            "average_response_time_ms": round(avg_response_time * 1000, 2),
            "requests_per_second": round(self.request_count / uptime, 2) if uptime > 0 else 0,
            "error_rate": round(self.error_count / self.request_count * 100, 2) if self.request_count > 0 else 0
        }

# Instância global de métricas
metrics = APIMetrics()

def log_request(func):
    """Decorator para logar requests e coletar métricas"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        metrics.increment_requests()
        
        try:
            # Log do início da request
            logger.info(f"Starting {func.__name__}")
            
            # Executar função
            result = await func(*args, **kwargs)
            
            # Calcular tempo de resposta
            response_time = time.time() - start_time
            metrics.add_response_time(response_time)
            
            # Log de sucesso
            logger.info(f"Completed {func.__name__} in {response_time:.3f}s")
            
            return result
            
        except Exception as e:
            # Calcular tempo de resposta mesmo em caso de erro
            response_time = time.time() - start_time
            metrics.add_response_time(response_time)
            metrics.increment_errors()
            
            # Log de erro
            logger.error(f"Error in {func.__name__} after {response_time:.3f}s: {str(e)}")
            raise
            
    return wrapper

def log_prediction(func):
    """Decorator específico para logar predições"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        metrics.increment_predictions()
        
        try:
            result = await func(*args, **kwargs)
            
            response_time = time.time() - start_time
            
            # Log estruturado da predição
            prediction_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "function": func.__name__,
                "response_time_ms": round(response_time * 1000, 2),
                "predicted_class": result.predicted_class if hasattr(result, 'predicted_class') else None,
                "confidence": result.confidence if hasattr(result, 'confidence') else None,
                "status": "success"
            }
            
            logger.info(f"PREDICTION: {json.dumps(prediction_log)}")
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            # Log estruturado do erro
            error_log = {
                "timestamp": datetime.utcnow().isoformat(),
                "function": func.__name__,
                "response_time_ms": round(response_time * 1000, 2),
                "error": str(e),
                "status": "error"
            }
            
            logger.error(f"PREDICTION_ERROR: {json.dumps(error_log)}")
            raise
            
    return wrapper

def log_health_check():
    """Log para health checks"""
    health_log = {
        "timestamp": datetime.utcnow().isoformat(),
        "type": "health_check",
        "metrics": metrics.get_metrics()
    }
    
    logger.info(f"HEALTH: {json.dumps(health_log)}")

class StructuredLogger:
    """Logger estruturado para Cloud Logging"""
    
    @staticmethod
    def log_startup():
        """Log de inicialização da aplicação"""
        startup_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "application_startup",
            "message": "Eye Disease Classifier API starting up"
        }
        logger.info(f"STARTUP: {json.dumps(startup_log)}")
    
    @staticmethod
    def log_shutdown():
        """Log de encerramento da aplicação"""
        shutdown_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "application_shutdown",
            "message": "Eye Disease Classifier API shutting down",
            "final_metrics": metrics.get_metrics()
        }
        logger.info(f"SHUTDOWN: {json.dumps(shutdown_log)}")
    
    @staticmethod
    def log_model_load(success: bool, load_time: float = None, error: str = None):
        """Log de carregamento do modelo"""
        model_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "model_load",
            "success": success,
            "load_time_seconds": load_time,
            "error": error
        }
        
        if success:
            logger.info(f"MODEL_LOAD: {json.dumps(model_log)}")
        else:
            logger.error(f"MODEL_LOAD_ERROR: {json.dumps(model_log)}")

# Instância global do logger estruturado
structured_logger = StructuredLogger()
