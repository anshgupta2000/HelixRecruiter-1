import React, { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Textarea } from '../ui/textarea';
import SequenceStep from './SequenceStep';
import { useSequence } from '../../hooks/useSequence';

const SequenceEditor: React.FC = () => {
  const {
    currentSequence,
    isLoading,
    error,
    addStep,
    updateStep,
    deleteStep,
    updateSequence,
  } = useSequence();
  
  const [newStepContent, setNewStepContent] = useState('');
  const [isAddingStep, setIsAddingStep] = useState(false);
  const [isEditingTitle, setIsEditingTitle] = useState(false);
  const [title, setTitle] = useState(currentSequence?.title || '');

  const handleAddStep = () => {
    if (newStepContent.trim()) {
      addStep(newStepContent);
      setNewStepContent('');
      setIsAddingStep(false);
    }
  };

  const handleUpdateTitle = () => {
    if (title.trim() && currentSequence) {
      updateSequence({
        ...currentSequence,
        title,
      });
      setIsEditingTitle(false);
    }
  };

  if (!currentSequence) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-4 text-gray-500">
        <p>No sequence selected</p>
        <p className="text-sm mt-2">Start a chat conversation to create a sequence</p>
      </div>
    );
  }

  return (
    <div className="sequence-editor p-4">
      <div className="sequence-header mb-6">
        {isEditingTitle ? (
          <div className="flex items-center mb-4">
            <Input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="flex-grow"
            />
            <Button
              className="ml-2"
              onClick={handleUpdateTitle}
              disabled={!title.trim() || isLoading}
            >
              Save
            </Button>
            <Button
              variant="ghost"
              className="ml-2"
              onClick={() => {
                setTitle(currentSequence.title);
                setIsEditingTitle(false);
              }}
            >
              Cancel
            </Button>
          </div>
        ) : (
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">{currentSequence.title}</h2>
            <Button
              variant="outline"
              onClick={() => setIsEditingTitle(true)}
            >
              Edit Title
            </Button>
          </div>
        )}
      </div>

      <div className="sequence-steps">
        {currentSequence.steps.length > 0 ? (
          currentSequence.steps.map((step) => (
            <SequenceStep
              key={step.id || step.stepNumber}
              step={step}
              onUpdate={updateStep}
              onDelete={deleteStep}
            />
          ))
        ) : (
          <div className="text-center p-6 bg-gray-50 rounded-lg">
            <p className="text-gray-500">No steps in this sequence</p>
            <Button
              className="mt-2"
              onClick={() => setIsAddingStep(true)}
            >
              Add Step
            </Button>
          </div>
        )}
      </div>

      {isAddingStep ? (
        <div className="add-step-form mt-4 p-4 border rounded-lg">
          <h3 className="font-medium mb-2">Add New Step</h3>
          <Textarea
            value={newStepContent}
            onChange={(e) => setNewStepContent(e.target.value)}
            placeholder="Enter step content..."
            className="mb-2"
          />
          <div className="flex justify-end space-x-2">
            <Button
              variant="outline"
              onClick={() => {
                setNewStepContent('');
                setIsAddingStep(false);
              }}
            >
              Cancel
            </Button>
            <Button
              onClick={handleAddStep}
              disabled={!newStepContent.trim() || isLoading}
            >
              Add Step
            </Button>
          </div>
        </div>
      ) : (
        <div className="mt-4">
          <Button
            variant="outline"
            className="w-full"
            onClick={() => setIsAddingStep(true)}
          >
            + Add Step
          </Button>
        </div>
      )}

      {error && (
        <div className="error-message mt-4 p-2 bg-red-100 text-red-800 rounded">
          {error}
        </div>
      )}
    </div>
  );
};

export default SequenceEditor;
