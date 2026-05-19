'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { getAuthData } from '@/lib/api';
import Navbar from '@/components/Navbar';

export default function Dashboard() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  
  useEffect(() => {
    const { user: userData, token } = getAuthData();
    if (!token) {
      router.push('/login');
      return;
    }
    setUser(userData);
  }, [router]);
  
  if (!user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }
  
  return (
    <>
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <div className="grid md:grid-cols-3 gap-6">
          {/* Balance Card */}
          <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg shadow-md p-6">
            <h3 className="text-lg font-medium mb-2">Total Balance</h3>
            <p className="text-3xl font-bold">$1,250.75</p>
            <p className="text-sm mt-2 opacity-80">Available for transactions</p>
          </div>
          
          {/* Quick Actions */}
          <div className="bg-white rounded-lg shadow-md p-6 md:col-span-2">
            <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
            <div className="grid grid-cols-2 gap-4">
              <button className="btn-primary">
                Send Money
              </button>
              <button className="btn-secondary">
                Request Money
              </button>
              <button className="btn-secondary">
                Transaction History
              </button>
              <button className="btn-secondary">
                Add Money
              </button>
            </div>
          </div>
          
          {/* Profile Info */}
          <div className="bg-white rounded-lg shadow-md p-6 md:col-span-3">
            <h3 className="text-lg font-semibold mb-4">Profile Information</h3>
            <div className="space-y-2">
              <p><strong>Name:</strong> {user.full_name}</p>
              <p><strong>Email:</strong> {user.email}</p>
              <p><strong>Phone:</strong> {user.phone_number || 'Not provided'}</p>
              <p><strong>PIN Status:</strong> {user.has_pin ? '✅ Set' : '❌ Not set'}</p>
              <p><strong>Verification Status:</strong> {user.is_verified ? '✅ Verified' : '⚠️ Pending'}</p>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}