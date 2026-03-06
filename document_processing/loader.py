# pip install python-doc

import os
from pypdf import PdfReader
from docx import Document


def load_txt(path):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def load_pdf(path):
    reader = PdfReader(path)
    text = ""

    for page in reader.pages:
        text += page.extract_text() or ""

    return text


def load_docx(path):
    doc = Document(path)

    text = []
    for para in doc.paragraphs:
        text.append(para.text)

    return "\n".join(text)


def load_documents(folder_path):

    documents = []

    for filename in os.listdir(folder_path):

        path = os.path.join(folder_path, filename)

        try:

            if filename.endswith(".txt"):
                text = load_txt(path)

            elif filename.endswith(".pdf"):
                text = load_pdf(path)

            elif filename.endswith(".docx"):
                text = load_docx(path)

            else:
                continue

            documents.append({
                "doc_id": filename,
                "text": text.strip()
            })

        except Exception as e:
            print(f"Skipping {filename}: {e}")
    print("Loaded {} documents".format(len(documents)))
    return documents