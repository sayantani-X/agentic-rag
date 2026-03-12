import base64
import time
from config import client, VISION_MODEL


def ask_image_question(image_path, question):

    # read image
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    image_base64 = base64.b64encode(image_bytes).decode("utf-8")

    retries = 3
    delay = 2

    for attempt in range(retries):

        try:

            response = client.chat.completions.create(
                model=VISION_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": question},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:

            if attempt == retries - 1:
                raise e

            print(f"Retry {attempt + 1}/{retries} after error: {e}")
            time.sleep(delay)
            delay *= 2