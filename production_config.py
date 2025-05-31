"""
Configurações específicas para ambiente de produção
"""

import os
from typing import Dict, Any

class ProductionConfig:
    """Configurações para ambiente de produção"""
    
    # Configurações da aplicação
    APP_NAME = "eye-disease-classifier"
    VERSION = "1.0.0"
    ENVIRONMENT = "production"
    
    # Configurações do servidor
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8080))
    
    # Configurações de logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Configurações do modelo
    MODEL_PATH = "best_model.keras"
    MODEL_URL = "https://drive.google.com/uc?id=1vSIfD3viT5JSxpG4asA8APCwK0JK9Dvu"
    
    # Configurações de recursos
    MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
    SUPPORTED_FORMATS = {"jpg", "jpeg", "png"}
    
    # Configurações de timeout
    REQUEST_TIMEOUT = 300  # 5 minutos
    MODEL_LOAD_TIMEOUT = 600  # 10 minutos
    
    # Configurações de cache
    ENABLE_CACHE = True
    CACHE_TTL = 3600  # 1 hora
    
    # Configurações de segurança
    CORS_ORIGINS = ["*"]  # Em produção, especificar domínios específicos
    CORS_METHODS = ["GET", "POST"]
    CORS_HEADERS = ["*"]
    
    # Configurações do TensorFlow
    TF_CONFIG = {
        "TF_CPP_MIN_LOG_LEVEL": "2",
        "TF_ENABLE_ONEDNN_OPTS": "0",
        "TF_FORCE_GPU_ALLOW_GROWTH": "true",
        "OMP_NUM_THREADS": "2",
        "TF_NUM_INTEROP_THREADS": "2",
        "TF_NUM_INTRAOP_THREADS": "2"
    }
    
    # Configurações de monitoramento
    ENABLE_METRICS = True
    METRICS_ENDPOINT = "/metrics"
    HEALTH_ENDPOINT = "/health"
    
    @classmethod
    def get_tf_env_vars(cls) -> Dict[str, str]:
        """Retorna variáveis de ambiente do TensorFlow"""
        return cls.TF_CONFIG
    
    @classmethod
    def apply_tf_config(cls):
        """Aplica configurações do TensorFlow"""
        for key, value in cls.TF_CONFIG.items():
            os.environ[key] = value
    
    @classmethod
    def get_uvicorn_config(cls) -> Dict[str, Any]:
        """Retorna configurações do Uvicorn"""
        return {
            "host": cls.HOST,
            "port": cls.PORT,
            "reload": False,
            "log_level": cls.LOG_LEVEL.lower(),
            "access_log": True,
            "timeout_keep_alive": 30,
            "timeout_graceful_shutdown": 30
        }
    
    @classmethod
    def get_fastapi_config(cls) -> Dict[str, Any]:
        """Retorna configurações do FastAPI"""
        return {
            "title": "Eye Disease Classifier API",
            "description": """
            API para classificação de doenças oculares usando deep learning.
            
            Esta API pode detectar as seguintes condições:
            - **Catarata** (cataract)
            - **Retinopatia Diabética** (diabetic_retinopathy) 
            - **Glaucoma** (glaucoma)
            - **Normal** (normal)
            
            ## Como usar:
            1. Faça upload de uma imagem do olho usando o endpoint `/predict`
            2. A API retornará a classificação e a confiança da predição
            
            ## Formatos suportados:
            - JPEG (.jpg, .jpeg)
            - PNG (.png)
            """,
            "version": cls.VERSION,
            "contact": {
                "name": "Eye Disease Classifier API",
                "email": "support@example.com",
            },
            "license_info": {
                "name": "MIT",
            },
            "docs_url": "/docs",
            "redoc_url": "/redoc",
            "openapi_url": "/openapi.json"
        }
    
    @classmethod
    def get_cors_config(cls) -> Dict[str, Any]:
        """Retorna configurações do CORS"""
        return {
            "allow_origins": cls.CORS_ORIGINS,
            "allow_credentials": True,
            "allow_methods": cls.CORS_METHODS,
            "allow_headers": cls.CORS_HEADERS,
        }

class DevelopmentConfig(ProductionConfig):
    """Configurações para ambiente de desenvolvimento"""
    
    ENVIRONMENT = "development"
    LOG_LEVEL = "DEBUG"
    CORS_ORIGINS = ["http://localhost:3000", "http://localhost:8080"]
    
    @classmethod
    def get_uvicorn_config(cls) -> Dict[str, Any]:
        """Retorna configurações do Uvicorn para desenvolvimento"""
        config = super().get_uvicorn_config()
        config.update({
            "reload": True,
            "log_level": "debug"
        })
        return config

def get_config() -> ProductionConfig:
    """Retorna configuração baseada no ambiente"""
    env = os.getenv("ENVIRONMENT", "production").lower()
    
    if env == "development":
        return DevelopmentConfig()
    else:
        return ProductionConfig()

# Aplicar configurações do TensorFlow na importação
config = get_config()
config.apply_tf_config()
