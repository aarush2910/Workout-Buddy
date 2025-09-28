import os
import google.generativeai as genai  # type: ignore

model = None

async def configure_gemini_model():
    """
    Initializes Gemini Flash using API key from environment variable.
    """
    global model
    api_key = os.getenv("GEMINI_API_KEY")  # <-- make sure this is set in your .env

    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables!")
        return

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
        print("✅ Gemini Flash model initialized successfully")
    except Exception as e:
        print(f"❌ Error configuring Gemini: {e}")


async def generate_gemini_response(prompt: str) -> str:
    """
    Generates content from Gemini asynchronously.
    """
    if model is None:
        return "Error: Gemini model not initialized."

    try:
        # Run blocking call in a thread
        import asyncio
        response = await asyncio.to_thread(model.generate_content, prompt)
        return response.text
    except Exception as e:
        return f"Error generating content: {e}"
