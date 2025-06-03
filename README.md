# Eye Disease Classifier API

Uma API REST para classificação de doenças oculares usando deep learning, com integração MLFlow para tracking e monitoramento, pronta para deploy no Google Cloud Run.

## 🎯 Funcionalidades

- **Classificação de Doenças Oculares**: Detecta catarata, retinopatia diabética, glaucoma ou olhos normais
- **API REST**: Interface simples e bem documentada
- **Integração MLFlow**: Tracking automático de experimentos e métricas
- **Monitoramento Avançado**: Detecção de drift e análise de performance
- **Documentação Automática**: Swagger UI integrado
- **Pronto para Cloud**: Containerizado e otimizado para Google Cloud Run
- **Health Checks**: Monitoramento de saúde da aplicação

## 🔍 Doenças Detectadas

- **Catarata** (cataract)
- **Retinopatia Diabética** (diabetic_retinopathy)
- **Glaucoma** (glaucoma)
- **Normal** (normal)

## 📋 Formatos Suportados

- JPEG (.jpg, .jpeg)
- PNG (.png)

## 🚀 Deploy no Google Cloud Run

### Pré-requisitos

1. **Conta no Google Cloud Platform** com billing habilitado
2. **Google Cloud CLI** instalado ([Download aqui](https://cloud.google.com/sdk/docs/install))
3. **Projeto GCP** criado
4. **Docker** instalado (opcional, para testes locais)

### Deploy Automático (Recomendado)

Use o script de deploy automatizado:

```bash
# Tornar o script executável
chmod +x deploy.sh

# Executar deploy
./deploy.sh SEU_PROJECT_ID us-central1
```

### Deploy Manual

1. **Configure o projeto GCP**:
```bash
gcloud config set project SEU_PROJECT_ID
gcloud auth login
```

2. **Habilite as APIs necessárias**:
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

3. **Deploy usando Cloud Build**:
```bash
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=us-central1
```

4. **Deploy alternativo com Docker**:
```bash
# Build da imagem
docker build -t gcr.io/SEU_PROJECT_ID/eye-disease-classifier .

# Push para Container Registry
docker push gcr.io/SEU_PROJECT_ID/eye-disease-classifier

# Deploy no Cloud Run
gcloud run deploy eye-disease-classifier \
  --image gcr.io/SEU_PROJECT_ID/eye-disease-classifier \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --max-instances 10 \
  --port 8080
```

### Deploy com Configuração Personalizada

Para usar configurações específicas:

```bash
# Editar service.yaml com suas configurações
# Depois executar:
gcloud run services replace service-configured.yaml --region=us-central1
```

## 🛠️ Desenvolvimento Local

### Instalação

1. **Clone o repositório**:
```bash
git clone <seu-repositorio>
cd kumona-model-ai-api
```

2. **Instale as dependências**:
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação**:
```bash
python app.py
```

A API estará disponível em `http://localhost:8080`

### Docker Local com MLFlow

```bash
# Execute com Docker Compose (inclui MLFlow)
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### Docker Local (apenas API)

```bash
# Build da imagem
docker build -t eye-disease-classifier .

# Execute o container
docker run -p 8080:8080 eye-disease-classifier
```

## 📊 MLFlow Integration

Esta API está integrada com MLFlow para tracking avançado de experimentos e monitoramento de modelos.

### Funcionalidades MLFlow

- **Tracking Automático**: Todas as predições são automaticamente trackadas
- **Métricas de Performance**: Tempo de inferência, confiança, distribuição de classes
- **Detecção de Drift**: Monitoramento automático de degradação do modelo
- **Model Registry**: Suporte para versionamento de modelos (opcional)
- **Interface Web**: Dashboard visual para análise de métricas

### Acesso ao MLFlow

Quando executado com `docker-compose up`:

- **MLFlow UI**: http://localhost:5000
- **API**: http://localhost:8080
- **API Docs**: http://localhost:8080/docs

### Configuração MLFlow

```bash
# Variáveis de ambiente para MLFlow
export MLFLOW_TRACKING_URI=http://localhost:5000
export ENABLE_MLFLOW_TRACKING=true
export MLFLOW_EXPERIMENT_NAME=eye-disease-classifier
```

### Teste da Integração

```bash
# Execute o script de teste
python test_mlflow_integration.py
```

Para mais detalhes, consulte o [Guia MLFlow](MLFLOW_GUIDE.md).

## 📖 Uso da API

### Endpoints Principais

- **GET /** - Informações da API
- **GET /health** - Health check
- **GET /metrics** - Métricas da aplicação
- **POST /predict** - Classificação de imagem
- **GET /docs** - Documentação Swagger

### Exemplo de Uso

```bash
# Health check
curl http://localhost:8080/health

# Predição
curl -X POST "http://localhost:8080/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@eye_image.jpg"
```

### Resposta da Predição

```json
{
  "predicted_class": "normal",
  "confidence": 95.67,
  "all_predictions": {
    "cataract": 1.23,
    "diabetic_retinopathy": 2.10,
    "glaucoma": 1.00,
    "normal": 95.67
  }
}
```

## 🔧 Configuração

### Variáveis de Ambiente

- `PORT`: Porta da aplicação (padrão: 8080)
- `LOG_LEVEL`: Nível de log (padrão: INFO)

### Recursos do Cloud Run

- **Memória**: 2GB
- **CPU**: 2 vCPUs
- **Timeout**: 300 segundos
- **Instâncias máximas**: 10

## 📊 Monitoramento e Métricas

A API inclui sistema completo de monitoramento:

### Endpoints de Monitoramento

- **GET /health** - Status da aplicação e modelo
- **GET /metrics** - Métricas detalhadas da aplicação

### Métricas Disponíveis

```json
{
  "uptime_seconds": 3600.0,
  "total_requests": 150,
  "total_predictions": 45,
  "total_errors": 2,
  "average_response_time_ms": 250.5,
  "requests_per_second": 0.042,
  "error_rate": 1.33
}
```

### Logs Estruturados

A API gera logs estruturados em JSON para integração com Cloud Logging:

- **STARTUP** - Inicialização da aplicação
- **MODEL_LOAD** - Carregamento do modelo ML
- **PREDICTION** - Logs de predições
- **HEALTH** - Health checks
- **SHUTDOWN** - Encerramento da aplicação

### Monitoramento no Google Cloud

Configure alertas no Cloud Monitoring para:

- **Latência alta** (> 5 segundos)
- **Taxa de erro alta** (> 5%)
- **Uso de memória** (> 80%)
- **Falhas de health check**

```bash
# Exemplo de consulta de logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=eye-disease-classifier"
```

## 🔒 Segurança

- Container não-root
- CORS configurado
- Validação de entrada
- Error handling seguro

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para detalhes.

## 📞 Suporte

Para suporte, abra uma issue no repositório ou entre em contato através do email: support@example.com
