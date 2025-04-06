export interface SequenceStep {
  id?: number;
  sequenceId?: number;
  stepNumber: number;
  content: string;
  type: 'email' | 'message' | 'call' | 'other';
}

export interface Sequence {
  id?: number;
  userId?: number;
  title: string;
  createdAt: Date;
  steps: SequenceStep[];
}

export interface SequenceState {
  currentSequence: Sequence | null;
  sequences: Sequence[];
  isLoading: boolean;
  error: string | null;
}

export interface SequenceContextType {
  sequenceState: SequenceState;
  createSequence: (title: string) => Promise<void>;
  updateSequence: (sequence: Sequence) => Promise<void>;
  deleteSequence: (id: number) => Promise<void>;
  addStep: (step: Omit<SequenceStep, 'id' | 'sequenceId'>) => Promise<void>;
  updateStep: (step: SequenceStep) => Promise<void>;
  deleteStep: (stepId: number) => Promise<void>;
  setCurrentSequence: (sequence: Sequence | null) => void;
  clearWorkspace: () => void;
}
