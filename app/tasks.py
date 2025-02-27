import random
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from django.conf import settings
from celery import shared_task
from datetime import datetime
import uuid


def apply_perspective_effect(image):
    """Applies a slight random rotation to simulate a phone-captured shot."""
    angle = random.uniform(-5, 5)  # Rotate between -5 and +5 degrees
    return image.rotate(angle, expand=True)


@shared_task
def text_to_handwriting(
        text: str, font: str = "handwriting_1.ttf", ink_color=(50, 30, 20),
        background_image: str = "background_2.jpeg", x_offset: int = 50,
        word_spacing: int = 15, font_size: int = 50, line_spacing: int = 10,
        is_image: bool = True
):
    # Get the first static directory and build the font path
    font_path = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/fonts/{font}")
    background_image = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/background_images/{background_image}")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Load font
    font = ImageFont.truetype(font_path, size=font_size)

    # Load background image to get dimensions
    bg_sample = Image.open(background_image)
    max_width, max_height = bg_sample.size
    bg_sample.close()

    words = text.split()
    word_index = 0
    image_files = []  # Store generated image filenames

    # Step 1: Generate all images first
    while word_index < len(words):
        # Load a fresh background for each page
        bg = Image.open(background_image).convert("RGB")
        draw = ImageDraw.Draw(bg)

        x, y = x_offset, 50  # Start writing at the top

        while word_index < len(words):
            word = words[word_index]
            bbox = draw.textbbox((0, 0), word, font=font) or (0, 0, 0, 0)
            word_width, word_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # Move to next line if needed
            if x + word_width > max_width - 20:
                x = x_offset
                y += word_height + line_spacing

            # If text reaches the bottom, break and continue on a new page
            if y + word_height > max_height - 50:
                break

            # Draw the word
            draw.text((x, y), word, font=font, fill=ink_color)
            x += word_width + word_spacing
            word_index += 1  # Move to the next word

        # Apply rotation effect
        transformed_image = apply_perspective_effect(bg)
        # Save image with a unique filename
        image_filename = os.path.join('media', f"handwriting_{uuid.uuid4()}.jpg")
        transformed_image.save(image_filename, "JPEG")
        image_files.append(image_filename)

        print(f"Generated image: {image_filename} with word index starting at {word_index}")

    if is_image:
        image_paths = [os.path.abspath(img) for img in image_files]  # Convert all to absolute paths
        return image_paths  # Return the list properly

    # Step 2: Create PDF and add all images
    pdf = FPDF()
    for img_file in image_files:
        pdf.add_page()
        pdf.image(img_file, x=10, y=10, w=pdf.w - 20)

    # Save final PDF
    pdf.output(f'media/handwriting_{timestamp}.pdf')

    # Step 3: Clean up temporary images
    # for img_file in image_files:
    #     os.remove(img_file)
    #     print(f"Deleted temporary file: {img_file}")

    pdf_path = os.path.abspath(f"media/handwriting_{timestamp}.pdf")  # Get full path
    return pdf_path  # Return the full path instead of just printing it


def convert_images_to_pdf(image_files, output_pdf: str = f'output_{uuid.uuid4()}.pdf'):
    """Converts a list of images into a single PDF file."""
    pdf = FPDF()
    for img_file in image_files:
        pdf.add_page()
        pdf.image(img_file, x=10, y=10, w=pdf.w - 20)
        # Use MEDIA_ROOT instead of MEDIA_URL
    pdf_path = os.path.join(settings.MEDIA_ROOT, output_pdf)

    # Ensure the media directory exists
    os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

    pdf.output(pdf_path)
    return os.path.abspath(pdf_path)





