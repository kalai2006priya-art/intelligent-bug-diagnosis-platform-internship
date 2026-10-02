import React, { useState, useEffect } from 'react';
import { BarChart3, Filter, RotateCcw } from 'lucide-react';
import { analyticsApi } from '../api/analytics';
import { AnalyticsKpis } from '../components/analytics/AnalyticsKpis';
import { ComponentHotspots } from '../components/analytics/ComponentHotspots';
import { SemanticClusters } from '../components/analytics/SemanticClusters';
import { RootCauseThemes, ExceptionSignatures } from '../components/analytics/RootCauseThemes';
import { TimeTrends } from '../components/analytics/TimeTrends';

export function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  const [filters, setFilters] = useState({
    source: 'all',
    component: '',
    severity: '',
    priority: '',
    exception_type: ''
  });

  const [filterOptions, setFilterOptions] = useState({
    available_components: [],
    available_severities: [],
    available_priorities: [],
    available_exception_types: [],
    available_sources: []
  });

  useEffect(() => {
    async function loadFilterOptions() {
      try {
        const res = await analyticsApi.getFilters();
        if (res) setFilterOptions(res);
      } catch (err) {
        console.error('Failed to load filter options:', err);
      }
    }
    loadFilterOptions();
  }, []);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await analyticsApi.getOverview(filters);
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load analytics data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, [filters]);

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const resetFilters = () => {
    setFilters({
      source: 'all',
      component: '',
      severity: '',
      priority: '',
      exception_type: ''
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 pb-2 border-b border-slate-200">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-2.5 py-0.5 rounded-full text-[11px] font-semibold bg-brand-100 text-brand-800">
              Milestone 4.1
            </span>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <BarChart3 className="w-6 h-6 text-brand-600" />
              Defect Pattern Analytics
            </h1>
          </div>
          <p className="text-sm text-slate-500 mt-1">
            Automated recurrence mining, component hotspots, root cause themes, and semantic bug clusters.
          </p>
        </div>

        <button
          onClick={fetchAnalytics}
          disabled={loading}
          className="inline-flex items-center space-x-2 px-3 py-2 border border-slate-300 rounded-lg text-xs font-medium text-slate-700 bg-white hover:bg-slate-50 shadow-sm transition-colors"
        >
          <RotateCcw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-brand-600' : 'text-slate-400'}`} />
          <span>Refresh Analytics</span>
        </button>
      </div>

      {/* Filter Toolbar */}
      <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2 text-xs font-bold text-slate-700 uppercase tracking-wider">
            <Filter className="w-3.5 h-3.5 text-brand-600" />
            <span>Interactive Filters & Scope</span>
          </div>
          {(filters.component || filters.severity || filters.priority || filters.source !== 'all') && (
            <button
              onClick={resetFilters}
              className="text-xs text-brand-600 hover:text-brand-800 font-medium transition-colors"
            >
              Reset Filters
            </button>
          )}
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3 text-xs">
          <div>
            <label className="block text-slate-500 font-medium mb-1">Data Scope</label>
            <select
              value={filters.source}
              onChange={(e) => handleFilterChange('source', e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-brand-500 focus:bg-white text-slate-800"
            >
              <option value="all">All Data (Submitted + Historical)</option>
              <option value="submitted">Submitted User Bugs Only</option>
              <option value="historical">Historical Knowledge Base Only</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-500 font-medium mb-1">Component / Module</label>
            <select
              value={filters.component}
              onChange={(e) => handleFilterChange('component', e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-brand-500 focus:bg-white text-slate-800"
            >
              <option value="">All Components</option>
              {filterOptions.available_components.map((comp) => (
                <option key={comp} value={comp}>
                  {comp}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-slate-500 font-medium mb-1">Severity</label>
            <select
              value={filters.severity}
              onChange={(e) => handleFilterChange('severity', e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-brand-500 focus:bg-white text-slate-800"
            >
              <option value="">All Severities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div>
            <label className="block text-slate-500 font-medium mb-1">Priority</label>
            <select
              value={filters.priority}
              onChange={(e) => handleFilterChange('priority', e.target.value)}
              className="w-full bg-slate-50 border border-slate-300 rounded-lg p-2 focus:ring-1 focus:ring-brand-500 focus:bg-white text-slate-800"
            >
              <option value="">All Priorities</option>
              <option value="Critical">Critical</option>
              <option value="High">High</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs">
          <strong>Error:</strong> {error}
        </div>
      )}

      {loading && !data && (
        <div className="py-16 text-center">
          <RotateCcw className="w-8 h-8 animate-spin text-brand-600 mx-auto mb-2" />
          <p className="text-sm font-medium text-slate-600">Analyzing defect patterns & clusters...</p>
        </div>
      )}

      {data && (
        <div className="space-y-6">
          <AnalyticsKpis kpis={data.kpis} />

          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-200 space-x-6 text-xs font-semibold overflow-x-auto">
            {[
              { id: 'overview', label: 'Distribution & Hotspots' },
              { id: 'clusters', label: 'Semantic Bug Clusters' },
              { id: 'rootcauses', label: 'Root Cause & Fix Themes' },
              { id: 'exceptions', label: 'Recurring Exceptions' },
              { id: 'trends', label: 'Time Trends' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`pb-3 transition-colors border-b-2 whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-brand-600 text-brand-700'
                    : 'border-transparent text-slate-500 hover:text-slate-800'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'overview' && (
            <ComponentHotspots
              hotspots={data.component_hotspots}
              severityDist={data.severity_distribution}
              priorityDist={data.priority_distribution}
            />
          )}

          {activeTab === 'clusters' && (
            <SemanticClusters clusters={data.semantic_clusters} />
          )}

          {activeTab === 'rootcauses' && (
            <RootCauseThemes themes={data.root_cause_themes} />
          )}

          {activeTab === 'exceptions' && (
            <ExceptionSignatures exceptions={data.top_exception_patterns} />
          )}

          {activeTab === 'trends' && (
            <TimeTrends timeTrends={data.time_trends} />
          )}
        </div>
      )}
    </div>
  );
}
