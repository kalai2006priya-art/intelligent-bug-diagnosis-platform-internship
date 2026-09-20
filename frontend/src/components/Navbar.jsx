import React from 'react';
import { Bug, User as UserIcon, LogOut, ShieldAlert } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function Navbar({ currentRoute, setCurrentRoute }) {
  const { user, isAuthenticated, logout } = useAuth();

  return (
    <header className="bg-white border-b border-slate-200 sticky top-0 z-30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Logo & Brand */}
        <div 
          className="flex items-center space-x-3 cursor-pointer"
          onClick={() => setCurrentRoute(isAuthenticated ? 'dashboard' : 'landing')}
        >
          <div className="w-9 h-9 bg-brand-600 rounded-lg flex items-center justify-center text-white shadow-sm">
            <Bug className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-sm font-bold text-slate-900 tracking-tight leading-tight">
              Intelligent Bug Diagnosis Platform
            </h1>
            <p className="text-[11px] text-slate-500 font-medium">
              with Fix Recommendation Assistance
            </p>
          </div>
        </div>

        {/* Navigation & Profile */}
        <div className="flex items-center space-x-4">
          {isAuthenticated ? (
            <div className="flex items-center space-x-3">
              <div 
                className="flex items-center space-x-2 text-xs font-medium text-slate-700 bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-lg transition-colors cursor-pointer"
                onClick={() => setCurrentRoute('profile')}
              >
                <UserIcon className="w-3.5 h-3.5 text-slate-500" />
                <span>{user?.name || user?.email}</span>
              </div>
              <button
                onClick={logout}
                className="flex items-center space-x-1 text-xs font-medium text-slate-500 hover:text-red-600 hover:bg-red-50 px-2.5 py-1.5 rounded-lg transition-colors"
                title="Log Out"
              >
                <LogOut className="w-3.5 h-3.5" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setCurrentRoute('login')}
                className="text-xs font-medium text-slate-700 hover:text-brand-600 px-3 py-2 rounded-lg transition-colors"
              >
                Login
              </button>
              <button
                onClick={() => setCurrentRoute('signup')}
                className="text-xs font-semibold bg-brand-600 text-white hover:bg-brand-700 px-3.5 py-2 rounded-lg transition-colors shadow-sm"
              >
                Sign Up
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
