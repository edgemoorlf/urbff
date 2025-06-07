import React, { useState, useEffect, useRef } from 'react';
import { ChatMessage } from './components/ChatMessage';
import { ChatInput } from './components/ChatInput';
import { Message } from './types/chat';
import { ollamaApi } from './services/ollamaApi';
import './App.css';

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const generateId = () => {
    return Date.now().toString() + Math.random().toString(36).substr(2, 9);
  };

  const handleSendMessage = async (content: string) => {
    const userMessage: Message = {
      id: generateId(),
      content,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    try {
      const response = await ollamaApi.sendMessage([...messages, userMessage]);
      
      const assistantMessage: Message = {
        id: generateId(),
        content: response,
        sender: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '发生未知错误';
      setError(errorMessage);
      
      const errorResponse: Message = {
        id: generateId(),
        content: `抱歉，出了点小问题 😅 ${errorMessage}`,
        sender: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorResponse]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="chat-header">
        <h1>🎓 深圳大学生闺蜜聊天室</h1>
        <p>和你的AI闺蜜小雯聊天吧！她是深大心理学系的22岁学生 ✨</p>
      </div>
      
      <div className="chat-container">
        <div className="messages-container">
          {messages.length === 0 && (
            <div className="welcome-message">
              <div className="welcome-content">
                <span className="welcome-emoji">👋</span>
                <h3>嗨！我是小雯～</h3>
                <p>深大心理学系大三学生，超爱民谣和K-pop！周末经常去万象城逛街 🛍️</p>
                <p>想聊什么都可以哦～比如学习、追星、深圳的好吃好玩的地方！</p>
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          
          {isLoading && (
            <div className="typing-indicator">
              <div className="typing-content">
                <span>小雯正在输入</span>
                <div className="typing-dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>
        
        <ChatInput onSendMessage={handleSendMessage} disabled={isLoading} />
      </div>
      
      {error && (
        <div className="error-toast">
          {error}
        </div>
      )}
    </div>
  );
}

export default App; 