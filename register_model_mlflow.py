#!/usr/bin/env python3
"""
Script para registrar o modelo atual no MLFlow Registry
"""

import mlflow
import mlflow.tensorflow
import numpy as np
import os
import sys
import logging
from keras.models import load_model
import gdown
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_mlflow(tracking_uri="http://localhost:5000", experiment_name="eye-disease-classifier"):
    """Configura MLFlow"""
    try:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_experiment(experiment_name)
        logger.info(f"✅ MLFlow configurado: {tracking_uri}")
        return True
    except Exception as e:
        logger.error(f"❌ Erro ao configurar MLFlow: {e}")
        return False

def download_model_if_needed(model_path="best_model.keras"):
    """Baixa o modelo se não existir"""
    if not os.path.exists(model_path):
        logger.info("🔽 Baixando modelo...")
        model_url = "https://drive.google.com/uc?id=1vSIfD3viT5JSxpG4asA8APCwK0JK9Dvu"
        try:
            gdown.download(model_url, model_path, quiet=False)
            logger.info("✅ Modelo baixado com sucesso")
            return True
        except Exception as e:
            logger.error(f"❌ Erro ao baixar modelo: {e}")
            return False
    else:
        logger.info("✅ Modelo já existe localmente")
        return True

def create_model_signature(model):
    """Cria assinatura do modelo para MLFlow"""
    try:
        # Criar dados de exemplo para inferir a assinatura
        sample_input = np.random.random((1, 256, 256, 3)).astype(np.float32)
        sample_output = model.predict(sample_input, verbose=0)
        
        signature = mlflow.models.infer_signature(sample_input, sample_output)
        logger.info("✅ Assinatura do modelo criada")
        return signature
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível criar assinatura: {e}")
        return None

def register_model(model_path="best_model.keras", 
                  model_name="eye-disease-model",
                  description=None,
                  tags=None):
    """Registra o modelo no MLFlow Registry"""
    
    try:
        # Carregar modelo
        logger.info(f"📂 Carregando modelo: {model_path}")
        model = load_model(model_path)
        logger.info("✅ Modelo carregado com sucesso")
        
        # Informações do modelo
        model_info = {
            "model_type": "tensorflow/keras",
            "input_shape": str(model.input_shape),
            "output_shape": str(model.output_shape),
            "total_params": model.count_params(),
            "trainable_params": sum([np.prod(v.get_shape()) for v in model.trainable_weights]),
            "classes": ["cataract", "diabetic_retinopathy", "glaucoma", "normal"],
            "preprocessing": "resize_256x256_normalize",
            "framework_version": "tensorflow>=2.12.0"
        }
        
        # Tags padrão
        default_tags = {
            "model_type": "image_classification",
            "domain": "medical",
            "task": "eye_disease_detection",
            "framework": "tensorflow",
            "registered_at": datetime.utcnow().isoformat(),
            "version": "1.0.0"
        }
        
        if tags:
            default_tags.update(tags)
        
        # Descrição padrão
        if not description:
            description = """
            Modelo de classificação de doenças oculares treinado para detectar:
            - Catarata (cataract)
            - Retinopatia Diabética (diabetic_retinopathy) 
            - Glaucoma (glaucoma)
            - Olhos Normais (normal)
            
            Input: Imagens RGB 256x256
            Output: Probabilidades para 4 classes
            """
        
        # Criar assinatura
        signature = create_model_signature(model)
        
        # Iniciar run do MLFlow
        with mlflow.start_run(run_name=f"model_registration_{int(datetime.now().timestamp())}") as run:
            
            # Log parâmetros do modelo
            mlflow.log_params(model_info)
            
            # Log métricas básicas
            mlflow.log_metrics({
                "model_size_mb": os.path.getsize(model_path) / (1024 * 1024),
                "total_parameters": model_info["total_params"],
                "trainable_parameters": model_info["trainable_params"]
            })
            
            # Log artefatos adicionais
            with open("model_info.txt", "w") as f:
                f.write(f"Model Information\n")
                f.write(f"================\n")
                for key, value in model_info.items():
                    f.write(f"{key}: {value}\n")
            
            mlflow.log_artifact("model_info.txt")
            
            # Registrar modelo
            logger.info(f"📝 Registrando modelo: {model_name}")
            
            model_version = mlflow.tensorflow.log_model(
                model=model,
                artifact_path="model",
                registered_model_name=model_name,
                signature=signature,
                description=description,
                tags=default_tags
            )
            
            run_id = run.info.run_id
            
            logger.info(f"✅ Modelo registrado com sucesso!")
            logger.info(f"   Nome: {model_name}")
            logger.info(f"   Run ID: {run_id}")
            logger.info(f"   URI: runs:/{run_id}/model")
            
            return {
                "model_name": model_name,
                "run_id": run_id,
                "model_uri": f"runs:/{run_id}/model",
                "registry_uri": f"models:/{model_name}/1"
            }
            
    except Exception as e:
        logger.error(f"❌ Erro ao registrar modelo: {e}")
        return None

def promote_model_to_production(model_name="eye-disease-model", version=1):
    """Promove modelo para produção"""
    try:
        from mlflow.tracking import MlflowClient
        
        client = MlflowClient()
        
        # Promover para Production
        client.transition_model_version_stage(
            name=model_name,
            version=version,
            stage="Production",
            archive_existing_versions=True
        )
        
        logger.info(f"✅ Modelo {model_name} v{version} promovido para Production")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao promover modelo: {e}")
        return False

def test_model_loading(model_name="eye-disease-model", stage="Production"):
    """Testa carregamento do modelo do registry"""
    try:
        model_uri = f"models:/{model_name}/{stage}"
        logger.info(f"🧪 Testando carregamento: {model_uri}")
        
        model = mlflow.tensorflow.load_model(model_uri)
        
        # Teste básico
        test_input = np.random.random((1, 256, 256, 3)).astype(np.float32)
        prediction = model.predict(test_input, verbose=0)
        
        logger.info(f"✅ Modelo carregado e testado com sucesso")
        logger.info(f"   Shape de saída: {prediction.shape}")
        logger.info(f"   Soma das probabilidades: {prediction.sum():.4f}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao testar modelo: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Registro de Modelo no MLFlow Registry")
    print("=" * 50)
    
    # Configurar MLFlow
    if not setup_mlflow():
        sys.exit(1)
    
    # Baixar modelo se necessário
    if not download_model_if_needed():
        sys.exit(1)
    
    # Registrar modelo
    result = register_model()
    if not result:
        sys.exit(1)
    
    # Promover para produção
    if promote_model_to_production():
        logger.info("🎯 Modelo promovido para Production")
    
    # Testar carregamento
    if test_model_loading():
        logger.info("🧪 Teste de carregamento bem-sucedido")
    
    print("\n" + "=" * 50)
    print("✅ REGISTRO CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print(f"📋 Informações do modelo:")
    print(f"   Nome: {result['model_name']}")
    print(f"   Run ID: {result['run_id']}")
    print(f"   URI do Registry: {result['registry_uri']}")
    print(f"\n🌐 Acesse o MLFlow UI para ver detalhes:")
    print(f"   http://localhost:5000")
    print(f"\n🚀 Para fazer deploy:")
    print(f"   mlflow models serve --model-uri {result['registry_uri']} --port 8001")
    print(f"\n⚙️ Para usar na API:")
    print(f"   export ENABLE_MODEL_REGISTRY=true")
    print(f"   export MODEL_STAGE=Production")

if __name__ == "__main__":
    main()
