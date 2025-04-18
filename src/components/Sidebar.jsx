import React from 'react';
import ChatList from './ChatList';
import '../App.css'; // Importa o CSS principal

function Sidebar({ chats, activeChatId, onSelectChat, onNewChat }) {
  return (
    <div className=\"sidebar\">
      <div className=\"sidebar-header\">
        {/* Placeholder para a logo - substitua por <img /> se tiver a imagem */}
        <div className=\"logo-placeholder\">UFPB Logo</div>
        <button className=\"new-chat-button\" onClick={onNewChat}>
          + Novo Chat
        </button>
      </div>
      <ChatList
        chats={chats}
        activeChatId={activeChatId}
        onSelectChat={onSelectChat}
      />
      {/* Você pode adicionar um rodapé à sidebar aqui se desejar */}
    </div>
  );
}

export default Sidebar; 