import os
from config import gemini_client, IMAGE_MODEL

SAVE_DIR = "data/generated_images"


def generate_image(prompt):

    os.makedirs(SAVE_DIR, exist_ok=True)

    print("\nGenerating image with Imagen...")

    response = gemini_client.models.generate_images(
        model=IMAGE_MODEL,
        prompt=prompt
    )

    # Imagen returns a PIL image object
    image = response.generated_images[0].image

    filename = f"generated_{abs(hash(prompt))}.png"
    filepath = os.path.join(SAVE_DIR, filename)

    image.save(filepath)

    print("\nImage saved at:", filepath)

    return filepath