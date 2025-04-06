import React from 'react';
import { useSequence } from '../../hooks/useSequence';
import SequenceEditor from './SequenceEditor';

const WorkspaceContainer: React.FC = () => {
  const { currentSequence, isLoading } = useSequence();

  return (
    <div className="workspace-container flex flex-col h-full">
      <div className="workspace-header p-4 border-b">
        <h2 className="text-xl font-semibold">Workspace</h2>
      </div>
      
      <div className="workspace-content flex-grow overflow-y-auto">
        {isLoading ? (
          <div className="flex items-center justify-center h-full">
            <div className="loading-spinner"></div>
          </div>
        ) : (
          <SequenceEditor />
        )}
      </div>
    </div>
  );
};

export default WorkspaceContainer;
