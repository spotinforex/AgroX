import logging
import whisper
from pydub import AudioSegment
import os
import time

class Audio:
    ''' Class for Handling Audio Inputs '''
    def __init__(self, file_path, output_path=None):
        ''' Function for audio conversion to wav 
        Args:
            file_path: path to the audio
            output_path: optional converted audio path
        '''
        try:
            logging.info("Audio File Conversion In Progress")
            if file_path.endswith(".wav"):
                self.output_path = file_path
            else:
                sound = AudioSegment.from_file(file_path)
                sound = sound.set_frame_rate(16000).set_channels(1).set_sample_width(2)

                if not output_path:
                    output_path = os.path.splitext(file_path)[0] + ".wav"
                    
                sound.export(output_path, format="wav")
                self.output_path = output_path

        except Exception as e:
            logging.exception(f"An Error Occurred During Audio File Conversion: {e}")
            raise e

    def transcribe_audio(self):
        ''' Audio Conversion to Text 
        Returns:
            text: converted audio to text
        '''
        try:
            logging.info("Converting Audio in Progress")
            start = time.time()
            model = whisper.load_model("tiny")
            result = model.transcribe(self.output_path)
            end = time.time()
            logging.info(f"Conversion Completed, Time Taken {end - start}")")
            return result["text"]

        except Exception as e:
            logging.exception(f"An Error Occurred During Audio Conversion: {e}")
            raise e
