import { api } from './api';
import { Sequence, SequenceStep } from '../types/sequence';

export const sequenceService = {
  /**
   * Fetch all sequences
   */
  async getSequences(): Promise<Sequence[]> {
    const response = await api.get('/api/sequences');
    return response.data;
  },

  /**
   * Get a specific sequence by ID
   */
  async getSequence(id: number): Promise<Sequence> {
    const response = await api.get(`/api/sequences/${id}`);
    return response.data;
  },

  /**
   * Create a new sequence
   */
  async createSequence(title: string): Promise<Sequence> {
    const response = await api.post('/api/sequences', { title });
    return response.data;
  },

  /**
   * Update an existing sequence
   */
  async updateSequence(sequence: Sequence): Promise<Sequence> {
    const response = await api.put(`/api/sequences/${sequence.id}`, sequence);
    return response.data;
  },

  /**
   * Delete a sequence
   */
  async deleteSequence(id: number): Promise<void> {
    await api.delete(`/api/sequences/${id}`);
  },

  /**
   * Add a step to a sequence
   */
  async addStep(step: Omit<SequenceStep, 'id'>): Promise<SequenceStep> {
    const response = await api.post(`/api/sequences/${step.sequenceId}/steps`, step);
    return response.data;
  },

  /**
   * Update a step
   */
  async updateStep(step: SequenceStep): Promise<SequenceStep> {
    const response = await api.put(`/api/sequences/${step.sequenceId}/steps/${step.id}`, step);
    return response.data;
  },

  /**
   * Delete a step
   */
  async deleteStep(stepId: number): Promise<void> {
    await api.delete(`/api/steps/${stepId}`);
  },
};
