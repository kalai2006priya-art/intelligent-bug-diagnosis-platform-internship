import React from 'react';
import { ShieldAlert, Layers, Flame } from 'lucide-react';

export function ComponentHotspots({ hotspots, severityDist, priorityDist }) {
  const getRiskBadge = (risk) => {
    switch (risk?.toLowerCase()) {
      case 'high':
        return 'bg-red-100 text-red-800 border-red-200';
      case 'medium':
        return 'bg-amber-100 text-amber-800 border-amber-200';
      default:
        return 'bg-emerald-100 text-emerald-800 border-emerald-200';
    }
  };

  return (
    <div className="space-y-6">
      {/* Distributions Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Severity Breakdown */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <ShieldAlert className="w-4 h-4 text-brand-600" />
            Severity Distribution
          </h4>
          <div className="space-y-2.5">
            {severityDist.map((item) => (
              <div key={item.category} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-slate-700">{item.category}</span>
                  <span className="text-slate-500">{item.count} defects ({item.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.category === 'Critical'
                        ? 'bg-red-500'
                        : item.category === 'High'
                        ? 'bg-amber-500'
                        : item.category === 'Medium'
                        ? 'bg-blue-500'
                        : 'bg-slate-400'
                    }`}
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Priority Breakdown */}
        <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm">
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider mb-3 flex items-center gap-1.5">
            <Layers className="w-4 h-4 text-brand-600" />
            Priority Distribution
          </h4>
          <div className="space-y-2.5">
            {priorityDist.map((item) => (
              <div key={item.category} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-medium text-slate-700">{item.category}</span>
                  <span className="text-slate-500">{item.count} defects ({item.percentage}%)</span>
                </div>
                <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      item.category === 'Critical'
                        ? 'bg-red-500'
                        : item.category === 'High'
                        ? 'bg-amber-500'
                        : item.category === 'Medium'
                        ? 'bg-blue-500'
                        : 'bg-slate-400'
                    }`}
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Component Hotspots Table */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
              <Flame className="w-4 h-4 text-red-500" />
              Component Hotspots & Failure Density
            </h4>
            <p className="text-[11px] text-slate-500">Modules repeatedly affected by defects requiring architectural review.</p>
          </div>
          <span className="text-xs font-semibold px-2 py-0.5 rounded bg-slate-100 text-slate-600">
            {hotspots.length} Components
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-50 border-y border-slate-200 text-slate-600 uppercase font-semibold text-[10px]">
              <tr>
                <th className="py-2.5 px-3">Component</th>
                <th className="py-2.5 px-3">Defects</th>
                <th className="py-2.5 px-3">% of Total</th>
                <th className="py-2.5 px-3">Critical / High</th>
                <th className="py-2.5 px-3">Recurrence</th>
                <th className="py-2.5 px-3">Top Exceptions</th>
                <th className="py-2.5 px-3">Risk Level</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {hotspots.map((h) => (
                <tr key={h.component} className="hover:bg-slate-50 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-slate-800">{h.component}</td>
                  <td className="py-2.5 px-3">{h.defect_count}</td>
                  <td className="py-2.5 px-3">{h.percentage_of_total}%</td>
                  <td className="py-2.5 px-3">
                    <span className="text-red-600 font-bold">{h.critical_count}</span> /{' '}
                    <span className="text-amber-600 font-semibold">{h.high_count}</span>
                  </td>
                  <td className="py-2.5 px-3">{h.recurrence_rate}%</td>
                  <td className="py-2.5 px-3 text-slate-600 max-w-xs truncate">
                    {h.top_exceptions && h.top_exceptions.length > 0 ? h.top_exceptions.join(', ') : 'None extracted'}
                  </td>
                  <td className="py-2.5 px-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getRiskBadge(h.risk_level)}`}>
                      {h.risk_level} Risk
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
