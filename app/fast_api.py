from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from src.image_classifier import Image_Classifier
from src.rag_integration import retrieve_answer
from src.audio_handler import Audio
from src.translate_handler import Translation
from PIL import Image
import os
import uuid
import shutil

app = FastAPI()

image_model = None

@app.on_event("startup")
async def load_model():
    global image_model
    image_model = Image_Classifier()


@app.post("/infer")
async def infer(
    image: UploadFile = File(None),
    audio: UploadFile = File(None),
    text: str = Form(None)
):
    try:
        if not any([image, audio, text]):
            raise HTTPException(status_code=400, detail="At least one input (image, audio, or text) is required.")

        prompt = ""
        translator = None
        
        if image:
            image_ext = os.path.splitext(image.filename)[1]
            image_path = f"temp_{uuid.uuid4().hex}{image_ext}"
            with open(image_path, "wb") as f:
                shutil.copyfileobj(image.file, f)

            img = Image.open(image_path)
            label = image_model.classify_plant_image(img)
            prompt += f"Image shows: {label}. "
            os.remove(image_path)

        if audio:
            audio_ext = os.path.splitext(audio.filename)[1]
            audio_path = f"temp_{uuid.uuid4().hex}{audio_ext}"
            wav_path = f"temp_{uuid.uuid4().hex}.wav"
            with open(audio_path, "wb") as f:
                shutil.copyfileobj(audio.file, f)

            audio_handler = Audio(audio_path, output_path=wav_path)
            raw_text = audio_handler.transcribe_audio()

            translator = Translation(raw_text)
            if translator.lang == "ig":
                translated_text = translator.translate()
                prompt += f"Farmer said (in Igbo): {translated_text}. "
            else:
                prompt += f"Farmer said: {raw_text}. "

            os.remove(audio_path)
            os.remove(wav_path)

        if text:
            translator = Translation(text)
            if translator.lang == "ig":
                translated_text = translator.translate()
                prompt += f"Farmer typed (in Igbo): {translated_text}. "
            else:
                prompt += f"Farmer typed: {text}. "

        answer = retrieve_answer(prompt)

        if translator and translator.lang == "ig":
            back_translator = Translation(answer)
            answer_igbo = back_translator.translate()
            return {
                "prompt": prompt,
                "answer_english": answer,
                "answer_igbo": answer_igbo
            }

        return {"prompt": prompt, "answer": answer}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
