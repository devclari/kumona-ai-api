#!/bin/bash

# Script de deploy para Google Cloud Run
# Uso: ./deploy.sh [PROJECT_ID] [REGION]

set -e

# Configurações padrão
DEFAULT_REGION="us-central1"
SERVICE_NAME="eye-disease-classifier"

# Verificar argumentos
if [ $# -eq 0 ]; then
    echo "❌ Erro: PROJECT_ID é obrigatório"
    echo "Uso: $0 <PROJECT_ID> [REGION]"
    echo "Exemplo: $0 meu-projeto-gcp us-central1"
    exit 1
fi

PROJECT_ID=$1
REGION=${2:-$DEFAULT_REGION}

echo "🚀 Iniciando deploy da Eye Disease Classifier API"
echo "📋 Configurações:"
echo "   - Projeto: $PROJECT_ID"
echo "   - Região: $REGION"
echo "   - Serviço: $SERVICE_NAME"
echo ""

# Verificar se gcloud está instalado
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI não encontrado. Instale em: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Configurar projeto
echo "🔧 Configurando projeto GCP..."
gcloud config set project $PROJECT_ID

# Verificar autenticação
echo "🔐 Verificando autenticação..."
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "❌ Não autenticado. Execute: gcloud auth login"
    exit 1
fi

# Habilitar APIs necessárias
echo "🔌 Habilitando APIs necessárias..."
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Substituir PROJECT_ID no service.yaml
echo "🔧 Configurando service.yaml..."
sed "s/PROJECT_ID/$PROJECT_ID/g" service.yaml > service-configured.yaml

# Build e deploy usando Cloud Build
echo "🏗️ Iniciando build e deploy..."
gcloud builds submit --config cloudbuild.yaml --substitutions=_REGION=$REGION

# Obter URL do serviço
echo "🔍 Obtendo URL do serviço..."
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format="value(status.url)" 2>/dev/null || echo "")

echo ""
echo "✅ Deploy concluído com sucesso!"
echo "🌐 URL da API: $SERVICE_URL"
echo "📖 Documentação: $SERVICE_URL/docs"
echo "❤️ Health Check: $SERVICE_URL/health"
echo ""
echo "🧪 Teste a API:"
echo "curl $SERVICE_URL/health"
echo ""
echo "📱 Para testar predição:"
echo "curl -X POST \"$SERVICE_URL/predict\" \\"
echo "  -H \"accept: application/json\" \\"
echo "  -H \"Content-Type: multipart/form-data\" \\"
echo "  -F \"file=@sua_imagem.jpg\""
