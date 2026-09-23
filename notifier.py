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
    receiver = os.getenv("EMAIL_TO", sender)  # Ops inbox; defaults to the sender

    if not sender or not app_password:
        raise ValueError("Missing EMAIL_USER or EMAIL_PASS in environment variables")

    yag = yagmail.SMTP(sender, app_password)

    subject = f"[Logo Automation] Assets processed for {brand_id}"
    body = f"Hi Ops team,\n\nThe assets for brand '{brand_id}' have been processed and saved in {output_dir}.\n\nRegards,\nAutomation Bot"

    attachments = [os.path.join(output_dir, f) for f in os.listdir(output_dir)]

    yag.send(to=receiver, subject=subject, contents=body, attachments=attachments)
    print("[INFO] Email sent successfully.")
