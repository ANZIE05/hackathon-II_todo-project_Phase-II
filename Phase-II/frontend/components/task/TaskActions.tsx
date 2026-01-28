import React from 'react';
import Button from '@/components/ui/Button';

interface TaskActionsProps {
  onEdit: () => void;
  onDelete: () => void;
  onComplete: () => void;
  onCancel?: () => void;
  loading?: boolean;
  showCancel?: boolean;
  isCompleted?: boolean;
}

const TaskActions: React.FC<TaskActionsProps> = ({
  onEdit,
  onDelete,
  onComplete,
  onCancel,
  loading = false,
  showCancel = false,
  isCompleted = false
}) => {
  return (
    <div className="flex flex-wrap gap-2">
      {!isCompleted && (
        <Button
          variant="success"
          size="sm"
          onClick={onComplete}
          loading={loading}
        >
          Mark Complete
        </Button>
      )}
      {isCompleted && (
        <Button
          variant="secondary"
          size="sm"
          onClick={onComplete}
          loading={loading}
        >
          Mark Active
        </Button>
      )}
      <Button
        variant="secondary"
        size="sm"
        onClick={onEdit}
      >
        Edit
      </Button>
      <Button
        variant="danger"
        size="sm"
        onClick={onDelete}
      >
        Delete
      </Button>
      {showCancel && onCancel && (
        <Button
          variant="secondary"
          size="sm"
          onClick={onCancel}
        >
          Cancel
        </Button>
      )}
    </div>
  );
};

export default TaskActions;