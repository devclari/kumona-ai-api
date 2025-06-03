# 🚀 Guia de Deploy com MLFlow

Este guia mostra como fazer deploy da sua API usando a plataforma MLFlow de diferentes formas.

## 📋 Opções de Deploy

### 1. **MLFlow Model Serving** (Recomendado para modelos)
- Deploy direto do modelo via MLFlow
- Endpoint REST automático
- Versionamento integrado

### 2. **MLFlow Projects** (Para aplicações completas)
- Deploy da aplicação completa
- Controle de dependências
- Reprodutibilidade garantida

### 3. **Container Deploy** (Para produção)
- Deploy containerizado via MLFlow
- Integração com Kubernetes
- Escalabilidade automática

## 🎯 Método 1: MLFlow Model Serving

### Passo 1: Registrar o Modelo no MLFlow

Primeiro, vamos criar um script para registrar seu modelo atual no MLFlow Registry:

```python
# register_model.py
import mlflow
import mlflow.tensorflow
from keras.models import load_model
import os

# Configurar MLFlow
mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("eye-disease-classifier")

# Carregar modelo existente
model_path = "best_model.keras"
if not os.path.exists(model_path):
    # Baixar modelo se necessário
    import gdown
    model_url = "https://drive.google.com/uc?id=1vSIfD3viT5JSxpG4asA8APCwK0JK9Dvu"
    gdown.download(model_url, model_path, quiet=False)

model = load_model(model_path)

# Iniciar run e registrar modelo
with mlflow.start_run(run_name="model_registration") as run:
    # Log parâmetros do modelo
    mlflow.log_params({
        "model_type": "tensorflow",
        "input_shape": str(model.input_shape),
        "output_shape": str(model.output_shape),
        "classes": ["cataract", "diabetic_retinopathy", "glaucoma", "normal"]
    })
    
    # Log modelo
    mlflow.tensorflow.log_model(
        model=model,
        artifact_path="model",
        registered_model_name="eye-disease-model",
        signature=mlflow.models.infer_signature(
            model_input=np.random.random((1, 256, 256, 3)).astype(np.float32),
            model_output=model.predict(np.random.random((1, 256, 256, 3)).astype(np.float32))
        )
    )
    
    print(f"✅ Modelo registrado na run: {run.info.run_id}")
```

### Passo 2: Deploy do Modelo

```bash
# Deploy local para teste
mlflow models serve \
    --model-uri "models:/eye-disease-model/Production" \
    --port 8001 \
    --host 0.0.0.0

# Deploy com Docker
mlflow models build-docker \
    --model-uri "models:/eye-disease-model/Production" \
    --name "eye-disease-model"

docker run -p 8001:8080 eye-disease-model
```

### Passo 3: Testar o Deploy

```python
import requests
import numpy as np
import json

# Preparar dados de teste
data = {
    "inputs": np.random.random((1, 256, 256, 3)).tolist()
}

# Fazer predição
response = requests.post(
    "http://localhost:8001/invocations",
    headers={"Content-Type": "application/json"},
    data=json.dumps(data)
)

print(response.json())
```

## 🏗️ Método 2: MLFlow Projects

### Passo 1: Criar MLproject

```yaml
# MLproject
name: eye-disease-classifier

conda_env: conda.yaml

entry_points:
  main:
    parameters:
      port: {type: int, default: 8080}
      mlflow_uri: {type: str, default: "http://localhost:5000"}
    command: "python app.py --port {port} --mlflow-uri {mlflow_uri}"
  
  serve:
    parameters:
      model_version: {type: str, default: "Production"}
      port: {type: int, default: 8001}
    command: "mlflow models serve --model-uri models:/eye-disease-model/{model_version} --port {port} --host 0.0.0.0"
```

### Passo 2: Criar conda.yaml

```yaml
# conda.yaml
name: eye-disease-classifier
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pip
  - pip:
    - fastapi==0.104.1
    - uvicorn[standard]==0.24.0
    - python-multipart==0.0.6
    - numpy>=1.21.0
    - pillow>=9.0.0
    - tensorflow>=2.12.0
    - mlflow>=2.8.0
    - boto3>=1.26.0
    - psutil>=5.9.0
    - cloudpickle>=2.0.0
```

### Passo 3: Deploy via MLFlow Projects

```bash
# Deploy local
mlflow run . -P port=8080

# Deploy remoto (GitHub)
mlflow run https://github.com/seu-usuario/seu-repo.git \
    -P port=8080 \
    -P mlflow_uri=http://seu-mlflow-server:5000
```

## 🐳 Método 3: Container Deploy

### Passo 1: Dockerfile Otimizado para MLFlow

```dockerfile
# Dockerfile.mlflow
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Configurar MLFlow
ENV MLFLOW_TRACKING_URI=http://mlflow:5000
ENV ENABLE_MLFLOW_TRACKING=true
ENV ENABLE_MODEL_REGISTRY=true

# Expor porta
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Comando de inicialização
CMD ["python", "app.py"]
```

### Passo 2: Docker Compose para Produção

