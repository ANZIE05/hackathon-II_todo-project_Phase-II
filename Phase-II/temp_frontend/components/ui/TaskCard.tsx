import React from 'react';
import { Task } from '@/lib/types';
import Button from './Button';

interface TaskCardProps {
  task: Task;
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onCompleteToggle: (task: Task) => void;
}

const TaskCard: React.FC<TaskCardProps> = ({ task, onEdit, onDelete, onCompleteToggle }) => {
  const formatDate = (dateString: string) => {
    const options: Intl.DateTimeFormatOptions = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className={`border rounded-lg p-4 mb-3 shadow-sm ${
      task.status === 'completed' ? 'bg-gray-50 opacity-75' : 'bg-white'
    }`}>
      <div className="flex flex-col md:flex-row md:justify-between md:items-start gap-3">
        <div className="flex-1 min-w-0">
          <div className="flex items-center mb-1">
            <input
              type="checkbox"
              checked={task.status === 'completed'}
              onChange={() => onCompleteToggle(task)}
              className="h-4 w-4 text-blue-600 rounded focus:ring-blue-500 flex-shrink-0"
            />
            <h3 className={`ml-2 text-lg font-medium truncate ${
              task.status === 'completed' ? 'line-through text-gray-500' : 'text-gray-900'
            }`}>
              {task.title}
            </h3>
          </div>

          {task.description && (
            <p className="text-gray-600 text-sm md:ml-6 mt-1 md:mt-0 truncate">
              {task.description}
            </p>
          )}

          <div className="flex flex-wrap gap-2 mt-2 md:ml-6">
            <span className={`text-xs px-2 py-1 rounded-full ${getPriorityColor(task.priority)}`}>
              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
            </span>

            {task.dueDate && (
              <span className="text-xs px-2 py-1 rounded-full bg-blue-100 text-blue-800">
                Due: {formatDate(task.dueDate)}
              </span>
            )}

            {task.status === 'completed' && (
              <span className="text-xs px-2 py-1 rounded-full bg-green-100 text-green-800">
                Completed
              </span>
            )}
          </div>
        </div>

        <div className="flex space-x-2 md:ml-4 flex-shrink-0">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onEdit(task)}
          >
            Edit
          </Button>
          <Button
            variant="danger"
            size="sm"
            onClick={() => onDelete(task.id)}
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
};

export default TaskCard;