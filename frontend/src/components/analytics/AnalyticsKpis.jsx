import React from 'react';
import { Database, Repeat, Flame, ShieldAlert } from 'lucide-react';

export function AnalyticsKpis({ kpis }) {
  if (!kpis) return null;

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
        <div className="p-3 rounded-lg bg-brand-50 text-brand-600">
          <Database className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Total Analyzed</p>
          <h3 className="text-xl font-bold text-slate-900">{kpis.total_defects_analyzed}</h3>
          <p className="text-[10px] text-slate-400">Scoped across filters</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
        <div className="p-3 rounded-lg bg-amber-50 text-amber-600">
          <Repeat className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Recurrence Rate</p>
          <h3 className="text-xl font-bold text-slate-900">{kpis.recurring_pattern_rate}%</h3>
          <p className="text-[10px] text-emerald-600 font-medium">Bugs matching known pattern</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
        <div className="p-3 rounded-lg bg-red-50 text-red-600">
          <Flame className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Top Hotspot</p>
          <h3 className="text-base font-bold text-slate-900 truncate max-w-[140px]" title={kpis.top_affected_component}>
            {kpis.top_affected_component}
          </h3>
          <p className="text-[10px] text-slate-400">Most frequent locus</p>
        </div>
      </div>

      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm flex items-center space-x-3">
        <div className="p-3 rounded-lg bg-purple-50 text-purple-600">
          <ShieldAlert className="w-5 h-5" />
        </div>
        <div>
          <p className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">Critical / High</p>
          <h3 className="text-xl font-bold text-slate-900">{kpis.critical_high_percentage}%</h3>
          <p className="text-[10px] text-slate-400">High severity share</p>
        </div>
      </div>
    </div>
  );
}
