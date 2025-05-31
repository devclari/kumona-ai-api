#!/usr/bin/env python3
"""
Script de validação para verificar se o projeto está configurado corretamente
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Any

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_success(message: str):
    print(f"{Colors.GREEN}✅ {message}{Colors.ENDC}")

def print_error(message: str):
    print(f"{Colors.RED}❌ {message}{Colors.ENDC}")

def print_warning(message: str):
    print(f"{Colors.YELLOW}⚠️  {message}{Colors.ENDC}")

def print_info(message: str):
    print(f"{Colors.BLUE}ℹ️  {message}{Colors.ENDC}")

def print_header(message: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{message}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*50}{Colors.ENDC}")

class ProjectValidator:
    def __init__(self):
        self.project_root = Path.cwd()
        self.errors = []
        self.warnings = []
        
    def validate_files(self) -> bool:
        """Valida se todos os arquivos necessários existem"""
        print_header("Validando Arquivos do Projeto")
        
        required_files = [
            "app.py",
            "models.py", 
            "ml_service.py",
            "monitoring.py",
            "production_config.py",
            "tf_config.py",
            "requirements.txt",
            "Dockerfile",
            "cloudbuild.yaml",
            "service.yaml",
            "deploy.sh",
            "README.md"
        ]
        
        all_exist = True
        for file in required_files:
            file_path = self.project_root / file
            if file_path.exists():
                print_success(f"Arquivo encontrado: {file}")
            else:
                print_error(f"Arquivo não encontrado: {file}")
                self.errors.append(f"Arquivo obrigatório não encontrado: {file}")
                all_exist = False
                
        return all_exist
    
    def validate_python_syntax(self) -> bool:
        """Valida sintaxe dos arquivos Python"""
        print_header("Validando Sintaxe Python")
        
        python_files = [
            "app.py",
            "models.py",
            "ml_service.py", 
            "monitoring.py",
            "production_config.py",
            "tf_config.py",
            "test_api.py",
            "validate_setup.py"
        ]
        
        all_valid = True
        for file in python_files:
            file_path = self.project_root / file
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        compile(f.read(), file, 'exec')
                    print_success(f"Sintaxe válida: {file}")
                except SyntaxError as e:
                    print_error(f"Erro de sintaxe em {file}: {e}")
                    self.errors.append(f"Erro de sintaxe em {file}: {e}")
                    all_valid = False
                except Exception as e:
                    print_warning(f"Aviso em {file}: {e}")
                    self.warnings.append(f"Aviso em {file}: {e}")
            else:
                print_warning(f"Arquivo não encontrado para validação: {file}")
                
        return all_valid
    
    def validate_requirements(self) -> bool:
        """Valida arquivo requirements.txt"""
        print_header("Validando Requirements")
        
        req_file = self.project_root / "requirements.txt"
        if not req_file.exists():
            print_error("requirements.txt não encontrado")
            return False
            
        required_packages = [
            "fastapi",
            "uvicorn",
            "python-multipart",
            "numpy",
            "pillow",
            "tensorflow",
            "gdown",
            "pydantic"
        ]
        
        try:
            with open(req_file, 'r') as f:
                content = f.read().lower()
                
            all_found = True
            for package in required_packages:
                if package in content:
                    print_success(f"Pacote encontrado: {package}")
                else:
                    print_error(f"Pacote não encontrado: {package}")
                    self.errors.append(f"Pacote obrigatório não encontrado: {package}")
                    all_found = False
                    
            return all_found
            
        except Exception as e:
            print_error(f"Erro ao ler requirements.txt: {e}")
            return False
    
    def validate_docker_config(self) -> bool:
        """Valida configuração do Docker"""
        print_header("Validando Configuração Docker")
        
        dockerfile = self.project_root / "Dockerfile"
        if not dockerfile.exists():
            print_error("Dockerfile não encontrado")
            return False
            
        try:
            with open(dockerfile, 'r') as f:
                content = f.read()
                
            checks = [
                ("FROM python:", "Imagem base Python"),
                ("COPY requirements.txt", "Cópia do requirements.txt"),
                ("RUN pip install", "Instalação de dependências"),
                ("COPY . .", "Cópia do código"),
                ("EXPOSE 8080", "Exposição da porta"),
                ("CMD", "Comando de execução")
            ]
            
            all_valid = True
            for check, description in checks:
                if check in content:
                    print_success(f"Configuração encontrada: {description}")
                else:
                    print_warning(f"Configuração não encontrada: {description}")
                    self.warnings.append(f"Configuração Docker: {description}")
                    
            return all_valid
            
        except Exception as e:
            print_error(f"Erro ao ler Dockerfile: {e}")
            return False
    
    def validate_gcloud_cli(self) -> bool:
        """Valida se Google Cloud CLI está instalado"""
        print_header("Validando Google Cloud CLI")
        
        try:
            result = subprocess.run(['gcloud', 'version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print_success("Google Cloud CLI instalado")
                print_info(f"Versão: {result.stdout.split()[2]}")
                return True
            else:
                print_error("Google Cloud CLI não está funcionando corretamente")
                return False
        except FileNotFoundError:
            print_error("Google Cloud CLI não está instalado")
            self.errors.append("Google Cloud CLI não encontrado")
            return False
        except subprocess.TimeoutExpired:
            print_warning("Timeout ao verificar Google Cloud CLI")
            return False
        except Exception as e:
            print_warning(f"Erro ao verificar Google Cloud CLI: {e}")
            return False
    
    def validate_project_structure(self) -> bool:
        """Valida estrutura geral do projeto"""
        print_header("Validando Estrutura do Projeto")
        
        # Verificar se é um projeto Python válido
        if not any(self.project_root.glob("*.py")):
            print_error("Nenhum arquivo Python encontrado")
            return False
            
        print_success("Arquivos Python encontrados")
        
        # Verificar se há arquivos de configuração
        config_files = ["cloudbuild.yaml", "service.yaml", "docker-compose.yml"]
        for config_file in config_files:
            if (self.project_root / config_file).exists():
                print_success(f"Arquivo de configuração encontrado: {config_file}")
            else:
                print_warning(f"Arquivo de configuração não encontrado: {config_file}")
                
        return True
    
    def generate_report(self) -> Dict[str, Any]:
        """Gera relatório de validação"""
        return {
            "errors": self.errors,
            "warnings": self.warnings,
            "total_errors": len(self.errors),
            "total_warnings": len(self.warnings),
            "status": "PASS" if len(self.errors) == 0 else "FAIL"
        }
    
    def run_validation(self) -> bool:
        """Executa todas as validações"""
        print_header("🔍 VALIDAÇÃO DO PROJETO - EYE DISEASE CLASSIFIER API")
        
        validations = [
            ("Arquivos do Projeto", self.validate_files),
            ("Sintaxe Python", self.validate_python_syntax),
            ("Requirements", self.validate_requirements),
            ("Configuração Docker", self.validate_docker_config),
            ("Google Cloud CLI", self.validate_gcloud_cli),
            ("Estrutura do Projeto", self.validate_project_structure)
        ]
        
        results = []
        for name, validation_func in validations:
            try:
                result = validation_func()
                results.append(result)
            except Exception as e:
                print_error(f"Erro durante validação de {name}: {e}")
                results.append(False)
        
        # Gerar relatório final
        report = self.generate_report()
        
        print_header("📊 RELATÓRIO FINAL")
        
        if report["status"] == "PASS":
            print_success(f"✅ VALIDAÇÃO PASSOU! ({report['total_warnings']} avisos)")
        else:
            print_error(f"❌ VALIDAÇÃO FALHOU! ({report['total_errors']} erros, {report['total_warnings']} avisos)")
        
        if report["errors"]:
            print("\n🔴 ERROS ENCONTRADOS:")
            for error in report["errors"]:
                print(f"  • {error}")
        
        if report["warnings"]:
            print("\n🟡 AVISOS:")
            for warning in report["warnings"]:
                print(f"  • {warning}")
        
        print_header("🚀 PRÓXIMOS PASSOS")
        
        if report["status"] == "PASS":
            print_info("Projeto validado com sucesso! Você pode prosseguir com o deploy:")
            print("  1. Execute: chmod +x deploy.sh")
            print("  2. Execute: ./deploy.sh SEU_PROJECT_ID us-central1")
        else:
            print_info("Corrija os erros encontrados antes de prosseguir com o deploy.")
        
        return report["status"] == "PASS"

def main():
    """Função principal"""
    validator = ProjectValidator()
    success = validator.run_validation()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
