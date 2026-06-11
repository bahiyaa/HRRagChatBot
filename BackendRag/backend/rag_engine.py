import os
from getpass import getpass
from dotenv import load_dotenv

load_dotenv()

# Try env var first, otherwise prompt securely
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found")
os.environ['GROQ_API_KEY'] = GROQ_API_KEY
# Local PDF path (update to your actual file)
#PDF_PATH = r'C:\Users\jasim\Documents\BIA\bia_env\1RagChatBot\NovaTech_HR_Manual.pdf'

# RAG settings
#CHUNK_SIZE    = 1000
#CHUNK_OVERLAP = 100
#TOP_K         = 4
#EMBED_MODEL   = 'all-MiniLM-L6-v2'
#LLM_MODEL     = 'llama-3.1-8b-instant'


# Multiple PDF support
PDF_FOLDER = "./pdf"

# Persistent Vector DB
CHROMA_DIR = "./chroma_db"

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

TOP_K = 10
FINAL_K = 4

EMBED_MODEL = "BAAI/bge-small-en-v1.5"

LLM_MODEL = "llama-3.1-8b-instant"

# TTS settings
TTS_LANGUAGE = 'en'
TTS_SLOW     = False

print('✅ Configuration loaded.')

from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

documents = []

for pdf_file in Path(PDF_FOLDER).glob("*.pdf"):

    loader = PyPDFLoader(str(pdf_file))
    docs = loader.load()

    for doc in docs:
        doc.metadata["source_file"] = pdf_file.name

    documents.extend(docs)

print("Loaded pages:", len(documents))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP
)

chunks = splitter.split_documents(documents)

print("Total Chunks:", len(chunks))

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma

embedding_model = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL
)

if os.path.exists(CHROMA_DIR):

    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embedding_model
    )

    print("Loaded existing vector DB")

else:

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        persist_directory=CHROMA_DIR
    )

    print("Created new vector DB")

retriever = vectorstore.as_retriever(
    search_kwargs={"k": TOP_K}
)

from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser



llm = ChatGroq(
    model=LLM_MODEL
)

RAG_TEMPLATE = """
You are an enterprise knowledge assistant.

Use ONLY the provided context.

If answer not available in context say:

"I don't have that information."

Always mention the section name if available.

Context:
{context}

Question:
{question}

Answer:
"""

prompt = PromptTemplate(
    input_variables=["context","question"],
    template=RAG_TEMPLATE
)

# ── Helper ───────────────────────────────────────────────────────────────────
def format_docs(docs: list) -> str:
    """Merge retrieved document chunks into a single context string."""
    return '\n\n'.join(doc.page_content for doc in docs)

# ── Chain (LCEL) ──────────────────────────────────────────────────────────────
# Data flow:
#   question
#     ├─► retriever         (semantic search → top-k chunks)
#     │      └─► format_docs  (join chunks into context string)
#     └─► RunnablePassthrough (pass question unchanged)
#   → rag_prompt            (fill template with context + question)
#   → llm                   (generate answer)
#   → StrOutputParser       (extract plain text from LLM response)
rag_chain = (
    {'context': retriever | format_docs, 'question': RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

print('✅ RAG chain ready.')

import io
from gtts import gTTS
from IPython.display import Audio, display

def text_to_speech(text: str, lang: str = TTS_LANGUAGE, slow: bool = TTS_SLOW):
    """
    Convert text to speech and return an auto-playing IPython Audio widget.

    Uses Google TTS (gTTS) — natural voice quality, no API key needed.
    Audio is streamed into memory (no temp files written to disk).

    Args:
        text : Text to speak.
        lang : BCP-47 language code (e.g. 'en', 'hi', 'fr').
        slow : If True, speech is slower and more deliberate.

    Returns:
        IPython.display.Audio, or None on failure.
    """
    if not text or not text.strip():
        print('⚠️  TTS skipped — empty response.')
        return None

    try:
        tts = gTTS(text=text, lang=lang, slow=slow)

        # Write MP3 bytes directly into an in-memory buffer (no temp file needed)
        buffer = io.BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)

        return Audio(buffer.read(), autoplay=True)

    except Exception as e:
        print(f'❌ TTS error: {e}')
        return None

print('✅ TTS module ready (Google TTS — natural voice).')

chat_history = []

def build_history():

    history_text = ""

    for q,a in chat_history[-5:]:

        history_text += f"""
User: {q}
Assistant: {a}
"""

    return history_text
def ask(question):

    retrieved_docs = retriever.invoke(question)

    context = "\n\n".join(
        doc.page_content
        for doc in retrieved_docs
    )

    history = build_history()

    final_prompt = f"""
Previous Conversation:

{history}

Context:

{context}

Question:

{question}
"""

    answer = llm.invoke(final_prompt).content
    #generate_voice(answer)   

    chat_history.append(
        (question, answer)
    )

    sources = []

    for doc in retrieved_docs:

        sources.append({
            "file": doc.metadata.get("source_file", "Unknown"),
            "page": doc.metadata.get("page", "N/A")
        })

    return {
        "answer": answer,
        "sources": sources
    }

from gtts import gTTS
from IPython.display import Audio, display

def generate_voice(text):

    tts = gTTS(
        text=text,
        lang='en'
    )

    tts.save("answer.mp3")

    display(Audio("answer.mp3"))