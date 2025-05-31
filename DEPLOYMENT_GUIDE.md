# 🚀 Guia Completo de Deploy - Eye Disease Classifier API

## 📋 Checklist Pré-Deploy

### ✅ Pré-requisitos
- [ ] Conta Google Cloud Platform com billing habilitado
- [ ] Google Cloud CLI instalado e configurado
- [ ] Projeto GCP criado
- [ ] APIs necessárias habilitadas

### ✅ Verificação dos Arquivos
- [ ] `app.py` - Aplicação principal FastAPI
- [ ] `models.py` - Modelos Pydantic
- [ ] `ml_service.py` - Serviço de ML
- [ ] `monitoring.py` - Sistema de monitoramento
- [ ] `production_config.py` - Configurações de produção
- [ ] `tf_config.py` - Configurações TensorFlow
- [ ] `requirements.txt` - Dependências Python
- [ ] `Dockerfile` - Configuração do container
- [ ] `cloudbuild.yaml` - Configuração Cloud Build
- [ ] `service.yaml` - Configuração Cloud Run
- [ ] `deploy.sh` - Script de deploy

## 🚀 Processo de Deploy

### Método 1: Deploy Automático (Recomendado)

```bash
# 1. Clonar/navegar para o diretório do projeto
cd kumona-model-ai-api

# 2. Tornar script executável
chmod +x deploy.sh

# 3. Executar deploy
./deploy.sh SEU_PROJECT_ID us-central1
```

### Método 2: Deploy Manual

```bash
# 1. Configurar projeto
gcloud config set project SEU_PROJECT_ID
gcloud auth login

# 2. Habilitar APIs
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# 3. Build e deploy
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=us-central1

# 4. Verificar deploy
gcloud run services describe eye-disease-classifier --region=us-central1
```

## 🔧 Configurações Importantes

### Recursos do Cloud Run
- **Memória**: 2GB (necessário para TensorFlow)
- **CPU**: 2 vCPUs (otimizado para ML)
- **Timeout**: 300 segundos (para carregamento do modelo)
- **Concorrência**: 4 requests por instância
- **Instâncias máximas**: 10

### Variáveis de Ambiente
```yaml
PORT: 8080
LOG_LEVEL: INFO
ENVIRONMENT: production
TF_CPP_MIN_LOG_LEVEL: 2
```

## 📊 Verificação Pós-Deploy

### 1. Health Check
```bash
curl https://SEU_SERVICE_URL/health
```

Resposta esperada:
```json
{
  "status": "healthy",
  "model_loaded": true,
  "version": "1.0.0"
}
```

### 2. Teste de Predição
```bash
curl -X POST "https://SEU_SERVICE_URL/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg"
```

### 3. Verificar Métricas
```bash
curl https://SEU_SERVICE_URL/metrics
```

### 4. Documentação
Acesse: `https://SEU_SERVICE_URL/docs`

## 🐛 Troubleshooting

### Problema: Build falha com erro de memória
**Solução**: Aumentar recursos do Cloud Build
```yaml
options:
  machineType: 'E2_HIGHCPU_8'
  diskSizeGb: '100'
```

### Problema: Timeout no carregamento do modelo
**Solução**: Aumentar timeout do Cloud Run
```bash
gcloud run services update eye-disease-classifier \
  --timeout=600 \
  --region=us-central1
```

### Problema: Erro de permissões
**Solução**: Verificar IAM roles
```bash
gcloud projects add-iam-policy-binding SEU_PROJECT_ID \
  --member="user:SEU_EMAIL" \
  --role="roles/run.admin"
```

### Problema: Modelo não carrega
**Verificações**:
1. URL do modelo está correta
2. Modelo é acessível publicamente
3. Formato do modelo é compatível
4. Memória suficiente alocada

### Problema: Alta latência
**Otimizações**:
1. Aumentar CPU para 4 vCPUs
2. Configurar min-instances para 1
3. Habilitar CPU boost
```bash
gcloud run services update eye-disease-classifier \
  --cpu=4 \
  --min-instances=1 \
  --cpu-boost \
  --region=us-central1
```

## 📈 Monitoramento

### Logs
```bash
# Ver logs em tempo real
gcloud logging tail "resource.type=cloud_run_revision AND resource.labels.service_name=eye-disease-classifier"

# Filtrar logs de erro
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=eye-disease-classifier AND severity>=ERROR"
```

### Métricas no Cloud Monitoring
- Request count
- Request latency
- Error rate
- Memory utilization
- CPU utilization

### Alertas Recomendados
1. **Latência alta**: > 5 segundos
2. **Taxa de erro**: > 5%
3. **Uso de memória**: > 80%
4. **Falhas de health check**: > 3 consecutivas

## 🔒 Segurança

### Configurações de Produção
1. **Remover allow-unauthenticated** se necessário
2. **Configurar CORS** para domínios específicos
3. **Implementar rate limiting**
4. **Configurar Cloud Armor** para proteção DDoS

### Exemplo de configuração segura:
```bash
gcloud run services update eye-disease-classifier \
  --no-allow-unauthenticated \
  --region=us-central1
```

## 📞 Suporte

### Comandos Úteis
```bash
# Status do serviço
gcloud run services describe eye-disease-classifier --region=us-central1

# Listar revisões
gcloud run revisions list --service=eye-disease-classifier --region=us-central1

# Rollback para revisão anterior
gcloud run services update-traffic eye-disease-classifier \
  --to-revisions=REVISION_NAME=100 \
  --region=us-central1

# Deletar serviço
gcloud run services delete eye-disease-classifier --region=us-central1
```

### Links Úteis
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Cloud Build Documentation](https://cloud.google.com/build/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [TensorFlow Optimization](https://www.tensorflow.org/guide/optimization)
