# 🚀 Git + Deploy Guide - Eye Disease Classifier API

## 📋 Processo Completo: Git → Deploy

Este guia mostra como subir seu código no Git e fazer deploy automaticamente.

## 🎯 Opção 1: Processo Automático (Recomendado)

### Comando Único
```bash
# Commit + Deploy automático
./git_deploy.sh
```

### Com Parâmetros Customizados
```bash
# Commit custom + Deploy específico
./git_deploy.sh "feat: nova versão do modelo" api 8080
./git_deploy.sh "fix: correção de bug" docker 8080
./git_deploy.sh "docs: atualização documentação" model 8001
```

## 🔧 Opção 2: Processo Manual

### Passo 1: Configurar Git (primeira vez)
```bash
# Configuração automática
./setup_git.sh

# Ou com repositório específico
./setup_git.sh https://github.com/seu-usuario/seu-repo.git

# Ou manual
git config --global user.name "Seu Nome"
git config --global user.email "seu@email.com"
git remote add origin https://github.com/seu-usuario/seu-repo.git
```

### Passo 2: Commit e Push
```bash
# Adicionar arquivos
git add .

# Commit
git commit -m "feat: Implementação completa MLFlow"

# Push
git push -u origin main
```

### Passo 3: Deploy
```bash
# Deploy da API
./deploy_complete.sh api 8080

# Ou deploy do modelo
./deploy_complete.sh model 8001

# Ou deploy com Docker
./deploy_complete.sh docker 8080
```

## 📁 Estrutura de Arquivos

### Scripts Criados
```
📦 Projeto/
├── 🚀 Scripts de Deploy
│   ├── git_deploy.sh              # Git + Deploy automático
│   ├── setup_git.sh               # Configuração Git
│   ├── deploy_complete.sh         # Deploy completo
│   ├── register_model_mlflow.py   # Registro modelo
│   └── deploy_mlflow.py           # Deploy programático
│
├── ⚙️ Configurações
│   ├── .gitignore                 # Arquivos ignorados
│   ├── MLproject                  # MLFlow Projects
│   ├── conda.yaml                # Ambiente Conda
│   └── Dockerfile.mlflow          # Container otimizado
│
└── 📚 Documentação
    ├── GIT_DEPLOY_README.md       # Este guia
    ├── MLFLOW_DEPLOY_GUIDE.md     # Guia detalhado
    ├── DEPLOY_SUMMARY.md          # Resumo completo
    └── MLFLOW_GUIDE.md            # Guia MLFlow
```

### Arquivos Ignorados pelo Git
```
# Não serão commitados
mlruns/                 # Dados MLFlow locais
mlflow_artifacts/       # Artefatos MLFlow
*.keras                 # Modelos (muito grandes)
*.h5                    # Modelos TensorFlow
.env                    # Variáveis de ambiente
logs/                   # Logs da aplicação
__pycache__/           # Cache Python
```

## 🌐 Repositórios Sugeridos

### GitHub
```bash
# Criar repositório no GitHub primeiro, depois:
git remote add origin https://github.com/seu-usuario/eye-disease-classifier.git
./git_deploy.sh "feat: implementação inicial"
```

### GitLab
```bash
git remote add origin https://gitlab.com/seu-usuario/eye-disease-classifier.git
./git_deploy.sh "feat: implementação inicial"
```

### Bitbucket
```bash
git remote add origin https://bitbucket.org/seu-usuario/eye-disease-classifier.git
./git_deploy.sh "feat: implementação inicial"
```

## 🔄 Fluxo de Trabalho

### Desenvolvimento
```bash
# 1. Fazer mudanças no código
# 2. Testar localmente
python test_mlflow_integration.py

# 3. Commit + Deploy
./git_deploy.sh "feat: nova funcionalidade"
```

### Produção
```bash
# 1. Clone do repositório
git clone https://github.com/seu-usuario/eye-disease-classifier.git
cd eye-disease-classifier

# 2. Deploy direto
./deploy_complete.sh docker 8080
```

### Colaboração
```bash
# 1. Pull das mudanças
git pull origin main

# 2. Deploy atualizado
./deploy_complete.sh api 8080
```

## 📊 Monitoramento Pós-Deploy

### Verificar Status
```bash
# Testar integração
python test_mlflow_integration.py

# Verificar logs
docker-compose logs -f

# Status dos serviços
docker-compose ps
```

### Acessos
- **API**: http://localhost:8080
- **Docs**: http://localhost:8080/docs
- **MLFlow**: http://localhost:5000
- **Health**: http://localhost:8080/health

## 🚨 Troubleshooting

### Problema: Git não configurado
```bash
# Solução
./setup_git.sh
```

### Problema: Remote não existe
```bash
# Solução
git remote add origin https://github.com/seu-usuario/repo.git
```

### Problema: Deploy falha
```bash
# Verificar dependências
python -c "import mlflow, tensorflow, fastapi"

# Verificar MLFlow
curl http://localhost:5000/health

# Logs detalhados
./deploy_complete.sh api 8080
```

### Problema: Arquivo muito grande
```bash
# Verificar .gitignore
cat .gitignore

# Remover do staging
git reset HEAD arquivo_grande.keras
```

## 📝 Convenções de Commit

### Tipos Recomendados
```bash
feat: nova funcionalidade
fix: correção de bug
docs: documentação
style: formatação
refactor: refatoração
test: testes
chore: manutenção
```

### Exemplos
```bash
./git_deploy.sh "feat: adicionar endpoint de métricas"
./git_deploy.sh "fix: corrigir carregamento do modelo"
./git_deploy.sh "docs: atualizar README"
./git_deploy.sh "refactor: otimizar código MLFlow"
```

## 🎯 Comandos Rápidos

### Setup Inicial
```bash
./setup_git.sh https://github.com/seu-usuario/repo.git
./git_deploy.sh "feat: implementação inicial"
```

### Deploy Rápido
```bash
./git_deploy.sh                    # Padrão: API porta 8080
./git_deploy.sh "" docker 8080     # Docker porta 8080
./git_deploy.sh "" model 8001      # Modelo porta 8001
```

### Apenas Git (sem deploy)
```bash
git add .
git commit -m "sua mensagem"
git push
```

### Apenas Deploy (sem Git)
```bash
./deploy_complete.sh api 8080
```

## 🎉 Resultado Final

Após executar `./git_deploy.sh`, você terá:

✅ **Código no Git** - Versionado e compartilhável  
✅ **Deploy Automático** - API rodando localmente  
✅ **MLFlow Ativo** - Tracking e monitoramento  
✅ **Documentação** - Guias completos  
✅ **Testes** - Validação automática  

### Acessos Finais
- 📱 **API**: http://localhost:8080/docs
- 📊 **MLFlow**: http://localhost:5000
- 📦 **Repositório**: Seu URL do Git
- 📚 **Documentação**: Arquivos MD no projeto

---

**🚀 Pronto para produção com Git + MLFlow!**
