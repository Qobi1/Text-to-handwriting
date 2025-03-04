import random
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from django.conf import settings
from celery import shared_task
from datetime import datetime
import uuid


# def apply_perspective_effect(image):
#     """Applies a slight random rotation to simulate a phone-captured shot."""
#     angle = random.uniform(-5, 5)  # Rotate between -5 and +5 degrees
#     return image.rotate(angle, expand=True)
#
#
# @shared_task
# def text_to_handwriting(
#         text: str, font: str = "handwriting_1.ttf", ink_color=(50, 30, 20),
#         background_image: str = "background_2.jpeg", x_offset: int = 50,
#         word_spacing: int = 15, font_size: int = 50, line_spacing: int = 10,
#         is_image: bool = True
# ):
#     # Get the first static directory and build the font path
#     font_path = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/fonts/{font}")
#     background_image = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/background_images/{background_image}")
#     timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
#
#     # Load font
#     font = ImageFont.truetype(font_path, size=font_size)
#
#     # Load background image to get dimensions
#     bg_sample = Image.open(background_image)
#     max_width, max_height = bg_sample.size
#     bg_sample.close()
#
#     words = text.split()
#     word_index = 0
#     image_files = []  # Store generated image filenames
#
#     # Step 1: Generate all images first
#     while word_index < len(words):
#         # Load a fresh background for each page
#         bg = Image.open(background_image).convert("RGB")
#         draw = ImageDraw.Draw(bg)
#
#         x, y = x_offset, 50  # Start writing at the top
#
#         while word_index < len(words):
#             word = words[word_index]
#             bbox = draw.textbbox((0, 0), word, font=font) or (0, 0, 0, 0)
#             word_width, word_height = bbox[2] - bbox[0], bbox[3] - bbox[1]
#
#             # Move to next line if needed
#             if x + word_width > max_width - 20:
#                 x = x_offset
#                 y += word_height + line_spacing
#
#             # If text reaches the bottom, break and continue on a new page
#             if y + word_height > max_height - 50:
#                 break
#
#             # Draw the word
#             draw.text((x, y), word, font=font, fill=ink_color)
#             x += word_width + word_spacing
#             word_index += 1  # Move to the next word
#
#         # Apply rotation effect
#         transformed_image = apply_perspective_effect(bg)
#         # Save image with a unique filename
#         image_filename = os.path.join('media', f"handwriting_{uuid.uuid4()}.jpg")
#         transformed_image.save(image_filename, "JPEG")
#         image_files.append(image_filename)
#
#         print(f"Generated image: {image_filename} with word index starting at {word_index}")
#
#     if is_image:
#         image_paths = [os.path.abspath(img) for img in image_files]  # Convert all to absolute paths
#         return image_paths  # Return the list properly
#
#     # Step 2: Create PDF and add all images
#     pdf = FPDF()
#     for img_file in image_files:
#         pdf.add_page()
#         pdf.image(img_file, x=10, y=10, w=pdf.w - 20)
#
#     # Save final PDF
#     pdf.output(f'media/handwriting_{timestamp}.pdf')
#
#     # Step 3: Clean up temporary images
#     # for img_file in image_files:
#     #     os.remove(img_file)
#     #     print(f"Deleted temporary file: {img_file}")
#
#     pdf_path = os.path.abspath(f"media/handwriting_{timestamp}.pdf")  # Get full path
#     return pdf_path  # Return the full path instead of just printing it

import os
import uuid
import random
from datetime import datetime
from celery import shared_task
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF


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
    font_size: int = 50,
    line_spacing: int = 10,
    is_image: bool = True,
):
    font_size *= 3
    line_spacing *= 5
    word_spacing *= 8
    # Load font correctly
    font_path = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/fonts/{font}")
    background_image = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/background_images/{background_image}")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Load background image for size reference
    bg_sample = Image.open(background_image)
    max_width, max_height = bg_sample.size
    bg_sample.close()

    # Convert frontend font size to backend DPI scale
    pixels_per_inch = 96  # Web standard DPI
    scaled_font_size = int((font_size / 96) * pixels_per_inch)  # Scale accordingly

    # Load font
    font = ImageFont.truetype(font_path, size=scaled_font_size)

    # Set a constant line height based on the font size
    fixed_line_height = int(font_size * 1.5)  # 1.5x font size for consistent spacing

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
            word_width = bbox[2] - bbox[0]  # Get word width

            # Move to new line if needed
            if x + word_width > max_width - 20:
                x = x_offset
                y += fixed_line_height  # Use fixed height instead of word-based height

            if y + fixed_line_height > max_height - 50:
                break

            # Draw the word
            draw.text((x, y), word, font=font, fill=ink_color)
            x += word_width + word_spacing  # Keep word spacing

            word_index += 1

        # Apply natural rotation
        transformed_image = apply_perspective_effect(bg)

        # Save the generated image
        image_filename = os.path.join("media", f"handwriting_{uuid.uuid4()}.jpg")
        transformed_image.save(image_filename, "JPEG")
        image_files.append(image_filename)

        print(f"Generated image: {image_filename} (word index: {word_index})")

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





