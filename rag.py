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
# from text_search import search
from vector_search import search


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

PROMPTS = {
    "baseline": """
You are an expert assistant for the OpenAI documentation.

Answer the QUESTION using ONLY the CONTEXT below.

If the answer is not contained in the context, say you don't know.

CONTEXT

{context}

QUESTION

{question}
""",

    "strict_grounding": """
You are an expert assistant for the OpenAI documentation.

Answer the QUESTION using ONLY the information explicitly stated
in the CONTEXT.

Do not use outside knowledge or make assumptions.

If the answer is not contained in the CONTEXT, say:
"I don't know based on the provided documentation."

Give a concise and direct answer.

CONTEXT

{context}

QUESTION

{question}
"""
}

def build_prompt(question, context, prompt_name="strict_grounding"):

    prompt_template = PROMPTS[prompt_name]

    return prompt_template.format(
        context=context,
        question=question,
    )


# ============================================================
# Ask OpenAI
# ============================================================

INPUT_COST_PER_MILLION = 0.75
OUTPUT_COST_PER_MILLION = 4.50


def ask_llm(prompt):

    response = client.responses.create(
        model=MODEL_NAME,
        input=prompt,
        temperature=0,
    )

    usage = response.usage

    input_tokens = usage.input_tokens
    output_tokens = usage.output_tokens
    total_tokens = usage.total_tokens

    cost_usd = (
        (input_tokens / 1_000_000) * INPUT_COST_PER_MILLION +
        (output_tokens / 1_000_000) * OUTPUT_COST_PER_MILLION
    )

    return {
        "answer": response.output_text,
        "usage": {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
        },
        "cost_usd": round(cost_usd, 6),
    }


# ============================================================
# RAG
# ============================================================

def rag(question, prompt_name="strict_grounding"):

    retrieved_chunks = search(
        query=question,
        top_k=TOP_K,
    )

    context = build_context(retrieved_chunks)

    prompt = build_prompt(
    question,
    context,
    prompt_name=prompt_name,
    )

    llm_result = ask_llm(prompt)


    return {
        "answer": llm_result["answer"],
        "sources": retrieved_chunks,
        "model": MODEL_NAME,
        "top_k": TOP_K,
        "usage": llm_result["usage"],
        "cost_usd": llm_result["cost_usd"],
        "prompt": prompt_name,
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