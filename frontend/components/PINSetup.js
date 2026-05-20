'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import toast from 'react-hot-toast';
import { authAPI } from '@/lib/api';
import { useRouter } from 'next/navigation';

const pinSchema = z.object({
  pin: z.string().length(4, 'PIN must be 4 digits').regex(/^\d+$/, 'PIN must contain only numbers'),
  confirm_pin: z.string().length(4, 'PIN must be 4 digits'),
}).refine((data) => data.pin === data.confirm_pin, {
  message: "PINs don't match",
  path: ["confirm_pin"],
});

export default function PINSetup() {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();
  
  const { register, handleSubmit, formState: { errors } } = useForm({
    resolver: zodResolver(pinSchema),
  });
  
  const onSubmit = async (data) => {
    setIsLoading(true);
    try {
      await authAPI.setupPIN({ pin: data.pin, confirm_pin: data.confirm_pin });
      toast.success('PIN setup successful!');
      router.push('/dashboard');
    } catch (error) {
      toast.error(error.response?.data?.error || 'Failed to setup PIN');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-lg shadow-md">
        <div>
          <h2 className="text-center text-3xl font-extrabold text-gray-900">
            Setup Transaction PIN
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Set a 4-digit PIN for secure transactions
          </p>
        </div>
        
        <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700">PIN</label>
            <input
              type="password"
              {...register('pin')}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-center text-2xl tracking-widest"
              placeholder="****"
              maxLength={4}
            />
            {errors.pin && (
              <p className="mt-1 text-red-500 text-sm">{errors.pin.message}</p>
            )}
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700">Confirm PIN</label>
            <input
              type="password"
              {...register('confirm_pin')}
              className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-center text-2xl tracking-widest"
              placeholder="****"
              maxLength={4}
            />
            {errors.confirm_pin && (
              <p className="mt-1 text-red-500 text-sm">{errors.confirm_pin.message}</p>
            )}
          </div>
          
          <button
            type="submit"
            disabled={isLoading}
            className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {isLoading ? 'Setting up...' : 'Setup PIN'}
          </button>
        </form>
        
        <p className="text-xs text-gray-500 text-center">
          Your PIN is encrypted and secure. Never share it with anyone.
        </p>
      </div>
    </div>
  );
}