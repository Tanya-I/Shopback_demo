# ShopBack Demo - Merchant Logo Automation

This is a prototype demo for **automating brand onboarding workflow** at ShopBack.  
It allows merchants to upload logos through a simple portal, automatically generates the required asset variants (resized + inverted logos), and notifies the Ops team via email.

---

## 🚀 Features
- **Upload Portal (Streamlit):** Merchants upload logos directly.
- **Automated Processing:** Python (Pillow) resizes images and creates inverted logos.
- **Output Storage:** Saves processed files into structured folders (`output/brand_id`).
- **Email Notifications:** Automatically emails Ops with processed files attached.

---

## 📂 Project Structure
