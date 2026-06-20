import React, { useState } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

export default function App() {
  const [query, setQuery] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    // Construct the payload matching our FastAPI ThreatQuery schema
    const payload = {
      query: query,
      filters: sourceFilter ? { source: sourceFilter } : null,
    };

    try {
      const response = await axios.post('http://127.0.0.1:8000/api/analyze', payload);
      if (response.data.status === 'success') {
        setResult(response.data.response);
      } else {
        setError('Failed to fetch valid threat analysis.');
      }
    } catch (err) {
      console.error(err);
      setError(err.response?.data?.detail || 'Could not connect to CyberWolf RAG Engine.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      {/* Top Navigation Bar */}
      <header className="border-b border-slate-800 bg-slate-950 px-6 py-4 flex items-center justify-between shadow-lg">
        <div className="flex items-center space-x-3">
          <span className="text-2xl">🛡️</span>
          <div>
            <h1 className="text-xl font-bold tracking-wider text-white">CYBERWOLF VULNSTREAM</h1>
            <p className="text-xs text-emerald-400 font-mono tracking-widest uppercase">Real-Time Threat Intel Engine</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
          <span className="text-xs font-mono text-slate-400">RAG CORE CORE-V1: ONLINE</span>
        </div>
      </header>

      {/* Main Container */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 flex flex-col space-y-6">
        {/* Search & Control Dashboard Panel */}
        <section className="bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-md">
          <form onSubmit={handleSearch} className="space-y-4">
            <div className="flex flex-col space-y-2">
              <label className="text-sm font-semibold tracking-wide text-slate-300">Threat Intelligence Query</label>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., Explain vulnerabilities allowing unauthenticated remote code execution..."
                className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-3 text-white placeholder-slate-500 focus:outline-none focus:border-emerald-500 transition-colors"
              />
            </div>

            {/* Filter Selection Grid */}
            <div className="flex flex-col sm:flex-row gap-4 items-end justify-between pt-2">
              <div className="w-full sm:w-1/3 flex flex-col space-y-2">
                <label className="text-xs font-mono text-slate-400 uppercase tracking-wider">Source Origin Filter</label>
                <select
                  value={sourceFilter}
                  onChange={(e) => setSourceFilter(e.target.value)}
                  className="bg-slate-900 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 focus:outline-none focus:border-emerald-500"
                >
                  <option value="">All Repositories (Global Search)</option>
                  <option value="NVD">NVD (National Vulnerability Database)</option>
                  <option value="CISA_KEV">CISA KEV (Known Exploited Vulnerabilities)</option>
                  <option value="MITRE_ATTACK">MITRE ATT&CK Matrix</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full sm:w-auto bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-800 text-slate-950 font-bold px-6 py-2.5 rounded-lg transition-all shadow-md active:scale-95 flex items-center justify-center space-x-2"
              >
                {loading ? (
                  <span>Analyzing Context...</span>
                ) : (
                  <>
                    <span>Execute Stream Search</span>
                    <span>⚡</span>
                  </>
                )}
              </button>
            </div>
          </form>
        </section>

        {/* Output Console Results Display */}
        <section className="flex-1 bg-slate-950 border border-slate-800 rounded-xl p-6 shadow-inner min-h-[350px] flex flex-col">
          <div className="border-b border-slate-800 pb-3 mb-4 flex items-center justify-between">
            <h3 className="text-sm font-mono tracking-wider text-slate-400 uppercase">Analysis Output Streams</h3>
            <span className="text-xs font-mono text-slate-500">Grounded LLM Frame</span>
          </div>

          <div className="flex-1 overflow-auto">
            {loading && (
              <div className="h-full flex flex-col items-center justify-center space-y-3 py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-500"></div>
                <p className="text-sm font-mono text-slate-400">Querying vector space and synthesizing intelligence frames...</p>
              </div>
            )}

            {error && (
              <div className="bg-red-950/40 border border-red-900/50 text-red-400 p-4 rounded-lg font-mono text-sm">
                ⚠️ [CRITICAL ERROR]: {error}
              </div>
            )}

            {!loading && !result && !error && (
              <div className="h-full flex items-center justify-center text-slate-600 font-mono text-sm py-12 text-center">
                Console idle. Enter an active intelligence query above to trace patterns.
              </div>
            )}

            {result && (
              <div className="prose prose-invert max-w-none font-sans leading-relaxed text-slate-200">
                <ReactMarkdown 
                  components={{
                    h1: ({node, ...props}) => <h1 className="text-2xl font-bold text-white mt-4 mb-2" {...props} />,
                    h2: ({node, ...props}) => <h2 className="text-xl font-semibold text-emerald-400 mt-4 mb-2" {...props} />,
                    h3: ({node, ...props}) => <h3 className="text-lg font-medium text-white mt-3 mb-1" {...props} />,
                    p: ({node, ...props}) => <p className="mb-3 text-slate-300" {...props} />,
                    ul: ({node, ...props}) => <ul className="list-disc pl-5 mb-3 space-y-1" {...props} />,
                    li: ({node, ...props}) => <li className="text-slate-300" {...props} />,
                    strong: ({node, ...props}) => <strong className="text-white font-semibold" {...props} />,
                  }}
                >
                  {result}
                </ReactMarkdown>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}