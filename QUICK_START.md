# ⚡ Quick Start - Eye Disease Classifier API

## 🚀 Deploy em 3 Passos

### 1️⃣ Validar Projeto
```bash
python validate_setup.py
```

### 2️⃣ Deploy Automático
```bash
chmod +x deploy.sh
./deploy.sh SEU_PROJECT_ID us-central1
```

### 3️⃣ Testar API
```bash
# Substituir SEU_SERVICE_URL pela URL retornada no deploy
curl https://SEU_SERVICE_URL/health
```

## 📋 Pré-requisitos Rápidos

1. **Google Cloud CLI** instalado
2. **Projeto GCP** criado com billing
3. **Autenticação** configurada: `gcloud auth login`

## 🔗 URLs Importantes

Após o deploy, você terá:

- **API Base**: `https://SEU_SERVICE_URL/`
- **Health Check**: `https://SEU_SERVICE_URL/health`
- **Métricas**: `https://SEU_SERVICE_URL/metrics`
- **Documentação**: `https://SEU_SERVICE_URL/docs`
- **Predição**: `POST https://SEU_SERVICE_URL/predict`

## 🧪 Teste Rápido de Predição

```bash
curl -X POST "https://SEU_SERVICE_URL/predict" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sua_imagem.jpg"
```

## 📊 Resposta Esperada

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

## 🆘 Problemas Comuns

### ❌ "gcloud not found"
```bash
# Instalar Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### ❌ "Permission denied"
```bash
gcloud auth login
gcloud config set project SEU_PROJECT_ID
```

### ❌ "APIs not enabled"
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
```

### ❌ "Build timeout"
```bash
# Aumentar timeout no cloudbuild.yaml
timeout: '1800s'  # 30 minutos
```

## 📚 Documentação Completa

- **README.md** - Documentação principal
- **DEPLOYMENT_GUIDE.md** - Guia detalhado de deploy
- **PROJECT_SUMMARY.md** - Resumo do projeto

## 🎯 Próximos Passos

1. ✅ Deploy realizado
2. 🧪 Testar endpoints
3. 📊 Verificar métricas
4. 🔧 Configurar monitoramento
5. 🚀 Integrar com sua aplicação

---

**🎉 Sua API está pronta para produção!**
