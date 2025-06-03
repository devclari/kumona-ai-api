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
