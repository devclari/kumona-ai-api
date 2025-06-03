# 🚀 Guia de Integração MLFlow - Eye Disease Classifier API

## 📋 Visão Geral

Esta API agora está integrada com MLFlow para fornecer:
- **Tracking de Experimentos**: Rastreamento automático de predições e métricas
- **Model Registry**: Gerenciamento de versões de modelos (opcional)
- **Monitoramento de Performance**: Detecção de drift e análise de performance
- **Logs Estruturados**: Logs detalhados para análise e debugging

## 🏗️ Arquitetura MLFlow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI App   │───▶│  MLFlow Server  │───▶│  File Storage   │
│                 │    │   (Port 5000)   │    │   (mlruns/)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Predictions   │    │   Experiments   │    │   Artifacts     │
│   Tracking      │    │   Tracking      │    │   Storage       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Como Executar

### 1. Usando Docker Compose (Recomendado)

```bash
# Iniciar todos os serviços (API + MLFlow)
docker-compose up -d

# Verificar logs
docker-compose logs -f

# Parar serviços
docker-compose down
```

### 2. Executar Localmente

```bash
# 1. Instalar dependências
pip install -r requirements.txt

# 2. Iniciar servidor MLFlow (terminal separado)
mlflow server --backend-store-uri file:./mlruns --default-artifact-root ./mlflow_artifacts --host 0.0.0.0 --port 5000

# 3. Configurar variáveis de ambiente
export MLFLOW_TRACKING_URI=http://localhost:5000
export ENABLE_MLFLOW_TRACKING=true

# 4. Iniciar API
python app.py
```

## 🌐 Acessos

- **API**: http://localhost:8080
- **MLFlow UI**: http://localhost:5000
- **API Docs**: http://localhost:8080/docs
- **Health Check**: http://localhost:8080/health

## 📊 Funcionalidades MLFlow

### 1. Tracking Automático de Predições

Cada predição é automaticamente trackada com:
- Tempo de inferência
- Confiança da predição
- Distribuição de probabilidades por classe
- Metadados da imagem (se disponível)

### 2. Métricas de Performance

- **Tempo médio de inferência**
- **Distribuição de confiança**
- **Distribuição de classes preditas**
- **Taxa de erro**
- **Detecção de drift**

### 3. Health Check Tracking

- Tempo de resposta do health check
- Status do modelo
- Contadores de verificações

### 4. Monitoramento de Drift

O sistema detecta automaticamente possível drift baseado em:
- Confiança média muito baixa (< 60%)
- Alta proporção de predições com baixa confiança (> 30%)
- Tempo de inferência muito alto (> 5s)
- Distribuição de classes muito desbalanceada (> 80% uma classe)

## ⚙️ Configurações

### Variáveis de Ambiente

```bash
# MLFlow Server
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=eye-disease-classifier
MLFLOW_MODEL_NAME=eye-disease-model

# Funcionalidades
ENABLE_MLFLOW_TRACKING=true
ENABLE_MODEL_REGISTRY=false

# Model Registry (se habilitado)
MODEL_STAGE=Production
MODEL_VERSION=latest
```

### Configurações de Produção

Para produção, considere:

1. **Banco de Dados Backend**: Use PostgreSQL ou MySQL em vez de arquivos
2. **Armazenamento de Artefatos**: Use S3, Azure Blob ou GCS
3. **Autenticação**: Configure usuário/senha para MLFlow
4. **Backup**: Configure backup automático dos dados MLFlow

Exemplo para produção:
```bash
export MLFLOW_TRACKING_URI=postgresql://user:pass@host:5432/mlflow
export MLFLOW_DEFAULT_ARTIFACT_ROOT=s3://my-bucket/mlflow-artifacts
export MLFLOW_USERNAME=admin
export MLFLOW_PASSWORD=secure_password
```

## 📈 Usando a Interface MLFlow

### 1. Acessar Experimentos
1. Abra http://localhost:5000
2. Clique no experimento "eye-disease-classifier"
3. Visualize runs e métricas

### 2. Analisar Métricas
- **Metrics**: Gráficos de tempo de inferência, confiança, etc.
- **Parameters**: Configurações do modelo e API
- **Artifacts**: Logs e arquivos salvos

### 3. Comparar Runs
- Selecione múltiplas runs
- Clique em "Compare"
- Analise diferenças em métricas e parâmetros

## 🔧 Model Registry (Opcional)

Para habilitar o Model Registry:

```bash
export ENABLE_MODEL_REGISTRY=true
```

### Registrar Modelo

```python
# Exemplo de como registrar um modelo
import mlflow.tensorflow

# Durante o treinamento
with mlflow.start_run():
    # ... treinar modelo ...
    
    # Salvar modelo
    mlflow.tensorflow.log_model(
        model=model,
        artifact_path="model",
        registered_model_name="eye-disease-model"
    )
```

### Usar Modelo do Registry

A API automaticamente tentará carregar do registry se configurado:
- Primeiro tenta carregar do MLFlow Registry
- Se falhar, faz fallback para modelo local

## 📊 Métricas Disponíveis

### Métricas de Predição
- `prediction_inference_time_ms`: Tempo de inferência em ms
- `prediction_confidence`: Confiança da predição (0-100)
- `prediction_count`: Contador de predições
- `prob_[classe]`: Probabilidade para cada classe

### Métricas de Sessão
- `session_total_predictions`: Total de predições na sessão
- `session_avg_inference_time_ms`: Tempo médio de inferência
- `session_avg_confidence`: Confiança média
- `class_dist_[classe]`: Distribuição de classes

### Métricas de Performance
- `recent_avg_confidence`: Confiança média recente
- `recent_low_confidence_ratio`: Proporção de baixa confiança
- `drift_detected`: Indicador de drift (0/1)

## 🚨 Troubleshooting

### MLFlow não conecta
```bash
# Verificar se o servidor está rodando
curl http://localhost:5000/health

# Verificar logs do container
docker-compose logs mlflow
```

### Erro de permissão nos volumes
```bash
# Criar diretórios com permissões corretas
mkdir -p mlruns mlflow_artifacts
chmod 755 mlruns mlflow_artifacts
```

### API não tracka métricas
```bash
# Verificar variáveis de ambiente
echo $MLFLOW_TRACKING_URI
echo $ENABLE_MLFLOW_TRACKING

# Verificar logs da API
docker-compose logs api
```

## 📚 Próximos Passos

1. **Configurar Alertas**: Implementar alertas para drift detectado
2. **Dashboard Customizado**: Criar dashboard específico para métricas de negócio
3. **A/B Testing**: Usar MLFlow para comparar diferentes versões do modelo
4. **Automated Retraining**: Configurar retreinamento automático baseado em métricas
5. **Data Validation**: Adicionar validação de dados de entrada

## 🔗 Links Úteis

- [MLFlow Documentation](https://mlflow.org/docs/latest/)
- [MLFlow Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [MLFlow Tracking](https://mlflow.org/docs/latest/tracking.html)
- [MLFlow REST API](https://mlflow.org/docs/latest/rest-api.html)
