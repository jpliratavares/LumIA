import React from 'react';
import '../App.css';

function ChatList({ chats, activeChatId, onSelectChat }) {
  // Mostra os chats mais recentes primeiro
  const reversedChats = [...chats]; //.reverse(); // Remover reverse se preferir ordem de criação

  return (
    <div className=\"chat-list\">
      {reversedChats.length > 0 ? (
        reversedChats.map(chat => (
          <div
            key={chat.id}
            className={`chat-list-item ${chat.id === activeChatId ? 'active' : ''}`}
            onClick={() => onSelectChat(chat.id)}
            role="button"
            tabIndex={0} // Para acessibilidade
            onKeyPress={(e) => e.key === 'Enter' && onSelectChat(chat.id)} // Permite seleção com Enter
          >
            {/* Tenta pegar um título das mensagens, ou usa o padrão */}
            {chat.title || 'Chat'}
          </div>
        ))
      ) : (
        <div className=\"chat-list-empty\">Nenhum chat ainda.</div>
      )}
    </div>
  );
}

export default ChatList; 