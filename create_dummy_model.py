#!/usr/bin/env python3
"""
Cria um modelo dummy para testar deploy sem o modelo grande
"""

import tensorflow as tf
import numpy as np
import os

def create_dummy_model():
    """Cria um modelo dummy pequeno para testes"""
    
    print("🔧 Criando modelo dummy para testes...")
    
    # Criar modelo simples
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(256, 256, 3)),
        tf.keras.layers.GlobalAveragePooling2D(),
        tf.keras.layers.Dense(128, activation='relu'),
        tf.keras.layers.Dropout(0.5),
        tf.keras.layers.Dense(4, activation='softmax')  # 4 classes
    ])
    
    # Compilar modelo
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    # Treinar com dados dummy (apenas para ter pesos)
    print("📊 Treinando com dados dummy...")
    
    # Dados dummy
    x_dummy = np.random.random((10, 256, 256, 3))
    y_dummy = tf.keras.utils.to_categorical(np.random.randint(0, 4, 10), 4)
    
    # Treinar por 1 época
    model.fit(x_dummy, y_dummy, epochs=1, verbose=0)
    
    # Salvar modelo
    model_path = "best_model.keras"
    model.save(model_path)
    
    # Verificar tamanho
    file_size = os.path.getsize(model_path) / (1024 * 1024)
    
    print(f"✅ Modelo dummy criado: {model_path}")
    print(f"📏 Tamanho: {file_size:.1f} MB")
    print(f"🏗️ Arquitetura: {model.count_params()} parâmetros")
    
    # Testar predição
    test_input = np.random.random((1, 256, 256, 3))
    prediction = model.predict(test_input, verbose=0)
    
    print(f"🧪 Teste de predição: {prediction.shape}")
    print(f"📊 Probabilidades: {prediction[0]}")
    
    return model_path

if __name__ == "__main__":
    create_dummy_model()
    
    print("\n🎯 MODELO DUMMY CRIADO!")
    print("=" * 40)
    print("✅ Agora você pode testar o deploy:")
    print("   1. git add .")
    print("   2. git commit -m 'feat: Adicionar modelo dummy para teste'")
    print("   3. git push")
    print("   4. Deploy no Railway/Render")
    print("\n💡 Depois que o deploy funcionar, substitua pelo modelo real!")
