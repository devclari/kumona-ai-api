"""
Gerenciador de download de modelos de múltiplas fontes
"""

import os
import requests
import logging
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)

class ModelDownloader:
    """Classe para gerenciar download de modelos de diferentes fontes"""
    
    def __init__(self, model_path: str = "best_model.keras"):
        self.model_path = model_path
        self.download_sources = [
            {
                "name": "Hugging Face",
                "url": "https://huggingface.co/devclari/eye-disease-classifier/resolve/main/best_model.keras",
                "method": self._download_from_url,
                "timeout": 300
            },
            {
                "name": "GitHub Releases",
                "url": "https://github.com/devclari/kumona-ai-api/releases/download/v1.0.0/best_model.keras",
                "method": self._download_from_url,
                "timeout": 300
            },
            {
                "name": "Direct URL",
                "url": "https://storage.googleapis.com/eye-disease-models/best_model.keras",
                "method": self._download_from_url,
                "timeout": 300
            },
            {
                "name": "Google Drive",
                "url": "https://drive.google.com/uc?id=1vSIfD3viT5JSxpG4asA8APCwK0JK9Dvu",
                "method": self._download_from_gdrive,
                "timeout": 600
            }
        ]
    
    def download_model(self) -> bool:
        """Tenta baixar o modelo de diferentes fontes"""
        try:
            if os.path.exists(self.model_path):
                file_size = os.path.getsize(self.model_path) / (1024 * 1024)
                logger.info(f"✅ Model already exists locally ({file_size:.1f} MB)")
                return True
            
            logger.info("🔽 Starting model download...")
            
            for source in self.download_sources:
                logger.info(f"🔄 Trying {source['name']}...")
                
                try:
                    start_time = time.time()
                    
                    if source["method"](source["url"], source.get("timeout", 300)):
                        download_time = time.time() - start_time
                        file_size = os.path.getsize(self.model_path) / (1024 * 1024)
                        
                        logger.info(f"✅ Model downloaded from {source['name']}")
                        logger.info(f"   Size: {file_size:.1f} MB")
                        logger.info(f"   Time: {download_time:.1f}s")
                        
                        return True
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to download from {source['name']}: {str(e)}")
                    # Limpar arquivo parcial se existir
                    if os.path.exists(self.model_path):
                        os.remove(self.model_path)
                    continue
            
            logger.error("❌ Failed to download model from all sources")
            return False
            
        except Exception as e:
            logger.error(f"❌ Error in model download: {str(e)}")
            return False
    
    def _download_from_url(self, url: str, timeout: int = 300) -> bool:
        """Download direto via requests com progress"""
        try:
            logger.info(f"📥 Downloading from: {url}")
            
            # Headers para evitar bloqueios
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, stream=True, timeout=timeout, headers=headers)
            response.raise_for_status()
            
            # Obter tamanho total se disponível
            total_size = int(response.headers.get('content-length', 0))
            
            downloaded = 0
            chunk_size = 8192
            
            with open(self.model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Log progress a cada 10MB
                        if downloaded % (10 * 1024 * 1024) == 0:
                            if total_size > 0:
                                progress = (downloaded / total_size) * 100
                                logger.info(f"📊 Progress: {progress:.1f}% ({downloaded / (1024*1024):.1f}MB)")
                            else:
                                logger.info(f"📊 Downloaded: {downloaded / (1024*1024):.1f}MB")
            
            # Verificar se o arquivo foi baixado corretamente
            if os.path.exists(self.model_path) and os.path.getsize(self.model_path) > 1024:
                return True
            else:
                logger.error("❌ Downloaded file is invalid or too small")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"❌ Download error: {str(e)}")
            return False
    
    def _download_from_gdrive(self, url: str, timeout: int = 600) -> bool:
        """Download via gdown (Google Drive)"""
        try:
            import gdown
            
            logger.info("📥 Downloading from Google Drive...")
            
            # Configurar timeout para gdown
            result = gdown.download(url, self.model_path, quiet=False)
            
            if result and os.path.exists(self.model_path):
                return True
            else:
                logger.error("❌ Google Drive download failed")
                return False
                
        except ImportError:
            logger.error("❌ gdown not installed, skipping Google Drive")
            return False
        except Exception as e:
            logger.error(f"❌ Google Drive error: {str(e)}")
            return False
    
    def add_download_source(self, name: str, url: str, method: str = "url", timeout: int = 300):
        """Adiciona uma nova fonte de download"""
        method_func = self._download_from_url if method == "url" else self._download_from_gdrive
        
        source = {
            "name": name,
            "url": url,
            "method": method_func,
            "timeout": timeout
        }
        
        # Adicionar no início da lista (prioridade)
        self.download_sources.insert(0, source)
        logger.info(f"✅ Added download source: {name}")
    
    def get_model_info(self) -> Optional[Dict]:
        """Retorna informações do modelo se existir"""
        if not os.path.exists(self.model_path):
            return None
        
        file_size = os.path.getsize(self.model_path)
        
        return {
            "path": self.model_path,
            "size_bytes": file_size,
            "size_mb": file_size / (1024 * 1024),
            "exists": True
        }

# Instância global
model_downloader = ModelDownloader()

# Função de conveniência
def download_model(model_path: str = "best_model.keras") -> bool:
    """Função simples para download do modelo"""
    downloader = ModelDownloader(model_path)
    return downloader.download_model()

# Configuração para diferentes ambientes
def setup_download_sources_for_production():
    """Configura fontes otimizadas para produção"""
    
    # Adicionar fontes rápidas para produção
    production_sources = [
        {
            "name": "CDN Primary",
            "url": "https://cdn.yourdomain.com/models/best_model.keras"
        },
        {
            "name": "AWS S3",
            "url": "https://your-bucket.s3.amazonaws.com/models/best_model.keras"
        },
        {
            "name": "Google Cloud Storage",
            "url": "https://storage.googleapis.com/your-bucket/models/best_model.keras"
        }
    ]
    
    for source in production_sources:
        model_downloader.add_download_source(
            name=source["name"],
            url=source["url"],
            method="url",
            timeout=180  # Timeout menor para produção
        )

if __name__ == "__main__":
    # Teste do downloader
    print("🧪 Testing model downloader...")
    
    if download_model():
        info = model_downloader.get_model_info()
        print(f"✅ Model downloaded successfully: {info}")
    else:
        print("❌ Model download failed")
