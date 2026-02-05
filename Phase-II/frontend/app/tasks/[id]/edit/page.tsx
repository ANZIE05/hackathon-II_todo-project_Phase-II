'use client';

import React, { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { useRouter, useParams } from 'next/navigation';
import { taskApi } from '@/lib/api';
import { Task } from '@/lib/types';
import Button from '@/components/ui/Button';

interface FormData {
  title: string;
  description: string;
  priority: 'low' | 'medium' | 'high';
  dueDate: string;
  status: 'active' | 'completed';
}

interface FormErrors {
  title?: string;
  description?: string;
  priority?: string;
  dueDate?: string;
  status?: string;
}

const EditTaskPage = () => {
  const router = useRouter();
  const params = useParams();
  const taskId = params.id as string;

  const [formData, setFormData] = useState<FormData>({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
    status: 'active',
  });

  const [errors, setErrors] = useState<FormErrors>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTask = async () => {
      try {
        setLoading(true);
        const response = await taskApi.getTasks();
        const task = response.tasks.find((t: Task) => t.id === taskId);

        if (task) {
          setFormData({
            title: task.title,
            description: task.description || '',
            priority: task.priority,
            dueDate: task.dueDate || '',
            status: task.status,
          });
        } else {
          setError('Task not found');
        }
      } catch (err: any) {
        setError(err.message || 'Failed to load task');
      } finally {
        setLoading(false);
      }
    };

    if (taskId) fetchTask();
  }, [taskId]);

  const validateField = (name: keyof FormData, value: string) => {
    switch (name) {
      case 'title':
        if (!value) return 'Title is required';
        if (value.length > 255) return 'Title must be less than 255 characters';
        return '';
      case 'description':
        if (value.length > 1000) return 'Description must be less than 1000 characters';
        return '';
      default:
        return '';
    }
  };

  const validateForm = () => {
    const newErrors: FormErrors = {};

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

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    if (errors[name as keyof FormData]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) return;

    setError(null);
    setLoading(true);

    try {
      await taskApi.updateTask(taskId, formData);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || 'An error occurred while updating the task');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white shadow rounded-lg p-6">
            <h1 className="text-2xl font-bold mb-6">Edit Task</h1>

            <form onSubmit={handleSubmit}>
              {/* form unchanged */}
            </form>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default EditTaskPage;
