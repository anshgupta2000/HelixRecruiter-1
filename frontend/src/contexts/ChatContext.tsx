import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { ChatState, Message, ChatContextType } from '../types/chat';
import { chatService } from '../services/chatService';
import { useSocket } from '../hooks/useSocket';

const initialChatState: ChatState = {
  messages: [],
  isLoading: false,
  error: null,
};

const ChatContext = createContext<ChatContextType | undefined>(undefined);

export const ChatProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [chatState, setChatState] = useState<ChatState>(initialChatState);
  const socket = useSocket();

  // Listen for incoming messages from the socket
  React.useEffect(() => {
    if (!socket) return;

    socket.on('message', (message: Message) => {
      setChatState((prev) => ({
        ...prev,
        messages: [...prev.messages, message],
        isLoading: false,
      }));
    });

    return () => {
      socket.off('message');
    };
  }, [socket]);

  const sendMessage = useCallback(async (content: string) => {
    try {
      setChatState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      // Add the user message to the UI right away
      const userMessage: Message = {
        content,
        role: 'user',
        timestamp: new Date(),
      };

      setChatState((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
      }));

      // Send the message to the backend
      await chatService.sendMessage(content);
      
      // The assistant's response will be handled by the socket
    } catch (error) {
      setChatState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to send message',
      }));
    }
  }, []);

  const clearChat = useCallback(() => {
    setChatState(initialChatState);
  }, []);

  return (
    <ChatContext.Provider
      value={{
        chatState,
        sendMessage,
        clearChat,
      }}
    >
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = (): ChatContextType => {
  const context = useContext(ChatContext);
  if (context === undefined) {
    throw new Error('useChat must be used within a ChatProvider');
  }
  return context;
};
