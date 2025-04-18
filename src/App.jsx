import React, { useState, useEffect, useCallback } from 'react';
import Sidebar from './components/Sidebar';
import ChatWindow from './components/ChatWindow';
import './App.css';

function App() {
  const [chats, setChats] = useState([]); // Formato: [{ id: string, title: string, messages: [] }]
  const [activeChatId, setActiveChatId] = useState(null);

  // Carregar chats do localStorage na inicialização
  useEffect(() => {
    try {
      const savedChats = JSON.parse(localStorage.getItem('lumiaChats') || '[]');
      setChats(savedChats);
      // Define o primeiro chat como ativo se houver chats salvos e nenhum ativo
      if (savedChats.length > 0 && !activeChatId) {
        setActiveChatId(savedChats[0].id);
      }
    } catch (error) {
      console.error("Erro ao carregar chats do localStorage:", error);
      setChats([]); // Reseta em caso de erro
    }
  }, []); // Executa apenas uma vez no mount

  // Salvar chats no localStorage sempre que 'chats' mudar
  useEffect(() => {
    try {
      localStorage.setItem('lumiaChats', JSON.stringify(chats));
    } catch (error) {
      console.error("Erro ao salvar chats no localStorage:", error);
    }
  }, [chats]);

  const handleSelectChat = (chatId) => {
    setActiveChatId(chatId);
  };

  const handleNewChat = () => {
    const newChatId = `chat-${Date.now()}`;
    const newChat = {
      id: newChatId,
      title: `Novo Chat ${chats.length + 1}`,
      messages: [], // Começa vazio ou com msg inicial
    };
    // Adiciona no início da lista para aparecer no topo
    setChats([newChat, ...chats]);
    setActiveChatId(newChatId);
  };

  // Função para atualizar as mensagens de um chat específico
  // Usamos useCallback para otimizar, evitando recriações desnecessárias
  const updateChatMessages = useCallback((chatId, newMessages) => {
    setChats(prevChats =>
      prevChats.map(chat =>
        chat.id === chatId ? { ...chat, messages: newMessages } : chat
      )
    );
  }, []); // A dependência vazia significa que a função não será recriada

  const getActiveChat = () => {
    return chats.find(chat => chat.id === activeChatId);
  };

  const activeChat = getActiveChat();

  return (
    <div className=\"app-container\">
      <Sidebar
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={handleSelectChat}
        onNewChat={handleNewChat}
      />
      {activeChat ? (
        <ChatWindow
          key={activeChat.id} // Importante para resetar estado interno do ChatWindow ao mudar de chat
          chat={activeChat}
          updateChatMessages={updateChatMessages}
        />
      ) : (
        <div className=\"chat-window no-chat-selected\">
          <h1>Bem-vindo(a) à LumIA!</h1>
          <p>Selecione um chat na barra lateral ou clique em "Novo Chat" para começar.</p>
        </div>
      )}
    </div>
  );
}

export default App; 