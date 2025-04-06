import React from 'react';
import { Message } from '../../types/chat';
import { formatTimestamp, isUserMessage } from '../../utils/helpers';

interface ChatBubbleProps {
  message: Message;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ message }) => {
  const isUser = isUserMessage(message);
  
  return (
    <div className={`chat-bubble ${isUser ? 'user' : 'assistant'} mb-4`}>
      <div 
        className={`p-3 rounded-lg max-w-[80%] ${
          isUser 
            ? 'bg-blue-500 text-white ml-auto rounded-br-none' 
            : 'bg-gray-200 text-gray-800 mr-auto rounded-bl-none'
        }`}
      >
        <div className="message-content">{message.content}</div>
        <div 
          className={`text-xs mt-1 ${
            isUser ? 'text-blue-100' : 'text-gray-500'
          }`}
        >
          {formatTimestamp(message.timestamp)}
        </div>
      </div>
    </div>
  );
};

export default ChatBubble;
