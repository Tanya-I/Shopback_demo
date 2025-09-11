import yagmail
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

def send_email_notification(brand_id, output_dir):
    """
    Sends an email notification with processed assets attached.
    """
    sender = os.getenv("EMAIL_USER")  # from .env
    app_password = os.getenv("EMAIL_PASS")  # from .env
    receiver = "tanya011@e.ntu.edu.sg"  # replace with your test email

    if not sender or not app_password:
        raise ValueError("Missing EMAIL_USER or EMAIL_PASS in environment variables")

    yag = yagmail.SMTP(sender, app_password)

    subject = f"[ShopBack] Assets processed for {brand_id}"
    body = f"Hi  Tanya,\n\nThe assets for brand '{brand_id}' have been processed and saved in {output_dir}.\n\nRegards,\nAutomation Bot"

    attachments = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]

    yag.send(to=receiver, subject=subject, contents=body, attachments=attachments)
    print("[INFO] Email sent successfully.")
