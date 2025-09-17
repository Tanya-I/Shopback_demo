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

    # Logo on black background (inverted version)
    if img.mode != "RGBA":
        img = img.convert("RGBA")
    
    # Analyze the logo to determine if it's predominantly light
    def is_light_color(r, g, b, threshold=127):
        # Calculate luminance using standard formula
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance > threshold
    
    def analyze_logo_brightness(image):
        data = image.getdata()
        light_pixels = 0
        dark_pixels = 0
        background_pixels = 0
        
        for item in data:
            r, g, b, a = item if len(item) == 4 else (*item, 255)
            
            # Skip fully transparent pixels
            if a < 10:
                continue
                
            # Count background pixels (white/very light)
            if r > 240 and g > 240 and b > 240:
                background_pixels += 1
            elif is_light_color(r, g, b):
                light_pixels += 1
            else:
                dark_pixels += 1
        
        total_content_pixels = light_pixels + dark_pixels
        if total_content_pixels == 0:
            return False  # No content, don't invert
            
        return light_pixels > dark_pixels
    
    logo_is_light = analyze_logo_brightness(img)
    
    # Process the image
    data = img.getdata()
    new_data = []
    
    for item in data:
        r, g, b, a = item if len(item) == 4 else (*item, 255)
        
        # If pixel is background (white/very light), make it transparent
        if r > 240 and g > 240 and b > 240:
            new_data.append((0, 0, 0, 0))  # Transparent
        else:
            # If logo is predominantly light, invert non-background colors
            if logo_is_light:
                # Invert the colors but keep alpha
                new_r = 255 - r
                new_g = 255 - g
                new_b = 255 - b
                new_data.append((new_r, new_g, new_b, a))
            else:
                # Keep original colors
                new_data.append((r, g, b, a))
    
    processed_img = Image.new("RGBA", img.size)
    processed_img.putdata(new_data)
    
    # Create black background version
    black_bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    black_bg.paste(processed_img, (0, 0), processed_img)
    black_bg.save(f"{output_dir}/logo_inverted.png")

    # Optional: Also create logo on white background for consistency
    white_bg = Image.new("RGBA", img.size, (255, 255, 255, 255))
    if img.mode in ("RGBA", "LA"):
        white_bg.paste(img, (0, 0), img)  # preserve transparency
    else:
        white_bg.paste(img, (0, 0))
    white_bg.save(f"{output_dir}/logo_on_white.png")

    return output_dir