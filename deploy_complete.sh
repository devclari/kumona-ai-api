#!/bin/bash

# Script completo para deploy da API com MLFlow
# Uso: ./deploy_complete.sh [tipo] [porta]

set -e

# Configurações padrão
DEPLOY_TYPE=${1:-"api"}  # api, model, docker, cloud
PORT=${2:-8080}
MLFLOW_URI="http://localhost:5000"
MODEL_NAME="eye-disease-model"

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funções de log
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

# Função para verificar dependências
check_dependencies() {
    log_info "Verificando dependências..."
    
    # Verificar Python
    if ! command -v python &> /dev/null; then
        log_error "Python não está instalado"
        exit 1
    fi
    
    # Verificar Docker (se necessário)
    if [[ "$DEPLOY_TYPE" == "docker" ]] && ! command -v docker &> /dev/null; then
        log_error "Docker não está instalado"
        exit 1
    fi
    
    # Verificar MLFlow
    if ! python -c "import mlflow" &> /dev/null; then
        log_error "MLFlow não está instalado. Execute: pip install mlflow"
        exit 1
    fi
    
    log_success "Dependências verificadas"
}

# Função para verificar se MLFlow está rodando
check_mlflow_server() {
    log_info "Verificando servidor MLFlow..."
    
    if curl -s -f "$MLFLOW_URI/health" > /dev/null 2>&1; then
        log_success "MLFlow está rodando em $MLFLOW_URI"
    else
        log_warning "MLFlow não está rodando"
        log_info "Iniciando MLFlow com Docker Compose..."
        
        if docker-compose up -d mlflow; then
            log_info "Aguardando MLFlow inicializar..."
            sleep 30
            
            if curl -s -f "$MLFLOW_URI/health" > /dev/null 2>&1; then
                log_success "MLFlow iniciado com sucesso"
            else
                log_error "Falha ao iniciar MLFlow"
                exit 1
            fi
        else
            log_error "Falha ao iniciar MLFlow via Docker Compose"
            exit 1
        fi
    fi
}

# Função para registrar modelo
register_model() {
    log_info "Verificando se modelo está registrado..."
    
    if python -c "
import mlflow
mlflow.set_tracking_uri('$MLFLOW_URI')
try:
    model = mlflow.tensorflow.load_model('models:/$MODEL_NAME/Production')
    print('Model exists')
except:
    print('Model not found')
" | grep -q "Model exists"; then
        log_success "Modelo já está registrado"
    else
        log_info "Registrando modelo no MLFlow..."
        if python register_model_mlflow.py; then
            log_success "Modelo registrado com sucesso"
        else
            log_error "Falha ao registrar modelo"
            exit 1
        fi
    fi
}

# Função para deploy da API completa
deploy_api() {
    log_info "Fazendo deploy da API completa..."
    
    export MLFLOW_TRACKING_URI="$MLFLOW_URI"
    export ENABLE_MODEL_REGISTRY="true"
    export MODEL_STAGE="Production"
    export PORT="$PORT"
    
    log_info "Iniciando API na porta $PORT..."
    python app.py &
    API_PID=$!
    
    # Aguardar API inicializar
    log_info "Aguardando API inicializar..."
    sleep 15
    
    # Testar API
    if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
        log_success "API está rodando em http://localhost:$PORT"
        log_info "Documentação: http://localhost:$PORT/docs"
        log_info "MLFlow UI: $MLFLOW_URI"
        
        # Manter processo vivo
        log_info "Pressione Ctrl+C para parar..."
        wait $API_PID
    else
        log_error "API não está respondendo"
        kill $API_PID 2>/dev/null || true
        exit 1
    fi
}

# Função para deploy apenas do modelo
deploy_model() {
    log_info "Fazendo deploy apenas do modelo..."
    
    log_info "Iniciando MLFlow Model Serving na porta $PORT..."
    mlflow models serve \
        --model-uri "models:/$MODEL_NAME/Production" \
        --port "$PORT" \
        --host 0.0.0.0 &
    
    MODEL_PID=$!
    
    # Aguardar modelo inicializar
    log_info "Aguardando modelo inicializar..."
    sleep 20
    
    # Testar modelo
    if curl -s -f "http://localhost:$PORT/invocations" \
        -H "Content-Type: application/json" \
        -d '{"inputs": [[[0.5]]]}' > /dev/null; then
        log_success "Modelo está servindo em http://localhost:$PORT"
        log_info "Endpoint: http://localhost:$PORT/invocations"
        
        # Manter processo vivo
        log_info "Pressione Ctrl+C para parar..."
        wait $MODEL_PID
    else
        log_error "Modelo não está respondendo"
        kill $MODEL_PID 2>/dev/null || true
        exit 1
    fi
}

