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

  const getCsrfToken = () => {
    const match = document.cookie.split(';')
      .map(c => c.trim())
      .find(c => c.startsWith('csrftoken='));
    return match ? match.split('=')[1] : '';
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = input;
    setMessages(prev => [...prev, { sender: 'user', text: userMessage }]);
    setInput('');
    setIsLoading(true);

    try {
      const res = await fetch('/chat/message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCsrfToken(),
        },
        body: JSON.stringify({ message: userMessage }),
      });

      const data = await res.json();
      const botText = res.ok
        ? data.response
        : 'Ocorreu um erro ao processar sua mensagem. Tente novamente.';

      setMessages(prev => [...prev, { sender: 'bot', text: botText }]);
    } catch {
      setMessages(prev => [...prev, {
        sender: 'bot',
        text: 'Não foi possível conectar ao servidor. Verifique sua conexão.',
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