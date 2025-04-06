import React, { useEffect, useRef } from 'react';
import ChatBubble from './ChatBubble';
import ChatInput from './ChatInput';
import { useChat } from '../../hooks/useChat';

const ChatContainer: React.FC = () => {
  const { messages, isLoading, sendMessage } = useChat();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="chat-container flex flex-col h-full border-r">
      <div className="chat-header p-4 border-b">
        <h2 className="text-xl font-semibold">Chat</h2>
      </div>
      
      <div className="messages-container flex-grow overflow-y-auto p-4">
        {messages.length === 0 && (
          <div className="flex items-center justify-center h-full text-gray-500">
            <p>Start a conversation to create recruiting sequences</p>
          </div>
        )}
        
        {messages.map((message, index) => (
          <ChatBubble key={index} message={message} />
        ))}
        
        {isLoading && (
          <div className="typing-indicator p-3 bg-gray-200 text-gray-800 rounded-lg inline-block">
            <div className="dot-flashing"></div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
    </div>
  );
};

export default ChatContainer;
