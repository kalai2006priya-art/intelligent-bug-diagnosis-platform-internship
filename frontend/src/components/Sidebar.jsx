import React from 'react';
import { LayoutDashboard, PlusCircle, History, Database, User, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export function Sidebar({ currentRoute, setCurrentRoute }) {
  const { logout } = useAuth();

  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'submit-bug', label: 'Submit Bug', icon: PlusCircle },
    { id: 'bug-history', label: 'Bug History', icon: History },
    { id: 'knowledge-base', label: 'Knowledge Base', icon: Database },
    { id: 'profile', label: 'Profile', icon: User },
  ];

  return (
    <aside className="w-64 bg-white border-r border-slate-200 min-h-[calc(100vh-4rem)] flex flex-col justify-between p-4">
      <div className="space-y-1">
        <div className="px-3 py-2 text-[11px] font-bold text-slate-400 uppercase tracking-wider">
          Developer Workspace
        </div>
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentRoute === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setCurrentRoute(item.id)}
              className={`w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-semibold transition-all ${
                isActive
                  ? 'bg-brand-50 text-brand-700 border border-brand-200 shadow-sm'
                  : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
              }`}
            >
              <Icon className={`w-4 h-4 ${isActive ? 'text-brand-600' : 'text-slate-400'}`} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </div>

      <div className="pt-4 border-t border-slate-100">
        <button
          onClick={logout}
          className="w-full flex items-center space-x-3 px-3.5 py-2.5 rounded-lg text-xs font-medium text-slate-600 hover:text-red-600 hover:bg-red-50 transition-colors"
        >
          <LogOut className="w-4 h-4 text-slate-400 group-hover:text-red-500" />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}
