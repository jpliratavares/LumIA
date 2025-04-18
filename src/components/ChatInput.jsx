import React, { useState } from 'react';
import '../App.css';

function ChatInput({ onSendMessage }) {
  const [inputValue, setInputValue] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault(); // Impede o refresh da página no submit do form
    if (inputValue.trim()) {
      onSendMessage(inputValue);
      setInputValue(''); // Limpa o campo após enviar
    }
  };

  const handleInputChange = (event) => {
    setInputValue(event.target.value);
  };

  const handleKeyDown = (event) => {
    // Envia com Enter, mas permite Shift+Enter para nova linha
    if (event.key === 'Enter' && !event.shiftKey) {
      handleSubmit(event);
    }
  };

  return (
    <form className=\"chat-input-form\" onSubmit={handleSubmit}>
      <textarea
        className=\"chat-input\"
        value={inputValue}
        onChange={handleInputChange}
        onKeyDown={handleKeyDown}
        placeholder=\"Digite sua mensagem aqui...\"
        rows={1} // Começa com uma linha, pode expandir
      />
      <button type=\"submit\" className=\"send-button\">
        Enviar
      </button>
    </form>
  );
}

export default ChatInput; 