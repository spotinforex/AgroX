from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import logging
import time

logging.basicConfig(level=logging.INFO)


class Load_Model:
    ''' Class for Loading and Using a Causal Language Model '''
    
    def __init__(self, model):
        ''' Initializes Model
        Args:
            model: LLM to be used 
        '''
        try:
            start = time.time()
            logging.info("Model Selection Initialized")
            self.tokenizer = AutoTokenizer.from_pretrained(model)
            self.model = AutoModelForCausalLM.from_pretrained(model)
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            self.model = self.model.to(self.device)
            end = time.time()
            logging.info(f"Model Initialization Complete, Time Taken {end - start}")
        except Exception as e:
            logging.exception("An Error Occurred during Model Initialization")
            raise e

    def generate_response(self, prompt, max_new_tokens=100):
        ''' Generate a response from the LLM
        Args:
            prompt (str): Input prompt.
            max_new_tokens (int): Max number of tokens to generate.
        Returns:
            str: Model's generated response.
        '''
        try:
            logging.info("Generating Response In Progress")
            inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                pad_token_id=self.tokenizer.eos_token_id
            )

            logging.info("Response Successfully Generated")
            return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        except Exception as e:
            logging.exception(f"An Error Occurred During Generating Response: {e}")
            raise e

            