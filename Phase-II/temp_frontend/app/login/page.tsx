'use client';

import LoginForm from '@/components/auth/LoginForm';
import { useAuth } from '@/lib/context';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function LoginPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  // Only render LoginForm if not authenticated
  if (isAuthenticated) {
    return null; // Or a loading indicator while redirecting
  }

  return (
    <LoginForm />
  );
}