# Função para deploy com Docker
deploy_docker() {
    log_info "Fazendo deploy com Docker..."
    
    # Build da imagem
    log_info "Construindo imagem Docker..."
    if docker build -f Dockerfile.mlflow -t eye-disease-classifier:latest .; then
        log_success "Imagem construída com sucesso"
    else
        log_error "Falha ao construir imagem"
        exit 1
    fi
    
    # Parar container existente se houver
    docker stop eye-disease-api 2>/dev/null || true
    docker rm eye-disease-api 2>/dev/null || true
    
    # Executar container
    log_info "Executando container na porta $PORT..."
    if docker run -d \
        --name eye-disease-api \
        --network kumona-ai-api_default \
        -p "$PORT:8080" \
        -e MLFLOW_TRACKING_URI="http://mlflow:5000" \
        -e ENABLE_MODEL_REGISTRY="true" \
        eye-disease-classifier:latest; then
        
        # Aguardar container inicializar
        log_info "Aguardando container inicializar..."
        sleep 20
        
        # Testar API
        if curl -s -f "http://localhost:$PORT/health" > /dev/null; then
            log_success "Container está rodando em http://localhost:$PORT"
            log_info "Logs: docker logs -f eye-disease-api"
            log_info "Parar: docker stop eye-disease-api"
        else
            log_error "Container não está respondendo"
            docker logs eye-disease-api
            exit 1
        fi
    else
        log_error "Falha ao executar container"
        exit 1
    fi
}

# Função para deploy em cloud
deploy_cloud() {
    log_info "Deploy em cloud não implementado neste script"
    log_info "Consulte MLFLOW_DEPLOY_GUIDE.md para instruções específicas"
    log_info "Opções disponíveis:"
    log_info "  - Google Cloud Run"
    log_info "  - AWS ECS/Fargate"
    log_info "  - Azure Container Instances"
    log_info "  - Kubernetes"
}

# Função para mostrar ajuda
show_help() {
    echo "🚀 Script de Deploy MLFlow - Eye Disease Classifier"
    echo ""
    echo "Uso: $0 [tipo] [porta]"
    echo ""
    echo "Tipos de deploy:"
    echo "  api     - Deploy da API completa (padrão)"
    echo "  model   - Deploy apenas do modelo via MLFlow"
    echo "  docker  - Deploy containerizado"
    echo "  cloud   - Instruções para deploy em cloud"
    echo ""
    echo "Exemplos:"
    echo "  $0 api 8080        # API completa na porta 8080"
    echo "  $0 model 8001      # Modelo na porta 8001"
    echo "  $0 docker 8080     # Container na porta 8080"
    echo ""
    echo "Pré-requisitos:"
    echo "  - Python 3.11+ com dependências instaladas"
    echo "  - Docker (para deploy docker)"
    echo "  - MLFlow rodando (será iniciado automaticamente)"
}

# Função principal
main() {
    echo "🚀 Deploy MLFlow - Eye Disease Classifier"
    echo "========================================"
    
    # Verificar argumentos
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        show_help
        exit 0
    fi
    
    log_info "Tipo de deploy: $DEPLOY_TYPE"
    log_info "Porta: $PORT"
    
    # Verificar dependências
    check_dependencies
    
    # Verificar MLFlow
    check_mlflow_server
    
    # Registrar modelo
    register_model
    
    # Fazer deploy baseado no tipo
    case $DEPLOY_TYPE in
        "api")
            deploy_api
            ;;
        "model")
            deploy_model
            ;;
        "docker")
            deploy_docker
            ;;
        "cloud")
            deploy_cloud
            ;;
        *)
            log_error "Tipo de deploy inválido: $DEPLOY_TYPE"
            show_help
            exit 1
            ;;
    esac
}

# Capturar Ctrl+C
trap 'log_info "Parando serviços..."; exit 0' INT

# Executar função principal
main "$@"
