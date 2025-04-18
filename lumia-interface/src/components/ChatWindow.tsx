import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Chat, Message, ApiResponse } from '../types/Chat';
import MessageBubble from './MessageBubble';
import styles from '../styles/App.module.css';

const API_URL = 'http://localhost:8000/api/ask';

interface ChatWindowProps {
  chat: Chat;
  updateChatMessages: (chatId: string, messages: Message[]) => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ chat, updateChatMessages }) => {
  const [messages, setMessages] = useState<Message[]>(chat.messages);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scrolla para baixo quando novas mensagens chegam
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Atualiza mensagens locais se o chat prop mudar
  useEffect(() => {
    setMessages(chat.messages);
  }, [chat]);

  // Função para enviar mensagem e chamar API
  const handleSendMessage = useCallback(async () => {
    const text = inputValue.trim();
    if (!text || isLoading) return;

    const userTimestamp = Date.now();
    const newUserMessage: Message = {
      id: `user-${userTimestamp}`,
      sender: 'user',
      text: text,
      timestamp: userTimestamp,
    };

    const loadingTimestamp = Date.now() + 1; // Garante ID diferente
    const loadingMessage: Message = {
      id: `loading-${loadingTimestamp}`,
      sender: 'loading',
      text: '...',
      timestamp: loadingTimestamp,
    };

    // Adiciona msg do usuário e loading localmente
    const updatedMessages = [...messages, newUserMessage, loadingMessage];
    setMessages(updatedMessages);
    setInputValue(''); // Limpa input
    setIsLoading(true);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        const errorBody = await response.text(); // Tenta ler corpo do erro
        throw new Error(`API Error: ${response.status} ${response.statusText} - ${errorBody}`);
      }

      const data: ApiResponse = await response.json();

      const lumiaTimestamp = Date.now();
      const lumiaResponse: Message = {
        id: `lumia-${lumiaTimestamp}`,
        sender: 'lumia',
        text: data.answer || 'Recebi sua mensagem, mas não houve resposta.', // Fallback
        timestamp: lumiaTimestamp,
      };

      // Atualiza o estado substituindo loading pela resposta
      setMessages(prev => prev.map(msg => msg.id === loadingMessage.id ? lumiaResponse : msg));

    } catch (error) {
      console.error("Erro ao contatar a API:", error);
      const errorTimestamp = Date.now();
      const errorMessage: Message = {
        id: `error-${errorTimestamp}`,
        sender: 'error',
        text: 'Erro ao conectar com a LumIA. Verifique o console ou tente novamente.',
        timestamp: errorTimestamp,
      };
      // Atualiza o estado substituindo loading pelo erro
      setMessages(prev => prev.map(msg => msg.id === loadingMessage.id ? errorMessage : msg));
    } finally {
      setIsLoading(false);
      // Atualiza o estado global no App.tsx após a resposta/erro
      // É importante chamar updateChatMessages aqui para persistir o estado final
      setMessages(currentMessages => {
          updateChatMessages(chat.id, currentMessages);
          return currentMessages; // Retorna o estado atual para setMessages
      })
    }
  }, [inputValue, isLoading, messages, chat.id, updateChatMessages]);

  const handleFormSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    handleSendMessage();
  };

  const handleKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault(); // Previne nova linha no textarea
      handleSendMessage();
    }
  };

  return (
    <div className={styles.chatWindow}>
      <div className={styles.chatHeader}>
        <h2>{chat.title}</h2>
      </div>
      <div className={styles.messageList}>
        {messages.map((msg) => (
          <MessageBubble key={msg.id} message={msg} />
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form className={styles.chatInputForm} onSubmit={handleFormSubmit}>
        <textarea
          className={styles.chatInput}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Digite sua mensagem aqui..."
          rows={1}
          disabled={isLoading}
        />
        <button
          type="submit"
          className={styles.sendButton}
          disabled={isLoading || !inputValue.trim()}
        >
          Enviar
        </button>
      </form>
    </div>
  );
};

export default ChatWindow; 