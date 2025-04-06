import { Message } from '../types/chat';

/**
 * Format a timestamp for display
 */
export const formatTimestamp = (date: Date): string => {
  return new Date(date).toLocaleTimeString([], {
    hour: '2-digit',
    minute: '2-digit',
  });
};

/**
 * Check if a message is from the user
 */
export const isUserMessage = (message: Message): boolean => {
  return message.role === 'user';
};

/**
 * Get the CSS class for a message bubble based on the sender
 */
export const getMessageClass = (message: Message): string => {
  return isUserMessage(message) ? 'user-message' : 'assistant-message';
};

/**
 * Replace template variables in a string
 * Example: replacePlaceholders("Hello {{name}}", { name: "John" })
 */
export const replacePlaceholders = (text: string, variables: Record<string, string>): string => {
  return Object.entries(variables).reduce(
    (result, [key, value]) => result.replace(new RegExp(`{{${key}}}`, 'g'), value),
    text
  );
};
