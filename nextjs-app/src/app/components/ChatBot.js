"use client";
import React, { useState, useEffect } from 'react';

export default function ChatBot({ jsonData }) {
  const [question, setQuestion] = useState('');
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);

  // Log the jsonData when it updates
  useEffect(() => {
    if (jsonData) {
      console.log("Received JSON data: ", jsonData);
    }
  }, [jsonData]);

  const handleQuestionSubmit = async (e) => {
    e.preventDefault();
    if (!question || !jsonData) return;

    const userMessage = { sender: 'user', text: question };
    setMessages([...messages, userMessage]);
    setQuestion('');
    setLoading(true);

    const ngrokUrl = `${process.env.NEXT_PUBLIC_NGROK_URL}/qa/`;

    const response = await fetch(ngrokUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question,
        context: JSON.stringify(jsonData)
      }),
    });

    if (!response.ok) {
      console.error("Error calling FastAPI");
      setLoading(false);
      return;
    }

    const data = await response.json();
    const botMessage = { sender: 'bot', text: data.answer };
    setMessages([...messages, userMessage, botMessage]);
    setLoading(false);
  };

  return (
    <div className="chat-container">
      <div className="chat-box">
        {messages.map((message, index) => (
          <div key={index} className={`chat-message ${message.sender}`}>
            {message.text}
          </div>
        ))}
        {loading && <div className="chat-message bot">Analyzing...</div>}
      </div>

      <form onSubmit={handleQuestionSubmit} className="chat-input-box">
        <input
          type="text"
          placeholder="Ask me anything..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          className="chat-input"
        />
        <button type="submit" className="chat-submit-button">
          Send
        </button>
      </form>
    </div>
  );
}
