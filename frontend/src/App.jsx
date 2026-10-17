import React, { useState } from 'react';
import './App.css';

// Punto di connessione all'API FastAPI
const API_BASE_URL = 'http://localhost:8000';

export default function App() {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState('');
  const [isFileLoaded, setIsFileLoaded] = useState(false);

  const [question, setQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [isAsking, setIsAsking] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);
    setUploadStatus('Caricamento ed indicizzazione in corso...');

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${API_BASE_URL}/upload`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        setUploadStatus(`Documento "${file.name}" pronto per le domande!`);
        setIsFileLoaded(true);
      } else {
        setUploadStatus(`Errore: ${data.detail || 'Impossibile caricare il file'}`);
      }
    } catch (error) {
      setUploadStatus('Errore di connessione con il server.');
    } finally {
      setIsUploading(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!question.trim() || !isFileLoaded || isAsking) return;

    const userQuestion = question.trim();
    setQuestion('');

    setChatHistory((prev) => [...prev, { sender: 'user', text: userQuestion }]);
    setIsAsking(true);

    try {
      const response = await fetch(`${API_BASE_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: userQuestion }),
      });

      const data = await response.json();

      if (response.ok) {
        setChatHistory((prev) => [
          ...prev,
          {
            sender: 'bot',
            text: data.answer,
            sources: data.sources,
          },
        ]);
      } else {
        setChatHistory((prev) => [
          ...prev,
          { sender: 'bot', text: `Errore: ${data.detail}` },
        ]);
      }
    } catch (error) {
      setChatHistory((prev) => [
        ...prev,
        { sender: 'bot', text: 'Impossibile ricevere risposta dal server.' },
      ]);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <div className="app-container">
      <header className="header">
        <h1>Naive RAG FAQ Bot</h1>
        <p>Carica un manuale PDF e fai domande sul suo contenuto</p>
      </header>

      {/* Caricamento File */}
      <section className="upload-section">
        <div className="upload-box">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileChange}
            disabled={isUploading}
          />
          <button onClick={handleUpload} disabled={!file || isUploading}>
            {isUploading ? 'Elaborazione...' : 'Carica PDF'}
          </button>
        </div>
        {uploadStatus && <p className="status-message">{uploadStatus}</p>}
      </section>

      {/* Interfaccia Chat */}
      <section className="chat-section">
        <div className="chat-history">
          {chatHistory.length === 0 ? (
            <p style={{ textAlign: 'center', color: '#94a3b8', marginTop: '40px' }}>
              {isFileLoaded
                ? 'Fai la tua prima domanda sul documento!'
                : 'Carica un file PDF per iniziare.'}
            </p>
          ) : (
            chatHistory.map((msg, index) => (
              <div key={index} className={`message ${msg.sender}`}>
                <p>{msg.text}</p>
                {msg.sources && msg.sources.length > 0 && (
                  <div className="sources">
                    Fonte: {msg.sources.join(', ')}
                  </div>
                )}
              </div>
            ))
          )}
          {isAsking && (
            <div className="message bot">
              <p>Ricerca informazioni nel documento...</p>
            </div>
          )}
        </div>

        <form className="chat-input" onSubmit={handleAsk}>
          <input
            type="text"
            placeholder={
              isFileLoaded
                ? 'Fai una domanda sul documento...'
                : 'Prima carica un PDF per abilitare la chat'
            }
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            disabled={!isFileLoaded || isAsking}
          />
          <button type="submit" disabled={!isFileLoaded || !question.trim() || isAsking}>
            Invia
          </button>
        </form>
      </section>
    </div>
  );
}
