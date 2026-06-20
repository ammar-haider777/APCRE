import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Layout, ArrowRight, Share2, HelpCircle, CheckCircle, RefreshCw } from "lucide-react";

export default function ArchitecturePanel() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchArchitecture = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("/api/architecture/recommend", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({}),
      });
      const resData = await res.json();
      if (resData.success) {
        setData(resData);
      } else {
        setError(resData.error || "Failed to analyze architecture.");
      }
    } catch (err) {
      setError("AI Engine offline. Utilizing premium offline simulation.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArchitecture();
  }, []);

  const steps = data && data.migration_plan && data.migration_plan.length > 0
    ? data.migration_plan.map((stepStr, idx) => {
        const parts = stepStr.split(":");
        return {
          title: parts[0]?.trim() || `Step ${idx + 1}`,
          desc: parts.slice(1).join(":")?.trim() || stepStr
        };
      })
    : [
        { title: "1. Isolate Domain Entities", desc: "Extract core OOP domain structures, decoupling business entities from Flask ORM hooks or SQL libraries." },
        { title: "2. Formulate Port Contracts", desc: "Design abstract protocols/interfaces mapping repository mutations and boundary calculations." },
        { title: "3. Implement Adapter Shells", desc: "Construct localized SQLite gateway adapters or JSON file engines inheriting port interfaces." },
        { title: "4. Establish Dependency Injection", desc: "Inject adapter shells at startup to isolate and execute core domain tasks decoupled from database modules." }
      ];

  const currentArch = data ? data.current_architecture : "Monolithic (coupled)";
  const recommendedArch = data ? data.recommended_architecture : "Hexagonal Architecture";

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35 }}
      className="space-y-6 text-slate-200"
    >
      {/* 1. Header */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Layout className="h-6 w-6 text-blue-500" />
            <span>Architecture Center</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">Audit coupling bounds and map your code's path to clean, decoupled Hexagonal architectures.</p>
        </div>
        
        <button
          onClick={fetchArchitecture}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-800/50 px-4 py-2.5 text-xs font-semibold text-white shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin text-blue-400" : "text-slate-400"}`} />
          {loading ? "Analyzing..." : "Audit Architecture"}
        </button>
      </div>

      {/* 2. Modern Decoupled Dependency SVG Flow Diagram */}
      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg flex flex-col items-center">
        <h3 className="text-xs font-bold text-white self-start mb-4 flex items-center gap-2 font-mono uppercase tracking-wider">
          <Share2 className="h-4 w-4 text-blue-400" />
          <span>Hexagonal (Ports & Adapters) Dependency Flow Map</span>
        </h3>
        
        {/* Animated coupling flow map */}
        <div className="relative w-full max-w-[600px] h-[180px] bg-slate-950/40 border border-slate-850 rounded-xl overflow-hidden p-4 flex justify-between items-center">
          
          {/* Adapter Module (Left) */}
          <div className="flex flex-col items-center z-10 w-24 p-2 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">Input</span>
            <span className="text-xs font-bold text-blue-400 mt-1">Adapters</span>
          </div>

          {/* Port Interface Contract (Middle-Left) */}
          <div className="flex flex-col items-center z-10 w-24 p-2 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">Contract</span>
            <span className="text-xs font-bold text-amber-400 mt-1">Ports</span>
          </div>

          {/* Domain Model (Center) */}
          <div className="flex flex-col items-center z-10 w-28 p-3 rounded-2xl bg-blue-500/10 border-2 border-blue-500/30 shadow-lg shadow-blue-500/5">
            <span className="text-[9px] uppercase tracking-widest text-blue-400 font-mono">Core Domain</span>
            <span className="text-sm font-extrabold text-white mt-1">Entities</span>
          </div>

          {/* Database Output Adapters (Right) */}
          <div className="flex flex-col items-center z-10 w-24 p-2 rounded-xl bg-slate-900 border border-slate-800">
            <span className="text-[9px] uppercase tracking-widest text-slate-500 font-mono">Persistence</span>
            <span className="text-xs font-bold text-indigo-400 mt-1">SQLite DB</span>
          </div>

          {/* SVG Animated Connector Flow Lines */}
          <svg className="absolute inset-0 w-full h-full pointer-events-none">
            {/* Adapter to Port */}
            <path d="M 120 90 L 190 90" fill="none" stroke="#1e293b" strokeWidth="2" />
            <path d="M 120 90 L 190 90" fill="none" stroke="#3b82f6" strokeWidth="2" strokeDasharray="5,5" className="animate-[dash_2s_linear_infinite]" />
            
            {/* Port to Domain */}
            <path d="M 285 90 L 325 90" fill="none" stroke="#1e293b" strokeWidth="2" />
            <path d="M 285 90 L 325 90" fill="none" stroke="#f59e0b" strokeWidth="2" strokeDasharray="5,5" className="animate-[dash_2.5s_linear_infinite]" />
            
            {/* DB to Domain */}
            <path d="M 475 90 L 435 90" fill="none" stroke="#1e293b" strokeWidth="2" />
            <path d="M 475 90 L 435 90" fill="none" stroke="#818cf8" strokeWidth="2" strokeDasharray="5,5" className="animate-[dash_3s_linear_infinite]" />
          </svg>
        </div>
      </div>

      {/* 3. Splitting columns */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Current Monolithic smells card */}
        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2 font-mono uppercase tracking-wider">
              <ArrowRight className="h-4 w-4 text-rose-400 rotate-45" />
              <span>Real-Time Codebase Profile</span>
            </h3>
            
            {error && (
              <div className="text-[10px] text-amber-400 font-mono mb-3 p-2 bg-amber-500/5 border border-amber-500/10 rounded-xl">
                {error}
              </div>
            )}

            <div className="space-y-3 text-xs text-slate-400">
              <div className="p-3 border border-slate-800 bg-slate-950/30 rounded-xl flex justify-between">
                <div>
                  <span className="font-semibold text-slate-200 block">Current Topology</span>
                  <span className="text-[10px] text-slate-400 leading-normal">Evaluated pattern from active directory.</span>
                </div>
                <span className="bg-rose-950/40 text-rose-400 border border-rose-900/30 font-mono font-bold px-2 py-0.5 rounded-lg text-[9px] h-fit uppercase">
                  {currentArch}
                </span>
              </div>
              <div className="p-3 border border-slate-800 bg-slate-950/30 rounded-xl flex justify-between">
                <div>
                  <span className="font-semibold text-slate-200 block">Recommended Pattern</span>
                  <span className="text-[10px] text-slate-400 leading-normal">Optimized migration target.</span>
                </div>
                <span className="bg-emerald-950/40 text-emerald-400 border border-emerald-900/30 font-mono font-bold px-2 py-0.5 rounded-lg text-[9px] h-fit uppercase">
                  {recommendedArch}
                </span>
              </div>
            </div>
          </div>

          {data && data.analysis_summary && (
            <div className="mt-4 p-3 border border-slate-800 bg-slate-950/30 rounded-xl text-xs text-slate-400 font-mono">
              <span className="font-bold text-slate-200 block mb-1 uppercase tracking-wider text-[9px]">Summary Metrics</span>
              Parsed {data.analysis_summary.files_count} files ({data.analysis_summary.total_lines} LOC) across {data.analysis_summary.modules_count} module directories.
            </div>
          )}
        </div>

        {/* Dynamic Migration Path checklist */}
        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg">
          <h3 className="text-sm font-bold text-white mb-3 flex items-center gap-2 font-mono uppercase tracking-wider">
            <CheckCircle className="h-4 w-4 text-emerald-400" />
            <span>Target Refactoring Steps</span>
          </h3>
          <div className="space-y-3.5">
            {steps.map((st, idx) => (
              <div key={idx} className="flex gap-3 text-xs">
                <CheckCircle className="h-4 w-4 text-emerald-500 shrink-0 mt-0.5" />
                <div>
                  <div className="font-bold text-slate-200">{st.title}</div>
                  <div className="text-slate-400 mt-0.5 leading-normal">{st.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}
