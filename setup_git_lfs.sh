#!/bin/bash

# Script para configurar Git LFS para o modelo
# Uso: ./setup_git_lfs.sh

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

echo "📦 Configuração Git LFS para Modelo Grande"
echo "=========================================="

# Verificar se Git LFS está instalado
if ! command -v git-lfs &> /dev/null; then
    log_error "Git LFS não está instalado"
    echo ""
    echo "💡 Como instalar:"
    echo "   Windows: Baixar de https://git-lfs.github.io/"
    echo "   macOS: brew install git-lfs"
    echo "   Ubuntu: sudo apt install git-lfs"
    echo "   CentOS: sudo yum install git-lfs"
    exit 1
fi

# Verificar se estamos em um repositório Git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Não é um repositório Git"
    exit 1
fi

# Inicializar Git LFS
log_info "Inicializando Git LFS..."
git lfs install

# Configurar tracking para arquivos .keras
log_info "Configurando tracking para arquivos .keras..."
git lfs track "*.keras"
git lfs track "*.h5"
git lfs track "*.pkl"
git lfs track "*.joblib"

# Adicionar .gitattributes
git add .gitattributes

# Verificar se o modelo existe
if [ -f "best_model.keras" ]; then
    log_info "Modelo encontrado: best_model.keras"
    
    # Verificar tamanho
    file_size=$(stat -f%z "best_model.keras" 2>/dev/null || stat -c%s "best_model.keras" 2>/dev/null)
    file_size_mb=$((file_size / 1024 / 1024))
    
    log_info "Tamanho do modelo: ${file_size_mb}MB"
    
    if [ $file_size_mb -gt 100 ]; then
        log_warning "Modelo > 100MB - Git LFS necessário"
        
        # Remover do cache normal se já foi adicionado
        git rm --cached best_model.keras 2>/dev/null || true
        
        # Adicionar via LFS
        git add best_model.keras
        
        log_success "Modelo adicionado via Git LFS"
    else
        log_info "Modelo < 100MB - Git normal OK"
        git add best_model.keras
    fi
else
    log_warning "Modelo best_model.keras não encontrado"
    log_info "Baixe o modelo primeiro ou use modo DEV"
fi

# Commit das mudanças
log_info "Fazendo commit das configurações LFS..."
git commit -m "feat: Configurar Git LFS para arquivos de modelo grandes"

# Verificar configuração LFS
log_info "Verificando configuração Git LFS..."
echo ""
echo "📋 Arquivos trackados pelo LFS:"
git lfs ls-files

echo ""
echo "📊 Status do LFS:"
git lfs status

echo ""
log_success "Git LFS configurado com sucesso!"
echo ""
echo "🚀 Próximos passos:"
echo "   1. git push (vai usar LFS automaticamente)"
echo "   2. Verificar no GitHub se aparece 'LFS' ao lado do arquivo"
echo "   3. Deploy vai funcionar normalmente"
echo ""
echo "💡 Limites do GitHub LFS:"
echo "   - 1GB grátis por mês"
echo "   - Arquivos até 2GB"
echo "   - Bandwidth: 1GB grátis por mês"
