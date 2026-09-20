import React from 'react';
import { User, Mail, Calendar, Key, Shield, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function ProfilePage({ setCurrentRoute }) {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    setCurrentRoute('landing');
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h1 className="text-lg font-bold text-slate-900">Developer Profile</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Account credentials and workspace authentication information.
        </p>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6 space-y-6">
        <div className="flex items-center space-x-4 pb-6 border-b border-slate-100">
          <div className="w-12 h-12 rounded-full bg-brand-100 text-brand-700 flex items-center justify-center font-bold text-base">
            {user?.name?.charAt(0).toUpperCase() || 'D'}
          </div>
          <div>
            <h2 className="text-sm font-bold text-slate-900">{user?.name}</h2>
            <p className="text-xs text-slate-500">{user?.email}</p>
          </div>
        </div>

        <div className="space-y-4">
          <div className="flex items-center justify-between py-2 border-b border-slate-50">
            <div className="flex items-center space-x-2 text-xs text-slate-500">
              <Mail className="w-4 h-4 text-slate-400" />
              <span>Email Address</span>
            </div>
            <span className="text-xs font-semibold text-slate-800">{user?.email}</span>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-slate-50">
            <div className="flex items-center space-x-2 text-xs text-slate-500">
              <Key className="w-4 h-4 text-slate-400" />
              <span>Developer ID</span>
            </div>
            <span className="text-xs font-mono text-slate-700">{user?.id}</span>
          </div>

          <div className="flex items-center justify-between py-2 border-b border-slate-50">
            <div className="flex items-center space-x-2 text-xs text-slate-500">
              <Calendar className="w-4 h-4 text-slate-400" />
              <span>Member Since</span>
            </div>
            <span className="text-xs text-slate-800">
              {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Active'}
            </span>
          </div>

          <div className="flex items-center justify-between py-2">
            <div className="flex items-center space-x-2 text-xs text-slate-500">
              <Shield className="w-4 h-4 text-slate-400" />
              <span>Authentication Type</span>
            </div>
            <span className="text-xs font-medium px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 border border-emerald-200">
              JWT Bearer (Bcrypt Secured)
            </span>
          </div>
        </div>

        <div className="pt-4 border-t border-slate-100 flex justify-end">
          <button
            onClick={handleLogout}
            className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-lg text-xs font-semibold text-red-600 bg-red-50 hover:bg-red-100 border border-red-200 transition-colors"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>Sign Out</span>
          </button>
        </div>
      </div>
    </div>
  );
}
