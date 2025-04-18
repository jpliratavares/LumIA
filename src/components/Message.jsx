import React from 'react';
import '../App.css';

function Message({ message }) {
  const { sender, text } = message;
  const messageClass = sender === 'user' ? 'user-message' : 'lumia-message';

  return (
    <div className={`message-row ${messageClass}`}>
      <div className=\"message-bubble\">
        <p>{text}</p>
      </div>
    </div>
  );
}

export default Message; 