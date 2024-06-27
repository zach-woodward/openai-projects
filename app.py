import os
import openai
import fitz  # PyMuPDF
from docx import Document
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes

openai.api_key = "your_openai_api_key_here"

def extract_text_from_pdf(file):
    text = ""
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file):
    doc = Document(file)
    text = "\n".join([para.text for para in doc.paragraphs])
    return text

@app.route('/process', methods=['POST'])
def process():
    try:
        user_text = request.form['userText']
        file = request.files['file']

        file_text = ""
        if file:
            filename = file.filename
            if filename.endswith('.pdf'):
                file_text = extract_text_from_pdf(file)
            elif filename.endswith('.docx'):
                file_text = extract_text_from_docx(file)
            else:
                file_text = file.read().decode('utf-8')

        combined_text = f"{user_text}\n\n{file_text}"

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": combined_text}
            ],
            max_tokens=1500
        )

        return jsonify({"response": response.choices[0].message['content'].strip()})
    except Exception as e:
        print(f"Error: {str(e)}")  # Print the error to the server console
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
