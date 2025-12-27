from src.image_classifier import Image_Classifier
from src.rag_integration import retrieve_answer  # RAG setup
from src.audio_handler import Audio
from src.translate_handler import Translation
from PIL import Image

image_path  = r"C:\Users\SPOT\Documents\AgroX\images\images (2).webp"
audio_path = r"C:\Users\SPOT\Documents\AgroX\audio\3 Jul, 12.10 am​.m4a"
igbo_audio_path = r"C:\Users\SPOT\Documents\AgroX\audio\3 Jul, 11.36 pm​.m4a"
output = r"C:\Users\SPOT\Documents\AgroX\audio\h1.wav"


if __name__ == "__main__":
    '''img = Image.open(image_path)
    image_model = Image_Classifier()
    label = image_model.classify_plant_image(img)
    prompt = f"Image shows: {label}."
    prompt += "What is the treatment?"'''
    audio = Audio(audio_path, output_path = output)
    raw_text = audio.transcribe_audio()
    print(raw_text)
    translator = Translation(raw_text)
    if translator.detect_language(raw_text) == "ig":
        text = translator.translate()
        prompt += f" ,Farmer Said:{text}"
        answer = qa_chain.invoke(prompt)
        print (answer)
        igbo_trans = Translation(answer)
        igbo_answer = igbo_trans.translate()
        print (igbo_answer)
    else:
        prompt += f" ,Farmer Said:{raw_text}"
        answer = retrieve_answer(prompt)
        print (answer)