from flask import Flask, render_template, request, redirect, url_for
import os
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader
import openai

app = Flask(__name__)
load_dotenv()

# Cloudinary config
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

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
                                "Extract all visible text from this image as clearly and accurately as possible. "
                                "Preserve any headings, bullet points, tables (as CSV), and flowcharts (as ASCII). "
                                "Prioritise structured formatting."
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
                "You are a layout assistant. Format the following structured text into clean, readable HTML. "
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

# --- Home Page ---
@app.route('/')
def index():
    return render_template('index.html')

# --- Process Upload and AI Layout ---
@app.route('/process', methods=['POST'])
def process():
    file = request.files.get('file')
    if file and file.filename:
        try:
            # Upload image to Cloudinary
            upload_result = cloudinary.uploader.upload(file)
            image_url = upload_result.get("secure_url")

            # Step 1: OCR
            extracted_text = extract_text_from_image_url(image_url)

            # Step 2: AI Layout
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
        generated_html_layout=generated_html_layout
    )

# --- Print-friendly export view ---
@app.route('/print_view', methods=['POST'])
def print_view():
    html_content = request.form.get('html_content')
    return render_template('print_view.html', html_content=html_content)

# --- Run Flask App ---
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)