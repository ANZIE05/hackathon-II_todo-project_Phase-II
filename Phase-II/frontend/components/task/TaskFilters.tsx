import React from 'react';

interface TaskFiltersProps {
  statusFilter: 'all' | 'active' | 'completed';
  priorityFilter: 'all' | 'low' | 'medium' | 'high';
  searchQuery: string;
  onStatusChange: (status: 'all' | 'active' | 'completed') => void;
  onPriorityChange: (priority: 'all' | 'low' | 'medium' | 'high') => void;
  onSearchChange: (query: string) => void;
}

const TaskFilters: React.FC<TaskFiltersProps> = ({
  statusFilter,
  priorityFilter,
  searchQuery,
  onStatusChange,
  onPriorityChange,
  onSearchChange
}) => {
  return (
    <div className="bg-white p-4 rounded-lg shadow mb-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label htmlFor="status-filter" className="block text-sm font-medium text-gray-700 mb-1">
            Status
          </label>
          <select
            id="status-filter"
            value={statusFilter}
            onChange={(e) => onStatusChange(e.target.value as 'all' | 'active' | 'completed')}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          >
            <option value="all">All</option>
            <option value="active">Active</option>
            <option value="completed">Completed</option>
          </select>
        </div>

        <div>
          <label htmlFor="priority-filter" className="block text-sm font-medium text-gray-700 mb-1">
            Priority
          </label>
          <select
            id="priority-filter"
            value={priorityFilter}
            onChange={(e) => onPriorityChange(e.target.value as 'all' | 'low' | 'medium' | 'high')}
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          >
            <option value="all">All Priorities</option>
            <option value="low">Low</option>
            <option value="medium">Medium</option>
            <option value="high">High</option>
          </select>
        </div>

        <div>
          <label htmlFor="search-query" className="block text-sm font-medium text-gray-700 mb-1">
            Search
          </label>
          <input
            type="text"
            id="search-query"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Search tasks..."
            className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
          />
        </div>
      </div>
    </div>
  );
};

export default TaskFilters;