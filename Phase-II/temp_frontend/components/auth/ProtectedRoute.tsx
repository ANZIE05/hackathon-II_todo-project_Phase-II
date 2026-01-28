'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/lib/context';
import { useRouter } from 'next/navigation';
import { ReactNode } from 'react';
import { isTokenExpired, getToken } from '@/lib/auth';

interface ProtectedRouteProps {
  children: ReactNode;
  fallbackUrl?: string;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  fallbackUrl = '/login'
}) => {
  const { isAuthenticated, isLoading, logout } = useAuth();
  const router = useRouter();
  const [showSessionExpired, setShowSessionExpired] = useState(false);

  useEffect(() => {
    // Check for session expiration periodically
    const checkSession = () => {
      const token = getToken();
      if (token && isTokenExpired(token)) {
        logout();
        setShowSessionExpired(true);
        setTimeout(() => {
          router.push(fallbackUrl);
        }, 3000); // Redirect after 3 seconds to show notification
      } else if (!isLoading && !isAuthenticated) {
        router.push(fallbackUrl);
      }
    };

    // Check immediately
    checkSession();

    // Check every minute
    const interval = setInterval(checkSession, 60000);

    return () => clearInterval(interval);
  }, [isAuthenticated, isLoading, router, fallbackUrl, logout]);

  // Show nothing while checking authentication status
  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  // Show session expired notification
  if (showSessionExpired) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="bg-white p-8 rounded-lg shadow-md text-center max-w-md">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <svg className="h-6 w-6 text-red-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <h3 className="mt-4 text-lg font-medium text-gray-900">Session Expired</h3>
          <p className="mt-2 text-sm text-gray-500">
            Your session has expired. You will be redirected to the login page shortly.
          </p>
        </div>
      </div>
    );
  }

  // If authenticated, render the protected content
  if (isAuthenticated) {
    return <>{children}</>;
  }

  // If not authenticated and not loading, return nothing (redirect happens via useEffect)
  return null;
};

export default ProtectedRoute;