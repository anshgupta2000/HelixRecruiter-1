import { useCallback } from 'react';
import { useSequence as useContextSequence } from '../contexts/SequenceContext';
import { Sequence, SequenceStep } from '../types/sequence';

export const useSequence = () => {
  const {
    sequenceState,
    createSequence,
    updateSequence,
    deleteSequence,
    addStep,
    updateStep,
    deleteStep,
    setCurrentSequence,
    clearWorkspace,
  } = useContextSequence();

  const handleCreateSequence = useCallback(
    async (title: string) => {
      if (!title.trim()) return;
      await createSequence(title);
    },
    [createSequence]
  );

  const handleAddStep = useCallback(
    async (content: string, type: SequenceStep['type'] = 'email') => {
      if (!content.trim()) return;

      const currentSteps = sequenceState.currentSequence?.steps || [];
      const stepNumber = currentSteps.length + 1;

      await addStep({
        content,
        type,
        stepNumber,
      });
    },
    [addStep, sequenceState.currentSequence]
  );

  return {
    currentSequence: sequenceState.currentSequence,
    sequences: sequenceState.sequences,
    isLoading: sequenceState.isLoading,
    error: sequenceState.error,
    createSequence: handleCreateSequence,
    updateSequence,
    deleteSequence,
    addStep: handleAddStep,
    updateStep,
    deleteStep,
    setCurrentSequence,
    clearWorkspace,
  };
};
