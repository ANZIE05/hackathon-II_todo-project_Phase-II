'use client';

import React, { useState } from 'react';
import { Task } from '@/lib/types';
import { taskApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import Button from '@/components/ui/Button';

interface FormData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  dueDate: string;
  status: 'active' | 'completed';
}

interface EditTaskFormProps {
  task: Task;
}

const EditTaskForm = ({ task }: EditTaskFormProps) => {
  const router = useRouter();

  const [formData, setFormData] = useState<FormData>({
    title: task.title,
    description: task.description || '',
    priority: task.priority,
    dueDate: task.dueDate || '',
    status: task.status,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await taskApi.updateTask(task.id, formData);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'Error updating task');
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      {error && <div className="text-red-500 mb-4">{error}</div>}
      <div className="mb-4">
        <label className="block font-medium mb-1">Title</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Description</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Priority</label>
        <select name="priority" value={formData.priority} onChange={handleChange} className="w-full border rounded p-2">
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
        </select>
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Due Date</label>
        <input
          type="date"
          name="dueDate"
          value={formData.dueDate}
          onChange={handleChange}
          className="w-full border rounded p-2"
        />
      </div>

      <div className="mb-4">
        <label className="block font-medium mb-1">Status</label>
        <select name="status" value={formData.status} onChange={handleChange} className="w-full border rounded p-2">
          <option value="active">Active</option>
          <option value="completed">Completed</option>
        </select>
      </div>

      <Button type="submit" disabled={loading}>
        {loading ? 'Saving...' : 'Update Task'}
      </Button>
    </form>
  );
};

export default EditTaskForm;
