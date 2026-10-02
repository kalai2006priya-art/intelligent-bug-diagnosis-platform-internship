import React from 'react';
import { CheckCircle2, Code, AlertTriangle } from 'lucide-react';

export function RootCauseThemes({ themes }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
          <CheckCircle2 className="w-4 h-4 text-emerald-600" />
          Recurring Root Causes & Actionable Fix Themes
        </h4>
        <p className="text-[11px] text-slate-500">
          Defects classified by underlying causal mechanisms with proven remediation code patterns.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4">
        {themes.map((theme) => (
          <div key={theme.theme_id} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-start justify-between">
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-100 text-amber-800">
                    {theme.frequency} DEFECTS ({theme.percentage}%)
                  </span>
                  <h5 className="text-sm font-bold text-slate-900">{theme.theme_name}</h5>
                </div>
                <p className="text-xs text-slate-600">{theme.description}</p>
              </div>

              <div className="text-right">
                <span className="text-[11px] text-slate-400">Affected modules:</span>
                <div className="flex gap-1 justify-end flex-wrap mt-0.5">
                  {theme.associated_components.map((comp) => (
                    <span key={comp} className="px-1.5 py-0.5 bg-slate-100 text-slate-600 rounded text-[10px] font-medium">
                      {comp}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {theme.common_remediations && theme.common_remediations.map((rem, idx) => (
              <div key={idx} className="bg-slate-50 border border-slate-200 rounded-lg p-3 space-y-2 text-xs">
                <div className="flex items-center space-x-1.5 font-bold text-brand-800">
                  <Code className="w-3.5 h-3.5" />
                  <span>Recommended Fix Pattern: {rem.pattern_title}</span>
                </div>
                <p className="text-slate-600 text-xs">{rem.recommended_action}</p>
                {rem.example_code_snippet && (
                  <pre className="bg-slate-900 text-slate-100 p-2.5 rounded font-mono text-[11px] overflow-x-auto">
                    {rem.example_code_snippet}
                  </pre>
                )}
              </div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}

export function ExceptionSignatures({ exceptions }) {
  return (
    <div className="space-y-4">
      <div>
        <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
          <AlertTriangle className="w-4 h-4 text-amber-500" />
          Recurring Exception Types & Stack Trace Patterns
        </h4>
        <p className="text-[11px] text-slate-500">
          Prevalent runtime exceptions and corresponding failure points.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {exceptions.map((exc) => (
          <div key={exc.exception_type} className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
            <div className="flex items-start justify-between">
              <div>
                <h5 className="text-sm font-bold text-red-600 font-mono">{exc.exception_type}</h5>
                <p className="text-xs text-slate-500 mt-0.5">
                  {exc.occurrence_count} occurrences ({exc.percentage}% of analyzed defects)
                </p>
              </div>
              <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-slate-100 text-slate-700">
                Top Error Pattern
              </span>
            </div>

            {exc.sample_failure_points && exc.sample_failure_points.length > 0 && (
              <div className="space-y-1">
                <span className="text-[11px] font-bold text-slate-600 uppercase">Frequent Failure Points:</span>
                <div className="space-y-1">
                  {exc.sample_failure_points.map((fp, i) => (
                    <div key={i} className="text-xs font-mono bg-slate-100 px-2 py-1 rounded text-slate-800">
                      {fp}
                    </div>
                  ))}
                </div>
              </div>
            )}

            <div className="pt-2 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
              <span>Affected: {exc.affected_components.join(', ')}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
