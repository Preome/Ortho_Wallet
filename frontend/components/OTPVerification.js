'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { authAPI, setAuthData } from '@/lib/api';
import { useRouter, useSearchParams } from 'next/navigation';

const otpSchema = z.object({
  otp_code: z.string().length(6, 'OTP must be 6 digits'),
});

export default function OTPVerification() {
  const [isLoading, setIsLoading] = useState(false);
  const [isResending, setIsResending] = useState(false);
  const [countdown, setCountdown] = useState(0);
  const router = useRouter();
  const searchParams = useSearchParams();
  
  const email = searchParams.get('email') || '';
  const purpose = searchParams.get('purpose') || 'login';
  
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(otpSchema),
  });
  
  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);
  
  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      const response = await authAPI.verifyOTP({
        email,
        otp_code: data.otp_code,
        purpose,
      });
      
      if (purpose === 'login') {
        setAuthData(response.data.token, response.data.user);
        toast.success('Login successful!');
        
        if (!response.data.user.has_pin) {
          router.push('/setup-pin');
        } else {
          router.push('/dashboard');
        }
      } else if (purpose === 'verification') {
        toast.success('Email verified successfully! Please login.');
        router.push('/login');
      }
    } catch (error) {
      toast.error(error.response?.data?.error || 'Invalid OTP');
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleResendOTP = async () => {
    setIsResending(true);
    try {
      await authAPI.sendOTP({ email, purpose });
      toast.success('OTP resent successfully!');
      setCountdown(60);
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to resend OTP');
    } finally {
      setIsResending(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Verify Your Email
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            We've sent a verification code to <strong>{email}</strong>
          </p>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">OTP Code</label>
            <input
              type="text"
              {...register('otp_code')}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-center text-2xl tracking-widest"
              placeholder="000000"
              maxLength={6}
            />
            {errors.otp_code && (
              <p className="mt-1 text-red-500 text-sm">{errors.otp_code.message}</p>
            )}
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? 'Verifying...' : 'Verify OTP'}
          </button>
        </form>
        
        <div className="text-center">
          <button
            onClick={handleResendOTP}
            disabled={isResending || countdown > 0}
            className="text-sm text-blue-600 hover:text-blue-500 disabled:text-gray-400 disabled:cursor-not-allowed"
          >
            {isResending 
              ? 'Sending...' 
              : countdown > 0 
                ? `Resend in ${countdown}s` 
                : 'Resend OTP'}
          </button>
        </div>
      </div>
    </div>
  );
}