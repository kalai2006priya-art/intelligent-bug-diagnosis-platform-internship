import React from 'react';
import { Inbox } from 'lucide-react';

export function EmptyState({ title = 'No records found', description = 'There are currently no items to display.', actionButton = null }) {
  return (
    <div className="text-center py-12 px-4 border border-dashed border-slate-200 rounded-lg bg-white/50">
      <div className="w-12 h-12 mx-auto mb-4 text-slate-400 flex items-center justify-center bg-slate-100 rounded-full">
        <Inbox className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-slate-800">{title}</h3>
      <p className="mt-1 text-xs text-slate-500 max-w-sm mx-auto">{description}</p>
      {actionButton && (
        <div className="mt-4">
          {actionButton}
        </div>
      )}
    </div>
  );
}
