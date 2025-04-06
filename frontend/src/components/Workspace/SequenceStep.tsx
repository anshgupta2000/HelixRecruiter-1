import React, { useState } from 'react';
import { Card, CardHeader, CardContent, CardFooter } from '../ui/card';
import { Button } from '../ui/button';
import { Textarea } from '../ui/textarea';
import { SequenceStep as SequenceStepType } from '../../types/sequence';

interface SequenceStepProps {
  step: SequenceStepType;
  onUpdate: (updatedStep: SequenceStepType) => void;
  onDelete: (stepId: number) => void;
}

const SequenceStep: React.FC<SequenceStepProps> = ({ step, onUpdate, onDelete }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [content, setContent] = useState(step.content);

  const handleSave = () => {
    if (content.trim()) {
      onUpdate({
        ...step,
        content,
      });
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setContent(step.content);
    setIsEditing(false);
  };

  const handleDelete = () => {
    if (step.id) {
      onDelete(step.id);
    }
  };

  return (
    <Card className="mb-4">
      <CardHeader className="py-3">
        <div className="flex justify-between items-center">
          <div className="font-medium">Step {step.stepNumber}</div>
          <div className="flex space-x-2">
            {!isEditing ? (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsEditing(true)}
                >
                  Edit
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleDelete}
                >
                  Delete
                </Button>
              </>
            ) : (
              <>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={handleCancel}
                >
                  Cancel
                </Button>
                <Button
                  variant="default"
                  size="sm"
                  onClick={handleSave}
                >
                  Save
                </Button>
              </>
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {isEditing ? (
          <Textarea
            value={content}
            onChange={(e) => setContent(e.target.value)}
            className="min-h-[100px]"
          />
        ) : (
          <div className="whitespace-pre-wrap">{step.content}</div>
        )}
      </CardContent>
    </Card>
  );
};

export default SequenceStep;
