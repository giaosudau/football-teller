import React, { useState } from 'react';
import ChatMessage from './ChatMessage';
import './ChatApp.css';

const ChatApp = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');

  const sendUserMessage = async () => {
    if (inputMessage.trim() === '') return;

    // Add the user's message to the chat
    const userMessage = { message: inputMessage, sender: 'user' };
    setMessages([...messages, userMessage]);
    setInputMessage('');

    // Send the user's message to the Flask API
    try {
      const response = await fetch('http://localhost/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: inputMessage }),
      });

      const data = await response.json();

      // Add the AI response to the chat history after a delay
      setTimeout(() => {
        const aiResponse = { message: data.answer, sender: 'ai' };
        setMessages([...messages, aiResponse]);
      }, 1000); // Adjust the delay as needed
    } catch (error) {
      console.error('Error sending user message:', error);
    }
  };

  return (
    <div className="chat-app">
      <div className="chat-area">
        {messages.map((msg, index) => (
          <ChatMessage key={index} message={msg.message} sender={msg.sender} />
        ))}
      </div>
      <div className="input-area">
        <input
          type="text"
          placeholder="Type a message..."
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
        />
        <button onClick={sendUserMessage}>Send</button>
      </div>
    </div>
  );
};
