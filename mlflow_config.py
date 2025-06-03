"""
Configurações e utilitários para integração com MLFlow
"""

import os
import mlflow
import mlflow.tensorflow
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class MLFlowConfig:
    """Configurações para MLFlow"""
    
    # Configurações do servidor MLFlow
    MLFLOW_TRACKING_URI = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    MLFLOW_EXPERIMENT_NAME = os.getenv("MLFLOW_EXPERIMENT_NAME", "eye-disease-classifier")
    MLFLOW_MODEL_NAME = os.getenv("MLFLOW_MODEL_NAME", "eye-disease-model")
    
    # Configurações do modelo
    MODEL_STAGE = os.getenv("MODEL_STAGE", "Production")  # None, Staging, Production, Archived
    MODEL_VERSION = os.getenv("MODEL_VERSION", None)  # Se None, usa a versão mais recente do stage
    
    # Configurações de tracking
    ENABLE_TRACKING = os.getenv("ENABLE_MLFLOW_TRACKING", "false").lower() == "true"
    ENABLE_MODEL_REGISTRY = os.getenv("ENABLE_MODEL_REGISTRY", "false").lower() == "true"
    
    # Configurações de autenticação (se necessário)
    MLFLOW_USERNAME = os.getenv("MLFLOW_USERNAME", None)
    MLFLOW_PASSWORD = os.getenv("MLFLOW_PASSWORD", None)
    
    # Configurações de armazenamento
    MLFLOW_ARTIFACT_ROOT = os.getenv("MLFLOW_ARTIFACT_ROOT", "./mlruns")
    
    # Tags padrão para experimentos
    DEFAULT_TAGS = {
        "project": "eye-disease-classifier",
        "framework": "tensorflow",
        "api_version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "production")
    }

