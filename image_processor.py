from PIL import Image, ImageOps
from collections import Counter
import os

OUTPUT_ROOT = "output"

# How close (per RGB channel) a pixel must be to the background colour to count as background
BACKGROUND_TOLERANCE = 15

def process_images(uploaded_file, brand_id):
    output_dir = f"{OUTPUT_ROOT}/{brand_id}"
    os.makedirs(output_dir, exist_ok=True)

    sizes = {
        "logo_500x500": (500, 500),
        "logo_1000x1000": (1000, 1000),
        "banner_1500x1000": (1500, 1000)
    }

    img = Image.open(uploaded_file).convert("RGBA")

    # Generate resized variants: scale to fit and pad with transparency so logos aren't stretched
    for name, size in sizes.items():
        resized = ImageOps.pad(img, size, method=Image.Resampling.LANCZOS, color=(0, 0, 0, 0))
        output_path = f"{output_dir}/{name}.png"
        resized.save(output_path)

    # Detect the background colour from the four corners.
    # Returns None if the logo already has a transparent background.
    def detect_background(image):
        w, h = image.size
        corners = [image.getpixel(p) for p in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]]
        opaque = [c[:3] for c in corners if c[3] >= 10]
        if not opaque:
            return None
        return Counter(opaque).most_common(1)[0][0]

    background = detect_background(img)

    def is_background(r, g, b):
        if background is None:
            return False
        br, bg, bb = background
        return abs(r - br) <= BACKGROUND_TOLERANCE and abs(g - bg) <= BACKGROUND_TOLERANCE and abs(b - bb) <= BACKGROUND_TOLERANCE

    # Analyze the logo to determine if it's predominantly light
    def is_light_color(r, g, b, threshold=127):
        # Calculate luminance using standard formula
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance > threshold

    def analyze_logo_brightness(image):
        light_pixels = 0
        dark_pixels = 0

        for r, g, b, a in image.getdata():
            # Skip transparent and background pixels
            if a < 10 or is_background(r, g, b):
                continue

            if is_light_color(r, g, b):
                light_pixels += 1
            else:
                dark_pixels += 1

        if light_pixels + dark_pixels == 0:
            return False  # No content, don't invert

        return light_pixels > dark_pixels

    logo_is_light = analyze_logo_brightness(img)

    # Process the image: remove the background, invert light logos
    new_data = []

    for r, g, b, a in img.getdata():
        if is_background(r, g, b):
            new_data.append((0, 0, 0, 0))  # Transparent
        elif logo_is_light:
            # Invert the colors but keep alpha
            new_data.append((255 - r, 255 - g, 255 - b, a))
        else:
            # Keep original colors
            new_data.append((r, g, b, a))

    processed_img = Image.new("RGBA", img.size)
    processed_img.putdata(new_data)

    # Create black background version
    black_bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    black_bg.paste(processed_img, (0, 0), processed_img)
    black_bg.save(f"{output_dir}/logo_inverted.png")

    # Also create logo on white background for consistency
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    white_bg.paste(img, (0, 0), img)  # preserve transparency
    white_bg.save(f"{output_dir}/logo_on_white.png")

    return output_dir
