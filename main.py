import streamlit as st
from PIL import Image
import os
from src.image_classifier import Image_Classifier
from src.rag_integration import qa_chain  # RAG setup

st.title("🌿 AgriSense Assistant")

# -- Camera and file input --
camera_image = st.camera_input("📸 Take a plant photo")
uploaded_file = st.file_uploader("📁 Or upload an image", type=["jpg", "jpeg", "png"])

user_question = st.text_input("💬 Ask a farming question (optional)")

# -- Handle image input: prioritize camera input --
image = None
if camera_image:
    image = Image.open(camera_image)
    st.info("Using photo from camera.")
elif uploaded_file:
    image = Image.open(uploaded_file)
    st.info("Using uploaded image.")

if image:
    os.makedirs("images", exist_ok=True)
    image_path = os.path.join("images", "live_leaf.jpg")
    image.save(image_path)

    image_model = Image_Classifier()
    label = image_model.classify_plant_image(image_path)
    st.success(f"🦠 Detected Disease: `{label}`")

    prompt = f"Image shows: {label}.\n"
    if user_question:
        prompt += f"Farmer asks: {user_question}"
    else:
        prompt += "What is the treatment?"

    with st.spinner("🧠 Thinking..."):
        answer = qa_chain.run(prompt)
        st.success("AgriSense says:")
        st.write(answer)

elif user_question:
    with st.spinner("🧠 Thinking..."):
        answer = qa_chain.run(user_question)
        st.success("AgriSense says:")
        st.write(answer)
else:
    st.info("📸 Take a photo or 📁 upload one, then ask a question.")