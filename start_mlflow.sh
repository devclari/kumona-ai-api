#!/bin/bash

# Script para inicializar a API com MLFlow
# Uso: ./start_mlflow.sh

set -e

echo "🚀 Iniciando Eye Disease Classifier API com MLFlow"
echo "=================================================="

# Verificar se Docker está instalado
if ! command -v docker &> /dev/null; then
    echo "❌ Docker não está instalado. Por favor, instale o Docker primeiro."
    exit 1
fi

# Verificar se Docker Compose está instalado
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose não está instalado. Por favor, instale o Docker Compose primeiro."
    exit 1
fi

# Criar diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p mlruns
mkdir -p mlflow_artifacts
mkdir -p logs

# Definir permissões
chmod 755 mlruns mlflow_artifacts logs

# Parar containers existentes (se houver)
echo "🛑 Parando containers existentes..."
docker-compose down --remove-orphans 2>/dev/null || true

# Construir e iniciar serviços
echo "🔨 Construindo e iniciando serviços..."
docker-compose up -d --build

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços ficarem prontos..."

# Função para verificar se um serviço está pronto
check_service() {
    local url=$1
    local service_name=$2
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $service_name está pronto!"
            return 0
        fi
        
        echo "   Tentativa $attempt/$max_attempts - Aguardando $service_name..."
        sleep 2
        attempt=$((attempt + 1))
    done
    
    echo "❌ $service_name não ficou pronto após $max_attempts tentativas"
    return 1
}

# Verificar MLFlow
if ! check_service "http://localhost:5000/health" "MLFlow"; then
    echo "❌ MLFlow não está respondendo. Verificando logs..."
    docker-compose logs mlflow
    exit 1
fi

# Verificar API
if ! check_service "http://localhost:8080/health" "API"; then
    echo "❌ API não está respondendo. Verificando logs..."
    docker-compose logs api
    exit 1
fi

echo ""
echo "🎉 Todos os serviços estão prontos!"
echo ""
echo "🌐 Acesse:"
echo "   API: http://localhost:8080"
echo "   API Docs: http://localhost:8080/docs"
echo "   MLFlow UI: http://localhost:5000"
echo "   Health Check: http://localhost:8080/health"
echo ""
echo "📊 Para testar a integração:"
echo "   python test_mlflow_integration.py"
echo ""
echo "📋 Para ver logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar:"
echo "   docker-compose down"
echo ""
echo "✅ Setup completo!"
