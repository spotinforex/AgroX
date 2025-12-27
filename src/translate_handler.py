from langdetect import detect
from argostranslate import package, translate
import logging
import time

logging.basicConfig(level=logging.INFO)

class Translation:
    '''Class for Handling Translation'''

    def __init__(self, text, supported_langs = ("ig", "en")):
        '''
        Initializes translation by detecting language and ensuring package installation.

        Args:
            text (str): Input text

        Returns:
            Tuple: (text, lang_code) if valid
        '''
        start = time.time()
        self.text = text
        self.lang = self.detect_language(self.text)
        if self.lang not in supported_langs:
            raise ValueError(f"{self.lang} is not supported")
        logging.info(f"Detected Language: {self.lang}")

        if self.lang == "ig":
            self.from_code, self.to_code = "ig", "en"
            installed = [
                (p.from_code, p.to_code) for p in package.get_installed_packages()
            ]
            if (self.from_code, self.to_code) not in installed:
                logging.info(f"Downloading translation package for {self.from_code} -> {self.to_code}...")
                pkg_path = package.download_package(self.from_code, self.to_code)
                package.install_from_path(pkg_path)
                end = time.time()
                logging.info(f" Loading Audio Package Time Taken {end - start}")
        elif self.lang == "en":
            logging.info("No translation needed for English.")
        else:
            raise ValueError(f"{self.lang} is not supported")

    @staticmethod
    def detect_language(text):
        '''Detect language using langdetect'''
        try:
            return detect(text)
        except Exception as e:
            logging.error(f"Language detection failed: {e}")
            raise ValueError(" This Language is not yet Supported ")

    @staticmethod
    def translate_to_english(text, from_lang_code="ig", to_lang_code="en"):
        '''Translate Igbo to English'''
        try:
            logging.info("Translating to English...")
            start = time.time()
            langs = translate.get_installed_languages()
            from_lang = next((lang for lang in langs if lang.code == from_lang_code), None)
            to_lang = next((lang for lang in langs if lang.code == to_lang_code), None)

            if not from_lang or not to_lang:
                raise ValueError("Required language packages not installed")

            translation = from_lang.get_translation(to_lang)
            end = time.time()
            logging.info(f" inference to translate to english  Time Taken {end - start}")
            return translation.translate(text)
        except Exception as e:
            logging.exception(f"Error translating to English: {e}")
            raise e

    @staticmethod
    def translate_to_igbo(text, from_lang_code="en", to_lang_code="ig"):
        '''Translate English to Igbo'''
        try:
            start = time.time()
            logging.info("Translating to Igbo...")
            langs = translate.get_installed_languages()
            from_lang = next((lang for lang in langs if lang.code == from_lang_code), None)
            to_lang = next((lang for lang in langs if lang.code == to_lang_code), None)

            if not from_lang or not to_lang:
                raise ValueError("Required language packages not installed")

            translation = from_lang.get_translation(to_lang)
            end = time.time()
            logging.info(f"inference time to translate to english Time Taken {end - start}")
            return translation.translate(text)
        except Exception as e:
            logging.exception(f"Error translating to Igbo: {e}")
            raise e

    def translate(self):
        ''' Handles Translation Logic to reduce complexity
        Returns:
            Text: Translated Text
        '''
        if self.lang == "ig":
            return self.translate_to_english(self.text)
            
        elif self.lang == "en":
             return self.translate_to_igbo(self.text)

        else:
            raise  ValueError(" Unsupported Format")
        
