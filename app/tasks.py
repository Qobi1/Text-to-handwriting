import random
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from django.conf import settings
from celery import shared_task
from datetime import datetime
import uuid


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


def apply_perspective_effect(image):
    """Applies a slight random rotation to simulate a phone-captured shot."""
    angle = random.uniform(-3, 3)  # Slight tilt for a natural look
    return image.rotate(angle, expand=True)


@shared_task
def text_to_handwriting(
    text: str,
    font: str = "handwriting_1.ttf",
    ink_color=(50, 30, 20),
    background_image: str = "background_2.jpeg",
    x_offset: int = 50,
    word_spacing: int = 4,  # Adjusted to match frontend
    font_size: int = 24,  # Match frontend default size
    line_spacing: int = 2,  # Match frontend default spacing
    is_image: bool = True,
):
    font_size = int(font_size * 3.5)  # More accurate scaling factor
    line_spacing = int(line_spacing * font_size * 0.5)  # Ensure correct line height

    font_path = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/fonts/{font}")

    if background_image == 'background_2.jpeg':
        # Use predefined background from static files
        background_image = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/background_images/{background_image}")


    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Load background image for size reference
    bg_sample = Image.open(background_image)
    max_width, max_height = bg_sample.size
    bg_sample.close()

    # Load font
    font = ImageFont.truetype(font_path, size=font_size)

    words = text.split()
    word_index = 0
    image_files = []

    while word_index < len(words):
        bg = Image.open(background_image).convert("RGB")
        draw = ImageDraw.Draw(bg)
        x, y = x_offset, 50  # Start position

        while word_index < len(words):
            word = words[word_index]
            bbox = draw.textbbox((0, 0), word, font=font) or (0, 0, 0, 0)
            word_width = bbox[2] - bbox[0]
            word_height = bbox[3] - bbox[1]

            # Move to new line if needed
            if x + word_width > max_width - 20:
                x = x_offset
                y += line_spacing + font_size  # Proper spacing like frontend

            if y + font_size > max_height - 50:
                break

            # Draw the word
            draw.text((x, y), word, font=font, fill=ink_color)
            x += word_width + word_spacing
            word_index += 1

        transformed_image = apply_perspective_effect(bg)

        # Save the generated image
        image_filename = os.path.join("media", f"handwriting_{uuid.uuid4()}.jpg")
        transformed_image.save(image_filename, "JPEG")
        image_files.append(image_filename)

    if is_image:
        return [os.path.abspath(img) for img in image_files]

    # Create PDF with all generated images
    pdf = FPDF()
    for img_file in image_files:
        pdf.add_page()
        pdf.image(img_file, x=10, y=10, w=pdf.w - 20)

    pdf_path = os.path.abspath(f"media/handwriting_{timestamp}.pdf")
    pdf.output(pdf_path)
    return pdf_path

