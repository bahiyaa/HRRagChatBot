import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ---------------- ENV ----------------
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")

os.environ["GROQ_API_KEY"] = GROQ_API_KEY

# ---------------- CONFIG ----------------
PDF_FOLDER = "./pdf"
CHROMA_DIR = "./chroma_db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100
TOP_K = 10

EMBED_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "llama-3.1-8b-instant"

chat_history = []

# ---------------- LAZY GLOBALS ----------------
vectorstore = None
retriever = None
llm = None


# ---------------- LOAD PDF + VECTOR DB ----------------
def load_vectorstore():
    global vectorstore, retriever

    if vectorstore is not None:
        return

    print("🔄 Loading vector database...")

    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_chroma import Chroma

    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL
    )

    if not os.path.exists(CHROMA_DIR):
        raise Exception(f"Chroma DB not found: {CHROMA_DIR}")

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model
    )

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": TOP_K}
    )

    print("✅ Vector database loaded")

# ---------------- LOAD LLM ----------------
def load_llm():
    global llm

    if llm is not None:
        return

    from langchain_groq import ChatGroq

    llm = ChatGroq(
        model=LLM_MODEL,
        api_key=GROQ_API_KEY
    )


# ---------------- CHAT HISTORY ----------------
def build_history():
    history_text = ""

    for q, a in chat_history[-5:]:
        history_text += f"\nUser: {q}\nAssistant: {a}\n"

    return history_text


# ---------------- MAIN ASK FUNCTION ----------------
def ask(question: str):

    load_vectorstore()
    load_llm()

    retrieved_docs = retriever.invoke(question)

    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    history = build_history()

    final_prompt = f"""
You are an enterprise knowledge assistant.

Use ONLY the provided context.

If answer not available in context say:
"I don't have that information."

Previous Conversation:
{history}

Context:
{context}

Question:
{question}

Answer:
"""

    answer = llm.invoke(final_prompt).content

    chat_history.append((question, answer))

    sources = [
        {
            "file": doc.metadata.get("source_file", "Unknown"),
            "page": doc.metadata.get("page", "N/A")
        }
        for doc in retrieved_docs
    ]

    return {
        "answer": answer,
        "sources": sources
    }