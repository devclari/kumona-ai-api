from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from PIL import Image
import io
import logging
import os
from contextlib import asynccontextmanager

from models import PredictionResponse, ErrorResponse, HealthResponse, APIInfo, DiseaseClass
from ml_service import ml_service
from monitoring import log_request, log_prediction, log_health_check, structured_logger, metrics
from production_config import get_config

# Importar MLFlow
from mlflow_utils import setup_mlflow_for_api, cleanup_mlflow_for_api, mlflow_track_prediction, mlflow_track_health_check

# Carregar configurações
config = get_config()

# Configurar logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL.upper()),
    format=config.LOG_FORMAT
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gerencia o ciclo de vida da aplicação"""
    # Startup
    structured_logger.log_startup()
    logger.info("🚀 Starting Eye Disease Classifier API...")

    # Configurar MLFlow
    mlflow_setup_success = setup_mlflow_for_api()
    if mlflow_setup_success:
        logger.info("✅ MLFlow configurado com sucesso")
    else:
        logger.warning("⚠️ MLFlow não pôde ser configurado, continuando sem tracking")

    # Carregar modelo na inicialização
    import time
    start_time = time.time()

    try:
        if not ml_service.load_model():
            structured_logger.log_model_load(False, error="Failed to load model")
            logger.error("❌ Failed to load model on startup")
            raise RuntimeError("Failed to load ML model")

        load_time = time.time() - start_time
        structured_logger.log_model_load(True, load_time)
        logger.info("✅ API started successfully")

    except Exception as e:
        load_time = time.time() - start_time
        structured_logger.log_model_load(False, load_time, str(e))
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down API...")

    # Cleanup MLFlow
    cleanup_mlflow_for_api()

    structured_logger.log_shutdown()
    logger.info("✅ API shutdown completed")

# Criar aplicação FastAPI
app = FastAPI(
    **config.get_fastapi_config(),
    lifespan=lifespan
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    **config.get_cors_config()
)

# Formatos de imagem suportados
SUPPORTED_FORMATS = config.SUPPORTED_FORMATS

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
@log_request
async def root():
    """Informações básicas da API"""
    return APIInfo(
        name="Eye Disease Classifier API",
        description="API para classificação de doenças oculares usando deep learning",
        version="1.0.0",
        supported_formats=list(SUPPORTED_FORMATS),
        diseases=[disease.value for disease in DiseaseClass]
    )

@app.get("/health", response_model=HealthResponse)
@mlflow_track_health_check
async def health_check():
    """Health check endpoint"""
    log_health_check()
    return HealthResponse(
        status="healthy",
        model_loaded=ml_service.is_model_loaded(),
        version="1.0.0"
    )

@app.get("/metrics")
async def get_metrics():
    """Endpoint para métricas da aplicação"""
    return metrics.get_metrics()

@app.post("/predict", response_model=PredictionResponse)
@log_prediction
@mlflow_track_prediction
async def predict_disease(file: UploadFile = File(..., description="Imagem do olho para classificação")):
    """
    Classifica doenças oculares a partir de uma imagem
    
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
        "app:app",
        **config.get_uvicorn_config()
    )
