from transformers import AutoImageProcessor, AutoModelForImageClassification
from PIL import Image
import torch
import logging
import os
import time

class Image_Classifier:
    ''' Class for Classifying Plant Images '''
    
    def __init__(self, image_model=r"C:\Users\SPOT\Documents\AgroX\models\image_classifier_model"):
        ''' Initialize image model '''
        try:
            logging.info("Initializing Image Model")
            start = time.time()
            self.processor = AutoImageProcessor.from_pretrained(image_model)
            self.model = AutoModelForImageClassification.from_pretrained(image_model)
            self.labels = self.model.config.id2label
            end = time.time()
            logging.info(f"Image Model initialized successfully,  Time Taken {end - start}")
        except Exception as e:
            logging.exception(f"An Error Occurred during Image Initialization: {e}")
            raise e

    def classify_plant_image(self, image_input):
        ''' Predict plant disease from image path or PIL.Image
        Args:
            image_input (str or PIL.Image): Path to image or Image object
        Returns:
            str: Predicted class label
        '''
        try:
            logging.info("Image Classification in Progress")
            start = time.time()

            # Accept both path and PIL image
            if isinstance(image_input, str) and os.path.exists(image_input):
                image = Image.open(image_input).convert("RGB")
            elif isinstance(image_input, Image.Image):
                image = image_input.convert("RGB")
            else:
                raise ValueError("Input must be a valid file path or PIL.Image.Image")

            # Run model
            inputs = self.processor(images=image, return_tensors="pt")
            with torch.no_grad():
                outputs = self.model(**inputs)
                predicted_idx = outputs.logits.argmax(dim=1).item()
            end = time.time()
            logging.info(f"Image Classified Successfully, Time Taken {end - start}")
            return self.labels[predicted_idx]

        except Exception as e:
            logging.exception(f"An Error Occurred during Image Classification: {e}")
            raise e
