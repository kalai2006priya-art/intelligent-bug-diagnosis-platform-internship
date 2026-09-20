import React from 'react';

export function StatusBadge({ status, type = 'status' }) {
  if (!status) return null;

  const val = status.toLowerCase();

  // Severity styles
  if (type === 'severity') {
    if (val === 'critical') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-red-100 text-red-800 border border-red-200">Critical</span>;
    }
    if (val === 'high') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-semibold bg-orange-100 text-orange-800 border border-orange-200">High</span>;
    }
    if (val === 'medium') {
      return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-amber-100 text-amber-800 border border-amber-200">Medium</span>;
    }
    return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">Low</span>;
  }

  // Duplicate status styles
  if (type === 'duplicate') {
    if (val.includes('likely duplicate')) {
      return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-100 text-rose-800 border border-rose-200">Likely Duplicate</span>;
    }
    if (val.includes('related')) {
      return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-100 text-amber-800 border border-amber-200">Related Issue</span>;
    }
    if (val.includes('insufficient')) {
      return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-300">Insufficient Evidence</span>;
    }
    return <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-100 text-emerald-800 border border-emerald-200">New / Unmatched</span>;
  }

  // General Bug status styles
  if (val === 'diagnosed' || val === 'completed') {
    return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">Diagnosed</span>;
  }
  if (val === 'analyzing') {
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-sky-50 text-sky-700 border border-sky-200 animate-pulse">
        <span className="w-1.5 h-1.5 mr-1.5 bg-sky-500 rounded-full animate-ping"></span>
        Analyzing
      </span>
    );
  }
  return <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-slate-100 text-slate-600 border border-slate-200">Submitted</span>;
}
