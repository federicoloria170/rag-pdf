import os
import shutil
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

app = FastAPI(title="Naive RAG FAQ Bot API")

# Permette le chiamate CORS da qualsiasi origine (richiesto per la comunicazione col frontend React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Variabili in-memory per memorizzare temporaneamente il Vector Store e il file corrente
vector_store = None
current_file_name = None


class QueryRequest(BaseModel):
    question: str


@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    global vector_store, current_file_name

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Il file deve essere un PDF.")

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # Salva il file PDF sul disco del container
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    try:
        # 1. Caricamento del PDF
        loader = PyPDFLoader(file_path)
        documents = loader.load()

        # 2. Chunking del testo (Naive RAG)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        splits = text_splitter.split_documents(documents)

        # 3. Embedding locale con HuggingFace (senza spazi errati!)
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

        vector_store = Chroma.from_documents(
            documents=splits,
            embedding=embeddings
        )

        current_file_name = file.filename

        return {
            "status": "success",
            "message": f"File '{file.filename}' caricato e indicizzato con successo!",
            "chunks_count": len(splits)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante l'elaborazione del PDF: {str(e)}")
@app.post("/ask")
async def ask_question(request: QueryRequest):
    global vector_store

    if vector_store is None:
        raise HTTPException(status_code=400, detail="Nessun documento caricato. Carica prima un PDF.")

    if not request.question.strip():
        raise HTTPException(status_code=400, detail="La domanda non può essere vuota.")

    try:
        # 1. Configurazione del Retriever (recupera i top 3 frammenti simili)
        retriever = vector_store.as_retriever(search_kwargs={"k": 3})

        # 2. Modello Generativo OpenAI
        # VECCHIO (OpenAI):
        # llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

        # NUOVO (Groq - usa llama-3.3-70b-versatile o llama3-8b-8192):
        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0
        )

        # 3. Prompt di Sistema per la risposta basata sul contesto
        system_prompt = (
            "Sei un assistente per le risposte alle domande basato sui documenti aziendali.\n"
            "Usa i seguenti frammenti di contesto recuperati per rispondere alla domanda.\n"
            "Se non conosci la risposta o l'informazione non è nel testo, dì che non è presente nel documento.\n"
            "Mantieni la risposta concisa, accurata e professionale.\n\n"
            "Contesto:\n{context}"
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}"),
        ])

        # 4. Creazione ed esecuzione della Chain RAG
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)

        response = rag_chain.invoke({"input": request.question})

        # Estrazione delle pagine usate come fonte
        sources = [
            f"Pagina {doc.metadata.get('page', 0) + 1}"
            for doc in response.get("context", [])
        ]

        return {
            "answer": response["answer"],
            "sources": list(set(sources))
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore durante la generazione della risposta: {str(e)}")


@app.get("/status")
async def get_status():
    return {
        "document_loaded": vector_store is not None,
        "current_file": current_file_name
    }
