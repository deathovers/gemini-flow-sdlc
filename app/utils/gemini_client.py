import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiClient:
    def __init__(self, model_name: str = "gemini-1.5-pro"):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)

    async def generate(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        # Note: In a real implementation, we'd use the async SDK properly
        # For this implementation, we'll use the standard generate_content
        response = self.model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
            )
        )
        return response.text
