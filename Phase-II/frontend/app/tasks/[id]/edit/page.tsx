// app/tasks/[id]/edit/page.tsx
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import EditTaskForm from './EditTaskForm'; // Client form component
import { Task } from '@/lib/types';

interface EditTaskPageProps {
  params: { id: string };
}

const EditTaskPage = async ({ params }: EditTaskPageProps) => {
  const taskId = params.id;

  let task: Task | null = null;

  try {
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/tasks`, {
      method: 'GET',
      cache: 'no-store', // always fresh data for SSR
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) throw new Error('Failed to fetch tasks');

    const data = await response.json();
    task = data.tasks.find((t: Task) => t.id === taskId) || null;
  } catch (err) {
    task = null;
  }

  if (!task) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="text-red-500 text-xl">Task not found</div>
      </div>
    );
  }

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white shadow rounded-lg p-6">
            <h1 className="text-2xl font-bold mb-6">Edit Task</h1>
            <EditTaskForm task={task} />
          </div>
        </div>
      </div>
    </ProtectedRoute>
  );
};

export default EditTaskPage;
