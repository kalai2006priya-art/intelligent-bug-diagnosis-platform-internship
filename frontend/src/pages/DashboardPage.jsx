import React, { useState, useEffect } from 'react';
import { PlusCircle, FileText, CheckCircle, Clock, ChevronRight, Loader2 } from 'lucide-react';
import { bugsApi } from '../api/bugs';
import { useAuth } from '../context/AuthContext';
import { StatusBadge } from '../components/StatusBadge';
import { EmptyState } from '../components/EmptyState';

export function DashboardPage({ setCurrentRoute, setSelectedBugId }) {
  const { user } = useAuth();
  const [stats, setStats] = useState({ total_bugs: 0, diagnosed_bugs: 0, pending_analysis: 0 });
  const [recentBugs, setRecentBugs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsData, bugsList] = await Promise.all([
          bugsApi.getBugStats(),
          bugsApi.listBugs(0, 5)
        ]);
        setStats(statsData);
        setRecentBugs(bugsList);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const handleOpenReport = (bugId) => {
    setSelectedBugId(bugId);
    setCurrentRoute('diagnosis-report');
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin mb-2" />
        <p className="text-xs text-slate-500">Loading developer dashboard...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div>
          <h1 className="text-lg font-bold text-slate-900">
            Welcome back, {user?.name || 'Developer'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Diagnose software defects, analyze stack traces, and retrieve historical fixes.
          </p>
        </div>
        <button
          onClick={() => setCurrentRoute('submit-bug')}
          className="inline-flex items-center space-x-2 bg-brand-600 hover:bg-brand-700 text-white text-xs font-semibold px-4 py-2.5 rounded-lg shadow-sm transition-colors"
        >
          <PlusCircle className="w-4 h-4" />
          <span>Submit Bug</span>
        </button>
      </div>

      {/* Real Statistics Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="w-10 h-10 rounded-lg bg-sky-50 text-brand-600 flex items-center justify-center">
            <FileText className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{stats.total_bugs}</div>
            <div className="text-xs text-slate-500 font-medium">Total Bugs Submitted</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="w-10 h-10 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <CheckCircle className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{stats.diagnosed_bugs}</div>
            <div className="text-xs text-slate-500 font-medium">Bugs Analyzed & Diagnosed</div>
          </div>
        </div>

        <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center space-x-4">
          <div className="w-10 h-10 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{stats.pending_analysis}</div>
            <div className="text-xs text-slate-500 font-medium">Pending Analysis</div>
          </div>
        </div>
      </div>

      {/* Recent Bug Reports */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-sm font-bold text-slate-900">Recent Bug Reports</h2>
          {recentBugs.length > 0 && (
            <button
              onClick={() => setCurrentRoute('bug-history')}
              className="text-xs font-semibold text-brand-600 hover:text-brand-700 flex items-center space-x-1"
            >
              <span>View All</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          )}
        </div>

        {recentBugs.length === 0 ? (
          <div className="p-6">
            <EmptyState
              title="No bug submissions yet"
              description="Submit your first bug report with description or stack trace to start multi-agent diagnosis."
              actionButton={
                <button
                  onClick={() => setCurrentRoute('submit-bug')}
                  className="inline-flex items-center space-x-1.5 text-xs font-semibold text-white bg-brand-600 hover:bg-brand-700 px-3 py-2 rounded-lg"
                >
                  <PlusCircle className="w-3.5 h-3.5" />
                  <span>Submit Bug</span>
                </button>
              }
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-50 border-b border-slate-100 text-slate-500 font-semibold">
                <tr>
                  <th className="px-6 py-3">Bug ID</th>
                  <th className="px-6 py-3">Title</th>
                  <th className="px-6 py-3">Component</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Submitted</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {recentBugs.map((bug) => (
                  <tr key={bug.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-slate-500">{bug.id.slice(0, 8)}</td>
                    <td className="px-6 py-3.5 font-medium text-slate-900 max-w-xs truncate">
                      {bug.title}
                    </td>
                    <td className="px-6 py-3.5 text-slate-600">
                      {bug.component || <span className="text-slate-400 italic">Unspecified</span>}
                    </td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={bug.status} />
                    </td>
                    <td className="px-6 py-3.5 text-slate-500">
                      {new Date(bug.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      {bug.status === 'Diagnosed' ? (
                        <button
                          onClick={() => handleOpenReport(bug.id)}
                          className="text-xs font-semibold text-brand-600 hover:text-brand-800"
                        >
                          View Report
                        </button>
                      ) : (
                        <button
                          onClick={() => handleOpenReport(bug.id)}
                          className="text-xs font-semibold text-sky-600 hover:text-sky-800"
                        >
                          Analyze Bug
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
