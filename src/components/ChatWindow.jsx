import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import ChatInput from './ChatInput';
import '../App.css';

// Define a URL da API fora do componente para fácil configuração
const API_URL = 'http://localhost:8000/api/ask';

function ChatWindow({ chat, updateChatMessages }) {
  // Estado local para as mensagens do chat ativo
  const [messages, setMessages] = useState(chat.messages);

  // Efeito para atualizar o estado local se o chat ativo mudar (prop `chat`)
  useEffect(() => {
    setMessages(chat.messages);
  }, [chat]);

  // Efeito para atualizar o estado global em App.jsx sempre que as mensagens locais mudarem
  // e também salvar no localStorage (indiretamente via App.jsx)
  useEffect(() => {
    // Só atualiza se as mensagens locais forem diferentes das do prop inicial,
    // para evitar loop infinito na primeira renderização.
    if (messages !== chat.messages) {
        updateChatMessages(chat.id, messages);
    }
  }, [messages, chat.id, chat.messages, updateChatMessages]);

  const handleSendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessageId = `msg-user-${Date.now()}`;
    const newUserMessage = {
      id: userMessageId,
      sender: 'user',
      text: text,
    };

    // ID temporário para a mensagem de carregamento
    const loadingMessageId = `msg-loading-${Date.now()}`;
    const loadingMessage = {
      id: loadingMessageId,
      sender: 'lumia',
      text: '...', // Indicador de carregamento
    };

    // Adiciona a mensagem do usuário e a mensagem de carregamento
    setMessages(prevMessages => [...prevMessages, newUserMessage, loadingMessage]);

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: text }),
      });

      if (!response.ok) {
        // Se a resposta não for OK (ex: 4xx, 5xx), lança um erro
        throw new Error(`Erro na API: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();

      // Pequeno delay para melhor UX antes de mostrar a resposta
      setTimeout(() => {
        const lumiaResponse = {
          id: `msg-lumia-${Date.now()}`, // Novo ID para a resposta final
          sender: 'lumia',
          text: data.answer, // Usa a resposta da API
        };

        // Substitui a mensagem de carregamento pela resposta da LumIA
        setMessages(prevMessages =>
          prevMessages.map(msg =>
            msg.id === loadingMessageId ? lumiaResponse : msg
          )
        );
      }, 200); // Delay de 200ms

    } catch (error) {
      console.error("Erro ao buscar resposta da API:", error);

      const errorMessage = {
        id: `msg-error-${Date.now()}`, // Novo ID para a mensagem de erro
        sender: 'lumia',
        text: 'Desculpe, ocorreu um erro ao buscar a resposta. Tente novamente.', // Mensagem de erro amigável
      };

      // Substitui a mensagem de carregamento pela mensagem de erro
      setMessages(prevMessages =>
        prevMessages.map(msg => (msg.id === loadingMessageId ? errorMessage : msg))
      );
    }
  };

  return (
    <div className=\"chat-window\">
      <div className=\"chat-header\">
        <h2>{chat.title || 'Chat'}</h2>
        {/* Adicionar mais informações ou botões ao cabeçalho se necessário */}
      </div>
      <MessageList messages={messages} />
      <ChatInput onSendMessage={handleSendMessage} />
    </div>
  );
}

export default ChatWindow; 