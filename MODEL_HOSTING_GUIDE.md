# 🏗️ Guia de Hospedagem do Modelo (160.9MB)

## 🚨 **Problema Identificado**
- Modelo: `best_model.keras` (160.9MB)
- Railway/Render: Timeout durante download no build
- Google Drive: Rate limits e lentidão

## 🌟 **Soluções Recomendadas**

### **🎯 1. Hugging Face Hub (MAIS RECOMENDADO)**

**Por que Hugging Face?**
- ✅ **Gratuito** e confiável
- ✅ **CDN global** super rápido
- ✅ **Sem limites** de download
- ✅ **Versionamento** automático
- ✅ **API simples** para download

**Como configurar:**

1. **Criar conta**: https://huggingface.co/join
2. **Criar repositório**: 
   - Nome: `eye-disease-classifier`
   - Tipo: Model
   - Público

3. **Upload do modelo**:
```bash
# Instalar huggingface_hub
pip install huggingface_hub

# Login (obter token em: https://huggingface.co/settings/tokens)
huggingface-cli login

# Upload
python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj='best_model.keras',
    path_in_repo='best_model.keras',
    repo_id='devclari/eye-disease-classifier',
    repo_type='model'
)
print('✅ Modelo enviado para Hugging Face!')
"
```

4. **URL final**: 
```
https://huggingface.co/devclari/eye-disease-classifier/resolve/main/best_model.keras
```

### **🎯 2. GitHub Releases**

**Como configurar:**

1. **Ir para**: https://github.com/devclari/kumona-ai-api/releases
2. **Create a new release**:
   - Tag: `v1.0.0`
   - Title: `Eye Disease Model v1.0.0`
   - Description: `TensorFlow model for eye disease classification`
3. **Attach files**: Arrastar `best_model.keras`
4. **Publish release**

**URL final**:
```
https://github.com/devclari/kumona-ai-api/releases/download/v1.0.0/best_model.keras
```

### **🎯 3. Google Cloud Storage**

**Como configurar:**

1. **Criar bucket**:
```bash
gsutil mb gs://eye-disease-models
```

2. **Upload modelo**:
```bash
gsutil cp best_model.keras gs://eye-disease-models/
```

3. **Tornar público**:
```bash
gsutil acl ch -u AllUsers:R gs://eye-disease-models/best_model.keras
```

**URL final**:
```
https://storage.googleapis.com/eye-disease-models/best_model.keras
```

### **🎯 4. AWS S3**

**Como configurar:**

1. **Criar bucket** no AWS Console
2. **Upload** do arquivo
3. **Configurar permissões** públicas
4. **Obter URL** pública

**URL final**:
```
https://your-bucket.s3.amazonaws.com/models/best_model.keras
```

## 🔧 **Implementação no Código**

O código já está preparado para múltiplas fontes! O arquivo `model_downloader.py` tenta automaticamente:

1. **Hugging Face** (mais rápido)
2. **GitHub Releases** (confiável)
3. **Google Cloud Storage** (se configurado)
4. **Google Drive** (fallback)

### **Para atualizar as URLs:**

Edite o arquivo `model_downloader.py`:

```python
self.download_sources = [
    {
        "name": "Hugging Face",
        "url": "https://huggingface.co/devclari/eye-disease-classifier/resolve/main/best_model.keras",
        "method": self._download_from_url,
        "timeout": 300
    },
    {
        "name": "GitHub Releases",
        "url": "https://github.com/devclari/kumona-ai-api/releases/download/v1.0.0/best_model.keras",
        "method": self._download_from_url,
        "timeout": 300
    },
    # ... outras fontes
]
```

## 🚀 **Passos para Deploy Remoto**

### **Opção A: Hugging Face (Recomendado)**

1. **Upload para Hugging Face**:
```bash
# Se você tem o modelo localmente
python -c "
from huggingface_hub import HfApi
api = HfApi()
api.upload_file(
    path_or_fileobj='best_model.keras',
    path_in_repo='best_model.keras',
    repo_id='devclari/eye-disease-classifier',
    repo_type='model'
)
"
```

2. **Atualizar URL no código**:
```python
# Em model_downloader.py, primeira fonte:
"url": "https://huggingface.co/devclari/eye-disease-classifier/resolve/main/best_model.keras"
```

3. **Commit e push**:
```bash
git add .
git commit -m "feat: Adicionar download multi-fonte com Hugging Face"
git push
```

4. **Deploy no Railway**:
   - Vai para Railway.app
   - Deploy do repositório
   - Agora vai funcionar! ✅

### **Opção B: GitHub Releases**

1. **Criar release** no GitHub com o modelo
2. **Atualizar URL** no código
3. **Deploy**

## 📊 **Comparação de Plataformas**

| Plataforma | Velocidade | Confiabilidade | Facilidade | Custo |
|------------|------------|----------------|------------|-------|
| Hugging Face | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Grátis |
| GitHub Releases | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | Grátis |
| Google Cloud | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Pago |
| AWS S3 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Pago |
| Google Drive | ⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Grátis |

## 🧪 **Teste Local**

Para testar o download:

```bash
python model_downloader.py
```

Ou:

```python
from model_downloader import download_model

if download_model():
    print("✅ Modelo baixado com sucesso!")
else:
    print("❌ Falha no download")
```

## 🔄 **Versionamento de Modelos**

### **Para futuras versões:**

1. **Hugging Face**: Upload com nome diferente
   ```
   best_model_v2.keras
   best_model_v3.keras
   ```

2. **GitHub**: Criar nova release
   ```
   v1.0.0 -> best_model.keras
   v1.1.0 -> best_model_v1.1.keras
   ```

3. **Configurar no código**:
   ```python
   MODEL_VERSION = os.getenv("MODEL_VERSION", "v1.0.0")
   model_url = f"https://github.com/.../releases/download/{MODEL_VERSION}/best_model.keras"
   ```

## 🚨 **Troubleshooting**

### **Se o download ainda falhar:**

1. **Verificar logs**:
```bash
# No Railway/Render, verificar build logs
# Procurar por mensagens de timeout ou erro de rede
```

2. **Reduzir timeout**:
```python
# Em model_downloader.py
"timeout": 180  # Reduzir de 300 para 180
```

3. **Usar CDN**:
```python
# Adicionar CDN como primeira opção
{
    "name": "CDN",
    "url": "https://cdn.jsdelivr.net/gh/devclari/kumona-ai-api@main/best_model.keras",
    "method": self._download_from_url,
    "timeout": 120
}
```

## 🎯 **Recomendação Final**

**Use Hugging Face Hub!**

1. **Mais rápido** para download
2. **Mais confiável** que Google Drive
3. **Gratuito** e sem limites
4. **Fácil** de configurar
5. **Profissional** para ML

### **Próximos passos:**
1. ✅ Criar conta no Hugging Face
2. ✅ Upload do modelo
3. ✅ Atualizar URL no código
4. ✅ Commit e push
5. ✅ Deploy no Railway

**Resultado**: Deploy funcionando em 5-10 minutos! 🚀
