import React from 'react';
import Header from './Header';
import ChatContainer from '../Chat/ChatContainer';
import WorkspaceContainer from '../Workspace/WorkspaceContainer';

const MainLayout: React.FC = () => {
  return (
    <div className="main-layout flex flex-col h-screen">
      <Header />
      
      <div className="layout-content flex flex-grow">
        <div className="w-1/2 max-w-[500px] min-w-[300px]">
          <ChatContainer />
        </div>
        <div className="flex-grow">
          <WorkspaceContainer />
        </div>
      </div>
    </div>
  );
};

export default MainLayout;
