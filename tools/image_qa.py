import time
import os
from config import gemini_client, VISION_MODEL


def ask_image_question(image_path, question):

    if not os.path.exists(image_path):
        return "Image file not found."

    retries = 3
    delay = 2

    for attempt in range(retries):

        try:

            with open(image_path, "rb") as f:
                image_bytes = f.read()

            response = gemini_client.models.generate_content(
                model=VISION_MODEL,
                contents=[
                    {
                        "role": "user",
                        "parts": [
                            {"text": question},
                            {
                                "inline_data": {
                                    "mime_type": "image/jpeg",
                                    "data": image_bytes
                                }
                            }
                        ]
                    }
                ]
            )

            return response.text

        except Exception as e:

            if attempt == retries - 1:
                return f"Image QA failed: {str(e)}"

            print(f"Retry {attempt + 1}/{retries} after error: {e}")

            time.sleep(delay)
            delay *= 2