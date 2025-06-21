from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def home():
    return redirect(url_for('capture'))

@app.route('/capture')
def capture():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    # For now, just simulate the flow — real OCR/NFC can come later
    return render_template('result.html')

if __name__ == '__main__':
    app.run(debug=True)