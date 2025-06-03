#!/usr/bin/env python3
"""
Script para testar a integração MLFlow da API
"""

import requests
import time
import json
import os
from PIL import Image
import io
import base64

# Configurações
API_URL = "http://localhost:8080"
MLFLOW_URL = "http://localhost:5000"

def check_services():
    """Verifica se os serviços estão rodando"""
    print("🔍 Verificando serviços...")
    
    # Verificar API
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API está rodando")
        else:
            print(f"❌ API retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com a API: {e}")
        return False
    
    # Verificar MLFlow
    try:
        response = requests.get(f"{MLFLOW_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ MLFlow está rodando")
        else:
            print(f"❌ MLFlow retornou status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com MLFlow: {e}")
        return False
    
    return True

def create_test_image():
    """Cria uma imagem de teste"""
    # Criar uma imagem simples para teste
    img = Image.new('RGB', (256, 256), color='red')
    
    # Salvar em bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)
    
    return img_bytes

def test_prediction():
    """Testa uma predição"""
    print("\n🧪 Testando predição...")
    
    # Criar imagem de teste
    img_bytes = create_test_image()
    
    # Fazer predição
    files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
    
    try:
        start_time = time.time()
        response = requests.post(f"{API_URL}/predict", files=files, timeout=30)
        end_time = time.time()
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Predição realizada em {end_time - start_time:.2f}s")
            print(f"   Classe predita: {result['predicted_class']}")
            print(f"   Confiança: {result['confidence']:.2f}%")
            return True
        else:
            print(f"❌ Erro na predição: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro na requisição: {e}")
        return False

def test_multiple_predictions(count=5):
    """Testa múltiplas predições"""
    print(f"\n🔄 Testando {count} predições...")
    
    success_count = 0
    total_time = 0
    
    for i in range(count):
        print(f"   Predição {i+1}/{count}...", end=" ")
        
        img_bytes = create_test_image()
        files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
        
        try:
            start_time = time.time()
            response = requests.post(f"{API_URL}/predict", files=files, timeout=30)
            end_time = time.time()
            
            if response.status_code == 200:
                success_count += 1
                total_time += (end_time - start_time)
                print("✅")
            else:
                print(f"❌ ({response.status_code})")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ (erro: {e})")
        
        # Pequena pausa entre requisições
        time.sleep(0.5)
    
    if success_count > 0:
        avg_time = total_time / success_count
        print(f"\n📊 Resultados:")
        print(f"   Sucessos: {success_count}/{count}")
        print(f"   Tempo médio: {avg_time:.2f}s")
    
    return success_count == count

def check_mlflow_experiment():
    """Verifica se o experimento foi criado no MLFlow"""
    print("\n🔬 Verificando experimento no MLFlow...")
    
    try:
        # Listar experimentos
        response = requests.get(f"{MLFLOW_URL}/api/2.0/mlflow/experiments/search", timeout=10)
        
        if response.status_code == 200:
            experiments = response.json().get('experiments', [])
            
            # Procurar pelo experimento da API
            api_experiment = None
            for exp in experiments:
                if exp.get('name') == 'eye-disease-classifier':
                    api_experiment = exp
                    break
            
            if api_experiment:
                print(f"✅ Experimento encontrado: {api_experiment['name']}")
                print(f"   ID: {api_experiment['experiment_id']}")
                
                # Verificar runs
                exp_id = api_experiment['experiment_id']
                runs_response = requests.get(
                    f"{MLFLOW_URL}/api/2.0/mlflow/runs/search",
                    json={"experiment_ids": [exp_id]},
                    timeout=10
                )
                
                if runs_response.status_code == 200:
                    runs = runs_response.json().get('runs', [])
                    print(f"   Runs encontradas: {len(runs)}")
                    
                    if runs:
                        latest_run = runs[0]
                        metrics = latest_run.get('data', {}).get('metrics', {})
                        print(f"   Métricas na última run: {len(metrics)}")
                        
                        # Mostrar algumas métricas
                        for key, value in list(metrics.items())[:5]:
                            print(f"     {key}: {value}")
                
                return True
            else:
                print("❌ Experimento 'eye-disease-classifier' não encontrado")
                print("   Experimentos disponíveis:")
                for exp in experiments:
                    print(f"     - {exp.get('name', 'N/A')}")
                return False
        else:
            print(f"❌ Erro ao listar experimentos: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao conectar com MLFlow: {e}")
        return False

def test_health_check():
    """Testa o health check"""
    print("\n❤️ Testando health check...")
    
    try:
        response = requests.get(f"{API_URL}/health", timeout=10)
        
        if response.status_code == 200:
            health_data = response.json()
            print("✅ Health check OK")
            print(f"   Status: {health_data.get('status')}")
            print(f"   Modelo carregado: {health_data.get('model_loaded')}")
            print(f"   Versão: {health_data.get('version')}")
            return True
        else:
            print(f"❌ Health check falhou: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro no health check: {e}")
        return False

def test_metrics_endpoint():
    """Testa o endpoint de métricas"""
    print("\n📊 Testando endpoint de métricas...")
    
    try:
        response = requests.get(f"{API_URL}/metrics", timeout=10)
        
        if response.status_code == 200:
            metrics = response.json()
            print("✅ Métricas obtidas")
            print(f"   Total de requests: {metrics.get('total_requests', 0)}")
            print(f"   Total de predições: {metrics.get('total_predictions', 0)}")
            print(f"   Tempo médio de resposta: {metrics.get('average_response_time_ms', 0):.2f}ms")
            return True
        else:
            print(f"❌ Erro ao obter métricas: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Erro ao obter métricas: {e}")
        return False

def main():
    """Função principal"""
    print("🚀 Teste de Integração MLFlow - Eye Disease Classifier API")
    print("=" * 60)
    
    # Verificar serviços
    if not check_services():
        print("\n❌ Serviços não estão disponíveis. Verifique se estão rodando:")
        print("   docker-compose up -d")
        return False
    
    # Aguardar um pouco para garantir que tudo está inicializado
    print("\n⏳ Aguardando inicialização completa...")
    time.sleep(5)
    
    # Executar testes
    tests = [
        ("Health Check", test_health_check),
        ("Predição Única", test_prediction),
        ("Múltiplas Predições", lambda: test_multiple_predictions(3)),
        ("Endpoint de Métricas", test_metrics_endpoint),
        ("Experimento MLFlow", check_mlflow_experiment),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Erro inesperado no teste '{test_name}': {e}")
            results.append((test_name, False))
    
    # Resumo dos resultados
    print("\n" + "="*60)
    print("📋 RESUMO DOS TESTES")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
        if result:
            passed += 1
    
    print(f"\nResultado: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 Todos os testes passaram! A integração MLFlow está funcionando corretamente.")
        print("\n🌐 Acesse:")
        print(f"   API: {API_URL}/docs")
        print(f"   MLFlow: {MLFLOW_URL}")
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam. Verifique os logs acima.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
