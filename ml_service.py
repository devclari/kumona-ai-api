import os
import numpy as np
# Importar configurações do TensorFlow primeiro
from tf_config import configure_tensorflow_for_cloud_run, get_tensorflow_info, optimize_model_for_inference

import tensorflow as tf
from keras.models import load_model
import gdown
from PIL import Image
import logging
from typing import Tuple, Dict

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
        # Log das configurações do TensorFlow
        tf_info = get_tensorflow_info()
        logger.info(f"TensorFlow configuration: {tf_info}")

    def download_model(self) -> bool:
        """Baixa o modelo se não existir"""
        try:
            if not os.path.exists(self.model_path):
                logger.info("🔽 Downloading model...")
                gdown.download(self.model_url, self.model_path, quiet=False)
                logger.info("✅ Model downloaded successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error downloading model: {str(e)}")
            return False
    
    def load_model(self) -> bool:
        """Carrega o modelo"""
        try:
            if not self.download_model():
                return False
                
            logger.info("✅ Loading model...")
            self.model = load_model(self.model_path)

            # Otimizar modelo para inferência
            self.model = optimize_model_for_inference(self.model)

            self.is_loaded = True
            logger.info("✅ Model loaded and optimized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error loading model: {str(e)}")
            self.is_loaded = False
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
        Faz predição na imagem
        
        Returns:
            Tuple contendo (classe_predita, confiança, todas_predições)
        """
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
            
            logger.info(f"Prediction: {predicted_class} with {confidence:.2f}% confidence")
            
            return predicted_class, confidence, all_predictions
            
        except Exception as e:
            logger.error(f"❌ Error making prediction: {str(e)}")
            raise
    
    def is_model_loaded(self) -> bool:
        """Verifica se o modelo está carregado"""
        return self.is_loaded

# Instância global do serviço
ml_service = MLService()
