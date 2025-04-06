export interface Message {
  id?: number;
  userId?: number;
  content: string;
  role: 'user' | 'assistant' | 'system';
  timestamp: Date;
}

export interface ChatState {
  messages: Message[];
  isLoading: boolean;
  error: string | null;
}

export interface ChatContextType {
  chatState: ChatState;
  sendMessage: (content: string) => Promise<void>;
  clearChat: () => void;
}
