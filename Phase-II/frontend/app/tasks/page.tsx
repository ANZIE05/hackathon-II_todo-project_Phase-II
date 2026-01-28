'use client';

import React, { useState } from 'react';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import TaskList from '@/components/ui/TaskList';
import EmptyState from '@/components/ui/EmptyState';
import TaskFilters from '@/components/task/TaskFilters';
import { Task } from '@/lib/types';
import { taskApi } from '@/lib/api';
import { useTasks } from '@/hooks/useTasks';
import { useAuth } from '@/lib/context';

const TasksPage = () => {
  const { user } = useAuth();
  const {
    tasks,
    loading,
    error,
    fetchTasks,
    deleteTask,
    toggleTaskCompletion,
    filterTasks
  } = useTasks();

  const [statusFilter, setStatusFilter] = useState<'all' | 'active' | 'completed'>('all');
  const [priorityFilter, setPriorityFilter] = useState<'all' | 'low' | 'medium' | 'high'>('all');
  const [searchQuery, setSearchQuery] = useState('');

  // Apply filters when tasks or filter changes
  const filteredTasks = filterTasks(statusFilter, priorityFilter, searchQuery);

  const handleEdit = (task: Task) => {
    // Navigate to edit page
    window.location.href = `/tasks/${task.id}/edit`;
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50">
        <div className="py-6">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center mb-6">
              <h1 className="text-2xl font-bold text-gray-900">My Tasks</h1>
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

            {/* Task Filters */}
            <TaskFilters
              statusFilter={statusFilter}
              priorityFilter={priorityFilter}
              searchQuery={searchQuery}
              onStatusChange={setStatusFilter}
              onPriorityChange={setPriorityFilter}
              onSearchChange={setSearchQuery}
            />

            {/* Error Message */}
            {error && (
              <div className="rounded-md bg-red-50 p-4 mb-4">
                <div className="text-sm text-red-700">{error}</div>
              </div>
            )}

            {/* Task List */}
            {filteredTasks.length === 0 && !loading ? (
              <EmptyState
                title={tasks.length === 0 ? "No tasks yet" : "No tasks match your filters"}
                description={
                  tasks.length === 0
                    ? "Get started by creating a new task."
                    : "Try changing your filters or search query."
                }
                actionText="Create Task"
                onAction={() => (window.location.href = '/tasks/new')}
                showAction={tasks.length === 0}
              />
            ) : (
              <TaskList
                tasks={filteredTasks}
                onEdit={handleEdit}
                onDelete={deleteTask}
                onCompleteToggle={toggleTaskCompletion}
                loading={loading}
                emptyMessage="No tasks match your current filters."
              />
            )}
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default TasksPage;