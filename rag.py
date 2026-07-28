"""
rag.py

Retrieval-Augmented Generation (RAG)

Pipeline

Question
    ↓
Retrieve relevant chunks
    ↓
Build context
    ↓
Prompt OpenAI
    ↓
Generate answer
"""

from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# from hybrid_search import search
from text_search import search
# from vector_search import search


# ============================================================
# Configuration
# ============================================================

#MODEL_NAME = "gpt-4.1-mini"
MODEL_NAME = "gpt-5.4-mini"


TOP_K = 5


client = OpenAI()


# ============================================================
# Build Context
# ============================================================

def build_context(results):
    """
    Convert retrieved chunks into a prompt context.
    """

    context = ""

    for chunk in results:

        context += f"""
Title:
{chunk["title"]}

Section:
{chunk.get("header1", "")}
{chunk.get("header2", "")}
{chunk.get("header3", "")}

Content:
{chunk["text"]}

----------------------------------------
"""

    return context


# ============================================================
# Build Prompt
# ============================================================

def build_prompt(question, context):

    prompt = f"""
You are an expert assistant for the OpenAI documentation.

Answer the QUESTION using ONLY the CONTEXT below.

If the answer is not contained in the context, say you don't know.

CONTEXT

{context}

QUESTION

{question}
"""

    return prompt


# ============================================================
# Ask OpenAI
# ============================================================

def ask_llm(prompt):

    response = client.chat.completions.create(

        model=MODEL_NAME,

        messages=[
            {
                "role": "system",
                "content":
                    "You answer questions using the supplied documentation."
            },
            {
                "role": "user",
                "content": prompt,
            }
        ],

        temperature=0,
    )

    return response.choices[0].message.content


# ============================================================
# RAG
# ============================================================

def rag(question):

    retrieved_chunks = search(
        query=question,
        top_k=TOP_K,
    )

    context = build_context(retrieved_chunks)

    prompt = build_prompt(question, context)

    answer = ask_llm(prompt)

    return {
    "answer": answer,
    "sources": retrieved_chunks,
    "model": MODEL_NAME,
    "top_k": TOP_K,
}


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    print("=" * 70)
    print("OpenAI Docs RAG")
    print("=" * 70)

    while True:

        question = input("\nQuestion (or 'exit'): ")

        if question.lower() == "exit":
            break

        answer = rag(question)

        print("\nAnswer\n")
        print(answer)


# ============================================================
# Streamlit UI Wrapper
# ============================================================        

def ask_rag(question):
    """
    Wrapper used by the Streamlit application.

    The UI only interacts with this function, allowing the
    backend implementation to change without affecting the UI.
    """

    return rag(question)