import React, { createContext, useContext, useState, ReactNode, useCallback } from 'react';
import { SequenceState, Sequence, SequenceStep, SequenceContextType } from '../types/sequence';
import { sequenceService } from '../services/sequenceService';
import { useSocket } from '../hooks/useSocket';

const initialSequenceState: SequenceState = {
  currentSequence: null,
  sequences: [],
  isLoading: false,
  error: null,
};

const SequenceContext = createContext<SequenceContextType | undefined>(undefined);

export const SequenceProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [sequenceState, setSequenceState] = useState<SequenceState>(initialSequenceState);
  const socket = useSocket();

  // Listen for sequence updates from the socket
  React.useEffect(() => {
    if (!socket) return;

    socket.on('sequence_update', (sequence: Sequence) => {
      setSequenceState((prev) => {
        // Update the sequences list
        const updatedSequences = prev.sequences.map((s) =>
          s.id === sequence.id ? sequence : s
        );

        // If this is the current sequence, update it too
        const updatedCurrentSequence =
          prev.currentSequence && prev.currentSequence.id === sequence.id
            ? sequence
            : prev.currentSequence;

        return {
          ...prev,
          sequences: updatedSequences,
          currentSequence: updatedCurrentSequence,
          isLoading: false,
        };
      });
    });

    return () => {
      socket.off('sequence_update');
    };
  }, [socket]);

  const createSequence = useCallback(async (title: string) => {
    try {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      const newSequence = await sequenceService.createSequence(title);
      
      setSequenceState((prev) => ({
        ...prev,
        sequences: [...prev.sequences, newSequence],
        currentSequence: newSequence,
        isLoading: false,
      }));
    } catch (error) {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create sequence',
      }));
    }
  }, []);

  const updateSequence = useCallback(async (sequence: Sequence) => {
    try {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      const updatedSequence = await sequenceService.updateSequence(sequence);
      
      setSequenceState((prev) => {
        const updatedSequences = prev.sequences.map((s) =>
          s.id === updatedSequence.id ? updatedSequence : s
        );

        return {
          ...prev,
          sequences: updatedSequences,
          currentSequence: prev.currentSequence?.id === updatedSequence.id
            ? updatedSequence
            : prev.currentSequence,
          isLoading: false,
        };
      });
    } catch (error) {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to update sequence',
      }));
    }
  }, []);

  const deleteSequence = useCallback(async (id: number) => {
    try {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      await sequenceService.deleteSequence(id);
      
      setSequenceState((prev) => {
        const filteredSequences = prev.sequences.filter((s) => s.id !== id);
        return {
          ...prev,
          sequences: filteredSequences,
          currentSequence: prev.currentSequence?.id === id
            ? null
            : prev.currentSequence,
          isLoading: false,
        };
      });
    } catch (error) {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to delete sequence',
      }));
    }
  }, []);

  const addStep = useCallback(async (step: Omit<SequenceStep, 'id' | 'sequenceId'>) => {
    if (!sequenceState.currentSequence) {
      setSequenceState((prev) => ({
        ...prev,
        error: 'No sequence selected',
      }));
      return;
    }

    try {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      const newStep = await sequenceService.addStep({
        ...step,
        sequenceId: sequenceState.currentSequence.id!,
      });
      
      setSequenceState((prev) => {
        if (!prev.currentSequence) return prev;
        
        const updatedCurrentSequence = {
          ...prev.currentSequence,
          steps: [...prev.currentSequence.steps, newStep],
        };

        return {
          ...prev,
          currentSequence: updatedCurrentSequence,
          isLoading: false,
        };
      });
    } catch (error) {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to add step',
      }));
    }
  }, [sequenceState.currentSequence]);

  const updateStep = useCallback(async (step: SequenceStep) => {
    if (!sequenceState.currentSequence) {
      setSequenceState((prev) => ({
        ...prev,
        error: 'No sequence selected',
      }));
      return;
    }

    try {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      const updatedStep = await sequenceService.updateStep(step);
      
      setSequenceState((prev) => {
        if (!prev.currentSequence) return prev;
        
        const updatedSteps = prev.currentSequence.steps.map((s) =>
          s.id === updatedStep.id ? updatedStep : s
        );

        const updatedCurrentSequence = {
          ...prev.currentSequence,
          steps: updatedSteps,
        };

        return {
          ...prev,
          currentSequence: updatedCurrentSequence,
          isLoading: false,
        };
      });
    } catch (error) {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to update step',
      }));
    }
  }, [sequenceState.currentSequence]);

  const deleteStep = useCallback(async (stepId: number) => {
    if (!sequenceState.currentSequence) {
      setSequenceState((prev) => ({
        ...prev,
        error: 'No sequence selected',
      }));
      return;
    }

    try {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: true,
        error: null,
      }));

      await sequenceService.deleteStep(stepId);
      
      setSequenceState((prev) => {
        if (!prev.currentSequence) return prev;
        
        const filteredSteps = prev.currentSequence.steps.filter((s) => s.id !== stepId);

        const updatedCurrentSequence = {
          ...prev.currentSequence,
          steps: filteredSteps,
        };

        return {
          ...prev,
          currentSequence: updatedCurrentSequence,
          isLoading: false,
        };
      });
    } catch (error) {
      setSequenceState((prev) => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to delete step',
      }));
    }
  }, [sequenceState.currentSequence]);

  const setCurrentSequence = useCallback((sequence: Sequence | null) => {
    setSequenceState((prev) => ({
      ...prev,
      currentSequence: sequence,
    }));
  }, []);

  const clearWorkspace = useCallback(() => {
    setSequenceState((prev) => ({
      ...prev,
      currentSequence: null,
    }));
  }, []);

  return (
    <SequenceContext.Provider
      value={{
        sequenceState,
        createSequence,
        updateSequence,
        deleteSequence,
        addStep,
        updateStep,
        deleteStep,
        setCurrentSequence,
        clearWorkspace,
      }}
    >
      {children}
    </SequenceContext.Provider>
  );
};

export const useSequence = (): SequenceContextType => {
  const context = useContext(SequenceContext);
  if (context === undefined) {
    throw new Error('useSequence must be used within a SequenceProvider');
  }
  return context;
};
