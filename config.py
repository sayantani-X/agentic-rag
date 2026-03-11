import os
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=os.getenv("OPENAI_API_KEY"))

EMBED_MODEL = "openai/text-embedding-3-small"
LLM_MODEL = "meta-llama/llama-3.1-8b-instruct"
VISION_MODEL = "openai/gpt-4o-mini"

TOP_K = 8