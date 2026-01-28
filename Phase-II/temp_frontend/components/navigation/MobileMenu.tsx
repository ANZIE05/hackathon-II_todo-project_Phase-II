import React, { useState } from 'react';
import Link from 'next/link';
import { useAuth } from '@/lib/context';
import Button from '@/components/ui/Button';

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

const MobileMenu: React.FC<MobileMenuProps> = ({ isOpen, onClose }) => {
  const { user, isAuthenticated, logout } = useAuth();

  if (!isOpen) return null;

  const handleLogout = () => {
    logout();
    window.location.href = '/login';
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 md:hidden">
      <div className="relative bg-white w-4/5 h-full">
        <div className="p-4 border-b">
          <div className="flex justify-between items-center">
            <span className="text-xl font-bold text-indigo-600">Todo App</span>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700"
            >
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-4">
          <nav className="flex flex-col space-y-4">
            <Link
              href="/dashboard"
              className="text-gray-700 hover:text-gray-900 py-2 px-4 rounded-md block"
              onClick={onClose}
            >
              Dashboard
            </Link>
            <Link
              href="/tasks"
              className="text-gray-700 hover:text-gray-900 py-2 px-4 rounded-md block"
              onClick={onClose}
            >
              Tasks
            </Link>
            <Link
              href="/tasks/new"
              className="text-gray-700 hover:text-gray-900 py-2 px-4 rounded-md block"
              onClick={onClose}
            >
              Create Task
            </Link>
            <Link
              href="#"
              className="text-gray-700 hover:text-gray-900 py-2 px-4 rounded-md block"
              onClick={onClose}
            >
              Settings
            </Link>
          </nav>

          <div className="mt-8 pt-4 border-t">
            {isAuthenticated ? (
              <div className="space-y-4">
                <p className="text-gray-700">Welcome, {user?.name}</p>
                <Button
                  variant="secondary"
                  fullWidth
                  onClick={handleLogout}
                >
                  Logout
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                <Link
                  href="/login"
                  className="block w-full py-2 px-4 border border-transparent text-center rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700"
                  onClick={onClose}
                >
                  Sign in
                </Link>
                <Link
                  href="/signup"
                  className="block w-full py-2 px-4 border border-gray-300 text-center rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50"
                  onClick={onClose}
                >
                  Sign up
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default MobileMenu;