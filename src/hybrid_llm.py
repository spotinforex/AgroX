import os
import logging
import requests
from langchain_core.language_models.llms import LLM as BaseLLM
import google.generativeai as genai
from src.model_loader import Load_Model
from pydantic import PrivateAttr

# Logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HybridLLM(BaseLLM):
    """Hybrid LLM: Uses online Gemini if available, falls back to local model"""
    _use_online: bool = PrivateAttr()
    _local_model: any = PrivateAttr()
    _temperature: float = PrivateAttr()


    def __init__(self, use_online=True, local_model_name=r"AgroX\models\gpt2", temperature=0.7):
        super().__init__()
        self._use_online = use_online
        self._temperature = temperature
        self._local_model = None

        # Setup Gemini
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise EnvironmentError("GEMINI_API_KEY not found.")
        genai.configure(api_key=api_key)

        # Load local model
        try:
            self._local_model = Load_Model(local_model_name)
            logger.info(f"Local model '{local_model_name}' loaded successfully.")
        except Exception as e:
            logger.exception("Failed to load local model.")
            if not self._use_online:
                raise RuntimeError("Offline mode selected, but local model failed to load.") from e

    def _call(self, prompt, stop=None, run_manager=None):
        """Main call method with routing logic."""
        try:
            if self._should_use_local(prompt):
                logger.info("Using local model for generation.")
                return self._local_model.generate_response(prompt)
            elif self._use_online and self._is_online():
                logger.info("Using Gemini API for generation.")
                return self._call_gemini(prompt)
            elif self._local_model:
                logger.warning("Falling back to local model due to no internet.")
                return self._local_model.generate_response(prompt)
            else:
                raise RuntimeError("No model available for inference.")
        except Exception as e:
            logger.exception("LLM generation failed.")
            raise e

    def _should_use_local(self, prompt: str) -> bool:
        """Simple keyword check to force offline mode."""
        return "<USE_OFFLINE>" in prompt

    def _is_online(self) -> bool:
        """Ping Google DNS for internet check."""
        try:
            requests.head("https://1.1.1.1", timeout=3)
            return True
        except requests.RequestException:
            return False

    def _call_gemini(self, prompt: str, model="gemini-2.5-flash") -> str:
        try:
            gemini_model = genai.GenerativeModel(model)
            response = gemini_model.generate_content(prompt, generation_config={"temperature": self.temperature})
            return response.text.strip()
        except Exception as e:
            logger.exception("Gemini API call failed.")
            raise e

    @property
    def _llm_type(self) -> str:
        return "hybrid-llm"
