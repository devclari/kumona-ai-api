#!/usr/bin/env python3
"""
Script para fazer deploy da API usando MLFlow
"""

import os
import sys
import subprocess
import time
import requests
import json
import logging
from typing import Dict, Any, Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLFlowDeployer:
    """Classe para gerenciar deploys via MLFlow"""
    
    def __init__(self, 
                 mlflow_uri: str = "http://localhost:5000",
                 model_name: str = "eye-disease-model",
                 model_stage: str = "Production"):
        self.mlflow_uri = mlflow_uri
        self.model_name = model_name
        self.model_stage = model_stage
        self.model_uri = f"models:/{model_name}/{model_stage}"
        
    def check_mlflow_connection(self) -> bool:
        """Verifica conexão com MLFlow"""
        try:
            response = requests.get(f"{self.mlflow_uri}/health", timeout=10)
            if response.status_code == 200:
                logger.info("✅ MLFlow está acessível")
                return True
            else:
                logger.error(f"❌ MLFlow retornou status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Erro ao conectar com MLFlow: {e}")
            return False
    
    def check_model_exists(self) -> bool:
        """Verifica se o modelo existe no registry"""
        try:
            import mlflow
            mlflow.set_tracking_uri(self.mlflow_uri)
            
            # Tentar carregar modelo
            model = mlflow.tensorflow.load_model(self.model_uri)
            logger.info(f"✅ Modelo encontrado: {self.model_uri}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Modelo não encontrado: {e}")
            logger.info(f"💡 Execute primeiro: python register_model_mlflow.py")
            return False
    
    def deploy_model_serving(self, port: int = 8001, host: str = "0.0.0.0") -> bool:
        """Deploy usando MLFlow Model Serving"""
        try:
            logger.info(f"🚀 Iniciando deploy do modelo via MLFlow Serving...")
            logger.info(f"   Modelo: {self.model_uri}")
            logger.info(f"   Porta: {port}")
            
            # Comando para servir modelo
            cmd = [
                "mlflow", "models", "serve",
                "--model-uri", self.model_uri,
                "--port", str(port),
                "--host", host,
                "--env-manager", "local"
            ]
            
            logger.info(f"🔧 Executando: {' '.join(cmd)}")
            
            # Iniciar processo
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar inicialização
            logger.info("⏳ Aguardando inicialização do serviço...")
            time.sleep(10)
            
            # Verificar se está rodando
            if self.test_model_endpoint(f"http://{host}:{port}"):
                logger.info(f"✅ Deploy concluído com sucesso!")
                logger.info(f"🌐 Endpoint: http://{host}:{port}/invocations")
                return True
            else:
                logger.error("❌ Serviço não está respondendo")
                process.terminate()
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no deploy: {e}")
            return False
    
    def deploy_with_docker(self, image_name: str = "eye-disease-model", port: int = 8001) -> bool:
        """Deploy usando Docker"""
        try:
            logger.info(f"🐳 Criando imagem Docker para o modelo...")
            
            # Build da imagem Docker
            cmd_build = [
                "mlflow", "models", "build-docker",
                "--model-uri", self.model_uri,
                "--name", image_name
            ]
            
            logger.info(f"🔧 Executando: {' '.join(cmd_build)}")
            result = subprocess.run(cmd_build, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Erro ao criar imagem: {result.stderr}")
                return False
            
            logger.info("✅ Imagem Docker criada com sucesso")
            
            # Executar container
            cmd_run = [
                "docker", "run", "-d",
                "--name", f"{image_name}-container",
                "-p", f"{port}:8080",
                image_name
            ]
            
            logger.info(f"🔧 Executando: {' '.join(cmd_run)}")
            result = subprocess.run(cmd_run, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"❌ Erro ao executar container: {result.stderr}")
                return False
            
            # Aguardar inicialização
            logger.info("⏳ Aguardando inicialização do container...")
            time.sleep(15)
            
            # Testar endpoint
            if self.test_model_endpoint(f"http://localhost:{port}"):
                logger.info(f"✅ Deploy Docker concluído!")
                logger.info(f"🌐 Endpoint: http://localhost:{port}/invocations")
                return True
            else:
                logger.error("❌ Container não está respondendo")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no deploy Docker: {e}")
            return False
    
    def test_model_endpoint(self, base_url: str) -> bool:
        """Testa endpoint do modelo"""
        try:
            import numpy as np
            
            # Preparar dados de teste
            test_data = {
                "inputs": np.random.random((1, 256, 256, 3)).tolist()
            }
            
            # Fazer requisição
            response = requests.post(
                f"{base_url}/invocations",
                headers={"Content-Type": "application/json"},
                data=json.dumps(test_data),
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Teste de predição bem-sucedido")
                logger.info(f"   Shape da resposta: {len(result)} predições")
                return True
            else:
                logger.error(f"❌ Teste falhou: {response.status_code}")
                logger.error(f"   Resposta: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste: {e}")
            return False
    
    def deploy_full_api(self, port: int = 8080) -> bool:
        """Deploy da API completa com MLFlow"""
        try:
            logger.info(f"🚀 Iniciando deploy da API completa...")
            
            # Configurar variáveis de ambiente
            env = os.environ.copy()
            env.update({
                "MLFLOW_TRACKING_URI": self.mlflow_uri,
                "ENABLE_MODEL_REGISTRY": "true",
                "MODEL_STAGE": self.model_stage,
                "PORT": str(port)
            })
            
            # Comando para executar API
            cmd = ["python", "app.py"]
            
            logger.info(f"🔧 Executando API com MLFlow Registry habilitado...")
            
            # Iniciar processo
            process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Aguardar inicialização
            logger.info("⏳ Aguardando inicialização da API...")
            time.sleep(10)
            
            # Testar API
            if self.test_api_endpoint(f"http://localhost:{port}"):
                logger.info(f"✅ API deploy concluído!")
                logger.info(f"🌐 API: http://localhost:{port}")
                logger.info(f"📚 Docs: http://localhost:{port}/docs")
                return True
            else:
                logger.error("❌ API não está respondendo")
                process.terminate()
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no deploy da API: {e}")
            return False
    
    def test_api_endpoint(self, base_url: str) -> bool:
        """Testa endpoint da API"""
        try:
            # Testar health check
            response = requests.get(f"{base_url}/health", timeout=10)
            
            if response.status_code == 200:
                health_data = response.json()
                logger.info(f"✅ API está saudável")
                logger.info(f"   Modelo carregado: {health_data.get('model_loaded')}")
                return True
            else:
                logger.error(f"❌ Health check falhou: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro no teste da API: {e}")
            return False
    
    def show_deployment_info(self, deployment_type: str, port: int):
        """Mostra informações do deployment"""
        print("\n" + "=" * 60)
        print("🎉 DEPLOY CONCLUÍDO COM SUCESSO!")
        print("=" * 60)
        print(f"📋 Tipo de Deploy: {deployment_type}")
        print(f"🔗 Modelo: {self.model_uri}")
        print(f"🌐 MLFlow UI: {self.mlflow_uri}")
        
        if deployment_type == "model_serving":
            print(f"🚀 Endpoint do Modelo: http://localhost:{port}/invocations")
            print(f"\n📝 Exemplo de uso:")
            print(f'curl -X POST "http://localhost:{port}/invocations" \\')
            print(f'  -H "Content-Type: application/json" \\')
            print(f'  -d \'{{"inputs": [[...]]}}\'')
            
        elif deployment_type == "full_api":
            print(f"🚀 API Completa: http://localhost:{port}")
            print(f"📚 Documentação: http://localhost:{port}/docs")
            print(f"❤️ Health Check: http://localhost:{port}/health")
            print(f"\n📝 Exemplo de uso:")
            print(f'curl -X POST "http://localhost:{port}/predict" \\')
            print(f'  -F "file=@image.jpg"')
        
        print(f"\n🛑 Para parar o serviço:")
        print(f"   Ctrl+C ou docker stop (se usando Docker)")

def main():
    """Função principal"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy via MLFlow")
    parser.add_argument("--type", choices=["model", "docker", "api"], 
                       default="api", help="Tipo de deploy")
    parser.add_argument("--port", type=int, default=8001, 
                       help="Porta para o serviço")
    parser.add_argument("--mlflow-uri", default="http://localhost:5000",
                       help="URI do MLFlow")
    parser.add_argument("--model-name", default="eye-disease-model",
                       help="Nome do modelo no registry")
    parser.add_argument("--model-stage", default="Production",
                       help="Stage do modelo")
    
    args = parser.parse_args()
    
    print("🚀 MLFlow Deploy Tool")
    print("=" * 40)
    
    # Criar deployer
    deployer = MLFlowDeployer(
        mlflow_uri=args.mlflow_uri,
        model_name=args.model_name,
        model_stage=args.model_stage
    )
    
    # Verificar pré-requisitos
    if not deployer.check_mlflow_connection():
        logger.error("💡 Inicie o MLFlow: docker-compose up mlflow")
        sys.exit(1)
    
    if not deployer.check_model_exists():
        logger.error("💡 Registre o modelo: python register_model_mlflow.py")
        sys.exit(1)
    
    # Fazer deploy
    success = False
    
    if args.type == "model":
        success = deployer.deploy_model_serving(port=args.port)
        if success:
            deployer.show_deployment_info("model_serving", args.port)
            
    elif args.type == "docker":
        success = deployer.deploy_with_docker(port=args.port)
        if success:
            deployer.show_deployment_info("docker", args.port)
            
    elif args.type == "api":
        success = deployer.deploy_full_api(port=args.port)
        if success:
            deployer.show_deployment_info("full_api", args.port)
    
    if not success:
        logger.error("❌ Deploy falhou!")
        sys.exit(1)
    
    # Manter processo vivo para deploys locais
    if args.type in ["model", "api"]:
        try:
            logger.info("\n⏳ Serviço rodando... Pressione Ctrl+C para parar")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("\n🛑 Parando serviço...")

if __name__ == "__main__":
    main()
