#!/bin/bash

# Script para configurar Git e repositório
# Uso: ./setup_git.sh [repo_url]

set -e

REPO_URL=$1

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
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

echo "🔧 Configuração Git - Eye Disease Classifier API"
echo "================================================"

# Verificar se Git está instalado
if ! command -v git &> /dev/null; then
    echo "❌ Git não está instalado. Instale primeiro:"
    echo "   Windows: https://git-scm.com/download/win"
    echo "   macOS: brew install git"
    echo "   Linux: sudo apt install git"
    exit 1
fi

# Configurar usuário se necessário
if ! git config user.name > /dev/null 2>&1; then
    log_warning "Configuração do Git necessária"
    read -p "Digite seu nome: " git_name
    git config --global user.name "$git_name"
    log_success "Nome configurado: $git_name"
fi

if ! git config user.email > /dev/null 2>&1; then
    read -p "Digite seu email: " git_email
    git config --global user.email "$git_email"
    log_success "Email configurado: $git_email"
fi

# Inicializar repositório se necessário
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_info "Inicializando repositório Git..."
    git init
    git branch -M main
    log_success "Repositório inicializado"
fi

# Configurar remote se fornecido
if [ -n "$REPO_URL" ]; then
    log_info "Configurando remote origin..."
    
    # Remover origin existente se houver
    git remote remove origin 2>/dev/null || true
    
    # Adicionar novo origin
    git remote add origin "$REPO_URL"
    log_success "Remote configurado: $REPO_URL"
fi

# Mostrar status
echo ""
log_info "Configuração atual:"
echo "  Nome: $(git config user.name)"
echo "  Email: $(git config user.email)"

if git remote | grep -q origin; then
    echo "  Remote: $(git remote get-url origin)"
else
    log_warning "Nenhum remote configurado"
    echo ""
    echo "💡 Para adicionar um remote:"
    echo "   git remote add origin https://github.com/usuario/repo.git"
    echo "   ou execute: ./setup_git.sh https://github.com/usuario/repo.git"
fi

echo ""
log_success "Git configurado com sucesso!"
echo ""
echo "🚀 Próximos passos:"
echo "   1. ./git_deploy.sh                    # Commit + Deploy automático"
echo "   2. ./git_deploy.sh \"sua mensagem\"     # Commit custom + Deploy"
echo "   3. ./deploy_complete.sh api 8080     # Apenas deploy"
