
from langchain_text_splitters import RecursiveCharacterTextSplitter


def create_chunks(extract_pages, source_filename):

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )

    chunks = []

    for page_data in extract_pages:

        page_number = page_data["page"]

        page_text = page_data["text"]

        split_texts = text_splitter.split_text(page_text)

        for chunk_number, chunk_text in enumerate(split_texts):

            chunks.append({

                "text": chunk_text,

                "metadata": {
                    "source": source_filename,
                    "page": page_number,
                    "chunk_number": chunk_number + 1
                }

            })

    return chunks