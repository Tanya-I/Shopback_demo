from flask import Flask, render_template, request, url_for, send_from_directory
from PIL import UnidentifiedImageError
from image_processor import process_images, OUTPUT_ROOT
from notifier import send_email_notification
import os
import re

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB upload limit

ALLOWED_EXTENSIONS = {".png", ".jpg", ".jpeg"}
BRAND_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/output/<brand_id>/<path:filename>')
def output_file(brand_id, filename):
    # send_from_directory rejects paths that escape the brand folder
    return send_from_directory(os.path.join(OUTPUT_ROOT, brand_id), filename)

@app.errorhandler(413)
def file_too_large(e):
    return "❌ File too large (max 10 MB)", 413

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "❌ No file uploaded", 400

    file = request.files['file']
    brand_id = request.form.get("brand_id", "demo_brand").strip()

    if file.filename == '':
        return "❌ No selected file", 400

    if not BRAND_ID_PATTERN.match(brand_id):
        return "❌ Brand ID may only contain letters, numbers, '-' and '_' (max 64 characters)", 400

    if os.path.splitext(file.filename)[1].lower() not in ALLOWED_EXTENSIONS:
        return "❌ Only PNG and JPEG files are supported", 400

    # Process file
    try:
        output_dir = process_images(file, brand_id)
    except UnidentifiedImageError:
        return "❌ The uploaded file is not a valid image", 400

    # Build list of processed images to preview
    images = [
        {"name": f, "url": url_for("output_file", brand_id=brand_id, filename=f)}
        for f in sorted(os.listdir(output_dir))
    ]

    # Try sending email
    try:
        send_email_notification(brand_id, output_dir)
        email_status = "Assets emailed to Ops successfully."
    except Exception as e:
        print(f"[ERROR] Email failed: {e}")
        email_status = None

    return render_template("result.html", brand_id=brand_id, output_dir=output_dir, images=images, email_status=email_status)

if __name__ == "__main__":
    app.run(port=5002, debug=True, use_reloader=False)
