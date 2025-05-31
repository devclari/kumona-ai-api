from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import io
import logging
import random
from contextlib import asynccontextmanager

from models import PredictionResponse, ErrorResponse, HealthResponse, APIInfo, DiseaseClass

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock ML Service para teste
class MockMLService:
    def __init__(self):
        self.is_loaded = True
        self.class_names = ['cataract', 'diabetic_retinopathy', 'glaucoma', 'normal']
    
    def load_model(self):
        logger.info("✅ Mock model loaded successfully")
        return True
    
    def predict(self, image):
        # Simulação de predição
        predicted_class = random.choice(self.class_names)
        confidence = random.uniform(70, 99)
        
        # Criar predições aleatórias que somam 100%
        remaining = 100 - confidence
        other_classes = [c for c in self.class_names if c != predicted_class]
        
        all_predictions = {predicted_class: confidence}
        for i, class_name in enumerate(other_classes):
            if i == len(other_classes) - 1:
                all_predictions[class_name] = remaining
            else:
                value = random.uniform(0, remaining / 2)
                all_predictions[class_name] = value
                remaining -= value
        
        logger.info(f"Mock prediction: {predicted_class} with {confidence:.2f}% confidence")
        return predicted_class, confidence, all_predictions
    
    def is_model_loaded(self):
        return self.is_loaded

# Instância do serviço mock
ml_service = MockMLService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    logger.info("🚀 Starting Eye Disease Classifier API (Mock Mode)...")
    
    # Carregar modelo na inicialização
    if not ml_service.load_model():
        logger.error("❌ Failed to load model on startup")
        raise RuntimeError("Failed to load ML model")
    
    logger.info("✅ API started successfully")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down API...")

# Criar aplicação FastAPI
app = FastAPI(
    title="Eye Disease Classifier API",
    description="""
    API para classificação de doenças oculares usando deep learning.
    
    **MODO DE TESTE** - Esta versão usa predições simuladas para demonstração.
    
    Esta API pode detectar as seguintes condições:
    - **Catarata** (cataract)
    - **Retinopatia Diabética** (diabetic_retinopathy) 
    - **Glaucoma** (glaucoma)
    - **Normal** (normal)
    
    ## Como usar:
    1. Faça upload de uma imagem do olho usando o endpoint `/predict`
    2. A API retornará a classificação e a confiança da predição
    
    ## Formatos suportados:
    - JPEG (.jpg, .jpeg)
    - PNG (.png)
    """,
    version="1.0.0-mock",
    contact={
        "name": "Eye Disease Classifier API",
        "email": "support@example.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Formatos de imagem suportados
SUPPORTED_FORMATS = {"jpg", "jpeg", "png"}

def validate_image(file: UploadFile) -> Image.Image:
    """Valida e processa o arquivo de imagem"""
    try:
        # Verificar tipo de arquivo
        if not file.content_type or not file.content_type.startswith("image/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be an image"
            )
        
        # Verificar extensão
        file_extension = file.filename.split(".")[-1].lower() if file.filename else ""
        if file_extension not in SUPPORTED_FORMATS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported image format. Supported formats: {', '.join(SUPPORTED_FORMATS)}"
            )
        
        # Ler e validar imagem
        image_data = file.file.read()
        if len(image_data) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file"
            )
        
        # Converter para PIL Image
        image = Image.open(io.BytesIO(image_data))
        
        # Converter para RGB se necessário
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        return image
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating image: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid image file"
        )

@app.get("/", response_model=APIInfo)
async def root():
    """Informações básicas da API"""
    return APIInfo(
        name="Eye Disease Classifier API (Mock)",
        description="API para classificação de doenças oculares usando deep learning - Modo de teste",
        version="1.0.0-mock",
        supported_formats=list(SUPPORTED_FORMATS),
        diseases=[disease.value for disease in DiseaseClass]
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        model_loaded=ml_service.is_model_loaded(),
        version="1.0.0-mock"
    )

@app.post("/predict", response_model=PredictionResponse)
async def predict_disease(file: UploadFile = File(..., description="Imagem do olho para classificação")):
    """
    Classifica doenças oculares a partir de uma imagem
    
    **MODO DE TESTE** - Retorna predições simuladas para demonstração.
    
    - **file**: Arquivo de imagem (JPEG, PNG)
    
    Retorna a classificação da doença com a confiança da predição.
    """
    try:
        # Verificar se o modelo está carregado
        if not ml_service.is_model_loaded():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="ML model not available"
            )
        
        # Validar e processar imagem
        image = validate_image(file)
        
        # Fazer predição
        predicted_class, confidence, all_predictions = ml_service.predict(image)
        
        return PredictionResponse(
            predicted_class=DiseaseClass(predicted_class),
            confidence=round(confidence, 2),
            all_predictions={k: round(v, 2) for k, v in all_predictions.items()}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in prediction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during prediction"
        )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handler personalizado para exceções HTTP"""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            detail=f"Status code: {exc.status_code}"
        ).dict()
    )

if __name__ == "__main__":
    uvicorn.run(
        "app_simple:app",
        host="0.0.0.0",
        port=8080,
        reload=False,
        log_level="info"
    )
