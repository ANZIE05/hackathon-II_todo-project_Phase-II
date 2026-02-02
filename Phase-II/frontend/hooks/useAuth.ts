'use client';

import { useState, useEffect } from 'react';
import { User } from '@/lib/types';
import { getUserFromToken, hasToken, removeToken } from '@/lib/auth';

/**
 * Custom hook for authentication state management
 */
const useAuth = () => {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Check authentication status on mount
  useEffect(() => {
    const checkAuthStatus = () => {
      setIsLoading(true);

      const userData = getUserFromToken();

      if (userData) {
        setUser({
          id: userData.userId || userData.sub || userData.id,
          email: userData.email,
          name: userData.name || userData.username || ''
        });
        setIsAuthenticated(true);
      } else {
        setUser(null);
        setIsAuthenticated(false);
      }

      setIsLoading(false);
    };

    checkAuthStatus();

    // Listen for storage changes to handle logout in other tabs
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'jwtToken') {
        checkAuthStatus();
      }
    };

    window.addEventListener('storage', handleStorageChange);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
    };
  }, []);

  const login = (token: string, userData: User) => {
    // In a real app, we'd typically just store the token and let the effect handle the rest
    // For now, we'll set the user directly
    localStorage.setItem('jwtToken', token);
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    removeToken();
    setUser(null);
    setIsAuthenticated(false);
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
  };
};

export default useAuth;
