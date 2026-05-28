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

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setInput('');
    setIsLoading(true);

    // MOCK: Simula a resposta do back-end (Para você testar sem o Python estar pronto)
    setTimeout(() => {
      setMessages(prev => [...prev, { 
        sender: 'bot', 
        text: `Entendi. Vou pedir para o sistema processar a alteração: "${userMessage}".` 
      }]);
      setIsLoading(false);
    }, 1500);
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