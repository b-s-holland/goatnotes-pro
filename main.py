from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv
from PIL import Image
import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

# Cloudinary configuration
cloudinary.config(
    cloud_name="dj9purdtw",
    api_key="558122275165898",
    api_secret="iOoqUCgEtV2_bUe2AxWKwopIr0Q",
    secure=True
)

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

load_dotenv()
OCR_API_KEY = os.getenv('OCR_API_KEY')
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    action = request.form.get('action')

    if action == "scan":
        # For now just simulate a placeholder
        extracted_text = "This is a simulated camera scan."
        filename = "placeholder-image.png"
    elif action == "upload":
        file = request.files.get('file')
        if file and file.filename:
            # Upload to Cloudinary instead of saving locally
            upload_result = cloudinary.uploader.upload(file)
            cloudinary_url = upload_result["secure_url"]

            # Send Cloudinary-hosted image to OCR provider
            response = requests.post(
                "https://api.ocr.space/parse/imageurl",
                data={
                    'apikey': OCR_API_KEY,
                    'url': cloudinary_url,
                    'language': 'eng',
                    'isOverlayRequired': False
                }
            )
            result = response.json()

            try:
                extracted_text = result['ParsedResults'][0]['ParsedText']
            except (KeyError, IndexError):
                extracted_text = "[OCR failed or returned no text]"

            filename = cloudinary_url  # Use the image URL in the result page
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

    return render_template("result.html", scanned_text=extracted_text, scanned_image=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
