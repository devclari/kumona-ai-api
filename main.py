import streamlit as st
from PIL import Image
import numpy as np
import tensorflow as tf
from keras.models import load_model
import gdown
import os

# Caminho do modelo
MODEL_PATH = "best_model.keras"
MODEL_URL = "https://drive.google.com/uc?id=1vSIfD3viT5JSxpG4asA8APCwK0JK9Dvu"  # substitua pelo seu ID

# Baixar modelo se necessário
if not os.path.exists(MODEL_PATH):
    st.write("🔽 Downloading model...")
    gdown.download(MODEL_URL, MODEL_PATH, quiet=False)

# Carregar modelo
st.write("✅ Loading model...")
model = load_model(MODEL_PATH)
class_names = ['cataract', 'diabetic_retinopathy', 'glaucoma', 'normal']

# Função de predição
def predict(model, img):
    img = img.resize((256, 256))  # Redimensionar a imagem PIL
    img_array = tf.keras.utils.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0).astype(np.float32)
    predictions = model.predict(img_array)
    predicted_class = class_names[np.argmax(predictions[0])]
    confidence = round(100 * np.max(predictions[0]), 2)  # Yüzde olarak, 2 ondalık
    return predicted_class, confidence

# Interface
st.title("Eye Disease Classifier")
st.write("Upload an image of your eye to detect diseases.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_container_width=True)

    # Fazer a predição
    predicted_class, confidence = predict(model, image)
    
    st.subheader("Result:")
    st.write(f"**Disease detected:** {predicted_class}")
    st.write(f"**Confidence:** {confidence:.2f}%")
