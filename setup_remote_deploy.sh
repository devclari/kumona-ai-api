#!/bin/bash

# Script para configurar deploy remoto
# Uso: ./setup_remote_deploy.sh

set -e

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo "🌐 Setup Deploy Remoto - Eye Disease Classifier API"
echo "=================================================="

# Verificar se estamos em um repositório Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Não é um repositório Git"
    exit 1
fi

# Verificar se há mudanças para commitar
if ! git diff --quiet || ! git diff --cached --quiet; then
    log_info "Commitando arquivos de configuração de deploy..."
    
    git add .
    git commit -m "feat: Adicionar configurações para deploy remoto (Railway, Render, Vercel, Docker)"
    
    log_success "Arquivos commitados"
else
    log_info "Nenhuma mudança para commitar"
fi

# Push para o repositório
log_info "Fazendo push para o repositório..."
git push

log_success "Configurações de deploy enviadas para o Git!"

echo ""
echo "🚀 DEPLOY REMOTO CONFIGURADO!"
echo "============================="
echo ""
echo "📦 Repositório: $(git remote get-url origin)"
echo ""
echo "🌟 OPÇÕES DE DEPLOY DISPONÍVEIS:"
echo ""

echo "1️⃣  RAILWAY (Recomendado - Mais Fácil)"
echo "   🔗 https://railway.app"
echo "   📋 Passos:"
echo "      1. Login com GitHub"
echo "      2. New Project → Deploy from GitHub"
echo "      3. Selecionar: devclari/kumona-ai-api"
echo "      4. Aguardar deploy (5-10 min)"
echo "   ✅ Configuração: railway.json (já incluído)"
echo ""

echo "2️⃣  RENDER"
echo "   🔗 https://render.com"
echo "   📋 Passos:"
echo "      1. New → Web Service"
echo "      2. Connect Repository"
echo "      3. Environment: Docker"
echo "   ✅ Configuração: render.yaml (já incluído)"
echo ""

echo "3️⃣  VERCEL"
echo "   🔗 https://vercel.com"
echo "   📋 Passos:"
echo "      1. Import Project"
echo "      2. Deploy"
echo "   ✅ Configuração: vercel.json (já incluído)"
echo ""

echo "4️⃣  DOCKER HUB + QUALQUER CLOUD"
echo "   🔗 GitHub Actions configurado"
echo "   📋 Imagem será criada automaticamente em:"
echo "      ghcr.io/devclari/kumona-ai-api:latest"
echo ""

echo "5️⃣  GOOGLE CLOUD RUN"
echo "   📋 Comando direto:"
echo "      gcloud run deploy --source ."
echo ""

echo "🎯 RECOMENDAÇÃO: Use Railway!"
echo "   • Setup em 2 minutos"
echo "   • Deploy automático"
echo "   • Free tier generoso"
echo "   • URL personalizada"
echo ""

echo "📊 APÓS O DEPLOY:"
echo "   • API: https://seu-app.plataforma.com"
echo "   • Docs: https://seu-app.plataforma.com/docs"
echo "   • Health: https://seu-app.plataforma.com/health"
echo ""

echo "🔧 TROUBLESHOOTING:"
echo "   • Logs disponíveis na plataforma"
echo "   • Build time: 5-10 minutos"
echo "   • Dockerfile.mlflow será usado automaticamente"
echo ""

log_success "Pronto para deploy remoto! Escolha uma plataforma acima."
