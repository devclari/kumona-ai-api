#!/usr/bin/env python3
"""
Script para dividir modelo grande em partes menores para GitHub
"""

import os
import math
import hashlib
import json

def split_file(file_path, chunk_size_mb=90):
    """Divide arquivo em partes menores"""
    
    if not os.path.exists(file_path):
        print(f"❌ Arquivo não encontrado: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"📁 Arquivo: {file_path}")
    print(f"📏 Tamanho: {file_size_mb:.1f} MB")
    
    if file_size_mb <= 100:
        print("✅ Arquivo já é menor que 100MB, não precisa dividir")
        return True
    
    chunk_size = chunk_size_mb * 1024 * 1024  # Converter para bytes
    total_chunks = math.ceil(file_size / chunk_size)
    
    print(f"🔪 Dividindo em {total_chunks} partes de ~{chunk_size_mb}MB cada")
    
    # Calcular hash do arquivo original
    print("🔐 Calculando hash do arquivo original...")
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    original_hash = sha256_hash.hexdigest()
    
    # Dividir arquivo
    base_name = os.path.splitext(file_path)[0]
    extension = os.path.splitext(file_path)[1]
    
    chunk_info = {
        "original_file": file_path,
        "original_size": file_size,
        "original_hash": original_hash,
        "chunk_size": chunk_size,
        "total_chunks": total_chunks,
        "chunks": []
    }
    
    with open(file_path, 'rb') as f:
        for i in range(total_chunks):
            chunk_filename = f"{base_name}.part{i+1:03d}"
            
            print(f"📦 Criando parte {i+1}/{total_chunks}: {chunk_filename}")
            
            with open(chunk_filename, 'wb') as chunk_file:
                chunk_data = f.read(chunk_size)
                chunk_file.write(chunk_data)
            
            # Calcular hash da parte
            chunk_hash = hashlib.sha256(chunk_data).hexdigest()
            chunk_size_actual = len(chunk_data)
            
            chunk_info["chunks"].append({
                "filename": chunk_filename,
                "size": chunk_size_actual,
                "hash": chunk_hash,
                "part_number": i + 1
            })
            
            print(f"   ✅ {chunk_filename} ({chunk_size_actual / (1024*1024):.1f} MB)")
    
    # Salvar informações das partes
    info_filename = f"{base_name}_parts.json"
    with open(info_filename, 'w') as f:
        json.dump(chunk_info, f, indent=2)
    
    print(f"📋 Informações salvas em: {info_filename}")
    
    # Criar script de reconstituição
    create_merge_script(base_name, extension)
    
    print("\n✅ Arquivo dividido com sucesso!")
    print(f"📦 Partes criadas: {total_chunks}")
    print(f"📋 Info: {info_filename}")
    print(f"🔧 Script de junção: merge_{base_name}.py")
    
    return True

def create_merge_script(base_name, extension):
    """Cria script para juntar as partes"""
    
    script_content = f'''#!/usr/bin/env python3
"""
Script para reconstituir {base_name}{extension} a partir das partes
"""

import os
import json
import hashlib

def merge_parts():
    """Junta as partes do modelo"""
    
    info_file = "{base_name}_parts.json"
    
    if not os.path.exists(info_file):
        print(f"❌ Arquivo de informações não encontrado: {{info_file}}")
        return False
    
    # Carregar informações
    with open(info_file, 'r') as f:
        info = json.load(f)
    
    original_file = info["original_file"]
    total_chunks = info["total_chunks"]
    original_hash = info["original_hash"]
    
    print(f"🔧 Reconstituindo {{original_file}}...")
    print(f"📦 Total de partes: {{total_chunks}}")
    
    # Verificar se todas as partes existem
    missing_parts = []
    for chunk in info["chunks"]:
        if not os.path.exists(chunk["filename"]):
            missing_parts.append(chunk["filename"])
    
    if missing_parts:
        print(f"❌ Partes faltando: {{missing_parts}}")
        return False
    
    # Juntar partes
    with open(original_file, 'wb') as output_file:
        for i, chunk in enumerate(info["chunks"]):
            chunk_filename = chunk["filename"]
            print(f"📥 Juntando parte {{i+1}}/{{total_chunks}}: {{chunk_filename}}")
            
            with open(chunk_filename, 'rb') as chunk_file:
                chunk_data = chunk_file.read()
                
                # Verificar hash da parte
                chunk_hash = hashlib.sha256(chunk_data).hexdigest()
                if chunk_hash != chunk["hash"]:
                    print(f"❌ Hash inválido para {{chunk_filename}}")
                    return False
                
                output_file.write(chunk_data)
    
    # Verificar hash do arquivo final
    print("🔐 Verificando integridade do arquivo final...")
    sha256_hash = hashlib.sha256()
    with open(original_file, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    
    final_hash = sha256_hash.hexdigest()
    
    if final_hash == original_hash:
        file_size = os.path.getsize(original_file)
        print(f"✅ Arquivo reconstituído com sucesso!")
        print(f"📁 Arquivo: {{original_file}}")
        print(f"📏 Tamanho: {{file_size / (1024*1024):.1f}} MB")
        print(f"🔐 Hash: {{final_hash}}")
        return True
    else:
        print(f"❌ Hash do arquivo final não confere!")
        print(f"   Esperado: {{original_hash}}")
        print(f"   Obtido:   {{final_hash}}")
        return False

if __name__ == "__main__":
    if merge_parts():
        print("\\n🎉 Modelo reconstituído com sucesso!")
    else:
        print("\\n❌ Falha na reconstituição do modelo")
'''
    
    script_filename = f"merge_{base_name}.py"
    with open(script_filename, 'w') as f:
        f.write(script_content)
    
    # Tornar executável
    os.chmod(script_filename, 0o755)
    
    return script_filename

def main():
    """Função principal"""
    import sys
    
    if len(sys.argv) != 2:
        print("Uso: python split_model.py <arquivo>")
        print("Exemplo: python split_model.py best_model.keras")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    if split_file(file_path):
        print("\\n🚀 Próximos passos:")
        print("   1. git add *.part* *_parts.json merge_*.py")
        print("   2. git commit -m 'feat: Adicionar modelo dividido em partes'")
        print("   3. git push")
        print("   4. No deploy, o modelo será reconstituído automaticamente")
    else:
        print("\\n❌ Falha ao dividir arquivo")
        sys.exit(1)

if __name__ == "__main__":
    main()
