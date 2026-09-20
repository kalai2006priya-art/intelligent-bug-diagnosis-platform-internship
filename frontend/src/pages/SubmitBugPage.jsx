import React, { useState, useRef } from 'react';
import { Upload, FileText, AlertCircle, Sparkles, Check, ArrowRight } from 'lucide-react';
import { bugsApi } from '../api/bugs';
import { ProgressTracker } from '../components/ProgressTracker';

export function SubmitBugPage({ setCurrentRoute, setSelectedBugId }) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [component, setComponent] = useState('');
  const [environment, setEnvironment] = useState('');
  const [stackTrace, setStackTrace] = useState('');
  const [errorLogs, setErrorLogs] = useState('');

  const [uploadingFile, setUploadingFile] = useState(false);
  const [uploadedFileName, setUploadedFileName] = useState(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);

  const [submitting, setSubmitting] = useState(false);
  const [currentStageIndex, setCurrentStageIndex] = useState(0);
  const [isComplete, setIsComplete] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const fileInputRef = useRef(null);

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setUploadingFile(true);
    setErrorMessage(null);
    setUploadSuccess(false);

    try {
      const parsed = await bugsApi.uploadLogFile(file);
      setUploadedFileName(parsed.filename);
      setUploadSuccess(true);
      // Populate fields automatically if currently empty
      if (!title) setTitle(parsed.title);
      if (!description) setDescription(parsed.description);
      if (parsed.stack_trace) setStackTrace(parsed.stack_trace);
      if (parsed.error_logs) setErrorLogs(parsed.error_logs);
    } catch (err) {
      setErrorMessage(`Upload error: ${err.message}`);
    } finally {
      setUploadingFile(false);
    }
  };

  const handleSubmitAndAnalyze = async (e) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!title.trim()) {
      setErrorMessage('Please provide a descriptive bug title.');
      return;
    }
    if (!description.trim() || description.length < 10) {
      setErrorMessage('Please provide a defect description of at least 10 characters.');
      return;
    }

    setSubmitting(true);
    setCurrentStageIndex(0);
    setIsComplete(false);

    try {
      // 1. Create bug record
      const bug = await bugsApi.createBug({
        title: title.trim(),
        description: description.trim(),
        stack_trace: stackTrace.trim() || null,
        error_logs: errorLogs.trim() || null,
        component: component.trim() || null,
        environment: environment.trim() || null,
      });

      // Animate stages smoothly while backend runs pipeline
      const interval = setInterval(() => {
        setCurrentStageIndex((prev) => (prev < 5 ? prev + 1 : prev));
      }, 700);

      // 2. Trigger 5-agent orchestration pipeline
      const diagnosis = await bugsApi.analyzeBug(bug.id);

      clearInterval(interval);
      setCurrentStageIndex(6); // Diagnosis ready
      setIsComplete(true);

      // Brief delay so user sees "Diagnosis Report Ready" checkmark
      setTimeout(() => {
        setSelectedBugId(bug.id);
        setCurrentRoute('diagnosis-report');
      }, 1000);

    } catch (err) {
      setErrorMessage(err.message || 'Diagnosis pipeline failed.');
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h1 className="text-lg font-bold text-slate-900">Submit Software Defect</h1>
        <p className="text-xs text-slate-500 mt-1">
          Provide issue symptoms, stack traces, and error logs for automated multi-agent diagnosis.
        </p>
      </div>

      {submitting ? (
        <ProgressTracker
          currentStageIndex={currentStageIndex}
          isComplete={isComplete}
          error={errorMessage}
        />
      ) : (
        <form onSubmit={handleSubmitAndAnalyze} className="space-y-6">
          {errorMessage && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2 text-xs text-red-700">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Section 1: Bug Information */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">1. Bug Information</h2>
            
            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Bug Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Login fails with NullPointerException during session initialization"
                className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">
                Bug Description <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={4}
                required
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Describe what occurred, steps to reproduce, and observed behavior vs expected behavior..."
                className="w-full px-3 py-2 text-xs border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none"
              />
            </div>
          </div>

          {/* Section 2: Logs & Stack Traces */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-wider text-slate-500">2. Diagnostic Traces & Logs</h2>
              
              {/* File Upload Trigger */}
              <div>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept=".txt,.log"
                  onChange={handleFileUpload}
                  className="hidden"
                />
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploadingFile}
                  className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 border border-slate-300 transition-colors"
                >
                  <Upload className="w-3.5 h-3.5 text-slate-500" />
                  <span>{uploadingFile ? 'Uploading...' : 'Upload .txt or .log'}</span>
                </button>
              </div>
            </div>

            {uploadSuccess && (
              <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg flex items-center space-x-2 text-xs text-emerald-700">
                <Check className="w-4 h-4 text-emerald-600" />
                <span>Successfully parsed <strong>{uploadedFileName}</strong> into diagnosis fields.</span>
              </div>
            )}

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Stack Trace</label>
              <textarea
                rows={5}
                value={stackTrace}
                onChange={(e) => setStackTrace(e.target.value)}
                placeholder="Paste Java, Python, C++, or JS runtime stack trace here..."
                className="w-full px-3 py-2 text-xs font-mono border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none bg-slate-50/50"
              />
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-700 mb-1">Runtime / Operational Logs</label>
              <textarea
                rows={4}
                value={errorLogs}
                onChange={(e) => setErrorLogs(e.target.value)}
                placeholder="Paste surrounding application logs or error messages..."
                className="w-full px-3 py-2 text-xs font-mono border border-slate-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:outline-none bg-slate-50/50"
              />
            </div>
          </div>

          {/* Submission Action */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => setCurrentRoute('dashboard')}
              className="px-4 py-2.5 rounded-lg text-xs font-medium text-slate-600 hover:bg-slate-100 border border-slate-300 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="inline-flex items-center space-x-2 px-6 py-2.5 rounded-lg text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 shadow-sm transition-colors"
            >
              <Sparkles className="w-4 h-4" />
              <span>Submit & Analyze Bug</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