```yaml
# docker-compose.prod.yml
version: '3.8'

services:
  # Banco de dados para MLFlow
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: mlflow
      POSTGRES_USER: mlflow
      POSTGRES_PASSWORD: mlflow_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  # Servidor MLFlow
  mlflow:
    image: python:3.11-slim
    depends_on:
      - postgres
    environment:
      - MLFLOW_BACKEND_STORE_URI=postgresql://mlflow:mlflow_password@postgres:5432/mlflow
      - MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://seu-bucket/mlflow-artifacts
      - AWS_ACCESS_KEY_ID=sua_access_key
      - AWS_SECRET_ACCESS_KEY=sua_secret_key
    ports:
      - "5000:5000"
    command: >
      bash -c "
        pip install mlflow[extras] psycopg2-binary boto3 &&
        mlflow server 
        --backend-store-uri postgresql://mlflow:mlflow_password@postgres:5432/mlflow
        --default-artifact-root s3://seu-bucket/mlflow-artifacts
        --host 0.0.0.0 
        --port 5000
      "
    restart: unless-stopped

  # API Principal
  api:
    build:
      context: .
      dockerfile: Dockerfile.mlflow
    depends_on:
      - mlflow
    environment:
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - ENABLE_MODEL_REGISTRY=true
      - MODEL_STAGE=Production
    ports:
      - "8080:8080"
    restart: unless-stopped

volumes:
  postgres_data:
```

## ☁️ Deploy em Cloud

### AWS (usando ECS/Fargate)

```bash
# 1. Build e push da imagem
docker build -f Dockerfile.mlflow -t eye-disease-classifier .
docker tag eye-disease-classifier:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/eye-disease-classifier:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/eye-disease-classifier:latest

# 2. Deploy via MLFlow
mlflow deployments create \
    --target ecs \
    --name eye-disease-classifier \
    --model-uri models:/eye-disease-model/Production \
    --config cluster=my-cluster \
    --config task_definition_arn=arn:aws:ecs:us-east-1:123456789:task-definition/mlflow-task
```

### Google Cloud (usando Cloud Run)

```bash
# 1. Build e push
gcloud builds submit --tag gcr.io/SEU_PROJECT/eye-disease-classifier .

# 2. Deploy
gcloud run deploy eye-disease-classifier \
    --image gcr.io/SEU_PROJECT/eye-disease-classifier \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars MLFLOW_TRACKING_URI=https://seu-mlflow.com \
    --set-env-vars ENABLE_MODEL_REGISTRY=true
```

### Azure (usando Container Instances)

```bash
# Deploy via MLFlow
mlflow deployments create \
    --target azureml \
    --name eye-disease-classifier \
    --model-uri models:/eye-disease-model/Production \
    --config subscription_id=sua_subscription \
    --config resource_group=seu_resource_group
```

## 🔧 Configurações Avançadas

### Auto-scaling baseado em métricas

```yaml
# kubernetes-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: eye-disease-classifier
spec:
  replicas: 3
  selector:
    matchLabels:
      app: eye-disease-classifier
  template:
    metadata:
      labels:
        app: eye-disease-classifier
    spec:
      containers:
      - name: api
        image: eye-disease-classifier:latest
        ports:
        - containerPort: 8080
        env:
        - name: MLFLOW_TRACKING_URI
          value: "http://mlflow-service:5000"
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
---
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: eye-disease-classifier-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: eye-disease-classifier
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

## 📊 Monitoramento do Deploy

### Health Checks Avançados

```python
# health_check_advanced.py
import requests
import time
import json

def check_deployment_health(base_url):
    """Verifica saúde do deployment"""
    
    checks = {
        "api_health": f"{base_url}/health",
        "api_metrics": f"{base_url}/metrics",
        "model_prediction": f"{base_url}/predict"
    }
    
    results = {}
    
    for check_name, url in checks.items():
        try:
            if check_name == "model_prediction":
                # Teste de predição com imagem fake
                files = {'file': ('test.jpg', open('test_image.jpg', 'rb'), 'image/jpeg')}
                response = requests.post(url, files=files, timeout=30)
            else:
                response = requests.get(url, timeout=10)
            
            results[check_name] = {
                "status": "OK" if response.status_code == 200 else "FAIL",
                "response_time": response.elapsed.total_seconds(),
                "status_code": response.status_code
            }
            
        except Exception as e:
            results[check_name] = {
                "status": "ERROR",
                "error": str(e)
            }
    
    return results

# Uso
health = check_deployment_health("http://localhost:8080")
print(json.dumps(health, indent=2))
```

## 🚨 Troubleshooting

### Problemas Comuns

1. **Modelo não carrega do Registry**
   ```bash
   # Verificar se modelo existe
   mlflow models list --name eye-disease-model
   
   # Verificar conectividade
   curl http://seu-mlflow:5000/health
   ```

2. **Erro de dependências**
   ```bash
   # Rebuild com cache limpo
   docker build --no-cache -f Dockerfile.mlflow .
   ```

3. **Performance baixa**
   ```bash
   # Verificar recursos
   docker stats
   
   # Ajustar configurações TensorFlow
   export TF_NUM_INTEROP_THREADS=4
   export TF_NUM_INTRAOP_THREADS=4
   ```

## 📚 Próximos Passos

1. **Configurar CI/CD** para deploy automático
2. **Implementar A/B testing** com diferentes versões
3. **Configurar alertas** para métricas de performance
4. **Implementar canary deployments**
5. **Configurar backup** automático do MLFlow

---

**🎯 Escolha o método que melhor se adequa ao seu ambiente e necessidades!**
