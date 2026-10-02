import React from 'react';
import { TrendingUp } from 'lucide-react';

export function TimeTrends({ timeTrends }) {
  if (!timeTrends) return null;

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <TrendingUp className="w-4 h-4 text-brand-600" />
            Temporal Defect Frequency & Velocity
          </h4>
          <p className="text-[11px] text-slate-500">Chronological defect volume tracking over time.</p>
        </div>

        <div className="flex items-center space-x-2 text-xs">
          <span className="font-semibold text-slate-600">Trend Status:</span>
          <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
            timeTrends.trend_direction === 'Increasing'
              ? 'bg-red-100 text-red-800'
              : timeTrends.trend_direction === 'Decreasing'
              ? 'bg-emerald-100 text-emerald-800'
              : 'bg-blue-100 text-blue-800'
          }`}>
            {timeTrends.trend_direction} ({timeTrends.velocity_percentage > 0 ? '+' : ''}{timeTrends.velocity_percentage}%)
          </span>
        </div>
      </div>

      <div className="space-y-2">
        {timeTrends.timeline && timeTrends.timeline.length > 0 ? (
          timeTrends.timeline.map((point) => (
            <div key={point.period} className="flex items-center justify-between p-2.5 bg-slate-50 rounded-lg text-xs">
              <div className="flex items-center space-x-3">
                <span className="font-mono font-bold text-slate-700">{point.period}</span>
                <span className="text-slate-600">Top Component: <strong>{point.top_component || 'N/A'}</strong></span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="font-semibold text-slate-800">{point.total_count} defects</span>
                {point.critical_count > 0 && (
                  <span className="px-1.5 py-0.5 rounded text-[10px] font-bold bg-red-100 text-red-700">
                    {point.critical_count} Critical
                  </span>
                )}
              </div>
            </div>
          ))
        ) : (
          <p className="text-xs text-slate-500 py-4 text-center">No timeline data available for selected filters.</p>
        )}
      </div>
    </div>
  );
}
