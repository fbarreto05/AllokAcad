import { useState, useRef, useEffect } from 'react';
import './App.css';

function App() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    { sender: 'bot', text: 'Olá! Sou a IA do AllokAcad. Como posso ajustar a sua grade?' }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const getAmbientId = () => {
    const pathParts = window.location.pathname.split('/').filter(Boolean);
    if (pathParts[0] === 'ambient' && pathParts.length >= 2) {
      const lastPart = pathParts[pathParts.length - 1];
      if (lastPart !== 'delete') {
        return lastPart;
      }
    }
    return null;
  };

  useEffect(() => {
    const ambientId = getAmbientId();
    if (!ambientId) return;

    let cancelled = false;
    fetch(`/ambient/chatbot/api/${ambientId}`)
      .then(response => response.ok ? response.json() : null)
      .then(data => {
        if (!cancelled && Array.isArray(data?.history) && data.history.length > 0) {
          setMessages(data.history);
        }
      })
      .catch(error => console.error(error));

    return () => {
      cancelled = true;
    };
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setInput('');
    setIsLoading(true);

    try {
      const ambientId = getAmbientId();
      if (!ambientId) {
        setMessages(prev => [...prev, { 
          sender: 'bot', 
          text: "Não foi possível identificar o ambiente atual. Certifique-se de que você está em uma página de ambiente." 
        }]);
        setIsLoading(false);
        return;
      }

      const response = await fetch(`/ambient/chatbot/api/${ambientId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userMessage })
      });

      if (!response.ok) {
        throw new Error('Erro na resposta do servidor');
      }

      const data = await response.json();
      if (Array.isArray(data.history) && data.history.length > 0) {
        setMessages(data.history);
      } else {
        setMessages(prev => [...prev, { 
          sender: 'bot', 
          text: data.response || "Comando processado com sucesso!" 
        }]);
      }

      if (data.should_reload || data.rules_changed) {
        setTimeout(() => {
          window.location.reload();
        }, 1500);
      }
    } catch (error) {
      console.error(error);
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: "Desculpe, ocorreu um erro ao se comunicar com o servidor." 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-wrapper">
      {!isOpen && (
        <button className="chat-trigger" onClick={() => setIsOpen(true)}>
          💬 IA Assistente
        </button>
      )}

      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <h4>AllokAcad Chat</h4>
            <button onClick={() => setIsOpen(false)}>X</button>
          </div>
          
          <div className="chat-body">
            {messages.map((msg, idx) => (
              <div key={idx} className={`message-bubble ${msg.sender}`}>
                {msg.text}
              </div>
            ))}
            {isLoading && <div className="message-bubble bot">Processando otimização...</div>}
            <div ref={messagesEndRef} />
          </div>

          <div className="chat-footer">
            <input 
              type="text" 
              value={input} 
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Digite o comando..."
              disabled={isLoading}
            />
            <button onClick={handleSend} disabled={isLoading}>Enviar</button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
