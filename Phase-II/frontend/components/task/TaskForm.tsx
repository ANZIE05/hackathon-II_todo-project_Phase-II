import React from 'react';
import { Task } from '@/lib/types';
import Button from '@/components/ui/Button';

interface TaskFormProps {
  task?: Task;
  onSubmit: (taskData: any) => void;
  onCancel: () => void;
  loading?: boolean;
}

interface FormData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  dueDate: string;
  status: 'active' | 'completed';
}

const TaskForm: React.FC<TaskFormProps> = ({ task, onSubmit, onCancel, loading = false }) => {
  const [formData, setFormData] = React.useState<FormData>({
    title: task?.title || '',
    description: task?.description || '',
    priority: task?.priority || 'medium',
    dueDate: task?.dueDate || '',
    status: task?.status || 'active'
  });
  const [errors, setErrors] = React.useState<Partial<FormData>>({});

  const validateField = (name: keyof FormData, value: string) => {
    switch (name) {
      case 'title':
        if (!value) {
          return 'Title is required';
        }
        if (value.length > 255) {
          return 'Title must be less than 255 characters';
        }
        return '';
      case 'description':
        if (value.length > 1000) {
          return 'Description must be less than 1000 characters';
        }
        return '';
      default:
        return '';
    }
  };

  const validateForm = () => {
    const newErrors: Partial<FormData> = {};
    Object.entries(formData).forEach(([key, value]) => {
      if (typeof value === 'string') {
        const error = validateField(key as keyof FormData, value);
        if (error) {
          newErrors[key as keyof FormData] = error;
        }
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear the error for this field when user starts typing
    if (errors[name as keyof FormData]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit}>
      <div className="space-y-6">
        <div>
          <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
            Title *
          </label>
          <input
            type="text"
            id="title"
            name="title"
            value={formData.title}
            onChange={handleChange}
            className={`appearance-none block w-full px-3 py-2 border ${
              errors.title ? 'border-red-300' : 'border-gray-300'
            } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
              errors.title ? 'ring-1 ring-red-500' : ''
            }`}
            placeholder="Task title"
          />
          {errors.title && (
            <p className="mt-1 text-sm text-red-600">{errors.title}</p>
          )}
        </div>

        <div>
          <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            id="description"
            name="description"
            rows={4}
            value={formData.description}
            onChange={handleChange}
            className={`appearance-none block w-full px-3 py-2 border ${
              errors.description ? 'border-red-300' : 'border-gray-300'
            } rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm ${
              errors.description ? 'ring-1 ring-red-500' : ''
            }`}
            placeholder="Task description"
          ></textarea>
          {errors.description && (
            <p className="mt-1 text-sm text-red-600">{errors.description}</p>
          )}
        </div>

        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-3">
          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-1">
              Priority
            </label>
            <select
              id="priority"
              name="priority"
              value={formData.priority}
              onChange={handleChange}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </div>

          <div>
            <label htmlFor="status" className="block text-sm font-medium text-gray-700 mb-1">
              Status
            </label>
            <select
              id="status"
              name="status"
              value={formData.status}
              onChange={handleChange}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="active">Active</option>
              <option value="completed">Completed</option>
            </select>
          </div>

          <div>
            <label htmlFor="dueDate" className="block text-sm font-medium text-gray-700 mb-1">
              Due Date
            </label>
            <input
              type="date"
              id="dueDate"
              name="dueDate"
              value={formData.dueDate}
              onChange={handleChange}
              className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      <div className="mt-8 flex justify-end space-x-3">
        <Button
          type="button"
          variant="secondary"
          onClick={onCancel}
        >
          Cancel
        </Button>
        <Button
          type="submit"
          variant="primary"
          loading={loading}
        >
          {task ? 'Update Task' : 'Create Task'}
        </Button>
      </div>
    </form>
  );
};

export default TaskForm;