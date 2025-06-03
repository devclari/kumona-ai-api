import os
import numpy as np
# Importar configurações do TensorFlow primeiro
from tf_config import configure_tensorflow_for_cloud_run, get_tensorflow_info, optimize_model_for_inference

import tensorflow as tf
from keras.models import load_model
import gdown
from PIL import Image
import logging
from typing import Tuple, Dict, Optional
import time

# Importar MLFlow
from mlflow_config import mlflow_manager
from mlflow_utils import performance_monitor

# Importar downloader de modelos
from model_downloader import model_downloader

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLService:
    """Serviço para carregar modelo e fazer predições"""
    
    def __init__(self):
        self.model = None
        self.class_names = ['cataract', 'diabetic_retinopathy', 'glaucoma', 'normal']
        self.model_path = "best_model.keras"
        self.model_url = "https://drive.google.com/uc?id=1vSIfD3viT5JSxpG4asA8APCwK0JK9Dvu"
        self.is_loaded = False
        self.model_source = "local"  # "local" ou "mlflow"
        self.model_version = None

        # Log das configurações do TensorFlow
        tf_info = get_tensorflow_info()
        logger.info(f"TensorFlow configuration: {tf_info}")

        # Configurar MLFlow
        self._setup_mlflow_integration()

    def _setup_mlflow_integration(self):
        """Configura integração com MLFlow"""
        try:
            # Verificar se deve usar MLFlow registry
            if mlflow_manager.config.ENABLE_MODEL_REGISTRY:
                logger.info("🔄 MLFlow Model Registry habilitado")
                self.model_source = "mlflow"
            else:
                logger.info("📁 Usando modelo local")
                self.model_source = "local"

        except Exception as e:
            logger.warning(f"⚠️ Erro na configuração MLFlow, usando modelo local: {str(e)}")
            self.model_source = "local"

    def _load_model_from_mlflow(self) -> bool:
        """Carrega modelo do MLFlow registry"""
        try:
            logger.info("🔄 Tentando carregar modelo do MLFlow registry...")

            # Carregar modelo do registry
            model = mlflow_manager.load_model()

            if model is not None:
                self.model = model
                self.model_version = mlflow_manager.config.MODEL_VERSION or "latest"
                logger.info(f"✅ Modelo carregado do MLFlow registry (versão: {self.model_version})")

                # Log parâmetros do modelo no MLFlow
                mlflow_manager.log_params({
                    "model_source": "mlflow_registry",
                    "model_name": mlflow_manager.config.MLFLOW_MODEL_NAME,
                    "model_stage": mlflow_manager.config.MODEL_STAGE,
                    "model_version": self.model_version,
                    "class_names": str(self.class_names)
                })

                return True
            else:
                logger.warning("⚠️ Não foi possível carregar do MLFlow, tentando modelo local...")
                return False

        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo do MLFlow: {str(e)}")
            return False

    def _load_model_local(self) -> bool:
        """Carrega modelo local"""
        try:
            if not self.download_model():
                return False

            logger.info("✅ Carregando modelo local...")
            self.model = load_model(self.model_path)

            # Otimizar modelo para inferência
            self.model = optimize_model_for_inference(self.model)

            # Log parâmetros do modelo no MLFlow
            mlflow_manager.log_params({
                "model_source": "local_file",
                "model_path": self.model_path,
                "model_url": self.model_url,
                "class_names": str(self.class_names)
            })

            logger.info("✅ Modelo local carregado e otimizado com sucesso")
            return True

        except Exception as e:
            logger.error(f"❌ Erro ao carregar modelo local: {str(e)}")
            return False

    def download_model(self) -> bool:
        """Baixa o modelo usando o downloader multi-fonte"""
        try:
            return model_downloader.download_model()
        except Exception as e:
            logger.error(f"❌ Error downloading model: {str(e)}")
            return False
    
    def load_model(self) -> bool:
        """Carrega o modelo (MLFlow ou local)"""
        start_time = time.time()

        try:
            success = False

            # Tentar carregar do MLFlow primeiro se habilitado
            if self.model_source == "mlflow":
                success = self._load_model_from_mlflow()

                # Se falhar, tentar modelo local como fallback
                if not success:
                    logger.info("🔄 Fallback para modelo local...")
                    success = self._load_model_local()
            else:
                # Carregar modelo local diretamente
                success = self._load_model_local()

            if success:
                self.is_loaded = True
                load_time = time.time() - start_time

                # Log métricas de carregamento no MLFlow
                mlflow_manager.log_metrics({
                    "model_load_time_seconds": load_time,
                    "model_load_success": 1
                })

                logger.info(f"✅ Modelo carregado com sucesso em {load_time:.2f}s")
                return True
            else:
                self.is_loaded = False
                load_time = time.time() - start_time

                # Log falha no carregamento
                mlflow_manager.log_metrics({
                    "model_load_time_seconds": load_time,
                    "model_load_success": 0
                })

                logger.error("❌ Falha ao carregar modelo")
                return False

        except Exception as e:
            self.is_loaded = False
            load_time = time.time() - start_time

            # Log erro no carregamento
            mlflow_manager.log_metrics({
                "model_load_time_seconds": load_time,
                "model_load_success": 0
            })

            mlflow_manager.log_params({
                "model_load_error": str(e)
            })

            logger.error(f"❌ Erro ao carregar modelo: {str(e)}")
            return False
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """Preprocessa a imagem para predição"""
        try:
            # Redimensionar para 256x256
            img = image.resize((256, 256))
            
            # Converter para array numpy
            img_array = tf.keras.utils.img_to_array(img)
            
            # Expandir dimensões para batch
            img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
            
            return img_array
        except Exception as e:
            logger.error(f"❌ Error preprocessing image: {str(e)}")
            raise
    
    def predict(self, image: Image.Image) -> Tuple[str, float, Dict[str, float]]:
        """
        Faz predição na imagem com tracking MLFlow

        Args:
            image: Imagem PIL para classificação

        Returns:
            Tuple contendo (classe_predita, confiança, todas_predições)
        """
        start_time = time.time()

        try:
            if not self.is_loaded:
                raise ValueError("Model not loaded")

            # Preprocessar imagem
            img_array = self.preprocess_image(image)

            # Fazer predição
            predictions = self.model.predict(img_array, verbose=0)

            # Obter classe predita
            predicted_class_idx = np.argmax(predictions[0])
            predicted_class = self.class_names[predicted_class_idx]

            # Calcular confiança
            confidence = float(np.max(predictions[0]) * 100)

            # Criar dicionário com todas as predições
            all_predictions = {}
            for i, class_name in enumerate(self.class_names):
                all_predictions[class_name] = float(predictions[0][i] * 100)

            # Calcular tempo de inferência
            inference_time = time.time() - start_time

            # Adicionar ao monitor de performance
            performance_monitor.add_prediction(predicted_class, confidence, inference_time)

            # Log métricas no MLFlow
            mlflow_manager.log_metrics({
                "prediction_inference_time_ms": inference_time * 1000,
                "prediction_confidence": confidence,
                "prediction_count": 1
            })

            # Log distribuição de probabilidades
            prob_metrics = {f"prob_{class_name}": prob for class_name, prob in all_predictions.items()}
            mlflow_manager.log_metrics(prob_metrics)

            logger.info(f"Prediction: {predicted_class} with {confidence:.2f}% confidence (inference: {inference_time:.3f}s)")

            return predicted_class, confidence, all_predictions

        except Exception as e:
            inference_time = time.time() - start_time

            # Log erro no MLFlow
            mlflow_manager.log_metrics({
                "prediction_error_count": 1,
                "prediction_error_time_ms": inference_time * 1000
            })

            mlflow_manager.log_params({
                "prediction_error": str(e)
            })

            logger.error(f"❌ Error making prediction: {str(e)}")
            raise
    
    def is_model_loaded(self) -> bool:
        """Verifica se o modelo está carregado"""
        return self.is_loaded

# Instância global do serviço
ml_service = MLService()
