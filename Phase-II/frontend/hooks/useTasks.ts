import { useState, useEffect } from 'react';
import { Task } from '@/lib/types';
import { taskApi } from '@/lib/api';

const useTasks = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch all tasks
  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await taskApi.getTasks();
      setTasks(response.tasks || []);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch tasks');
      console.error('Error fetching tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  // Create a new task
  const createTask = async (taskData: Omit<Task, 'id' | 'createdAt' | 'updatedAt' | 'userId'>) => {
    try {
      setLoading(true);
      const response = await taskApi.createTask(taskData);
      const newTask = response.task;
      setTasks([...tasks, newTask]);
      return newTask;
    } catch (err: any) {
      setError(err.message || 'Failed to create task');
      console.error('Error creating task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Update an existing task
  const updateTask = async (id: string, taskData: Partial<Task>) => {
    try {
      setLoading(true);
      const response = await taskApi.updateTask(id, taskData);
      const updatedTask = response.task;
      setTasks(tasks.map(task => task.id === id ? updatedTask : task));
      return updatedTask;
    } catch (err: any) {
      setError(err.message || 'Failed to update task');
      console.error('Error updating task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Delete a task
  const deleteTask = async (id: string) => {
    try {
      setLoading(true);
      await taskApi.deleteTask(id);
      setTasks(tasks.filter(task => task.id !== id));
    } catch (err: any) {
      setError(err.message || 'Failed to delete task');
      console.error('Error deleting task:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Toggle task completion status
  const toggleTaskCompletion = async (task: Task) => {
    try {
      const updatedStatus = task.status === 'active' ? 'completed' : 'active';
      return await updateTask(task.id, { status: updatedStatus });
    } catch (err) {
      console.error('Error toggling task completion:', err);
      throw err;
    }
  };

  // Get tasks by status
  const getTasksByStatus = (status: 'active' | 'completed') => {
    return tasks.filter(task => task.status === status);
  };

  // Get tasks by priority
  const getTasksByPriority = (priority: 'low' | 'medium' | 'high') => {
    return tasks.filter(task => task.priority === priority);
  };

  // Filter tasks based on multiple criteria
  const filterTasks = (
    status?: 'all' | 'active' | 'completed',
    priority?: 'all' | 'low' | 'medium' | 'high',
    searchQuery?: string
  ) => {
    return tasks.filter(task => {
      // Filter by status
      if (status && status !== 'all' && task.status !== status) {
        return false;
      }

      // Filter by priority
      if (priority && priority !== 'all' && task.priority !== priority) {
        return false;
      }

      // Filter by search query
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        const matchesTitle = task.title.toLowerCase().includes(query);
        const matchesDescription = task.description?.toLowerCase().includes(query) || false;
        if (!matchesTitle && !matchesDescription) {
          return false;
        }
      }

      return true;
    });
  };

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    toggleTaskCompletion,
    getTasksByStatus,
    getTasksByPriority,
    filterTasks,
  };
};

export default useTasks;