import React from 'react';

const ChatMessage = ({ message, sender }) => {
  return (
    <div className={`chat-message ${sender === 'user' ? 'user' : 'ai'}`}>
      <div className="message-content">{message.response}</div>
    </div>
  );
};

export default ChatMessage;