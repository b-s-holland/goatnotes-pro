from flask import Flask, render_template, request, redirect, url_for
import requests
import os
from dotenv import load_dotenv

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
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            # OCR.Space API call
            with open(filepath, 'rb') as image_file:
                response = requests.post(
                    'https://api.ocr.space/parse/image',
                    files={'filename': image_file},
                    data={'language': 'eng', 'isOverlayRequired': False},
                    headers={'apikey': OCR_API_KEY}
                )
            result = response.json()
            print("OCR API response:", result)
            try:
                extracted_text = result['ParsedResults'][0]['ParsedText']
            except (KeyError, IndexError):
                extracted_text = "[OCR failed or returned no text]"

            filename = file.filename
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

    return render_template("result.html", scanned_text=extracted_text, scanned_image=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
