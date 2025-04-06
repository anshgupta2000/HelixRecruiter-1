import { useCallback } from 'react';
import { useChat as useContextChat } from '../contexts/ChatContext';

export const useChat = () => {
  const { chatState, sendMessage, clearChat } = useContextChat();

  const handleSendMessage = useCallback(
    async (content: string) => {
      if (!content.trim()) return;
      await sendMessage(content);
    },
    [sendMessage]
  );

  return {
    messages: chatState.messages,
    isLoading: chatState.isLoading,
    error: chatState.error,
    sendMessage: handleSendMessage,
    clearChat,
  };
};
