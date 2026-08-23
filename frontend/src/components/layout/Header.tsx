import React from 'react';
import { Shield } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-border bg-surface/50 backdrop-blur-md px-6 py-4">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-accent-blue/10 text-accent-blue border border-accent-blue/20">
            <Shield className="h-5 w-5" />
          </div>
          <div>
            <h1 className="text-base font-semibold tracking-tight text-white">Mystic Security</h1>
            <p className="text-xs text-gray-400">Cybersecurity Assessment Platform</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono text-gray-400">
          <span className="inline-block h-2 w-2 rounded-full bg-accent-emerald animate-pulse"></span>
          <span>Phase 0.1 Foundation</span>
        </div>
      </div>
    </header>
  );
};
