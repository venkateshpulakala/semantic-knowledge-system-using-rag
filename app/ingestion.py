import pymupdf

def extract_text(pdf_path):
    doc = pymupdf.open(pdf_path)

    extracted_pages = []

    for page_number in range(doc.page_count):
        page = doc.load_page(page_number)
        text = page.get_text("text")

        if text.strip():
            extracted_pages.append({
                "page": page_number + 1,
                "text": text.strip()
            })

    doc.close()

    return extracted_pages