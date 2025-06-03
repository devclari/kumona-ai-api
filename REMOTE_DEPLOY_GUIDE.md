# 🌐 Deploy Remoto a partir do Git

## 🎯 Plataformas de Deploy Automático

Seu repositório está pronto para deploy em várias plataformas cloud que fazem deploy direto do Git:

**📦 Repositório**: https://github.com/devclari/kumona-ai-api.git

## 🚀 Opção 1: Railway (Recomendado - Mais Fácil)

### Por que Railway?
- ✅ Deploy automático do Git
- ✅ Suporte nativo ao Docker
- ✅ Free tier generoso
- ✅ Setup em 2 minutos

### Como fazer deploy:

1. **Acesse**: https://railway.app
2. **Login** com GitHub
3. **New Project** → **Deploy from GitHub repo**
4. **Selecione**: `devclari/kumona-ai-api`
5. **Configure**:
   ```
   Build Command: (deixe vazio - usa Dockerfile)
   Start Command: (deixe vazio - usa Dockerfile)
   ```
6. **Environment Variables**:
   ```
   PORT=8080
   MLFLOW_TRACKING_URI=http://localhost:5000
   ENABLE_MLFLOW_TRACKING=false
   ```

### URL final:
- Sua API ficará em: `https://seu-app.railway.app`
- Docs: `https://seu-app.railway.app/docs`

## 🚀 Opção 2: Render

### Como fazer deploy:

1. **Acesse**: https://render.com
2. **New** → **Web Service**
3. **Connect Repository**: `https://github.com/devclari/kumona-ai-api`
4. **Configure**:
   ```
   Name: eye-disease-classifier
   Environment: Docker
   Plan: Free
   ```
5. **Environment Variables**:
   ```
   PORT=8080
   PYTHON_VERSION=3.11
   ```

### URL final:
- `https://eye-disease-classifier.onrender.com`

## 🚀 Opção 3: Google Cloud Run

### Deploy automático via GitHub Actions:

1. **Configure GitHub Secrets** no seu repo:
   ```
   GCP_PROJECT_ID=seu-projeto-id
   GCP_SA_KEY=sua-service-account-key
   ```

2. **Crie arquivo** `.github/workflows/deploy.yml`:
   ```yaml
   name: Deploy to Cloud Run
   on:
     push:
       branches: [main]
   
   jobs:
     deploy:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v2
         
         - name: Setup Cloud SDK
           uses: google-github-actions/setup-gcloud@v0
           with:
             project_id: ${{ secrets.GCP_PROJECT_ID }}
             service_account_key: ${{ secrets.GCP_SA_KEY }}
             
         - name: Build and Deploy
           run: |
             gcloud builds submit --tag gcr.io/${{ secrets.GCP_PROJECT_ID }}/eye-disease-classifier
             gcloud run deploy eye-disease-classifier \
               --image gcr.io/${{ secrets.GCP_PROJECT_ID }}/eye-disease-classifier \
               --platform managed \
               --region us-central1 \
               --allow-unauthenticated
   ```

## 🚀 Opção 4: Heroku

### Como fazer deploy:

1. **Instale Heroku CLI**
2. **Login**: `heroku login`
3. **Crie app**: `heroku create eye-disease-classifier`
4. **Configure**:
   ```bash
   heroku config:set PORT=8080
   heroku config:set PYTHON_VERSION=3.11
   ```
5. **Deploy**:
   ```bash
   git push heroku main
   ```

## 🚀 Opção 5: Vercel

### Como fazer deploy:

1. **Acesse**: https://vercel.com
2. **Import Project** do GitHub
3. **Selecione**: `devclari/kumona-ai-api`
4. **Configure**:
   ```
   Framework Preset: Other
   Build Command: (deixe vazio)
   Output Directory: (deixe vazio)
   Install Command: pip install -r requirements.txt
   ```

## 🚀 Opção 6: DigitalOcean App Platform

### Como fazer deploy:

1. **Acesse**: https://cloud.digitalocean.com/apps
2. **Create App** → **GitHub**
3. **Selecione**: `devclari/kumona-ai-api`
4. **Configure**:
   ```
   Type: Web Service
   Source: Dockerfile
   HTTP Port: 8080
   ```

## 🐳 Deploy com Docker Hub + Cloud

### Passo 1: Configurar GitHub Actions para Docker Hub

Crie `.github/workflows/docker.yml`:
```yaml
name: Build and Push Docker
on:
  push:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}
          
      - name: Build and Push
        uses: docker/build-push-action@v2
        with:
          context: .
          file: ./Dockerfile.mlflow
          push: true
          tags: seu-usuario/eye-disease-classifier:latest
```

### Passo 2: Deploy em qualquer cloud
```bash
# Em qualquer servidor cloud:
docker run -d -p 8080:8080 seu-usuario/eye-disease-classifier:latest
```

## 🌟 RECOMENDAÇÃO: Railway (Mais Fácil)

### Por que Railway é a melhor opção:

1. **Setup em 2 minutos**
2. **Deploy automático** a cada push no Git
3. **Suporte nativo ao Docker**
4. **Free tier** com 500 horas/mês
5. **URL personalizada** incluída
6. **Logs em tempo real**

### Passo a passo Railway:

1. **Acesse**: https://railway.app
2. **"Start a New Project"**
3. **"Deploy from GitHub repo"**
4. **Autorize** acesso ao GitHub
5. **Selecione** `devclari/kumona-ai-api`
6. **Aguarde** o build (5-10 minutos)
7. **Acesse** sua URL gerada

### Configurações Railway:
```
Environment Variables:
- PORT: 8080
- ENABLE_MLFLOW_TRACKING: false
- LOG_LEVEL: INFO

Build:
- Detecta automaticamente o Dockerfile.mlflow
- Build time: ~5-10 minutos
- Deploy automático a cada push
```

## 📊 Comparação de Plataformas

| Plataforma | Facilidade | Free Tier | Docker | Auto Deploy |
|------------|------------|-----------|---------|-------------|
| Railway    | ⭐⭐⭐⭐⭐ | 500h/mês  | ✅      | ✅          |
| Render     | ⭐⭐⭐⭐   | 750h/mês  | ✅      | ✅          |
| Vercel     | ⭐⭐⭐     | Ilimitado | ❌      | ✅          |
| Heroku     | ⭐⭐⭐     | 550h/mês  | ✅      | ✅          |
| Cloud Run  | ⭐⭐       | Pay-per-use| ✅     | ⚙️          |

## 🎯 PRÓXIMOS PASSOS

### Opção Recomendada (Railway):
1. **Acesse**: https://railway.app
2. **Deploy** do seu repo: `devclari/kumona-ai-api`
3. **Aguarde** 5-10 minutos
4. **Teste** sua API online!

### Após o Deploy:
- ✅ **API Online**: `https://seu-app.railway.app`
- ✅ **Docs**: `https://seu-app.railway.app/docs`
- ✅ **Health**: `https://seu-app.railway.app/health`
- ✅ **Deploy Automático**: A cada push no Git

## 🔧 Troubleshooting

### Se o build falhar:
1. **Verifique logs** na plataforma
2. **Dockerfile.mlflow** está correto
3. **requirements.txt** tem todas as dependências

### Para habilitar MLFlow remoto:
1. **Deploy MLFlow** separadamente
2. **Configure** `MLFLOW_TRACKING_URI`
3. **Habilite** `ENABLE_MLFLOW_TRACKING=true`

---

**🚀 Seu código está pronto para deploy remoto!**

Escolha uma plataforma e em poucos minutos sua API estará online! 🌐
