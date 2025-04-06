import React from 'react';
import MainLayout from './components/Layout/MainLayout';
import { ChatProvider } from './contexts/ChatContext';
import { SequenceProvider } from './contexts/SequenceContext';

const App: React.FC = () => {
  return (
    <ChatProvider>
      <SequenceProvider>
        <MainLayout />
      </SequenceProvider>
    </ChatProvider>
  );
};

export default App;
