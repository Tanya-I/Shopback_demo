from PIL import Image, ImageOps
import os

def process_images(uploaded_file, brand_id):
    output_dir = f"output/{brand_id}"
    os.makedirs(output_dir, exist_ok=True)

    sizes = {
        "logo_500x500": (500, 500),
        "logo_1000x1000": (1000, 1000),
        "banner_1500x1000": (1500, 1000)
    }

    img = Image.open(uploaded_file).convert("RGBA")

    # Generate resized variants with exact dimensions
    for name, size in sizes.items():
        resized = img.copy().resize(size, Image.Resampling.LANCZOS)
        output_path = f"{output_dir}/{name}.png"
        resized.save(output_path)

    # Inverted logo
    inverted = ImageOps.invert(img.convert("RGB"))
    inverted.save(f"{output_dir}/logo_inverted.png")

    # Original logo on black background
    black_bg = Image.new("RGB", img.size, (0, 0, 0))
    if img.mode in ("RGBA", "LA"):
        black_bg.paste(img, (0, 0), img)  # preserve transparency
    else:
        black_bg.paste(img, (0, 0))
    black_bg.save(f"{output_dir}/logo_on_black.png")

    return output_dir
