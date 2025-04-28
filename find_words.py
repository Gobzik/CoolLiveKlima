import os
import shutil

import fitz
import pytesseract
from PIL import Image
import re


def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text_by_page = {}
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        text_by_page[page_num + 1] = text
    return text_by_page


def extract_text_from_image(image_path):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image, lang='rus')
    return text


def find_keywords(text, keywords):
    found_keywords = []
    for keyword in keywords:
        if re.search(r'\b' + re.escape(keyword) + r'\b', text, re.IGNORECASE):
            found_keywords.append(keyword)
    return found_keywords


def save_page_as_image(page, page_num, output_folder="founded"):
    pix = page.get_pixmap()
    image_path = os.path.join(output_folder, f"page_{page_num}.png")
    pix.save(image_path)
    return image_path


def analyze_document(document_path, keywords, is_pdf=True):
    shutil.rmtree("founded")
    os.makedirs("founded")
    if is_pdf:
        doc = fitz.open(document_path)
        text_by_page = {}
        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            text_by_page[page_num + 1] = text
    else:
        text_by_page = {1: extract_text_from_image(document_path)}

    relevant_pages = []
    for page_num, text in text_by_page.items():
        found_keywords = find_keywords(text, keywords)
        if found_keywords:
            relevant_pages.append((page_num, found_keywords))
            if is_pdf:
                page = doc.load_page(page_num - 1)
                save_page_as_image(page, page_num)
            else:
                image = Image.open(document_path)
                output_path = os.path.join("founded", f"page_{page_num}.png")
                image.save(output_path)

    return relevant_pages


keywords = ["кондиционер", "вентиляция", "охлаждение", "воздуховод", "климатизация", "Conditioning", "Air", "air"]

document_path = "plans/55554.pdf"

relevant_pages = analyze_document(document_path, keywords, is_pdf=True)


if relevant_pages:
    print("Страницы, связанные с кондиционерами:")
    for page_num, found_keywords in relevant_pages:
        print(f"Страница {page_num}: найдены ключевые слова — {', '.join(found_keywords)}")
else:
    print("Совпадений не найдено.")