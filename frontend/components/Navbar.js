'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { getAuthData, clearAuthData, authAPI } from '@/lib/api';
import toast from 'react-hot-toast';

export default function Navbar() {
  const [user, setUser] = useState(null);
  const router = useRouter();
  
  useEffect(() => {
    const { user: userData } = getAuthData();
    setUser(userData);
  }, []);
  
  const handleLogout = async () => {
    try {
      await authAPI.logout();
    } catch (error) {
      // Ignore errors
    } finally {
      clearAuthData();
      toast.success('Logged out successfully');
      router.push('/login');
    }
  };
  
  return (
    <nav className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-3">
        <div className="flex justify-between items-center">
          <Link href="/" className="text-xl font-bold text-blue-600">
            Ortho Wallet
          </Link>
          
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                <span className="text-gray-700">
                  Welcome, {user.full_name}
                </span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 transition"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-gray-700 hover:text-blue-600">
                  Login
                </Link>
                <Link href="/signup" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
}