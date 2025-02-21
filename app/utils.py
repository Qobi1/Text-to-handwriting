import random
import os
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF
from django.conf import settings


def apply_perspective_effect(image):
    """Applies a slight random rotation to simulate a phone-captured shot."""
    angle = random.uniform(-5, 5)  # Rotate between -5 and +5 degrees
    return image.rotate(angle, expand=True)


def text_to_handwriting(text, font="handwriting_1.ttf", ink_color=(50, 30, 20), background_image="background_2.jpeg", x_offset=500,
                        word_spacing=15, output_pdf="output.pdf"):
    print(font)
    # Get the first static directory and build the font path
    font_path = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/fonts/{font}")
    background_image = os.path.join(settings.STATICFILES_DIRS[0], f"api_data/background_images/{background_image}")

    # Load font
    font = ImageFont.truetype(font_path, size=50)

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
            bbox = draw.textbbox((0, 0), word, font=font)
            word_width, word_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

            # Move to next line if needed
            if x + word_width > max_width - 20:
                x = x_offset
                y += word_height + 10

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
        image_filename = f"temp_handwriting_{len(image_files)}.jpg"
        transformed_image.save(image_filename, "JPEG")
        image_files.append(image_filename)

        print(f"Generated image: {image_filename} with word index starting at {word_index}")

    # Step 2: Create PDF and add all images
    pdf = FPDF()
    for img_file in image_files:
        pdf.add_page()
        pdf.image(img_file, x=10, y=10, w=pdf.w - 20)

    # Save final PDF
    pdf.output(f'media/{output_pdf}')
    print(f"PDF saved as {output_pdf}")

    # Step 3: Clean up temporary images
    for img_file in image_files:
        os.remove(img_file)
        print(f"Deleted temporary file: {img_file}")

    pdf_path = os.path.abspath(f"media/{output_pdf}")  # Get full path
    return pdf_path  # Return the full path instead of just printing it

# # Example usage
# text_to_handwriting(
#     text="This is a long text that should continue across multiple pages instead of repeating the same content on every page. "
#          "Each page should start where the previous one left off, just like writing on paper. "
#          "This should look like a natural handwritten document taken from a phone." * 80,
#     font_path="static/handwriting.ttf",
#     ink_color=(50, 30, 20),
#     background_image="background_2.jpg",
#     x_offset=50,
#     word_spacing=15
# )
