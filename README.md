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

1. La fase di indicizzazione (Quando carichi il PDF)
Chunking: Il testo del PDF viene diviso in frammenti (chunk).

HuggingFace Embeddings (Modello Locale): Prende ogni singolo chunk di testo e lo trasforma in una lunga sequenza di numeri (un vettore, es. una lista di 384 numeri). Questo vettore rappresenta il significato semantico del testo.

ChromaDB (Database Vettoriale Locale): Salva questi vettori (insieme al testo originale) sul disco del container, creando il database vettoriale locale.

2. La fase di ricerca e risposta (Quando fai una domanda)
Quando scrivi una domanda nella chat, succede questo:

Vettorizzazione della domanda: La tua domanda testuale viene passata allo stesso modello di HuggingFace (all-MiniLM-L6-v2), che la converte in un vettore (numeri).

Cosine Similarity (Il vero motore di ricerca): ChromaDB prende il vettore della tua domanda e calcola la distanza del coseno (cosine similarity) confrontandolo con tutti i vettori dei chunk salvati nel database. Trova così i 3 chunk più vicini/simili alla tua domanda. (Nota: questo calcolo lo fa ChromaDB usando la matematica dei vettori, non l'LLM).

Groq LLM (Il modello generativo): A questo punto entra in gioco Groq. Al modello viene passato un prompt che contiene:

La domanda dell'utente.

I 3 chunk trovati da ChromaDB (il "Contesto").
Il compito dell'LLM (es. openai/gpt-oss-120b) non è fare la ricerca (quella è già fatta da ChromaDB), ma leggere il contesto e formulare una risposta in linguaggio naturale che risponda alla domanda basandosi solo su quei testi.

In sintesi:
HuggingFace (Embedding): Traduce parole in vettori numerici (sia i chunk che le domande).

ChromaDB: Fa il lavoro di geometria/matematica pura (cosine similarity) per trovare i chunk più pertinenti.

Groq (LLM): Legge i chunk trovati e scrive la risposta finale per l'utente.
