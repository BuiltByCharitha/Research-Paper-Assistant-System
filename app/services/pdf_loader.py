import PyPDF2

def extract_text(pdf_path):
    text = ""
    with open(pdf_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + " "
    return text

def chunk_text(text, chunk_size=500):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunks.append(" ".join(words[i:i+chunk_size]))
    return chunks


if __name__ == "__main__":
    sample_pdf = "C:/Users/chari/OneDrive/Documents/Research-Paper-Assistant-System/app/services/paper1.pdf"  
    text = extract_text(sample_pdf)
    chunks = chunk_text(text)
    print(f"Total chunks: {len(chunks)}")
    print("First chunk preview:", chunks[0][:200])

