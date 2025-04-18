import React from 'react';
import { Message } from '../types/Chat';
import styles from '../styles/App.module.css';

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  const { sender, text } = message;

  // Determina a classe CSS com base no sender
  let rowClass = styles.messageRow;
  switch (sender) {
    case 'user':
      rowClass += ` ${styles.userMessage}`;
      break;
    case 'lumia':
      rowClass += ` ${styles.lumiaMessage}`;
      break;
    case 'loading':
      rowClass += ` ${styles.loadingMessage}`;
      break;
    case 'error':
      rowClass += ` ${styles.errorMessage}`;
      break;
    default:
      break;
  }

  return (
    <div className={rowClass}>
      <div className={styles.messageBubble}>
        {/* Renderiza quebras de linha preservadas no texto */}
        {text.split('\n').map((line, index) => (
          <p key={index}>{line || '\u00A0'} {/* Garante que linhas vazias ocupem espaço */}</p>
        ))}
      </div>
    </div>
  );
};

export default MessageBubble; 