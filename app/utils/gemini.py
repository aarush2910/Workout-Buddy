import google.generativeai as genai  # type: ignore
import asyncio
from app.api.routes.api_key import get_api_key

# Global variable to store the configured Gemini model
model = None

async def configure_gemini_model():
    """
    Configures the Gemini API and initializes the model.
    This function should be called once during application startup.
    """
    global model
    try:
        response = await get_api_key()

        if not response or "data" not in response or "apiKey" not in response["data"]:
            raise ValueError("Invalid API key response format or missing API key.")

        api_key = response["data"]["apiKey"]
        print("✅ Gemini API key loaded successfully.")

        # Configure Gemini with Flash model
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        print("✅ Gemini Flash model configured successfully.")
        
    except Exception as e:
        print(f"❌ Error configuring Gemini: {e}")


async def generate_gemini_response(prompt: str) -> str:
    """
    Generates content from Gemini API based on a prompt asynchronously.
    Includes basic retry handling for rate limit errors.
    """
    if model is None:
        return "Error: Gemini model not initialized. Please ensure configure_gemini_model runs on startup."
    
    retries = 3
    for attempt in range(retries):
        try:
            response = await asyncio.to_thread(model.generate_content, prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait_time = 2 ** attempt
                print(f"⚠️ Rate limit hit. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            print(f"❌ Error during Gemini response generation: {e}")
            return "Error: Could not generate content."
