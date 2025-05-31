#!/usr/bin/env python3
"""
Script de teste para a Eye Disease Classifier API
"""

import requests
import json
import sys
from pathlib import Path

def test_api(base_url="http://localhost:8080"):
    """Testa os endpoints da API"""
    
    print(f"🧪 Testando API em: {base_url}")
    print("=" * 50)
    
    # Teste 1: Health Check
    print("1️⃣ Testando Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status')}")
            print(f"   ✅ Modelo carregado: {data.get('model_loaded')}")
            print(f"   ✅ Versão: {data.get('version')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Erro na conexão: {e}")
        return False
    
    # Teste 2: Informações da API
    print("\n2️⃣ Testando informações da API...")
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Nome: {data.get('name')}")
            print(f"   ✅ Versão: {data.get('version')}")
            print(f"   ✅ Formatos suportados: {data.get('supported_formats')}")
            print(f"   ✅ Doenças: {data.get('diseases')}")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 3: Documentação
    print("\n3️⃣ Testando documentação...")
    try:
        response = requests.get(f"{base_url}/docs", timeout=10)
        if response.status_code == 200:
            print("   ✅ Documentação Swagger disponível")
        else:
            print(f"   ❌ Erro: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    # Teste 4: Endpoint de predição (sem arquivo)
    print("\n4️⃣ Testando endpoint de predição (sem arquivo)...")
    try:
        response = requests.post(f"{base_url}/predict", timeout=10)
        if response.status_code == 422:
            print("   ✅ Validação funcionando (erro esperado sem arquivo)")
        else:
            print(f"   ⚠️ Status inesperado: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro: {e}")
    
    print("\n" + "=" * 50)
    print("✅ Testes básicos concluídos!")
    print(f"🌐 Acesse a documentação em: {base_url}/docs")
    print(f"❤️ Health check em: {base_url}/health")
    
    return True

def test_prediction_with_sample():
    """Testa predição com imagem de exemplo"""
    print("\n🖼️ Para testar com uma imagem real, use:")
    print("curl -X POST \"http://localhost:8080/predict\" \\")
    print("  -H \"accept: application/json\" \\")
    print("  -H \"Content-Type: multipart/form-data\" \\")
    print("  -F \"file=@sua_imagem.jpg\"")

if __name__ == "__main__":
    # Permitir URL customizada via argumento
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"
    
    if test_api(base_url):
        test_prediction_with_sample()
    else:
        sys.exit(1)
