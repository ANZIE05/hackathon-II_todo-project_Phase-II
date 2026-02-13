import ProtectedRoute from '@/components/auth/ProtectedRoute';
import EditTaskForm from './EditTaskForm'; // Client form component
import { taskApi } from '@/lib/api';
import { Task } from '@/lib/types';

interface EditTaskPageProps {
  params: { id: string };
}

const EditTaskPage = async ({ params }: EditTaskPageProps) => {
  const taskId = params.id;

  let task: Task | null = null;
  try {
    const response = await taskApi.getTasks();
    task = response.tasks.find((t: Task) => t.id === taskId) || null;
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
