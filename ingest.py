"""
ingest.py

This script demonstrates the complete ingestion pipeline:

1. Load Markdown files
2. Parse YAML front matter
3. Normalize metadata
4. Chunk documents
5. Generate unique chunk IDs
6. Prepare text for embeddings
"""


from pathlib import Path
import hashlib
import frontmatter
from langchain_text_splitters import MarkdownHeaderTextSplitter



# ==========================================================
# STEP 1 — Load Markdown Files
# ==========================================================

DATA_DIR = Path("data")

def load_markdown_files():

    documents = []

    # Loop through every Markdown file
    for path in DATA_DIR.glob("*.md"):

        # STEP 2 happens here
        document = parse_document(path)

        documents.append(document)

    return documents


# ==========================================================
# STEP 2 — Parse YAML Front Matter
# ==========================================================

def parse_document(path):
    post = frontmatter.load(path)

    metadata = post.metadata

    return {
        "filename": path.name,
         # YAML metadata
        "title": metadata.get("title"),
        "category": metadata.get("category"),
        "audience": metadata.get("audience"),
        "topics": metadata.get("topics", []),
        "related": metadata.get("related", []),
        "last_updated": metadata.get("last_updated"),

        # Markdown body only
        "content": post.content,
    }


# ==========================================================
# STEP 3 — Chunk Documents
# ==========================================================

HEADERS = [
    ("#", "h1"),
    ("##", "h2"),
    ("###", "h3"),
]


def chunk_documents(documents):
    """
    Split each document into smaller chunks while
    preserving metadata.
    """

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=HEADERS
    )

    chunks = []

    for document in documents:

        splits = splitter.split_text(document["content"])

        for i, split in enumerate(splits):

            chunk = {
                    "id": make_chunk_id(document["filename"], i),

                    "filename": document["filename"],
                    "title": document["title"],
                    "category": document["category"],
                    "audience": document["audience"],
                    "topics": document["topics"],
                    "related": document["related"],
                    "last_updated": document["last_updated"],

                    "header1": split.metadata.get("h1"),
                    "header2": split.metadata.get("h2"),
                    "header3": split.metadata.get("h3"),

                    "text": split.page_content,
                }

            chunks.append(chunk)

    return chunks


# ==========================================================
# STEP 4 — Generate Unique Chunk IDs
# ==========================================================

def make_chunk_id(filename, chunk_number):

    text = f"{filename}-{chunk_number}"

    return hashlib.md5(text.encode()).hexdigest()


# ==========================================================
# STEP 5 — Prepare Text for Embeddings
# ==========================================================

def prepare_texts(chunks):
    texts = []

    for chunk in chunks:
        embedding_text = f"""
Title: {chunk['title']}
Category: {chunk['category']}
Section: {chunk.get('header2') or chunk.get('header1')}

Content:
{chunk['text']}
""".strip()

        texts.append(embedding_text)

    return texts



# ==========================================================
# MAIN PIPELINE
# ==========================================================

def main():

    print("Loading Markdown files...")
    documents = load_markdown_files()
    print(f"Loaded {len(documents)} documents")

    print("Chunking documents...")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks")

    print("Preparing text for embeddings...")
    texts = prepare_texts(chunks)
    print(f"Prepared {len(texts)} chunks for embedding")




if __name__ == "__main__":
    main()