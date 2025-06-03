#!/bin/bash

# Script para subir no Git e fazer deploy
# Uso: ./git_deploy.sh [mensagem_commit] [tipo_deploy] [porta]

set -e

# Configurações
COMMIT_MESSAGE=${1:-"feat: Implementação completa MLFlow - Deploy ready"}
DEPLOY_TYPE=${2:-"api"}
PORT=${3:-8080}

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

# Função para verificar se Git está configurado
check_git_config() {
    log_info "Verificando configuração do Git..."
    
    if ! git config user.name > /dev/null 2>&1; then
        log_warning "Nome do usuário Git não configurado"
        read -p "Digite seu nome: " git_name
        git config user.name "$git_name"
    fi
    
    if ! git config user.email > /dev/null 2>&1; then
        log_warning "Email do usuário Git não configurado"
        read -p "Digite seu email: " git_email
        git config user.email "$git_email"
    fi
    
    log_success "Git configurado: $(git config user.name) <$(git config user.email)>"
}

# Função para verificar se é um repositório Git
check_git_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        log_warning "Não é um repositório Git. Inicializando..."
        git init
        log_success "Repositório Git inicializado"
    else
        log_success "Repositório Git encontrado"
    fi
}

# Função para criar .gitignore se não existir
create_gitignore() {
    if [ ! -f .gitignore ]; then
        log_info "Criando .gitignore..."
        cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# MLFlow
mlruns/
mlflow_artifacts/
model_info.txt

# Model files (grandes demais para Git)
*.keras
*.h5
*.pkl
*.joblib

# Environment variables
.env

# Docker
.dockerignore

# Temporary files
*.tmp
*.temp
EOF
        log_success ".gitignore criado"
    else
        log_success ".gitignore já existe"
    fi
}

# Função para verificar arquivos grandes
check_large_files() {
    log_info "Verificando arquivos grandes..."
    
    # Verificar se o modelo está sendo commitado
    if git ls-files --cached | grep -q "best_model.keras"; then
        log_warning "Modelo best_model.keras está sendo commitado (arquivo grande)"
        log_info "Removendo do staging..."
        git reset HEAD best_model.keras 2>/dev/null || true
        echo "best_model.keras" >> .gitignore
    fi
    
    # Verificar outros arquivos grandes
    large_files=$(find . -type f -size +50M -not -path "./.git/*" -not -path "./mlruns/*" 2>/dev/null || true)
    if [ -n "$large_files" ]; then
        log_warning "Arquivos grandes encontrados:"
        echo "$large_files"
        log_info "Considere usar Git LFS para arquivos grandes"
    fi
}

# Função para fazer commit e push
git_commit_push() {
    log_info "Preparando commit..."
    
    # Verificar se há mudanças
    if git diff --quiet && git diff --cached --quiet; then
        log_info "Nenhuma mudança para commitar"
        return 0
    fi
    
    # Adicionar arquivos
    log_info "Adicionando arquivos..."
    git add .
    
    # Verificar arquivos grandes novamente
    check_large_files
    
    # Mostrar status
    log_info "Status do repositório:"
    git status --short
    
    # Fazer commit
    log_info "Fazendo commit: $COMMIT_MESSAGE"
    git commit -m "$COMMIT_MESSAGE"
    log_success "Commit realizado"
    
    # Verificar se há remote configurado
    if git remote | grep -q origin; then
        log_info "Fazendo push para origin..."
        
        # Verificar se a branch atual tem upstream
        current_branch=$(git branch --show-current)
        if ! git rev-parse --abbrev-ref @{upstream} > /dev/null 2>&1; then
            log_info "Configurando upstream para branch $current_branch..."
            git push -u origin "$current_branch"
        else
            git push
        fi
        
        log_success "Push realizado com sucesso"
        
        # Mostrar URL do repositório se possível
        remote_url=$(git remote get-url origin 2>/dev/null || echo "")
        if [ -n "$remote_url" ]; then
            log_info "Repositório: $remote_url"
        fi
    else
        log_warning "Nenhum remote 'origin' configurado"
        log_info "Para adicionar um remote:"
        log_info "  git remote add origin https://github.com/usuario/repo.git"
        log_info "  git push -u origin main"
    fi
}

