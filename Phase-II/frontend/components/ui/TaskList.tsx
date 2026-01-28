import React from 'react';
import { Task } from '@/lib/types';
import TaskCard from './TaskCard';

interface TaskListProps {
  tasks: Task[];
  onEdit: (task: Task) => void;
  onDelete: (id: string) => void;
  onCompleteToggle: (task: Task) => void;
  loading?: boolean;
  emptyMessage?: string;
}

const TaskList: React.FC<TaskListProps> = ({
  tasks,
  onEdit,
  onDelete,
  onCompleteToggle,
  loading = false,
  emptyMessage = 'No tasks found.'
}) => {
  if (loading) {
    return (
      <div className="flex justify-center items-center py-10">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (tasks.length === 0) {
    return (
      <div className="text-center py-10">
        <p className="text-gray-500">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {tasks.map((task) => (
        <TaskCard
          key={task.id}
          task={task}
          onEdit={onEdit}
          onDelete={onDelete}
          onCompleteToggle={onCompleteToggle}
        />
      ))}
    </div>
  );
};

export default TaskList;