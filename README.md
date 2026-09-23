# Brand Asset Automator

A small workflow-automation tool that starts from a real operational problem and turns it into a working solution.
A user uploads a brand logo through a web portal. The tool generates every required logo variant (resized and dark-background versions), shows a preview, and emails the files to the operations team.

It works for any platform that onboards brands, partners or merchants and needs a consistent set of logo assets from each one.

---

## 🧩 Problem Scenario

When a platform onboards a new brand, someone has to prepare its logo for every place it appears:

- Resize it into several fixed dimensions (square icons, banners, and so on)
- Make a version that stays readable on a dark background
- Save the files in an organised way and hand them to the team that publishes them

Done by hand, this is **repetitive, slow and inconsistent**. Logos get stretched, light logos disappear on dark backgrounds, files get lost in chat threads, and every new brand adds more manual work.

## 💡 Solution

Automate the whole step so that one upload replaces the manual work:

| Pain point | How the automator solves it |
|------------|-----------------------------|
| Manual resizing into many sizes | All sizes are generated automatically in one pass |
| Logos get distorted | Logos are scaled to fit and padded, never stretched |
| Light logos vanish on dark backgrounds | Brightness detection inverts only the logos that need it |
| Messy backgrounds | The background colour is detected and removed automatically |
| Files scattered everywhere | Output goes to a consistent folder per brand: `output/<brand_id>/` |
| Ops has to chase the files | The assets are emailed to Ops automatically |

---

## ⚙️ How It Works

```
User ──► Upload Portal (Flask) ──► Image Processor (Pillow) ──► output/<brand_id>/
                                                  │
                                                  └──► Email Notifier (yagmail) ──► Ops inbox
```

1. **Upload:** The user enters a **Brand ID** and uploads a PNG or JPEG logo (max 10 MB).
2. **Validate:** The app checks the Brand ID, file type and file contents.
3. **Process:** `image_processor.py` generates the asset variants and saves them to `output/<brand_id>/`.
4. **Notify:** `notifier.py` emails Ops with every generated file attached.
5. **Review:** A results page previews each asset and shows whether the email was sent.

---

## 🖼️ Generated Assets

| File | Size | Description |
|------|------|-------------|
| `logo_500x500.png` | 500 × 500 | Square logo, small |
| `logo_1000x1000.png` | 1000 × 1000 | Square logo, large |
| `banner_1500x1000.png` | 1500 × 1000 | Banner format |
| `logo_inverted.png` | original | Logo on a **black** background |
| `logo_on_white.png` | original | Logo on a **white** background |

The resized variants keep the logo's aspect ratio. The logo is scaled to fit using LANCZOS resampling and centred on a transparent canvas.

### Dark-background (“inverted”) logic

Simply inverting every logo would ruin most of them, so the processor decides per logo:

1. **Detect the background.** It samples the four corners. If they are transparent, the logo already has no background. Otherwise the most common corner colour is taken as the background (white, grey or any solid colour).
2. **Remove the background.** Pixels within a small tolerance of that colour become transparent.
3. **Measure brightness.** For the remaining visible pixels it computes luminance (`0.299·R + 0.587·G + 0.114·B`) and counts light vs. dark pixels.
4. **Decide.**
   - **Mostly light logo:** the colours are inverted so the logo stays visible on black.
   - **Mostly dark or colourful logo:** the original colours are kept.
5. **Composite.** The result is placed on a solid black canvas.

---

## 📂 Project Structure

```
├── app.py               # Flask app: upload form, validation, results page, asset serving
├── image_processor.py   # Resizing, background removal and inversion logic (Pillow)
├── notifier.py          # Sends the Ops email with the assets attached (yagmail)
├── requirements.txt     # Python dependencies
├── templates/
│   ├── index.html       # Upload portal (Bootstrap)
│   └── result.html      # Results page with asset previews and email status
├── static/
│   └── style.css        # Page styling
└── output/              # Generated assets, one folder per brand (git-ignored)
```

---

## 🚀 Getting Started

### 1. Install dependencies

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

```bash
pip install -r requirements.txt
```

### 2. Configure email (optional)

Create a `.env` file in the project root:

```
EMAIL_USER=your_gmail_address@gmail.com
EMAIL_PASS=your_gmail_app_password
EMAIL_TO=ops_team@example.com
```

- `EMAIL_PASS` must be a Gmail **App Password**, not your normal password.
- `EMAIL_TO` is the address that receives the assets. If you leave it out, the email goes to `EMAIL_USER`.

If email isn't configured, the assets are still generated and previewed. The results page shows “Failed to send email” and the reason is printed in the terminal.

### 3. Run the app

```bash
python app.py
```

Open **http://localhost:5002**, enter a Brand ID, upload a logo and click **Process Logo**.

---

## 🛡️ Input Validation

- **Brand ID:** letters, numbers, `-` and `_` only (max 64 characters). This also stops path-traversal attempts such as `../`.
- **File type:** `.png`, `.jpg` and `.jpeg` only, and the file must actually be a readable image.
- **File size:** 10 MB maximum.

---

## 🧰 Tech Stack

- **Flask**: web portal, routing and serving generated assets
- **Pillow**: image resizing and pixel processing
- **yagmail**: sending the Gmail SMTP notification
- **python-dotenv**: loading credentials from `.env`
- **Bootstrap 5**: UI styling

---

## 🔭 Possible Extensions

- Configurable output sizes, e.g. from a config file, to suit different platforms
- Cloud storage (S3, Google Drive) instead of local folders
- Slack or Teams notifications alongside email
- Direct upload into a CMS or asset-management system
- Authentication on the upload portal
