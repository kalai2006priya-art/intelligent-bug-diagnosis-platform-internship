import React from 'react';
import { CheckCircle2, Circle, Loader2 } from 'lucide-react';

export const ORCHESTRATION_STAGES = [
  { key: 'triage', label: 'Running Triage Analysis (Severity & Priority)' },
  { key: 'logs', label: 'Analyzing Runtime Logs & Stack Traces' },
  { key: 'rag', label: 'Searching Historical Defect Knowledge Base (RAG)' },
  { key: 'root_cause', label: 'Synthesizing Probable Root Cause Hypothesis' },
  { key: 'duplicates', label: 'Evaluating Historical Duplicate Defect Matches' },
  { key: 'remediation', label: 'Generating Actionable Remediation & Validations' },
  { key: 'ready', label: 'Diagnosis Report Ready' }
];

export function ProgressTracker({ currentStageIndex = 0, isComplete = false, error = null }) {
  return (
    <div className="bg-slate-900 text-slate-100 rounded-xl p-6 border border-slate-800 shadow-xl max-w-xl mx-auto my-6">
      <div className="flex items-center justify-between pb-4 mb-4 border-b border-slate-800">
        <div>
          <h3 className="text-sm font-semibold text-white">Agent Orchestration Pipeline</h3>
          <p className="text-xs text-slate-400">Coordinating multi-agent diagnosis across historical defect knowledge</p>
        </div>
        {!isComplete && !error && (
          <span className="flex items-center text-xs text-sky-400 font-mono">
            <Loader2 className="w-4 h-4 mr-1.5 animate-spin" />
            Stage {Math.min(currentStageIndex + 1, ORCHESTRATION_STAGES.length)} of {ORCHESTRATION_STAGES.length}
          </span>
        )}
      </div>

      <div className="space-y-3">
        {ORCHESTRATION_STAGES.map((stage, idx) => {
          let status = 'pending';
          if (isComplete || idx < currentStageIndex) {
            status = 'done';
          } else if (idx === currentStageIndex) {
            status = error ? 'error' : 'running';
          }

          return (
            <div key={stage.key} className="flex items-center text-xs">
              <div className="w-6 flex items-center justify-center mr-3">
                {status === 'done' ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                ) : status === 'running' ? (
                  <Loader2 className="w-4 h-4 text-sky-400 animate-spin" />
                ) : (
                  <Circle className="w-3 h-3 text-slate-600" />
                )}
              </div>
              <span className={`font-mono transition-colors ${
                status === 'done' ? 'text-slate-300' :
                status === 'running' ? 'text-sky-300 font-medium' :
                'text-slate-500'
              }`}>
                {stage.label}
              </span>
            </div>
          );
        })}
      </div>

      {error && (
        <div className="mt-4 p-3 rounded bg-red-950/50 border border-red-800/60 text-xs text-red-200">
          <strong>Pipeline Exception:</strong> {error}
        </div>
      )}
    </div>
  );
}