# Função para criar README de deploy se não existir
create_deploy_readme() {
    if [ ! -f DEPLOY_README.md ]; then
        log_info "Criando DEPLOY_README.md..."
        cat > DEPLOY_README.md << 'EOF'
# 🚀 Deploy Guide - Eye Disease Classifier API

## Quick Start

```bash
# 1. Clone o repositório
git clone <seu-repo-url>
cd kumona-ai-api

# 2. Deploy automático
./deploy_complete.sh api 8080
```

## Acessos

- **API**: http://localhost:8080
- **Docs**: http://localhost:8080/docs  
- **MLFlow**: http://localhost:5000

## Comandos Úteis

```bash
# Deploy da API
./deploy_complete.sh api 8080

# Deploy apenas do modelo
./deploy_complete.sh model 8001

# Deploy com Docker
./deploy_complete.sh docker 8080

# Testar integração
python test_mlflow_integration.py
```

## Documentação

- [Guia MLFlow](MLFLOW_GUIDE.md)
- [Guia de Deploy](MLFLOW_DEPLOY_GUIDE.md)
- [Resumo de Deploy](DEPLOY_SUMMARY.md)
EOF
        log_success "DEPLOY_README.md criado"
    fi
}

# Função para executar deploy
execute_deploy() {
    log_info "Executando deploy..."
    
    # Verificar se o script de deploy existe
    if [ ! -f "./deploy_complete.sh" ]; then
        log_error "Script deploy_complete.sh não encontrado"
        exit 1
    fi
    
    # Tornar executável se necessário
    chmod +x deploy_complete.sh
    
    # Executar deploy
    log_info "Iniciando deploy tipo: $DEPLOY_TYPE na porta: $PORT"
    ./deploy_complete.sh "$DEPLOY_TYPE" "$PORT"
}

# Função para mostrar informações finais
show_final_info() {
    echo ""
    echo "🎉 PROCESSO CONCLUÍDO COM SUCESSO!"
    echo "=================================="
    echo ""
    echo "📋 Resumo:"
    echo "  ✅ Código commitado no Git"
    echo "  ✅ Deploy executado ($DEPLOY_TYPE)"
    echo "  ✅ Serviço rodando na porta $PORT"
    echo ""
    echo "🌐 Acessos:"
    echo "  📱 API: http://localhost:$PORT"
    if [ "$DEPLOY_TYPE" = "api" ]; then
        echo "  📚 Docs: http://localhost:$PORT/docs"
        echo "  ❤️ Health: http://localhost:$PORT/health"
    fi
    echo "  📊 MLFlow: http://localhost:5000"
    echo ""
    echo "🔧 Comandos úteis:"
    echo "  📊 Testar: python test_mlflow_integration.py"
    echo "  📋 Logs: docker-compose logs -f"
    echo "  🛑 Parar: Ctrl+C ou docker-compose down"
    echo ""
    
    # Mostrar URL do Git se disponível
    remote_url=$(git remote get-url origin 2>/dev/null || echo "")
    if [ -n "$remote_url" ]; then
        echo "📦 Repositório: $remote_url"
        echo ""
    fi
}

# Função para mostrar ajuda
show_help() {
    echo "🚀 Git + Deploy Script - Eye Disease Classifier"
    echo ""
    echo "Uso: $0 [mensagem] [tipo] [porta]"
    echo ""
    echo "Parâmetros:"
    echo "  mensagem  - Mensagem do commit (padrão: feat: Implementação completa MLFlow)"
    echo "  tipo      - Tipo de deploy: api, model, docker (padrão: api)"
    echo "  porta     - Porta do serviço (padrão: 8080)"
    echo ""
    echo "Exemplos:"
    echo "  $0                                    # Commit padrão + deploy API:8080"
    echo "  $0 \"fix: correção bug\" api 8080       # Commit custom + deploy API:8080"
    echo "  $0 \"feat: nova versão\" docker 8080   # Commit custom + deploy Docker:8080"
    echo ""
    echo "O script irá:"
    echo "  1. Configurar Git (se necessário)"
    echo "  2. Criar .gitignore (se necessário)"
    echo "  3. Fazer commit das mudanças"
    echo "  4. Fazer push para origin (se configurado)"
    echo "  5. Executar deploy automaticamente"
}

# Função principal
main() {
    echo "🚀 Git + Deploy - Eye Disease Classifier API"
    echo "============================================"
    
    # Verificar argumentos
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    log_info "Mensagem do commit: $COMMIT_MESSAGE"
    log_info "Tipo de deploy: $DEPLOY_TYPE"
    log_info "Porta: $PORT"
    echo ""
    
    # Executar passos
    check_git_config
    check_git_repo
    create_gitignore
    create_deploy_readme
    git_commit_push
    
    echo ""
    log_success "Git: Código enviado com sucesso!"
    echo ""
    
    # Perguntar se quer fazer deploy
    read -p "🚀 Executar deploy agora? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        execute_deploy
        show_final_info
    else
        log_info "Deploy cancelado pelo usuário"
        log_info "Para fazer deploy depois: ./deploy_complete.sh $DEPLOY_TYPE $PORT"
    fi
}

# Capturar Ctrl+C
trap 'log_info "Processo interrompido pelo usuário"; exit 1' INT

# Executar função principal
main "$@"
