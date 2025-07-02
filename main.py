from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import openai
import requests
import tempfile
import urllib.request

app = Flask(__name__)
load_dotenv()

# Cloudinary Config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# --- OCR Step 1: Extract Text from Image ---
def extract_text_from_image_url(image_url):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "You are a text extraction and layout assistant. RULES: Extract all text visible in this image as clearly and accurately as possible and format it appropriately based on the visual structure. If the image contains a table, return the extracted content as a clean, structured CSV table, replacing all commas within the cell text with semi-colons. If not, return the extracted text content, preserving structured formatting and line breaks. Use your best judgement.If the image contains shapes or flow chart elements, please sketch them out in text format. Group text wherever you can see it's visually sectioned off or grouped"
                            )
                        },
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ],
            max_tokens=1500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"[Text extraction failed: {e}]"

# --- Step 2: Generate HTML Layout from Extracted Text ---
def generate_html_layout_from_text(structured_text_output):
    try:
        # ✅ Simple CSV detection
        csv_line_count = structured_text_output.count('\n')
        csv_comma_count = structured_text_output.count(',')

        is_csv = csv_comma_count >= 2 and csv_line_count >= 2

        if is_csv:
            system_prompt = (
                "You are a layout assistant. Format the following CSV-style data into a clean, mobile-friendly HTML table. "
                "Use proper <table>, <thead>, <tbody>, <tr>, and <td> tags. "
                "Add light grey borders, cell padding, and spacing for readability. "
                "Do not wrap it in extra text. Just output the table HTML only."
            )
        else:
            system_prompt = (
                "You are a layout assistant. Format the following extracted note content into clean, minimal HTML for a single webpage section. Output only the inner HTML body content—headings, paragraphs, lists, and basic inline styles are okay. ❌ Do not include any outer HTML, HEAD, or BODY tags. ❌ Do not include scripts, forms, buttons, or full page structures. ✅ Only return the HTML needed for the content section itself. "
                "Use headings (<h2>, <h3>), sections, divs, and semantic spacing. "
                "Reflect any lists, headings, or flowchart structures where visible. "
                "Do not create a table unless the text is in CSV format."
            )

        user_prompt = f"Structured text:\n\n{structured_text_output}"

        response = openai.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=1500
        )

        content = response.choices[0].message.content.strip()

        # ✅ Clean markdown code fences
        if content.startswith("```html"):
            content = content[7:].strip()
        if content.endswith("```"):
            content = content[:-3].strip()

        return content

    except Exception as e:
        return f"[HTML layout generation failed: {e}]"



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    file = request.files.get('file')
    if file and file.filename:
        try:
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result.get("secure_url")

            extracted_text = extract_text_from_image_url(image_url)
            generated_html_layout = generate_html_layout_from_text(extracted_text)


        except Exception as e:
            extracted_text = f"[Error: {e}]"
            image_url = ""
            generated_html_layout = ""
    else:
        return redirect(url_for('index'))

    return render_template(
        "result.html",
        scanned_text=extracted_text,
        scanned_image=image_url,
        generated_html_layout=generated_html_layout,
    )

@app.route('/print_view', methods=['POST'])
def print_view():
    html_content = request.form.get('html_content')
    return render_template('print_view.html', html_content=html_content)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
