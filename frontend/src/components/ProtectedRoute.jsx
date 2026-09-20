import React from 'react';
import { useAuth } from '../context/AuthContext';
import { Loader2 } from 'lucide-react';

export function ProtectedRoute({ children, fallbackRoute = 'login', setCurrentRoute }) {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin mb-2" />
        <p className="text-xs text-slate-500">Checking authentication session...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    // If not authenticated, inform and route
    return (
      <div className="max-w-md mx-auto my-12 p-6 bg-white border border-slate-200 rounded-xl text-center shadow-sm">
        <h2 className="text-base font-semibold text-slate-800">Authentication Required</h2>
        <p className="text-xs text-slate-500 mt-2 mb-6">
          You must be signed in with a developer account to access this page.
        </p>
        <button
          onClick={() => setCurrentRoute(fallbackRoute)}
          className="w-full bg-brand-600 hover:bg-brand-700 text-white font-medium text-xs py-2.5 px-4 rounded-lg transition-colors"
        >
          Go to Login
        </button>
      </div>
    );
  }

  return children;
}
