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


            
            # Check and compress image if needed
            try:
                # Get file size
                file_size = os.path.getsize(filepath)
                
                if file_size > 900 * 1024:  # If larger than 900KB, compress
                    # Open and compress image
                    with Image.open(filepath) as img:
                        # Convert to RGB if necessary
                        if img.mode in ('RGBA', 'P'):
                            img = img.convert('RGB')
                        
                        # Calculate new dimensions to reduce file size
                        quality = 85
                        max_dimension = 1500
                        
                        # Resize if image is too large
                        if max(img.size) > max_dimension:
                            ratio = max_dimension / max(img.size)
                            new_size = (int(img.size[0] * ratio), int(img.size[1] * ratio))
                            img = img.resize(new_size, Image.Resampling.LANCZOS)
                        
                        # Save compressed version
                        compressed_path = os.path.join(app.config['UPLOAD_FOLDER'], f"compressed_{file.filename}")
                        img.save(compressed_path, 'JPEG', quality=quality, optimize=True)
                        
                        # Use compressed file for OCR
                        ocr_filepath = compressed_path
                else:
                    ocr_filepath = filepath

                # OCR.Space API call
                with open(ocr_filepath, 'rb') as image_file:
                    response = requests.post(
                        'https://api.ocr.space/parse/image',
                        files={'filename': image_file},
                        data={'language': 'eng', 'isOverlayRequired': False},
                        headers={'apikey': OCR_API_KEY}
                    )
                
                result = response.json()
                print("OCR API response:", result)
                
                # Better error handling
                if result.get('IsErroredOnProcessing'):
                    error_msg = result.get('ErrorMessage', ['Unknown error'])[0]
                    extracted_text = f"[OCR Error: {error_msg}]"
                elif result.get('ParsedResults') and len(result['ParsedResults']) > 0:
                    extracted_text = result['ParsedResults'][0].get('ParsedText', '[No text found]')
                else:
                    extracted_text = "[OCR failed or returned no text]"
                    
            except Exception as e:
                print(f"Error processing image: {str(e)}")
                extracted_text = f"[Error processing image: {str(e)}]"

            filename = file.filename
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))

    return render_template("result.html", scanned_text=extracted_text, scanned_image=filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
