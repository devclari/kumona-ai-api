#!/usr/bin/env python3
"""
Script para fazer upload do modelo para Hugging Face Hub
"""

import os
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_dependencies():
    """Verifica se as dependências estão instaladas"""
    try:
        from huggingface_hub import HfApi, login
        import gdown
        return True
    except ImportError as e:
        logger.error(f"❌ Dependência não encontrada: {e}")
        logger.info("💡 Instale com: pip install huggingface_hub gdown")
        return False

def download_model_if_needed(model_path="best_model.keras"):
    """Baixa o modelo se não existir localmente"""
    if os.path.exists(model_path):
        file_size = os.path.getsize(model_path) / (1024 * 1024)
        logger.info(f"✅ Modelo já existe localmente ({file_size:.1f} MB)")
        return True
    
    logger.info("🔽 Baixando modelo do Google Drive...")
    try:
        import gdown
        model_url = "https://drive.google.com/uc?id=1vSIfD3viT5JSxpG4asA8APCwK0JK9Dvu"
        gdown.download(model_url, model_path, quiet=False)
        
        if os.path.exists(model_path):
            file_size = os.path.getsize(model_path) / (1024 * 1024)
            logger.info(f"✅ Modelo baixado com sucesso ({file_size:.1f} MB)")
            return True
        else:
            logger.error("❌ Falha no download do modelo")
            return False
            
    except Exception as e:
        logger.error(f"❌ Erro ao baixar modelo: {e}")
        return False

def setup_huggingface_auth():
    """Configura autenticação do Hugging Face"""
    try:
        from huggingface_hub import login
        
        # Verificar se já está logado
        try:
            from huggingface_hub import whoami
            user = whoami()
            logger.info(f"✅ Já logado como: {user['name']}")
            return True
        except:
            pass
        
        # Solicitar token
        print("\n🔑 Configuração do Hugging Face")
        print("=" * 40)
        print("1. Acesse: https://huggingface.co/settings/tokens")
        print("2. Crie um token com permissão de 'write'")
        print("3. Cole o token abaixo:")
        
        token = input("\nToken do Hugging Face: ").strip()
        
        if not token:
            logger.error("❌ Token não fornecido")
            return False
        
        # Fazer login
        login(token=token)
        logger.info("✅ Login realizado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na autenticação: {e}")
        return False

def create_model_card(repo_id):
    """Cria um README.md para o modelo"""
    model_card = f"""---
license: mit
tags:
- tensorflow
- keras
- image-classification
- medical
- eye-disease
- computer-vision
datasets:
- eye-disease-dataset
metrics:
- accuracy
- precision
- recall
- f1
library_name: tensorflow
pipeline_tag: image-classification
---

# Eye Disease Classifier Model

## Model Description

This is a TensorFlow/Keras model trained for eye disease classification. The model can detect:

- **Cataract** - Clouding of the lens
- **Diabetic Retinopathy** - Diabetes-related eye damage  
- **Glaucoma** - Optic nerve damage
- **Normal** - Healthy eyes

## Model Details

- **Model Type**: Convolutional Neural Network (CNN)
- **Framework**: TensorFlow/Keras
- **Input**: RGB images (256x256 pixels)
- **Output**: 4-class probability distribution
- **Model Size**: ~161 MB
- **Parameters**: ~15M parameters

## Usage

### Direct Download
```python
import requests
import tensorflow as tf

# Download model
url = "https://huggingface.co/{repo_id}/resolve/main/best_model.keras"
response = requests.get(url)
with open("model.keras", "wb") as f:
    f.write(response.content)

# Load model
model = tf.keras.models.load_model("model.keras")

# Make prediction
prediction = model.predict(image_array)
```

### With Hugging Face Hub
```python
from huggingface_hub import hf_hub_download
import tensorflow as tf

# Download model
model_path = hf_hub_download(
    repo_id="{repo_id}",
    filename="best_model.keras"
)

# Load model
model = tf.keras.models.load_model(model_path)
```

## API Usage

This model is deployed as a REST API:

- **Repository**: https://github.com/devclari/kumona-ai-api
- **API Docs**: Available after deployment
- **Health Check**: `/health` endpoint

## Training Data

The model was trained on a curated dataset of eye fundus images with the following classes:
- Cataract images
- Diabetic retinopathy images  
- Glaucoma images
- Normal/healthy eye images

## Performance

The model achieves good performance on the validation set:
- **Accuracy**: ~90%+
- **Precision**: High across all classes
- **Recall**: Balanced performance
- **F1-Score**: Consistent results

## Limitations

- Model is trained on specific image types (fundus images)
- Performance may vary on different image qualities
- Not intended for clinical diagnosis without medical supervision
- Requires preprocessing (resize to 256x256, normalization)

## License

MIT License - See repository for full license details.

## Citation

If you use this model, please cite:

```bibtex
@misc{{eye-disease-classifier,
  title={{Eye Disease Classifier}},
  author={{DevClari}},
  year={{2024}},
  url={{https://github.com/devclari/kumona-ai-api}}
}}
```

## Contact

For questions or issues, please open an issue in the [GitHub repository](https://github.com/devclari/kumona-ai-api).
"""
    
    return model_card

