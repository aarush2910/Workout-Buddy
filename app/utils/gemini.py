# app/utils/gemini.py

import google.generativeai as genai  # type: ignore
import asyncio
from typing import Dict, Any
from app.api.routes.api_key import get_api_key

# Global variable to store the configured Gemini model
model = None


async def configure_gemini_model():
    """
    Initializes the Gemini AI model.
    Must be called on application startup.
    """
    global model
    try:
        # Fetch API key (adjust get_api_key() according to your implementation)
        response = await get_api_key()
        api_key = response.get("data", {}).get("apiKey")

        if not api_key:
            raise ValueError("API key missing in response")

        # Configure Gemini with the Flash model
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        print("✅ Gemini model initialized successfully.")

    except Exception as e:
        model = None
        print(f"❌ Error configuring Gemini: {e}")


async def generate_gemini_response(prompt: str) -> Dict[str, Any]:
    """
    Generates a response from Gemini API safely.
    Returns a dict with success, message, and data.
    """
    global model

    if model is None:
        return {
            "success": False,
            "message": "Gemini model not initialized",
            "data": None
        }

    retries = 3
    for attempt in range(retries):
        try:
            # Run the blocking Gemini call in a thread
            response = await asyncio.to_thread(model.generate_content, prompt)
            return {
                "success": True,
                "message": "Response generated successfully",
                "data": response.text
            }
        except Exception as e:
            # Retry on rate-limit errors
            if "429" in str(e) and attempt < retries - 1:
                wait_time = 2 ** attempt
                print(f"⚠️ Rate limit hit. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)
                continue
            return {
                "success": False,
                "message": "Error during Gemini response generation",
                "data": str(e)
            }
