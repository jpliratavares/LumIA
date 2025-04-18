import React from 'react';
import { Chat } from '../types/Chat';
import styles from '../styles/App.module.css';

interface SidebarProps {
  chats: Chat[];
  activeChatId: string | null;
  onSelectChat: (chatId: string) => void;
  onNewChat: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ chats, activeChatId, onSelectChat, onNewChat }) => {
  return (
    <div className={styles.sidebar}>
      <div className={styles.sidebarHeader}>
        {/* Idealmente, substituir por <img src="/path/to/logo.png" alt="LumIA Logo" /> */}
        <div className={styles.logoPlaceholder}>LumIA</div>
        <button className={styles.newChatButton} onClick={onNewChat}>
          + Novo Chat
        </button>
      </div>
      <div className={styles.chatList}>
        {chats.length > 0 ? (
          chats.map(chat => (
            <div
              key={chat.id}
              className={`${styles.chatListItem} ${chat.id === activeChatId ? styles.chatListItemActive : ''}`}
              onClick={() => onSelectChat(chat.id)}
              role="button"
              tabIndex={0}
              onKeyPress={(e) => e.key === 'Enter' && onSelectChat(chat.id)}
            >
              {chat.title || 'Chat sem título'} {/* Fallback para título */}
            </div>
          ))
        ) : (
          <div className={styles.chatListEmpty}>Nenhum chat ainda.</div>
        )}
      </div>
    </div>
  );
};

export default Sidebar; 