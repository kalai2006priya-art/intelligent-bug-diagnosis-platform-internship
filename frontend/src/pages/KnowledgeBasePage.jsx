import React, { useState, useEffect } from 'react';
import { Database, Search, Filter, Loader2, BookOpen, Sparkles, ExternalLink } from 'lucide-react';
import { knowledgeApi } from '../api/knowledge';
import { EmptyState } from '../components/EmptyState';

export function KnowledgeBasePage() {
  const [stats, setStats] = useState(null);
  const [defects, setDefects] = useState([]);
  const [loading, setLoading] = useState(true);

  // Search & Filter State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [searchingSemantic, setSearchingSemantic] = useState(false);
  const [isSemanticMode, setIsSemanticMode] = useState(false);

  useEffect(() => {
    fetchInitialData();
  }, [selectedSource]);

  const fetchInitialData = async () => {
    setLoading(true);
    setIsSemanticMode(false);
    try {
      const [statsData, listData] = await Promise.all([
        knowledgeApi.getStats(),
        knowledgeApi.listDefects({ source: selectedSource || undefined, limit: 50 })
      ]);
      setStats(statsData);
      setDefects(listData);
    } catch (err) {
      console.error('Failed to load knowledge base data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSemanticSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      fetchInitialData();
      return;
    }

    setSearchingSemantic(true);
    try {
      const res = await knowledgeApi.searchSemantic(searchQuery, 10, selectedSource || null);
      setDefects(res.results);
      setIsSemanticMode(true);
    } catch (err) {
      console.error('Semantic search failed:', err);
    } finally {
      setSearchingSemantic(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <h1 className="text-lg font-bold text-slate-900">Historical Defect Knowledge Base</h1>
        <p className="text-xs text-slate-500 mt-0.5">
          Explore and query indexed open-source defect repositories (Mozilla, Apache, Eclipse) and continuously grown platform-resolved defects (M4.2).
        </p>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Mozilla Bugzilla</div>
            <div className="text-xl font-bold text-slate-900 mt-1">{stats.sources?.Mozilla || 0}</div>
            <div className="text-[10px] text-slate-400">Indexed defects</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Apache Jira</div>
            <div className="text-xl font-bold text-slate-900 mt-1">{stats.sources?.Apache || 0}</div>
            <div className="text-[10px] text-slate-400">Indexed defects</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">Eclipse Bugzilla</div>
            <div className="text-xl font-bold text-slate-900 mt-1">{stats.sources?.Eclipse || 0}</div>
            <div className="text-[10px] text-slate-400">Indexed defects</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-emerald-200 bg-emerald-50/30 shadow-sm">
            <div className="flex items-center justify-between">
              <span className="text-[11px] font-semibold text-emerald-700 uppercase">Platform Contributed</span>
              <span className="text-[9px] font-bold px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800">M4.2</span>
            </div>
            <div className="text-xl font-bold text-emerald-700 mt-1">{stats.sources?.Platform || 0}</div>
            <div className="text-[10px] text-emerald-600/70">Self-grown defects</div>
          </div>

          <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm col-span-2 sm:col-span-1">
            <div className="text-[11px] font-semibold text-slate-500 uppercase">ChromaDB Vectors</div>
            <div className="text-xl font-bold text-brand-600 mt-1">{stats.total_vector_chunks || 0}</div>
            <div className="text-[10px] text-slate-400">384-d semantic chunks</div>
          </div>
        </div>
      )}

      {/* Semantic Search Bar */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm">
        <form onSubmit={handleSemanticSearch} className="flex flex-col sm:flex-row items-center gap-3">
          <div className="relative flex-1 w-full">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Test vector similarity: e.g. Null pointer crash during network request cancellation..."
              className="w-full pl-9 pr-3 py-2 text-xs border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500"
            />
          </div>

          <div className="flex items-center space-x-2 w-full sm:w-auto">
            <select
              value={selectedSource}
              onChange={(e) => setSelectedSource(e.target.value)}
              className="text-xs border border-slate-300 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-brand-500"
            >
              <option value="">All Repositories</option>
              <option value="Mozilla">Mozilla</option>
              <option value="Apache">Apache</option>
              <option value="Eclipse">Eclipse</option>
              <option value="Platform">Platform Resolved (M4.2)</option>
            </select>

            <button
              type="submit"
              disabled={searchingSemantic}
              className="inline-flex items-center space-x-1.5 text-xs font-semibold bg-brand-600 hover:bg-brand-700 text-white px-4 py-2 rounded-lg transition-colors whitespace-nowrap shadow-sm disabled:opacity-50"
            >
              {searchingSemantic ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
              <span>Semantic Search</span>
            </button>
          </div>
        </form>

        {isSemanticMode && (
          <div className="mt-3 flex items-center justify-between text-xs text-brand-700 bg-brand-50/70 px-3 py-1.5 rounded-lg border border-brand-200">
            <span>Displaying vector similarity results for query: <strong>"{searchQuery}"</strong></span>
            <button
              onClick={fetchInitialData}
              className="font-semibold underline hover:text-brand-900 text-[11px]"
            >
              Clear Search
            </button>
          </div>
        )}
      </div>

      {/* Defect Cards & Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="p-12 text-center">
            <Loader2 className="w-6 h-6 text-brand-600 animate-spin mx-auto mb-2" />
            <p className="text-xs text-slate-500">Querying historical knowledge base...</p>
          </div>
        ) : defects.length === 0 ? (
          <div className="p-6">
            <EmptyState
              title="No historical defects found"
              description="No defect records matched your filter criteria or semantic query."
            />
          </div>
        ) : (
          <div className="divide-y divide-slate-100">
            {defects.map((d, idx) => (
              <div key={idx} className="p-5 hover:bg-slate-50/70 transition-colors space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-xs font-bold text-slate-800 bg-slate-100 px-2 py-0.5 rounded border border-slate-200">
                      {d.bug_id}
                    </span>
                    <span className="text-xs font-semibold px-2 py-0.5 rounded bg-sky-50 text-sky-700 border border-sky-200">
                      {d.dataset_source}
                    </span>
                    {d.project && (
                      <span className="text-xs text-slate-500 font-medium">
                        ({d.project})
                      </span>
                    )}
                    {d.component && (
                      <span className="text-xs text-slate-500">
                        &bull; {d.component}
                      </span>
                    )}
                  </div>

                  <div className="flex items-center space-x-3">
                    {d.similarity !== undefined && d.similarity !== null && (
                      <span className="inline-flex items-center text-xs font-mono font-bold text-emerald-700 bg-emerald-50 px-2.5 py-0.5 rounded-full border border-emerald-200">
                        Similarity: {Math.round(d.similarity * 100)}%
                      </span>
                    )}
                    <span className="text-xs font-medium text-slate-500 bg-slate-50 px-2 py-0.5 rounded border border-slate-200">
                      {d.resolution || 'CLOSED'}
                    </span>
                  </div>
                </div>

                <h3 className="text-xs font-bold text-slate-900">
                  {d.title}
                </h3>

                <p className="text-xs text-slate-600 line-clamp-2 leading-relaxed">
                  {d.description}
                </p>

                {d.comments && (
                  <div className="text-[11px] text-slate-500 bg-slate-50 p-2 rounded border border-slate-200/60 font-mono">
                    <strong className="text-slate-700">Resolution Note:</strong> {d.comments}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
