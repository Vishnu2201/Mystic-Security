import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-border bg-surface/30 px-6 py-4 text-xs text-gray-500">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div>
          <span>Mystic Security Platform</span>
          <span className="mx-2">&bull;</span>
          <span>Capability-Driven Security Testing</span>
        </div>
        <div>
          <span>Real Data Only Policy Enforced</span>
        </div>
      </div>
    </footer>
  );
};
