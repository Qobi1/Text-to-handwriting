import random
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from django.conf import settings
from celery import shared_task
from datetime import datetime
import uuid
from django.core.files.storage import default_storage
from io import BytesIO
import requests
import tempfile


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
        word_spacing: int = 4,
        font_size: int = 24,
        line_spacing: int = 2,
        is_image: bool = True,
        letter_spacing: int = 1,
        left_padding: int = 20,
        right_padding: int = 20,
):
    font_size = int(font_size * 3.5)
    line_spacing = int(line_spacing * font_size * 0.5)
    left_padding *= 2
    right_padding *= 2
    letter_spacing *= 2

    font_path = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/fonts/{font}")

    if background_image == 'background_2.jpeg':
        background_image = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/background_images/{background_image}")

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    bg_sample = Image.open(background_image)
    max_width, max_height = bg_sample.size
    bg_sample.close()

    font = ImageFont.truetype(font_path, size=font_size)
    words = text.split()
    word_index = 0
    image_files = []

    while word_index < len(words):
        bg = Image.open(background_image).convert("RGB")
        draw = ImageDraw.Draw(bg)
        x, y = left_padding, 50

        while word_index < len(words):
            word = words[word_index]
            bbox = draw.textbbox((0, 0), word, font=font) or (0, 0, 0, 0)
            word_width = bbox[2] - bbox[0]
            word_height = bbox[3] - bbox[1]

            if x + word_width > max_width - right_padding:
                x = left_padding
                y += line_spacing + font_size

            if y + font_size > max_height - 50:
                break

            for letter in word:
                letter_bbox = draw.textbbox((0, 0), letter, font=font) or (0, 0, 0, 0)
                letter_width = letter_bbox[2] - letter_bbox[0]
                draw.text((x, y), letter, font=font, fill=ink_color)
                x += letter_width + letter_spacing

            x += word_spacing
            word_index += 1

        transformed_image = apply_perspective_effect(bg)

        image_filename = f"handwriting_{uuid.uuid4()}.jpg"
        image_io = BytesIO()
        transformed_image.save(image_io, format="JPEG")  # Save image to BytesIO buffer
        image_io.seek(0)  # Move to the beginning of the BytesIO object

        image_path = default_storage.save(image_filename, image_io)  # Upload to S3
        image_files.append(default_storage.url(image_path))  # Store the file URL

    if is_image:
        return image_files

    pdf = FPDF()
    for img_url in image_files:
        pdf.add_page()

        # 🔥 Fetch image and convert to PNG
        img_io = fetch_s3_image(img_url)  # ⬅️ Download from S3
        img = Image.open(img_io)  # ⬅️ Open in PIL

        # 🔥 Save to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
            img.save(tmp_file, format="PNG")
            tmp_file_path = tmp_file.name  # Get the file path

        # ✅ Use the temporary file path in FPDF
        pdf.image(tmp_file_path, x=10, y=10, w=pdf.w - 20)

    pdf_filename = f"handwriting_{timestamp}.pdf"

    # Save to a temporary file first
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        tmp_pdf_path = tmp_pdf.name
        pdf.output(tmp_pdf_path)

    # Read the file into memory
    with open(tmp_pdf_path, 'rb') as f:
        pdf_io = BytesIO(f.read())
    pdf_io.seek(0)

    # Upload to S3
    pdf_path = default_storage.save(pdf_filename, pdf_io)
    pdf_url = default_storage.url(pdf_path)

    # Optional: clean up the temp file
    os.remove(tmp_pdf_path)

    return pdf_url


def fetch_s3_image(image_url):
    """Downloads an image from S3 and returns a BytesIO object."""
    response = requests.get(image_url, stream=True)
    if response.status_code == 200:
        img_io = BytesIO(response.content)
        img_io.seek(0)
        return img_io
    raise RuntimeError(f"Failed to fetch image: {image_url}")
