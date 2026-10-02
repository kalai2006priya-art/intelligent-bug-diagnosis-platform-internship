import React, { useState } from 'react';
import { 
  Sparkles, CheckCircle2, AlertTriangle, ShieldCheck, Database, 
  Code, ArrowRight, Loader2, Check 
} from 'lucide-react';
import { growthApi } from '../../api/growth';

export function ResolutionPromotionCard({ bug, diagnosis, onPromoted }) {
  const [resolutionNotes, setResolutionNotes] = useState(bug.resolution_notes || '');
  const [fixCode, setFixCode] = useState(bug.confirmed_fix_code || '');
  const [loading, setLoading] = useState(false);
  const [validating, setValidating] = useState(false);
  const [gateResult, setGateResult] = useState(null);
  const [error, setError] = useState(null);
  const [successMsg, setSuccessMsg] = useState(null);

  const isAlreadyIndexed = bug.indexed_in_kb;

  const handleValidate = async () => {
    setValidating(true);
    setError(null);
    try {
      const res = await growthApi.validateQualityGate(bug.id);
      setGateResult(res);
    } catch (err) {
      setError(err.message || 'Validation failed.');
    } finally {
      setValidating(false);
    }
  };

  const handlePromote = async (e) => {
    e.preventDefault();
    if (!resolutionNotes.trim()) {
      setError('Please provide resolution notes before indexing.');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const payload = {
        resolution_notes: resolutionNotes,
        confirmed_fix_code: fixCode || undefined,
        component: bug.component || undefined
      };
      const res = await growthApi.promoteToKnowledgeBase(bug.id, payload);
      setSuccessMsg(res.message || 'Defect successfully indexed into Knowledge Base!');
      if (onPromoted) onPromoted(res);
    } catch (err) {
      setError(err.message || 'Promotion to Knowledge Base failed.');
    } finally {
      setLoading(false);
    }
  };

  if (isAlreadyIndexed) {
    return (
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-5 shadow-sm space-y-2">
        <div className="flex items-center space-x-2 text-emerald-800 font-bold text-sm">
          <CheckCircle2 className="w-5 h-5 text-emerald-600 shrink-0" />
          <span>Permanently Indexed in Historical Defect Knowledge Base (M4.2)</span>
        </div>
        <p className="text-xs text-emerald-700 leading-relaxed">
          This verified resolution and code patch have been vectorized with 384-dimensional embeddings and indexed into ChromaDB.
          It now actively serves as empirical precedent for future Root Cause, Duplicate Detection, and Remediation diagnoses.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white border border-brand-200 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2 pb-3 border-b border-slate-100">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-brand-100 text-brand-800">
              Milestone 4.2
            </span>
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-1.5">
              <Database className="w-4 h-4 text-brand-600" />
              Contribute Verified Fix to AI Knowledge Base
            </h3>
          </div>
          <p className="text-xs text-slate-500 mt-0.5">
            Close the continuous learning feedback loop by saving and indexing your verified fix.
          </p>
        </div>

        <button
          type="button"
          onClick={handleValidate}
          disabled={validating}
          className="inline-flex items-center space-x-1.5 text-xs font-semibold px-3 py-1.5 rounded-lg border border-slate-300 text-slate-700 bg-slate-50 hover:bg-slate-100 transition-colors shrink-0"
        >
          {validating ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />}
          <span>Verify Quality Gate</span>
        </button>
      </div>

      {/* Quality Gate Checklist Display */}
      {gateResult && (
        <div className="p-3 bg-slate-50 rounded-lg border border-slate-200 space-y-2 text-xs">
          <div className="flex items-center justify-between">
            <span className="font-bold text-slate-700 uppercase text-[10px]">
              Quality Gate Audit (Score: {Math.round(gateResult.quality_score * 100)}%)
            </span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
              gateResult.is_eligible ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
            }`}>
              {gateResult.is_eligible ? 'Eligible for Indexing' : 'Action Required'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
            {gateResult.criteria.map((c, i) => (
              <div key={i} className="flex items-start space-x-1.5 text-[11px]">
                {c.status === 'Passed' ? (
                  <Check className="w-3.5 h-3.5 text-emerald-600 mt-0.5 shrink-0" />
                ) : (
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-500 mt-0.5 shrink-0" />
                )}
                <div>
                  <strong className="text-slate-800">{c.criterion}:</strong>{' '}
                  <span className="text-slate-600">{c.details}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-emerald-700 text-xs flex items-center space-x-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Resolution Input Form */}
      <form onSubmit={handlePromote} className="space-y-3">
        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1">
            Confirmed Resolution Notes & Fix Rationale <span className="text-red-500">*</span>
          </label>
          <textarea
            value={resolutionNotes}
            onChange={(e) => setResolutionNotes(e.target.value)}
            rows={2}
            placeholder="Explain the verified fix (e.g. Added null safety precondition in LoginService.java line 42 to avoid dereferencing uninitialized token)..."
            className="w-full text-xs p-2.5 border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-500 text-slate-800 bg-white"
            required
          />
        </div>

        <div>
          <label className="block text-xs font-semibold text-slate-700 mb-1 flex items-center gap-1.5">
            <Code className="w-3.5 h-3.5 text-brand-600" />
            <span>Confirmed Code Patch / Implementation (Optional but Recommended)</span>
          </label>
          <textarea
            value={fixCode}
            onChange={(e) => setFixCode(e.target.value)}
            rows={3}
            placeholder="// Paste the verified code patch or configuration change here..."
            className="w-full text-xs font-mono p-2.5 border border-slate-300 rounded-lg focus:ring-1 focus:ring-brand-500 text-slate-800 bg-slate-50"
          />
        </div>

        <div className="pt-2 flex justify-end">
          <button
            type="submit"
            disabled={loading}
            className="inline-flex items-center space-x-2 px-4 py-2 bg-brand-600 hover:bg-brand-700 text-white rounded-lg text-xs font-semibold shadow-sm transition-all disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="w-3.5 h-3.5 animate-spin" />
                <span>Vectorizing & Indexing into ChromaDB...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Validate, Embed & Promote to Knowledge Base</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
}
