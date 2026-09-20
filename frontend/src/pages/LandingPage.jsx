import React from 'react';
import { Bug, LogIn, UserPlus } from 'lucide-react';

export function LandingPage({ setCurrentRoute }) {
  return (
    <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4 sm:px-6">
      <div className="max-w-xl w-full text-center space-y-8 py-12">
        {/* Brand Icon */}
        <div className="w-14 h-14 bg-brand-600 rounded-xl flex items-center justify-center text-white mx-auto shadow-sm">
          <Bug className="w-8 h-8" />
        </div>

        {/* Project Title */}
        <div className="space-y-3">
          <h1 className="text-2xl sm:text-4xl font-bold text-slate-900 tracking-tight leading-tight">
            Intelligent Bug Diagnosis Platform
            <span className="block text-brand-600 mt-1">with Fix Recommendation Assistance</span>
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 max-w-md mx-auto">
            Software defect analysis and diagnostic platform for developers.
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2 max-w-xs mx-auto">
          <button
            onClick={() => setCurrentRoute('login')}
            className="w-full flex items-center justify-center space-x-2 px-5 py-2.5 rounded-lg text-xs font-semibold bg-brand-600 text-white hover:bg-brand-700 transition-colors shadow-sm"
          >
            <LogIn className="w-4 h-4" />
            <span>Login</span>
          </button>
          
          <button
            onClick={() => setCurrentRoute('signup')}
            className="w-full flex items-center justify-center space-x-2 px-5 py-2.5 rounded-lg text-xs font-semibold bg-white border border-slate-300 text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <UserPlus className="w-4 h-4" />
            <span>Sign Up</span>
          </button>
        </div>
      </div>
    </div>
  );
}
