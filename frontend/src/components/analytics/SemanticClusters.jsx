import React, { useState } from 'react';
import { Sparkles, Bug, ChevronUp, ChevronDown } from 'lucide-react';

export function SemanticClusters({ clusters }) {
  const [expandedClusterId, setExpandedClusterId] = useState(null);

  const toggleCluster = (id) => {
    setExpandedClusterId((prev) => (prev === id ? null : id));
  };

  const getSeverityBadge = (sev) => {
    switch (sev?.toLowerCase()) {
      case 'critical':
        return 'bg-red-50 text-red-700 border-red-200';
      case 'high':
        return 'bg-amber-50 text-amber-700 border-amber-200';
      case 'medium':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h4 className="text-xs font-bold text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-brand-600" />
            Semantic Bug Clusters (Vector Similarity Groups)
          </h4>
          <p className="text-[11px] text-slate-500">
            Defects grouped together based on embedding proximity (cosine similarity &ge; 70%).
          </p>
        </div>
        <span className="text-xs text-brand-700 bg-brand-50 border border-brand-200 px-2.5 py-1 rounded-lg font-medium">
          ChromaDB 384-d MiniLM Embeddings
        </span>
      </div>

      <div className="grid grid-cols-1 gap-3">
        {clusters.map((cluster) => {
          const isExpanded = expandedClusterId === cluster.cluster_id;
          return (
            <div
              key={cluster.cluster_id}
              className="bg-white border border-slate-200 rounded-xl overflow-hidden shadow-sm transition-all"
            >
              <div
                onClick={() => toggleCluster(cluster.cluster_id)}
                className="p-4 flex items-center justify-between cursor-pointer hover:bg-slate-50"
              >
                <div className="space-y-1 max-w-2xl">
                  <div className="flex items-center space-x-2">
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-800">
                      {cluster.cluster_id.toUpperCase()}
                    </span>
                    <h5 className="text-sm font-bold text-slate-900">{cluster.cluster_theme}</h5>
                  </div>
                  <p className="text-xs text-slate-500">
                    Representative Defect: <span className="font-medium text-slate-700">"{cluster.representative_defect}"</span>
                  </p>
                </div>

                <div className="flex items-center space-x-4">
                  <div className="text-right text-xs">
                    <p className="font-bold text-slate-900">{cluster.defect_count} Defects ({cluster.percentage_of_total}%)</p>
                    <p className="text-[11px] text-emerald-600 font-semibold">{Math.round(cluster.average_similarity * 100)}% Similarity</p>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className="w-4 h-4 text-slate-400" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-slate-400" />
                  )}
                </div>
              </div>

              {isExpanded && (
                <div className="p-4 bg-slate-50 border-t border-slate-200 space-y-2">
                  <h6 className="text-[11px] font-bold text-slate-600 uppercase tracking-wider">
                    Cluster Member Defects ({cluster.members.length}):
                  </h6>
                  <div className="space-y-1.5">
                    {cluster.members.map((member) => (
                      <div
                        key={member.id}
                        className="bg-white p-2.5 rounded-lg border border-slate-200 flex items-center justify-between text-xs"
                      >
                        <div className="flex items-center space-x-2 truncate max-w-lg">
                          <Bug className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                          <span className="font-bold text-slate-700">#{member.bug_id}</span>
                          <span className="text-slate-800 truncate">{member.title}</span>
                        </div>
                        <div className="flex items-center space-x-3 shrink-0">
                          <span className="text-[10px] font-semibold text-slate-500">{member.component}</span>
                          <span className={`px-1.5 py-0.5 rounded text-[10px] border font-bold ${getSeverityBadge(member.severity)}`}>
                            {member.severity}
                          </span>
                          <span className="text-[10px] text-brand-700 font-semibold bg-brand-50 px-1.5 py-0.5 rounded">
                            {Math.round(member.similarity_to_centroid * 100)}% match
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
