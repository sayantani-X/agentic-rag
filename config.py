import os
from openai import OpenAI
import dotenv
from google import genai

dotenv.load_dotenv()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENAI_API_KEY"))
gemini_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

EMBED_MODEL = "openai/text-embedding-3-small"
LLM_MODEL = "meta-llama/llama-3.1-8b-instruct"
VISION_MODEL = "gemini-3-flash-preview"
# IMAGE_MODEL = "google/gemma-3-4b-it:free"
IMAGE_MODEL = "imagen-4.0-generate-001"

TOP_K = 8