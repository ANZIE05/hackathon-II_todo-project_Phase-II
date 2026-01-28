'use client';

import React, { useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import TaskList from '@/components/ui/TaskList';
import EmptyState from '@/components/ui/EmptyState';
import { Task } from '@/lib/types';
import { taskApi } from '@/lib/api';
import { useAuth } from '@/lib/context';

const DashboardPage = () => {
  const { user } = useAuth();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [filteredTasks, setFilteredTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed'>('all');

  // Load tasks on component mount
  React.useEffect(() => {
    const fetchTasks = async () => {
      try {
        setLoading(true);
        const response = await taskApi.getTasks();
        setTasks(response.tasks || []);
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, []);

  // Apply filters when tasks or filter changes
  React.useEffect(() => {
    let result = [...tasks];

    if (statusFilter !== 'all') {
      result = result.filter(task => task.status === statusFilter);
    }

    setFilteredTasks(result);
  }, [tasks, statusFilter]);

  const handleEdit = (task: Task) => {
    // Navigate to edit page
    window.location.href = `/tasks/${task.id}/edit`;
  };

  const handleDelete = async (id: string) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      try {
        await taskApi.deleteTask(id);
        setTasks(tasks.filter(task => task.id !== id));
      } catch (error) {
        console.error('Failed to delete task:', error);
      }
    }
  };

  const handleCompleteToggle = async (task: Task) => {
    try {
      const updatedStatus = task.status === 'active' ? 'completed' : 'active';
      const updatedTask = await taskApi.updateTask(task.id, {
        ...task,
        status: updatedStatus
      });

      setTasks(tasks.map(t => t.id === task.id ? updatedTask.task : t));
    } catch (error) {
      console.error('Failed to update task status:', error);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <div className="py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
              <div className="flex items-center space-x-4">
                <span className="text-gray-700">Welcome, {user?.name}!</span>
                <a
                  href="/tasks/new"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                >
                  Add Task
                </a>
              </div>
            </div>

            {/* Filter Controls */}
            <div className="mb-6 flex space-x-4">
              <button
                onClick={() => setStatusFilter('all')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  statusFilter === 'all'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                All Tasks
              </button>
              <button
                onClick={() => setStatusFilter('active')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  statusFilter === 'active'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Active
              </button>
              <button
                onClick={() => setStatusFilter('completed')}
                className={`px-4 py-2 rounded-md text-sm font-medium ${
                  statusFilter === 'completed'
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                Completed
              </button>
            </div>

            {/* Task List */}
            <div className="grid grid-cols-1 gap-6">
              {filteredTasks.length === 0 && !loading ? (
                <div className="col-span-full">
                  <EmptyState
                    title="No tasks yet"
                    description="Get started by creating a new task."
                    actionText="Create Task"
                    onAction={() => (window.location.href = '/tasks/new')}
                    showAction={true}
                  />
                </div>
              ) : (
                <TaskList
                  tasks={filteredTasks}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                  onCompleteToggle={handleCompleteToggle}
                  loading={loading}
                  emptyMessage="No tasks match your current filters."
                />
              )}
            </div>
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default DashboardPage;