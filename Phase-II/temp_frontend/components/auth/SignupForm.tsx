'use client';

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { authApi } from '@/lib/api';
import { setToken } from '@/lib/auth';
import { useAuth } from '@/lib/context';
import Button from '../ui/Button';

interface FormData {
  email: string;
  password: string;
  name: string;
}

const SignupForm: React.FC = () => {
  const [formData, setFormData] = useState<FormData>({ email: '', password: '', name: '' });
  const [errors, setErrors] = useState<Partial<FormData>>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const router = useRouter();
  const { login } = useAuth();

  const validateField = (name: keyof FormData, value: string) => {
    switch (name) {
      case 'name':
        if (!value) {
          return 'Name is required';
        }
        if (value.length < 2) {
          return 'Name must be at least 2 characters';
        }
        if (value.length > 100) {
          return 'Name must be less than 100 characters';
        }
        return '';
      case 'email':
        if (!value) {
          return 'Email is required';
        }
        if (!/\S+@\S+\.\S+/.test(value)) {
          return 'Email address is invalid';
        }
        return '';
      case 'password':
        if (!value) {
          return 'Password is required';
        }
        if (value.length < 6) {
          return 'Password must be at least 6 characters';
        }
        return '';
      default:
        return '';
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));

    // Clear the error for this field when user starts typing
    if (errors[name as keyof FormData]) {
      setErrors(prev => ({ ...prev, [name]: undefined }));
    }
  };

  const validateForm = () => {
    const newErrors: Partial<FormData> = {};
    Object.entries(formData).forEach(([key, value]) => {
      const error = validateField(key as keyof FormData, value);
      if (error) {
        newErrors[key as keyof FormData] = error;
      }
    });

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setError(null);
    setLoading(true);

    try {
      const response = await authApi.signup(formData);
      const { token, user } = response;

      // Store token and update auth context
      setToken(token);
      login(token, user);

      // Redirect to dashboard
      router.push('/dashboard');
      router.refresh(); // Refresh to update the UI based on auth state
    } catch (err: any) {
      setError(err.message || 'An error occurred during signup');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="text-sm text-red-700">{error}</div>
            </div>
          )}

          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="name" className="sr-only">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                required
                value={formData.name}
                onChange={handleChange}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.name ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm ${
                  errors.name ? 'ring-1 ring-red-500' : ''
                }`}
                placeholder="Full Name"
              />
              {errors.name && (
                <p className="mt-1 text-sm text-red-600">{errors.name}</p>
              )}
            </div>
            <div>
              <label htmlFor="email-address" className="sr-only">
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={formData.email}
                onChange={handleChange}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.email ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm ${
                  errors.email ? 'ring-1 ring-red-500' : ''
                }`}
                placeholder="Email address"
              />
              {errors.email && (
                <p className="mt-1 text-sm text-red-600">{errors.email}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                required
                value={formData.password}
                onChange={handleChange}
                className={`appearance-none rounded-none relative block w-full px-3 py-2 border ${
                  errors.password ? 'border-red-300' : 'border-gray-300'
                } placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm ${
                  errors.password ? 'ring-1 ring-red-500' : ''
                }`}
                placeholder="Password"
              />
              {errors.password && (
                <p className="mt-1 text-sm text-red-600">{errors.password}</p>
              )}
            </div>
          </div>

          <div>
            <Button
              type="submit"
              loading={loading}
              fullWidth
              variant="primary"
            >
              Sign up
            </Button>
          </div>

          <div className="text-sm text-center">
            <a href="/login" className="font-medium text-blue-600 hover:text-blue-500">
              Already have an account? Sign in
            </a>
          </div>
        </form>
      </div>
    </div>
  );
};

export default SignupForm;