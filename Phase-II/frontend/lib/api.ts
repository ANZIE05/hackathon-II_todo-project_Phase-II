import { AuthResponse, LoginCredentials, SignupData, Task } from '@/lib/types';
import { getToken } from '@/lib/auth';

const API_BASE_URL = (process.env.NEXT_PUBLIC_API_BASE_URL || '').replace(/\/$/, '');

const buildUrl = (path: string) => {
  if (path.startsWith('http')) {
    return path;
  }
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  return API_BASE_URL ? `${API_BASE_URL}${normalizedPath}` : normalizedPath;
};

const parseErrorMessage = async (response: Response) => {
  try {
    const data = await response.json();
    return data?.detail || data?.message || response.statusText;
  } catch (error) {
    return response.statusText;
  }
};

const request = async <T>(path: string, options: RequestInit = {}) => {
  const headers = new Headers(options.headers || {});
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  const token = getToken();
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(buildUrl(path), {
    ...options,
    headers,
  });

  if (!response.ok) {
    const message = await parseErrorMessage(response);
    throw new Error(message);
  }

  if (response.status === 204) {
    return null as T;
  }

  return response.json() as Promise<T>;
};

const mapTaskFromApi = (task: any): Task => ({
  id: String(task.id),
  title: task.title,
  description: task.description ?? '',
  priority: task.priority ?? 'medium',
  status: task.completed ? 'completed' : 'active',
  dueDate: task.due_date ?? task.dueDate ?? '',
  createdAt: task.created_at ?? task.createdAt,
  updatedAt: task.updated_at ?? task.updatedAt,
  userId: task.user_id ?? task.userId,
});

const mapTaskToApi = (task: Partial<Task>) => ({
  title: task.title,
  description: task.description,
  priority: task.priority,
  due_date: task.dueDate === '' ? null : task.dueDate,
  completed: task.status ? task.status === 'completed' : undefined,
});

export const authApi = {
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    return request<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });
  },
  signup: async (data: SignupData): Promise<AuthResponse> => {
    return request<AuthResponse>('/api/auth/register', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  logout: async (): Promise<{ success: boolean }> => {
    await request('/api/auth/logout', {
      method: 'POST',
    });
    return { success: true };
  },
};

export const taskApi = {
  getTasks: async (): Promise<{ tasks: Task[] }> => {
    const response = await request<{ tasks: any[] }>('/api/tasks', {
      method: 'GET',
    });
    return {
      tasks: response.tasks.map(mapTaskFromApi),
    };
  },
  createTask: async (taskData: Partial<Task>): Promise<{ task: Task }> => {
    const response = await request<any>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(mapTaskToApi(taskData)),
    });
    return { task: mapTaskFromApi(response) };
  },
  updateTask: async (id: string, taskData: Partial<Task>): Promise<{ task: Task }> => {
    const response = await request<any>(`/api/tasks/${id}`, {
      method: 'PUT',
      body: JSON.stringify(mapTaskToApi(taskData)),
    });
    return { task: mapTaskFromApi(response) };
  },
  deleteTask: async (id: string): Promise<void> => {
    await request(`/api/tasks/${id}`, { method: 'DELETE' });
  },
};
