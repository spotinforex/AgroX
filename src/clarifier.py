from llama_cpp import Llama
import json
import re
import hashlib
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Router:
    def __init__(self):
        self.default_crop = "maize"
        self.default_month = "July"
        self.default_location = "Onitsha"  # Major agricultural/commercial center in Southeast Nigeria
        
        # Initialize LLM with proper parameters
        self.llm = Llama(
            model_path="models/qwen-1.5b.Q4_K_M.gguf",
            n_ctx=2048,
            n_threads=4,
            verbose=False
        )
        
        # Simple in-memory cache
        self.clarification_cache = {}
        self.routing_cache = {}
        
    def ask_llm(self, prompt: str, max_tokens: int = 150, temperature: float = 0.3) -> str:
        """
        Wrapper for LLM calls with proper error handling and logging
        """
        try:
            response = self.llm.create_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                stop=["</s>", "\n\n", "Input:", "Original:"],
                echo=False
            )
            
            result = response["choices"][0]["text"].strip()
            logger.info(f"LLM response length: {len(result)} characters")
            return result
            
        except Exception as e:
            logger.error(f"LLM call failed: {str(e)}")
            return ""
    
    def get_cache_key(self, text: str) -> str:
        """Generate cache key from input text"""
        return hashlib.md5(text.encode()).hexdigest()[:16]
    
    def clarify_and_route(self, user_input: str) -> Dict[str, Any]:
        """
        Clarifies user input and determines routing strategy with caching
        """
        cache_key = self.get_cache_key(user_input)
        
        # Check cache first
        if cache_key in self.routing_cache:
            logger.info(f"Cache hit for input: {user_input[:50]}...")
            return self.routing_cache[cache_key]
        
        try:
            # Clarify input
            clarified = self.clarify_input(user_input)
            if not clarified:
                logger.warning("Clarification failed, using original input")
                clarified = user_input
            
            # Route the query
            route_info = self.determine_route(user_input, clarified)
            
            result = {
                "original_input": user_input,
                "clarified_query": clarified,
                "route_type": route_info["route_type"],
                "extracted_info": route_info["extracted_info"],
                "reasoning": route_info["reasoning"]
            }
            
            # Cache the result
            self.routing_cache[cache_key] = result
            
            return result
            
        except Exception as e:
            logger.error(f"Clarify and route failed: {str(e)}")
            return self.create_fallback_response(user_input)
    
    def clarify_input(self, user_input: str) -> str:
        """Clarify and standardize user input with caching"""
        cache_key = self.get_cache_key(f"clarify_{user_input}")
        
        if cache_key in self.clarification_cache:
            return self.clarification_cache[cache_key]
        
        prompt = f"""You are a farming assistant clarifier. Rewrite the query to include all necessary information.

Rules:
- If no crop mentioned, assume "maize"
- If no month mentioned, assume "July"
- If no location mentioned, assume "Onitsha"
- Keep original intent but make complete
- Output ONLY the clarified query

Examples:
Input: "which plant is good to grow in Onitsha south"
Output: Which plant is good to grow in Onitsha south in July?

Input: "soil pH for tomatoes"
Output: What is the soil pH requirement for tomatoes in Onitsha in July?

Input: "how to plant maize"
Output: How to plant maize in Onitsha in July?

Input: "{user_input}"
Output: """
        
        try:
            result = self.ask_llm(prompt, max_tokens=100, temperature=0.2)
            if result:
                self.clarification_cache[cache_key] = result
                return result
            else:
                logger.warning("Empty clarification result")
                return user_input
                
        except Exception as e:
            logger.error(f"Clarification failed: {str(e)}")
            return user_input
    
    def determine_route(self, original_input: str, clarified_input: str) -> Dict[str, Any]:
        """Determine routing with structured JSON output"""
        
        route_prompt = f"""You are a farming assistant router. Analyze the query and return JSON response.

DATA SOURCES:
- RAG: How-to guides, farming procedures, planting steps
- DATABASE: Soil properties, pH, nutrients, fertilizers, crop suitability for locations
- BOTH: Needs both farming procedures AND soil/location data

Respond in valid JSON format:
{{
  "ROUTE": "RAG or DATABASE or BOTH",
  "REASON": "brief explanation",
  "CROP": "extracted crop name",
  "LOCATION": "extracted location",
  "MONTH": "extracted month"
}}

Original: "{original_input}"
Clarified: "{clarified_input}"

JSON Response:"""

        try:
            response = self.ask_llm(route_prompt, max_tokens=200, temperature=0.1)
            
            # Try to parse JSON response
            try:
                # Extract JSON from response (handle cases where model adds extra text)
                json_match = re.search(r'\{.*\}', response, re.DOTALL)
                if json_match:
                    json_str = json_match.group(0)
                    route_data = json.loads(json_str)
                    
                    return {
                        "route_type": route_data.get("ROUTE", "BOTH"),
                        "reasoning": route_data.get("REASON", "LLM provided route"),
                        "extracted_info": {
                            "crop": route_data.get("CROP", self.default_crop),
                            "location": route_data.get("LOCATION", self.default_location),
                            "month": route_data.get("MONTH", self.default_month)
                        }
                    }
                else:
                    logger.warning("No JSON found in LLM response")
                    return self.fallback_routing(clarified_input)
                    
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed: {str(e)}")
                # Try regex fallback parsing
                return self.parse_route_response_regex(response, clarified_input)
                
        except Exception as e:
            logger.error(f"Route determination failed: {str(e)}")
            return self.fallback_routing(clarified_input)
    
    def parse_route_response_regex(self, response: str, clarified_input: str) -> Dict[str, Any]:
        """Fallback regex parsing when JSON fails"""
        try:
            route_match = re.search(r'(?:ROUTE|route)["\']?\s*:\s*["\']?(\w+)', response, re.IGNORECASE)
            reason_match = re.search(r'(?:REASON|reason)["\']?\s*:\s*["\']?([^"}\n]+)', response, re.IGNORECASE)
            crop_match = re.search(r'(?:CROP|crop)["\']?\s*:\s*["\']?([^"}\n]+)', response, re.IGNORECASE)
            location_match = re.search(r'(?:LOCATION|location)["\']?\s*:\s*["\']?([^"}\n]+)', response, re.IGNORECASE)
            month_match = re.search(r'(?:MONTH|month)["\']?\s*:\s*["\']?([^"}\n]+)', response, re.IGNORECASE)
            
            return {
                "route_type": route_match.group(1).upper() if route_match else "BOTH",
                "reasoning": reason_match.group(1).strip(' "') if reason_match else "Regex fallback parsing",
                "extracted_info": {
                    "crop": crop_match.group(1).strip(' "') if crop_match else self.default_crop,
                    "location": location_match.group(1).strip(' "') if location_match else self.default_location,
                    "month": month_match.group(1).strip(' "') if month_match else self.default_month
                }
            }
            
        except Exception as e:
            logger.error(f"Regex parsing failed: {str(e)}")
            return self.fallback_routing(clarified_input)
    
    def fallback_routing(self, clarified_input: str) -> Dict[str, Any]:
        """Rule-based fallback routing when LLM fails"""
        text = clarified_input.lower()
        
        # Keyword-based routing
        if any(phrase in text for phrase in ['how to', 'how do', 'steps to', 'guide to', 'procedure', 'method']):
            route_type = "RAG"
            reason = "Contains how-to/procedural keywords"
        elif any(word in text for word in ['soil', 'ph', 'nutrient', 'fertilizer', 'nitrogen', 'phosphorus', 'potassium']):
            route_type = "DATABASE"
            reason = "Contains soil/nutrient keywords"
        elif any(phrase in text for phrase in ['what to plant', 'which plant', 'good to grow', 'suitable for']):
            route_type = "DATABASE"
            reason = "Contains crop suitability keywords"
        elif 'plant' in text and any(word in text for word in ['prepare', 'land', 'field']):
            route_type = "RAG"
            reason = "Contains land preparation keywords"
        else:
            route_type = "DATABASE"
            reason = "Default fallback to database"
        
        return {
            "route_type": route_type,
            "reasoning": f"Fallback routing: {reason}",
            "extracted_info": {
                "crop": self.default_crop,
                "location": self.default_location,
                "month": self.default_month
            }
        }
    
    def create_fallback_response(self, user_input: str) -> Dict[str, Any]:
        """Create a safe fallback response when everything fails"""
        return {
            "original_input": user_input,
            "clarified_query": user_input,
            "route_type": "BOTH",
            "extracted_info": {
                "crop": self.default_crop,
                "location": self.default_location,
                "month": self.default_month
            },
            "reasoning": "System fallback - routing to both sources for safety"
        }
    
    def clear_cache(self):
        """Clear all caches"""
        self.clarification_cache.clear()
        self.routing_cache.clear()
        logger.info("Caches cleared")
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics"""
        return {
            "clarification_cache_size": len(self.clarification_cache),
            "routing_cache_size": len(self.routing_cache)
        }

# Usage example
def main():
    router = FarmingAssistantRouter()
    
    # Test queries
    test_queries = [
        "which plant is good to grow in Onitsha south",        # DATABASE
        "soil pH for tomatoes",                                # DATABASE
        "how to plant maize",                                  # RAG
        "fertilizer requirements for maize in August",         # DATABASE
        "step by step guide to planting cassava",              # RAG
        "what is the nitrogen content of my soil",             # DATABASE
        "how to prepare land for farming",                     # RAG
        "phosphorus levels in Onitsha soil"                    # DATABASE
    ]
    
    for query in test_queries:
        try:
            result = router.clarify_and_route(query)
            print(f"\n{'='*60}")
            print(f"Original: {result['original_input']}")
            print(f"Clarified: {result['clarified_query']}")
            print(f"Route: {result['route_type']}")
            print(f"Reasoning: {result['reasoning']}")
            print(f"Extracted: {result['extracted_info']}")
            
        except Exception as e:
            logger.error(f"Test failed for query '{query}': {str(e)}")
    
    # Show cache stats
    print(f"\nCache stats: {router.get_cache_stats()}")

if __name__ == "__main__":
    main()