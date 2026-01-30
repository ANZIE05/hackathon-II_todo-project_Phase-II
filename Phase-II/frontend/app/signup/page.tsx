'use client';

import SignupForm from '@/components/auth/SignupForm';
import { useAuth } from '../../lib/context';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function SignupPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();

  // If already authenticated, redirect to dashboard
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  // Only render SignupForm if not authenticated
  if (isAuthenticated) {
    return null; // Or a loading indicator while redirecting
  }

  return (
    <SignupForm />
  );
}