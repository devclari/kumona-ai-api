from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class DiseaseClass(str, Enum):
    """Enum para as classes de doenças oculares"""
    CATARACT = "cataract"
    DIABETIC_RETINOPATHY = "diabetic_retinopathy"
    GLAUCOMA = "glaucoma"
    NORMAL = "normal"

class PredictionResponse(BaseModel):
    """Modelo de resposta para predições"""
    predicted_class: DiseaseClass = Field(..., description="Classe da doença predita")
    confidence: float = Field(..., ge=0, le=100, description="Confiança da predição em porcentagem")
    all_predictions: dict = Field(..., description="Todas as predições com suas probabilidades")
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_class": "normal",
                "confidence": 95.67,
                "all_predictions": {
                    "cataract": 1.23,
                    "diabetic_retinopathy": 2.10,
                    "glaucoma": 1.00,
                    "normal": 95.67
                }
            }
        }

class ErrorResponse(BaseModel):
    """Modelo de resposta para erros"""
    error: str = Field(..., description="Mensagem de erro")
    detail: Optional[str] = Field(None, description="Detalhes adicionais do erro")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "Invalid image format",
                "detail": "Only JPEG, PNG and JPG formats are supported"
            }
        }

class HealthResponse(BaseModel):
    """Modelo de resposta para health check"""
    status: str = Field(..., description="Status da API")
    model_loaded: bool = Field(..., description="Se o modelo está carregado")
    version: str = Field(..., description="Versão da API")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "model_loaded": True,
                "version": "1.0.0"
            }
        }

class APIInfo(BaseModel):
    """Informações básicas da API"""
    name: str = Field(..., description="Nome da API")
    description: str = Field(..., description="Descrição da API")
    version: str = Field(..., description="Versão da API")
    supported_formats: List[str] = Field(..., description="Formatos de imagem suportados")
    diseases: List[str] = Field(..., description="Doenças que podem ser detectadas")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Eye Disease Classifier API",
                "description": "API para classificação de doenças oculares usando deep learning",
                "version": "1.0.0",
                "supported_formats": ["jpg", "jpeg", "png"],
                "diseases": ["cataract", "diabetic_retinopathy", "glaucoma", "normal"]
            }
        }