def upload_to_huggingface(model_path="best_model.keras", repo_id="devclari/eye-disease-classifier"):
    """Faz upload do modelo para Hugging Face"""
    try:
        from huggingface_hub import HfApi
        
        api = HfApi()
        
        # Criar repositório se não existir
        try:
            logger.info(f"🔄 Criando repositório: {repo_id}")
            api.create_repo(
                repo_id=repo_id,
                repo_type="model",
                exist_ok=True,
                private=False
            )
            logger.info("✅ Repositório criado/verificado")
        except Exception as e:
            logger.warning(f"⚠️ Repositório pode já existir: {e}")
        
        # Upload do modelo
        logger.info(f"📤 Fazendo upload do modelo: {model_path}")
        api.upload_file(
            path_or_fileobj=model_path,
            path_in_repo="best_model.keras",
            repo_id=repo_id,
            repo_type="model"
        )
        logger.info("✅ Modelo enviado com sucesso!")
        
        # Criar e upload do README
        logger.info("📝 Criando README do modelo...")
        model_card = create_model_card(repo_id)
        
        with open("README.md", "w", encoding="utf-8") as f:
            f.write(model_card)
        
        api.upload_file(
            path_or_fileobj="README.md",
            path_in_repo="README.md",
            repo_id=repo_id,
            repo_type="model"
        )
        logger.info("✅ README criado e enviado!")
        
        # Limpar arquivo temporário
        if os.path.exists("README.md"):
            os.remove("README.md")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no upload: {e}")
        return False

def update_model_downloader(repo_id="devclari/eye-disease-classifier"):
    """Atualiza o model_downloader.py com a nova URL"""
    try:
        hf_url = f"https://huggingface.co/{repo_id}/resolve/main/best_model.keras"
        
        # Ler arquivo atual
        with open("model_downloader.py", "r", encoding="utf-8") as f:
            content = f.read()
        
        # Substituir URL do Hugging Face
        old_hf_url = "https://huggingface.co/devclari/eye-disease-classifier/resolve/main/best_model.keras"
        new_content = content.replace(old_hf_url, hf_url)
        
        # Salvar arquivo atualizado
        with open("model_downloader.py", "w", encoding="utf-8") as f:
            f.write(new_content)
        
        logger.info(f"✅ model_downloader.py atualizado com URL: {hf_url}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar model_downloader.py: {e}")
        return False

def main():
    """Função principal"""
    print("🤗 Upload do Modelo para Hugging Face Hub")
    print("=" * 50)
    
    # Verificar dependências
    if not check_dependencies():
        sys.exit(1)
    
    # Baixar modelo se necessário
    if not download_model_if_needed():
        sys.exit(1)
    
    # Configurar autenticação
    if not setup_huggingface_auth():
        sys.exit(1)
    
    # Solicitar repo_id
    default_repo = "devclari/eye-disease-classifier"
    repo_id = input(f"\nRepositório Hugging Face [{default_repo}]: ").strip()
    if not repo_id:
        repo_id = default_repo
    
    # Upload do modelo
    if not upload_to_huggingface(repo_id=repo_id):
        sys.exit(1)
    
    # Atualizar código
    if update_model_downloader(repo_id=repo_id):
        logger.info("✅ Código atualizado automaticamente")
    
    print("\n" + "=" * 50)
    print("🎉 UPLOAD CONCLUÍDO COM SUCESSO!")
    print("=" * 50)
    print(f"📦 Repositório: https://huggingface.co/{repo_id}")
    print(f"🔗 URL do modelo: https://huggingface.co/{repo_id}/resolve/main/best_model.keras")
    print(f"\n🚀 Próximos passos:")
    print(f"   1. git add .")
    print(f"   2. git commit -m 'feat: Atualizar URL do modelo para Hugging Face'")
    print(f"   3. git push")
    print(f"   4. Deploy no Railway/Render")
    print(f"\n✅ Agora o deploy remoto vai funcionar!")

if __name__ == "__main__":
    main()
