from flask import Flask, render_template, request, url_for
from image_processor import process_images
from notifier import send_email_notification
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return "❌ No file uploaded"

    file = request.files['file']
    brand_id = request.form.get("brand_id", "demo_brand")

    if file.filename == '':
        return "❌ No selected file"

    # Process file
    output_dir = process_images(file, brand_id)

    # Build list of processed images to preview
    images = [f"../output/{brand_id}/{f}" for f in os.listdir(output_dir)]

    # Try sending email
    try:
        send_email_notification(brand_id, output_dir)
        email_status = f"Assets emailed to Ops successfully."
    except Exception as e:
        email_status = None

    return render_template("result.html", brand_id=brand_id, output_dir=output_dir, images=images, email_status=email_status)

if __name__ == "__main__":
    app.run(port=5001, debug=True, use_reloader=False)
