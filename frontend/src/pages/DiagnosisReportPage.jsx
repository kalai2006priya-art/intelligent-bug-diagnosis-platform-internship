import React, { useState, useEffect } from 'react';
import { 
  ArrowLeft, Bug, ShieldAlert, Terminal, Layers, Search, Wrench, 
  CheckCircle2, AlertTriangle, HelpCircle, Copy, Check, FileCode, Clock
} from 'lucide-react';
import { bugsApi } from '../api/bugs';
import { StatusBadge } from '../components/StatusBadge';
import { ProgressTracker } from '../components/ProgressTracker';

export function DiagnosisReportPage({ bugId, setCurrentRoute }) {
  const [bug, setBug] = useState(null);
  const [diagnosis, setDiagnosis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [analysisStage, setAnalysisStage] = useState(0);
  const [copiedCodeIdx, setCopiedCodeIdx] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!bugId) return;

    const fetchReport = async () => {
      setLoading(true);
      setError(null);
      try {
        const bugData = await bugsApi.getBug(bugId);
        setBug(bugData);

        try {
          const diagData = await bugsApi.getDiagnosis(bugId);
          setDiagnosis(diagData);
        } catch (diagErr) {
          // If no diagnosis exists yet, we offer the "Run Diagnosis" action
          setDiagnosis(null);
        }
      } catch (err) {
        setError(err.message || 'Failed to load defect details.');
      } finally {
        setLoading(false);
      }
    };

    fetchReport();
  }, [bugId]);

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    setAnalysisStage(0);
    setError(null);

    const interval = setInterval(() => {
      setAnalysisStage((prev) => (prev < 5 ? prev + 1 : prev));
    }, 700);

    try {
      const newDiag = await bugsApi.analyzeBug(bugId);
      clearInterval(interval);
      setAnalysisStage(6);
      setTimeout(() => {
        setDiagnosis(newDiag);
        setBug((prev) => ({ ...prev, status: 'Diagnosed', has_diagnosis: true }));
        setAnalyzing(false);
      }, 800);
    } catch (err) {
      clearInterval(interval);
      setError(err.message || 'Failed to execute diagnosis pipeline.');
      setAnalyzing(false);
    }
  };

  const copyToClipboard = (text, idx) => {
    navigator.clipboard.writeText(text);
    setCopiedCodeIdx(idx);
    setTimeout(() => setCopiedCodeIdx(null), 2000);
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <div className="w-8 h-8 border-2 border-brand-600 border-t-transparent rounded-full animate-spin mb-2"></div>
        <p className="text-xs text-slate-500">Loading diagnostic findings...</p>
      </div>
    );
  }

  if (error || !bug) {
    return (
      <div className="max-w-2xl mx-auto my-12 p-6 bg-white border border-red-200 rounded-xl text-center shadow-sm">
        <AlertTriangle className="w-8 h-8 text-red-500 mx-auto mb-2" />
        <h2 className="text-sm font-bold text-slate-900">Diagnosis Report Unavailable</h2>
        <p className="text-xs text-slate-500 mt-1 mb-4">{error || 'Bug report not found.'}</p>
        <button
          onClick={() => setCurrentRoute('bug-history')}
          className="text-xs font-semibold text-brand-600 hover:text-brand-800"
        >
          &larr; Back to Bug History
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Back button & Report Header */}
      <div>
        <button
          onClick={() => setCurrentRoute('bug-history')}
          className="inline-flex items-center space-x-1.5 text-xs font-semibold text-slate-500 hover:text-slate-800 mb-3"
        >
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Back to Defect Submissions</span>
        </button>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <div className="flex items-center space-x-2.5">
              <h1 className="text-lg font-bold text-slate-900">Bug Diagnosis Report</h1>
              <StatusBadge status={bug.status} />
              {diagnosis && (
                <span className="text-[11px] font-mono px-2 py-0.5 rounded bg-slate-100 text-slate-600 border border-slate-200">
                  Confidence: {Math.round(diagnosis.overall_confidence * 100)}%
                </span>
              )}
            </div>
            <div className="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 mt-1.5">
              <span><strong>Bug ID:</strong> <code className="text-slate-700">{bug.id}</code></span>
              <span><strong>Submitted:</strong> {new Date(bug.created_at).toLocaleString()}</span>
              {bug.component && <span><strong>Component:</strong> {bug.component}</span>}
            </div>
          </div>

          {!diagnosis && !analyzing && (
            <button
              onClick={handleRunAnalysis}
              className="inline-flex items-center space-x-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition-colors"
            >
              <Bug className="w-4 h-4" />
              <span>Run Multi-Agent Diagnosis</span>
            </button>
          )}
        </div>
      </div>

      {analyzing && (
        <ProgressTracker
          currentStageIndex={analysisStage}
          isComplete={false}
          error={null}
        />
      )}

      {/* ========================================================================= */}
      {/* SECTION 1: ORIGINAL BUG (USER INPUT) */}
      {/* ========================================================================= */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <span className="w-6 h-6 rounded-full bg-slate-200 text-slate-700 text-xs font-bold flex items-center justify-center">1</span>
            <h2 className="text-sm font-bold text-slate-900">Original Bug Information</h2>
          </div>
          <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400 bg-white px-2 py-0.5 rounded border border-slate-200">
            User-Submitted Input
          </span>
        </div>

        <div className="p-6 space-y-4">
          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Title</h3>
            <p className="text-sm font-medium text-slate-900 mt-0.5">{bug.title}</p>
          </div>

          <div>
            <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Description</h3>
            <p className="text-xs text-slate-700 mt-0.5 whitespace-pre-wrap leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200/60">
              {bug.description}
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Component</h3>
              <p className="text-xs text-slate-800 mt-0.5">{bug.component || 'Unspecified by user'}</p>
            </div>
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Environment</h3>
              <p className="text-xs text-slate-800 mt-0.5">{bug.environment || 'Unspecified'}</p>
            </div>
          </div>

          {bug.stack_trace && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Submitted Stack Trace</h3>
              <pre className="p-3 bg-slate-900 text-slate-100 rounded-lg text-xs font-mono overflow-x-auto border border-slate-800">
                {bug.stack_trace}
              </pre>
            </div>
          )}

          {bug.error_logs && (
            <div>
              <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Submitted Error Logs</h3>
              <pre className="p-3 bg-slate-900 text-slate-100 rounded-lg text-xs font-mono overflow-x-auto border border-slate-800">
                {bug.error_logs}
              </pre>
            </div>
          )}
        </div>
      </div>

      {/* If diagnosis is ready, display Sections 2 through 6 */}
      {diagnosis && (
        <>
          {/* ========================================================================= */}
          {/* SECTION 2: TRIAGE ANALYSIS */}
          {/* ========================================================================= */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">2</span>
                <h2 className="text-sm font-bold text-slate-900">Triage Agent Analysis</h2>
              </div>
              <span className="text-[11px] font-semibold uppercase tracking-wider text-brand-600 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                Agent Classification
              </span>
            </div>

            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">Severity</div>
                  <div className="mt-1">
                    <StatusBadge status={diagnosis.triage.severity} type="severity" />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">Priority</div>
                  <div className="mt-1">
                    <StatusBadge status={diagnosis.triage.priority} type="severity" />
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">Affected Component</div>
                  <div className="mt-1 text-xs font-semibold text-slate-900 truncate">
                    {diagnosis.triage.affected_component}
                  </div>
                </div>

                <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                  <div className="text-[11px] font-semibold text-slate-500 uppercase">Confidence</div>
                  <div className="mt-1 text-xs font-mono font-bold text-brand-700">
                    {Math.round(diagnosis.triage.confidence * 100)}%
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Triage Reasoning</h3>
                <p className="text-xs text-slate-700 mt-1 leading-relaxed bg-brand-50/30 p-3 rounded-lg border border-brand-100">
                  {diagnosis.triage.reasoning}
                </p>
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* SECTION 3: LOG ANALYSIS */}
          {/* ========================================================================= */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">3</span>
                <h2 className="text-sm font-bold text-slate-900">Log Analysis Agent</h2>
              </div>
              <span className="text-[11px] font-semibold uppercase tracking-wider text-brand-600 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                Stack & Trace Parser
              </span>
            </div>

            <div className="p-6 space-y-4">
              {diagnosis.log_analysis.status === 'Insufficient Evidence' ? (
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-xs text-slate-600">
                  <strong>Insufficient Evidence:</strong> {diagnosis.log_analysis.error_message}
                </div>
              ) : (
                <>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                      <div className="text-[11px] font-semibold text-slate-500 uppercase">Exception Type</div>
                      <div className="mt-1 font-mono text-xs font-bold text-red-600">
                        {diagnosis.log_analysis.exception_type || 'N/A'}
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                      <div className="text-[11px] font-semibold text-slate-500 uppercase">Failure Point</div>
                      <div className="mt-1 font-mono text-xs font-semibold text-slate-900">
                        {diagnosis.log_analysis.failure_point || 'Unknown'}
                      </div>
                    </div>

                    <div className="p-3 rounded-lg bg-slate-50 border border-slate-200/80">
                      <div className="text-[11px] font-semibold text-slate-500 uppercase">Parser Confidence</div>
                      <div className="mt-1 font-mono text-xs font-bold text-brand-700">
                        {Math.round(diagnosis.log_analysis.confidence * 100)}%
                      </div>
                    </div>
                  </div>

                  {diagnosis.log_analysis.affected_code_path && (
                    <div>
                      <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-1">Affected Call Hierarchy</h3>
                      <div className="p-2.5 bg-slate-900 text-sky-300 font-mono text-xs rounded-lg border border-slate-800 overflow-x-auto">
                        {diagnosis.log_analysis.affected_code_path}
                      </div>
                    </div>
                  )}

                  <div>
                    <h3 className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Root Error Message</h3>
                    <p className="text-xs text-slate-700 mt-1 font-mono bg-slate-50 p-2.5 rounded border border-slate-200">
                      {diagnosis.log_analysis.error_message || 'None detected'}
                    </p>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* ========================================================================= */}
          {/* SECTION 4: ROOT CAUSE ANALYSIS (STRICT EVIDENCE SEPARATION) */}
          {/* ========================================================================= */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">4</span>
                <h2 className="text-sm font-bold text-slate-900">Root Cause Agent (RAG Grounded)</h2>
              </div>
              <span className="text-[11px] font-semibold uppercase tracking-wider text-brand-600 bg-brand-50 px-2 py-0.5 rounded border border-brand-200">
                Grounded Diagnosis
              </span>
            </div>

            <div className="p-6 space-y-5">
              {/* Hypothesis Block */}
              <div>
                <div className="flex items-center justify-between mb-1.5">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                    Probable Root Cause Hypothesis
                  </h3>
                  <span className="text-xs font-mono font-semibold text-slate-500">
                    Confidence: {Math.round(diagnosis.root_cause.confidence * 100)}%
                  </span>
                </div>
                <div className="p-3.5 rounded-lg bg-amber-50/60 border border-amber-200 text-xs text-amber-950 font-medium leading-relaxed">
                  {diagnosis.root_cause.root_cause_hypothesis}
                </div>
              </div>

              {/* Deductive Reasoning */}
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-1">
                  Agent Analytical Reasoning
                </h3>
                <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-200">
                  {diagnosis.root_cause.reasoning}
                </p>
              </div>

              {/* Retrieved Historical Evidence Table */}
              <div>
                <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                  Retrieved Historical Defect Evidence (Mozilla / Apache / Eclipse)
                </h3>
                {diagnosis.root_cause.supporting_evidence.length === 0 ? (
                  <p className="text-xs text-slate-500 italic">No direct historical defect precedents met the retrieval threshold.</p>
                ) : (
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                        <tr>
                          <th className="px-4 py-2.5">Historical Defect ID</th>
                          <th className="px-4 py-2.5">Source Repository</th>
                          <th className="px-4 py-2.5">Semantic Similarity</th>
                          <th className="px-4 py-2.5">Precedent Evidence</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {diagnosis.root_cause.supporting_evidence.map((item, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/60">
                            <td className="px-4 py-2.5 font-mono font-semibold text-slate-700">{item.bug_id}</td>
                            <td className="px-4 py-2.5 text-slate-600">{item.source}</td>
                            <td className="px-4 py-2.5 font-mono text-emerald-700 font-semibold">
                              {Math.round(item.similarity * 100)}%
                            </td>
                            <td className="px-4 py-2.5 text-slate-700">{item.evidence}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* ========================================================================= */}
          {/* SECTION 5: DUPLICATE DETECTION */}
          {/* ========================================================================= */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">5</span>
                <h2 className="text-sm font-bold text-slate-900">Duplicate Detection Agent</h2>
              </div>
              <StatusBadge status={diagnosis.duplicate_detection.status} type="duplicate" />
            </div>

            <div className="p-6 space-y-4">
              <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-200 leading-relaxed">
                {diagnosis.duplicate_detection.reasoning}
              </p>

              {diagnosis.duplicate_detection.matches.length > 0 && (
                <div>
                  <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
                    Top Matching Historical Issues
                  </h3>
                  <div className="border border-slate-200 rounded-lg overflow-hidden">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 border-b border-slate-200 text-slate-500 font-semibold">
                        <tr>
                          <th className="px-4 py-2.5">Bug ID</th>
                          <th className="px-4 py-2.5">Similarity</th>
                          <th className="px-4 py-2.5">Title</th>
                          <th className="px-4 py-2.5">Source</th>
                          <th className="px-4 py-2.5">Resolution Summary</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {diagnosis.duplicate_detection.matches.map((m, idx) => (
                          <tr key={idx} className="hover:bg-slate-50/60">
                            <td className="px-4 py-2.5 font-mono font-semibold text-slate-800">{m.bug_id}</td>
                            <td className="px-4 py-2.5 font-mono font-bold text-brand-700">
                              {Math.round(m.similarity * 100)}%
                            </td>
                            <td className="px-4 py-2.5 text-slate-900 font-medium">{m.title}</td>
                            <td className="px-4 py-2.5 text-slate-600">{m.source || 'Historical'}</td>
                            <td className="px-4 py-2.5 text-slate-600">{m.resolution_summary || 'N/A'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* ========================================================================= */}
          {/* SECTION 6: RECOMMENDED REMEDIATION & ACTIONABLE CODE */}
          {/* ========================================================================= */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="px-6 py-4 bg-slate-50/70 border-b border-slate-200 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-6 h-6 rounded-full bg-brand-100 text-brand-700 text-xs font-bold flex items-center justify-center">6</span>
                <h2 className="text-sm font-bold text-slate-900">Remediation Agent (Actionable Fixes)</h2>
              </div>
              <span className="text-[11px] font-semibold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200">
                Actionable Remedies
              </span>
            </div>

            <div className="p-6 space-y-6">
              {diagnosis.remediation.recommendations.map((rec, idx) => (
                <div key={idx} className="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="px-2 py-0.5 rounded text-[11px] font-semibold bg-brand-100 text-brand-800 border border-brand-200">
                        Basis: {rec.basis}
                      </span>
                      {rec.affected_module && (
                        <span className="font-mono text-xs text-slate-700">
                          {rec.affected_module}
                        </span>
                      )}
                    </div>
                    <span className="text-xs font-mono font-semibold text-slate-600">
                      Confidence: {Math.round(rec.confidence * 100)}%
                    </span>
                  </div>

                  <p className="text-xs font-semibold text-slate-900 leading-relaxed">
                    {rec.recommendation}
                  </p>

                  {rec.suggested_code && (
                    <div className="relative">
                      <div className="flex items-center justify-between px-3 py-1.5 bg-slate-800 text-slate-300 text-[11px] rounded-t-lg font-mono">
                        <span className="flex items-center space-x-1">
                          <FileCode className="w-3.5 h-3.5" />
                          <span>Suggested Code Implementation</span>
                        </span>
                        <button
                          onClick={() => copyToClipboard(rec.suggested_code, idx)}
                          className="flex items-center space-x-1 hover:text-white"
                        >
                          {copiedCodeIdx === idx ? (
                            <>
                              <Check className="w-3 h-3 text-emerald-400" />
                              <span className="text-emerald-400">Copied</span>
                            </>
                          ) : (
                            <>
                              <Copy className="w-3 h-3" />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>
                      <pre className="p-3 bg-slate-900 text-slate-100 rounded-b-lg text-xs font-mono overflow-x-auto border-x border-b border-slate-800">
                        {rec.suggested_code}
                      </pre>
                    </div>
                  )}

                  {rec.validation_steps && rec.validation_steps.length > 0 && (
                    <div className="pt-2">
                      <h4 className="text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">
                        Verification & Validation Steps
                      </h4>
                      <ul className="space-y-1">
                        {rec.validation_steps.map((step, sIdx) => (
                          <li key={sIdx} className="flex items-start text-xs text-slate-700">
                            <span className="w-1.5 h-1.5 bg-emerald-500 rounded-full mt-1.5 mr-2 flex-shrink-0"></span>
                            <span>{step}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ))}

              {diagnosis.remediation.general_guidance && (
                <div className="p-3 rounded-lg bg-white border border-slate-200 text-xs text-slate-600 leading-relaxed">
                  <strong>Architectural Guidance:</strong> {diagnosis.remediation.general_guidance}
                </div>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