class MLFlowManager:
    """Gerenciador para operações do MLFlow"""
    
    def __init__(self):
        self.config = MLFlowConfig()
        self.experiment_id = None
        self.run_id = None

        # Só configurar MLFlow se estiver habilitado
        if self.config.ENABLE_TRACKING:
            try:
                self._setup_mlflow()
            except Exception as e:
                logger.error(f"❌ Erro ao configurar MLFlow: {str(e)}")
                logger.warning("⚠️ Desabilitando MLFlow devido ao erro")
                self.config.ENABLE_TRACKING = False
    
    def _setup_mlflow(self):
        """Configura o MLFlow"""
        try:
            # Configurar URI de tracking
            mlflow.set_tracking_uri(self.config.MLFLOW_TRACKING_URI)
            
            # Configurar autenticação se necessário
            if self.config.MLFLOW_USERNAME and self.config.MLFLOW_PASSWORD:
                os.environ["MLFLOW_TRACKING_USERNAME"] = self.config.MLFLOW_USERNAME
                os.environ["MLFLOW_TRACKING_PASSWORD"] = self.config.MLFLOW_PASSWORD
            
            # Criar ou obter experimento
            if self.config.ENABLE_TRACKING:
                self._setup_experiment()
            
            logger.info(f"✅ MLFlow configurado com sucesso. URI: {self.config.MLFLOW_TRACKING_URI}")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar MLFlow: {str(e)}")
            raise
    
    def _setup_experiment(self):
        """Configura o experimento do MLFlow"""
        try:
            # Verificar se o experimento existe
            experiment = mlflow.get_experiment_by_name(self.config.MLFLOW_EXPERIMENT_NAME)
            
            if experiment is None:
                # Criar novo experimento
                self.experiment_id = mlflow.create_experiment(
                    name=self.config.MLFLOW_EXPERIMENT_NAME,
                    artifact_location=self.config.MLFLOW_ARTIFACT_ROOT,
                    tags=self.config.DEFAULT_TAGS
                )
                logger.info(f"✅ Experimento criado: {self.config.MLFLOW_EXPERIMENT_NAME}")
            else:
                self.experiment_id = experiment.experiment_id
                logger.info(f"✅ Experimento encontrado: {self.config.MLFLOW_EXPERIMENT_NAME}")
            
            # Definir experimento ativo
            mlflow.set_experiment(self.config.MLFLOW_EXPERIMENT_NAME)
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar experimento: {str(e)}")
            raise
    
    def start_run(self, run_name: Optional[str] = None, tags: Optional[Dict[str, str]] = None):
        """Inicia uma nova run do MLFlow"""
        if not self.config.ENABLE_TRACKING:
            return None
        
        try:
            # Combinar tags padrão com tags customizadas
            all_tags = self.config.DEFAULT_TAGS.copy()
            if tags:
                all_tags.update(tags)
            
            # Iniciar run
            run = mlflow.start_run(
                experiment_id=self.experiment_id,
                run_name=run_name,
                tags=all_tags
            )
            
            self.run_id = run.info.run_id
            logger.info(f"✅ MLFlow run iniciada: {self.run_id}")
            
            return run
            
        except Exception as e:
            logger.error(f"❌ Erro ao iniciar run: {str(e)}")
            return None
    
    def end_run(self, status: str = "FINISHED"):
        """Finaliza a run atual"""
        if not self.config.ENABLE_TRACKING or not self.run_id:
            return
        
        try:
            mlflow.end_run(status=status)
            logger.info(f"✅ MLFlow run finalizada: {self.run_id}")
            self.run_id = None
            
        except Exception as e:
            logger.error(f"❌ Erro ao finalizar run: {str(e)}")
    
    def log_metrics(self, metrics: Dict[str, float], step: Optional[int] = None):
        """Loga métricas no MLFlow"""
        if not self.config.ENABLE_TRACKING or not self.run_id:
            return
        
        try:
            for key, value in metrics.items():
                mlflow.log_metric(key, value, step=step)
            
        except Exception as e:
            logger.error(f"❌ Erro ao logar métricas: {str(e)}")
    
    def log_params(self, params: Dict[str, Any]):
        """Loga parâmetros no MLFlow"""
        if not self.config.ENABLE_TRACKING or not self.run_id:
            return
        
        try:
            mlflow.log_params(params)
            
        except Exception as e:
            logger.error(f"❌ Erro ao logar parâmetros: {str(e)}")
    
    def log_artifacts(self, local_path: str, artifact_path: Optional[str] = None):
        """Loga artefatos no MLFlow"""
        if not self.config.ENABLE_TRACKING or not self.run_id:
            return
        
        try:
            mlflow.log_artifacts(local_path, artifact_path)
            
        except Exception as e:
            logger.error(f"❌ Erro ao logar artefatos: {str(e)}")
    
    def get_model_uri(self) -> Optional[str]:
        """Obtém URI do modelo do registry"""
        if not self.config.ENABLE_MODEL_REGISTRY:
            return None
        
        try:
            if self.config.MODEL_VERSION:
                # Versão específica
                model_uri = f"models:/{self.config.MLFLOW_MODEL_NAME}/{self.config.MODEL_VERSION}"
            else:
                # Versão mais recente do stage
                model_uri = f"models:/{self.config.MLFLOW_MODEL_NAME}/{self.config.MODEL_STAGE}"
            
            logger.info(f"✅ URI do modelo: {model_uri}")
            return model_uri
            
        except Exception as e:
            logger.error(f"❌ Erro ao obter URI do modelo: {str(e)}")
            return None
    
    def load_model(self):
        """Carrega modelo do MLFlow registry"""
        model_uri = self.get_model_uri()
        if not model_uri:
            return None
        
        try:
            model = mlflow.tensorflow.load_model(model_uri)
            logger.info(f"✅ Modelo carregado do MLFlow: {model_uri}")
            return model
            
        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo do MLFlow: {str(e)}")
            return None
    
    def register_model(self, model_path: str, model_name: Optional[str] = None) -> bool:
        """Registra modelo no MLFlow registry"""
        if not self.config.ENABLE_MODEL_REGISTRY:
            return False
        
        model_name = model_name or self.config.MLFLOW_MODEL_NAME
        
        try:
            # Registrar modelo
            model_version = mlflow.register_model(
                model_uri=f"runs:/{self.run_id}/{model_path}",
                name=model_name
            )
            
            logger.info(f"✅ Modelo registrado: {model_name} v{model_version.version}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Erro ao registrar modelo: {str(e)}")
            return False

# Instância global do gerenciador MLFlow
mlflow_manager = MLFlowManager()
