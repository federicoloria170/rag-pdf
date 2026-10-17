# 🤖 Naive RAG FAQ Bot

Un'applicazione full-stack per interrogare documenti PDF tramite una pipeline **Naive RAG** (Retrieval-Augmented Generation). Sfrutta l'infrastruttura ad alta velocità di **Groq** per la generazione e **HuggingFace** per gli embedding locali.

---

## 🏗️ Architettura del Sistema

```text
[ React + Vite + Nginx ] --(Port 3000)--> [ User Browser ]
           |
           +--(Port 8000)--> [ FastAPI Backend ]
                                  |
                                  +--> [ HuggingFace Embeddings ] -> [ ChromaDB ]
                                  +--> [ Groq LLM Inference ]
```
🛠️ Tech Stack

Backend: Python 3.10, FastAPI, LangChain, ChromaDB, PyPDF

Frontend: React 18, Vite, CSS3, Nginx

Inference & Embeddings: Groq API (openai/gpt-oss-120b), HuggingFace (all-MiniLM-L6-v2)

Orchestration: Docker, Docker Compose

## COME FUNZIONA IL PROGETTO
```

[ Domanda Utente ]
       │
       ▼
 🔤  Vettorizzazione Query (HuggingFace Embeddings)
       │  └─ Conversione della domanda in un vettore 384d
       ▼
 📐  Cosine Similarity Search (ChromaDB)
       │  └─ Confronto vettoriale e selezione dei Top-K chunk (k=3)
       ▼
 📝  Costruzione Prompt (Domanda + Contesto dei 3 Chunk)
       │
       ▼
 🧠  Inference LLM (Groq API)
       │  └─ Elaborazione del testo e generazione della risposta finale
       ▼
[ Risposta al Frontend ]
```
<img width="1337" height="772" alt="Schermata del 2026-10-17 22-23-17" src="https://github.com/user-attachments/assets/94b2b277-69cd-4fe6-8cb1-cc53fbfc21f0" />

