import { api } from './api';
import { Message } from '../types/chat';

export const chatService = {
  /**
   * Fetch chat history
   */
  async getChatHistory(): Promise<Message[]> {
    const response = await api.get('/api/chat');
    return response.data;
  },

  /**
   * Send a message to the backend
   */
  async sendMessage(content: string): Promise<Message> {
    const response = await api.post('/api/chat', { content });
    return response.data;
  },

  /**
   * Clear chat history
   */
  async clearChat(): Promise<void> {
    await api.delete('/api/chat');
  },
};
