import React, { useState, useEffect } from 'react';
import { Search, Filter, FileText, ChevronRight, Loader2, ArrowUpDown } from 'lucide-react';
import { bugsApi } from '../api/bugs';
import { StatusBadge } from '../components/StatusBadge';
import { EmptyState } from '../components/EmptyState';

export function BugHistoryPage({ setCurrentRoute, setSelectedBugId }) {
  const [bugs, setBugs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');

  useEffect(() => {
    const fetchBugs = async () => {
      try {
        const data = await bugsApi.listBugs(0, 100);
        setBugs(data);
      } catch (err) {
        console.error('Failed to list bugs:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchBugs();
  }, []);

  const handleOpenReport = (bugId) => {
    setSelectedBugId(bugId);
    setCurrentRoute('diagnosis-report');
  };

  const filteredBugs = bugs.filter((b) => {
    const matchesQuery = b.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         (b.component && b.component.toLowerCase().includes(searchQuery.toLowerCase())) ||
                         b.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'ALL' || b.status === statusFilter;
    return matchesQuery && matchesStatus;
  });

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh]">
        <Loader2 className="w-8 h-8 text-brand-600 animate-spin mb-2" />
        <p className="text-xs text-slate-500">Loading bug history...</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-lg font-bold text-slate-900">Defect Submissions History</h1>
          <p className="text-xs text-slate-500 mt-0.5">
            Audit and review previous bug reports and their multi-agent diagnostic records.
          </p>
        </div>
        <button
          onClick={() => setCurrentRoute('submit-bug')}
          className="inline-flex items-center text-xs font-semibold bg-brand-600 text-white hover:bg-brand-700 px-4 py-2 rounded-lg shadow-sm"
        >
          Submit New Bug
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center gap-3">
        <div className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by title, component, or Bug ID..."
            className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
          />
        </div>
        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="text-xs border border-slate-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            <option value="ALL">All Statuses</option>
            <option value="Diagnosed">Diagnosed</option>
            <option value="Submitted">Submitted</option>
            <option value="Analyzing">Analyzing</option>
          </select>
        </div>
      </div>

      {/* Bug Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {filteredBugs.length === 0 ? (
          <div className="p-6">
            <EmptyState
              title="No matching bug records"
              description="No defects matched your filter criteria. Try adjusting your query or submit a new bug report."
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
                  <th className="px-6 py-3">Lifecycle</th>
                  <th className="px-6 py-3">Diagnosis Status</th>
                  <th className="px-6 py-3">Submitted</th>
                  <th className="px-6 py-3 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filteredBugs.map((bug) => (
                  <tr key={bug.id} className="hover:bg-slate-50/80 transition-colors">
                    <td className="px-6 py-3.5 font-mono text-slate-500">{bug.id.slice(0, 8)}</td>
                    <td className="px-6 py-3.5 font-medium text-slate-900 max-w-sm truncate">
                      {bug.title}
                    </td>
                    <td className="px-6 py-3.5 text-slate-600">
                      {bug.component || <span className="text-slate-400 italic">Unspecified</span>}
                    </td>
                    <td className="px-6 py-3.5">
                      <StatusBadge status={bug.status} />
                    </td>
                    <td className="px-6 py-3.5">
                      {bug.has_diagnosis || bug.status === 'Diagnosed' ? (
                        <span className="inline-flex items-center text-emerald-700 text-xs font-semibold">
                          Complete
                        </span>
                      ) : (
                        <span className="text-slate-400 text-xs italic">Pending</span>
                      )}
                    </td>
                    <td className="px-6 py-3.5 text-slate-500">
                      {new Date(bug.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-3.5 text-right">
                      <button
                        onClick={() => handleOpenReport(bug.id)}
                        className="inline-flex items-center space-x-1 text-xs font-semibold text-brand-600 hover:text-brand-800"
                      >
                        <span>{bug.status === 'Diagnosed' ? 'View Report' : 'Analyze'}</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
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
