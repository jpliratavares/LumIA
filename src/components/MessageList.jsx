import React, { useEffect, useRef } from 'react';
import Message from './Message';
import '../App.css';

function MessageList({ messages }) {
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(() => {
    scrollToBottom();
  }, [messages]); // Rola sempre que as mensagens mudarem

  return (
    <div className=\"message-list\">
      {messages.map((msg) => (
        <Message key={msg.id} message={msg} />
      ))}
      {/* Elemento vazio no final para ajudar no scroll automático */}
      <div ref={messagesEndRef} />
    </div>
  );
}

export default MessageList; 