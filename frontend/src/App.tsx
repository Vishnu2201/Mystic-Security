import React, { useEffect, useState } from 'react';
import { Layout } from './components/layout/Layout';
import { Server, Database, Code2, CheckCircle2, AlertCircle, Info } from 'lucide-react';

interface BackendHealth {
  status: string;
  app_name: string;
  version: string;
  environment: string;
}

export const App: React.FC = () => {
  const [health, setHealth] = useState<BackendHealth | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const apiBase = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    fetch(`${apiBase}/api/v1/health`)
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then((data: BackendHealth) => {
        setHealth(data);
        setLoading(false);
      })
      .catch((err: Error) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <Layout>
      <div className="space-y-6">
        {/* Main Banner */}
        <div className="rounded-xl border border-border bg-surface p-6 shadow-sm">
          <div className="flex items-start justify-between">
            <div>
              <h2 className="text-xl font-bold text-white">Platform Foundation Initialized</h2>
              <p className="mt-1 text-sm text-gray-400">
                Phase 0.1 project infrastructure, backend FastAPI framework, and React frontend shell established.
              </p>
            </div>
            <span className="inline-flex items-center rounded-full bg-accent-blue/10 px-3 py-1 text-xs font-medium text-accent-blue border border-accent-blue/20">
              Phase 0.1 Complete
            </span>
          </div>

          <div className="mt-6 grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="rounded-lg border border-border bg-background/50 p-4">
              <div className="flex items-center space-x-3">
                <Code2 className="h-5 w-5 text-accent-blue" />
                <div>
                  <div className="text-xs text-gray-400">Frontend Stack</div>
                  <div className="text-sm font-medium text-white">React 18 + TS + Vite</div>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-background/50 p-4">
              <div className="flex items-center space-x-3">
                <Server className="h-5 w-5 text-accent-indigo" />
                <div>
                  <div className="text-xs text-gray-400">Backend API</div>
                  <div className="text-sm font-medium text-white">FastAPI 0.110+</div>
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-border bg-background/50 p-4">
              <div className="flex items-center space-x-3">
                <Database className="h-5 w-5 text-accent-emerald" />
                <div>
                  <div className="text-xs text-gray-400">Infrastructure</div>
                  <div className="text-sm font-medium text-white">PostgreSQL 16 Container</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Backend Connectivity Check */}
        <div className="rounded-xl border border-border bg-surface p-6">
          <h3 className="text-sm font-semibold uppercase tracking-wider text-gray-400">
            Backend API Health Verification
          </h3>

          <div className="mt-4">
            {loading && (
              <div className="flex items-center space-x-2 text-sm text-gray-400">
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-accent-blue border-t-transparent"></div>
                <span>Checking backend health at /api/v1/health...</span>
              </div>
            )}

            {!loading && health && (
              <div className="flex items-center justify-between rounded-lg border border-emerald-500/20 bg-emerald-500/5 p-4 text-emerald-400">
                <div className="flex items-center space-x-3">
                  <CheckCircle2 className="h-5 w-5 flex-shrink-0" />
                  <div>
                    <div className="text-sm font-semibold">Backend Connection Verified</div>
                    <div className="text-xs text-emerald-500/80 font-mono mt-0.5">
                      {health.app_name} v{health.version} ({health.environment}) &bull; Status: {health.status}
                    </div>
                  </div>
                </div>
                <span className="text-xs font-mono bg-emerald-500/10 px-2.5 py-1 rounded text-emerald-300">
                  HTTP 200 OK
                </span>
              </div>
            )}

            {!loading && error && (
              <div className="flex items-center justify-between rounded-lg border border-amber-500/20 bg-amber-500/5 p-4 text-amber-400">
                <div className="flex items-center space-x-3">
                  <AlertCircle className="h-5 w-5 flex-shrink-0" />
                  <div>
                    <div className="text-sm font-semibold">Backend API Offline / Unreachable</div>
                    <div className="text-xs text-amber-500/80 font-mono mt-0.5">
                      Unable to connect to FastAPI endpoint ({error}). Start backend server via uvicorn or docker compose.
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Real Data Only & Architectural Notice */}
        <div className="rounded-xl border border-border bg-surface p-6">
          <div className="flex items-start space-x-3">
            <Info className="h-5 w-5 text-accent-blue flex-shrink-0 mt-0.5" />
            <div className="space-y-2 text-xs text-gray-400">
              <h4 className="font-semibold text-gray-200 text-sm">Strict Real-Data-Only Architectural Invariant</h4>
              <p>
                In accordance with project rules, this platform contains zero demo targets, mock findings, seeded data, or fake dashboard metrics.
              </p>
              <p>
                Target registration, authorization management, scope validation, assessment planning, capabilities (starting with DNS resolution), and evidence tracking will be introduced in subsequent phase rollouts.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default App;
