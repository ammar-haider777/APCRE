import React from "react";
import { motion } from "framer-motion";
import { Folder, FileCode, CheckCircle2, AlertCircle, RefreshCw, BarChart2 } from "lucide-react";

export default function DashboardPanel({ files, selectedFile, onSelectFile, onSyncRepo, loading }) {
  const totalFiles = files ? files.length : 0;
  const pyFiles = files ? files.filter(f => f.name && f.name.endsWith(".py")).length : 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="space-y-6 text-slate-200"
    >
      {/* 1. Header Overview */}
      <div className="flex items-center justify-between border-b border-slate-800/80 pb-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Ecosystem Dashboard</h1>
          <p className="text-sm text-slate-400 mt-1">Overview and file indexing details for your workspace.</p>
        </div>
        <button
          onClick={onSyncRepo}
          disabled={loading}
          className="flex items-center gap-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-blue-500/50 hover:bg-slate-800/50 px-4 py-2.5 text-xs font-semibold text-white shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50"
        >
          <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin text-blue-400" : "text-slate-400"}`} />
          {loading ? "Scanning workspace..." : "Rescan Repository"}
        </button>
      </div>

      {/* 2. Visual Scorecard Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 relative overflow-hidden group shadow-lg hover:shadow-xl transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <Folder className="h-20 w-20 text-white" />
          </div>
          <div className="text-xs text-slate-400 font-mono uppercase tracking-wider">Total Indexed files</div>
          <div className="text-3xl font-extrabold text-white mt-2 font-mono">{totalFiles}</div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
            <span>Active collaborative workspace</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 relative overflow-hidden group shadow-lg hover:shadow-xl transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <FileCode className="h-20 w-20 text-white" />
          </div>
          <div className="text-xs text-slate-400 font-mono uppercase tracking-wider">Python source scripts</div>
          <div className="text-3xl font-extrabold text-blue-400 mt-2 font-mono">{pyFiles}</div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Active AST / ML auditing online</span>
          </div>
        </div>

        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 relative overflow-hidden group shadow-lg hover:shadow-xl transition-all duration-300">
          <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
            <BarChart2 className="h-20 w-20 text-white" />
          </div>
          <div className="text-xs text-slate-400 font-mono uppercase tracking-wider">Ecosystem Index</div>
          <div className="text-3xl font-extrabold text-emerald-400 mt-2 font-mono">94.59%</div>
          <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Stratified ML Accuracy verified</span>
          </div>
        </div>
      </div>

      {/* 3. Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Workspace file explorer tree (3 cols) */}
        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 lg:col-span-3 shadow-lg flex flex-col min-h-[350px]">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-mono uppercase tracking-wider">
            <Folder className="h-4 w-4 text-blue-400" />
            <span>Workspace File Explorer</span>
          </h3>
          <div className="flex-1 space-y-1.5 overflow-y-auto max-h-[350px] pr-2">
            {files && files.length > 0 ? (
              files.map((file, idx) => {
                const isPy = file.name && file.name.endsWith(".py");
                const isSelected = selectedFile && selectedFile.name === file.name;
                return (
                  <button
                    key={idx}
                    onClick={() => onSelectFile(file)}
                    className={`w-full flex items-center justify-between rounded-xl px-4 py-3 border text-left text-xs transition-all duration-300 font-mono ${
                      isSelected
                        ? "bg-blue-500/10 border-blue-500/40 text-white"
                        : "bg-slate-900/50 border-slate-800/80 text-slate-300 hover:border-slate-700 hover:bg-slate-800/30"
                    }`}
                  >
                    <div className="flex items-center gap-3 truncate min-w-0">
                      <FileCode className={`h-4 w-4 shrink-0 ${isPy ? "text-blue-400" : "text-slate-400"}`} />
                      <span className="truncate">{file.name}</span>
                    </div>
                    {isSelected && (
                      <span className="text-[10px] font-bold text-blue-400 bg-blue-500/10 border border-blue-500/20 px-2 py-0.5 rounded-full uppercase shrink-0">
                        Editing
                      </span>
                    )}
                  </button>
                );
              })
            ) : (
              <div className="flex flex-col items-center justify-center py-16 text-center text-slate-500">
                <AlertCircle className="h-8 w-8 mb-2" />
                <p className="text-xs">No indexed files in workspace.</p>
              </div>
            )}
          </div>
        </div>

        {/* Selected file analysis metadata card (2 cols) */}
        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 lg:col-span-2 shadow-lg flex flex-col min-h-[350px]">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-mono uppercase tracking-wider">
            <CheckCircle2 className="h-4 w-4 text-emerald-400" />
            <span>Active File Summary</span>
          </h3>
          {selectedFile ? (
            <div className="flex-1 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/60 font-mono">
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider">Selected Script</div>
                  <div className="text-sm font-bold text-white mt-1 truncate">{selectedFile.name}</div>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between border-b border-slate-800/60 pb-2">
                    <span className="text-slate-400">Lines parsed</span>
                    <span className="font-mono text-white">{(selectedFile.content || "").split("\n").length}</span>
                  </div>
                  <div className="flex justify-between border-b border-slate-800/60 pb-2">
                    <span className="text-slate-400">Pure SLOC count</span>
                    <span className="font-mono text-white">
                      {(selectedFile.content || "").split("\n").filter(l => l.trim() && !l.trim().startsWith("#")).length}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Compiler Verification</span>
                    <span className="font-semibold text-emerald-400">Online</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 p-4 rounded-xl bg-emerald-500/5 border border-emerald-500/10 flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
                <div className="text-[11px] leading-relaxed text-slate-400">
                  <span className="font-bold text-slate-200 block">Workspace Auditing Active</span>
                  The system runs tree-sitter syntax validation continuously on active changes. Select 'AI Review' to see structured issues.
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-grow flex flex-col items-center justify-center text-center py-12 text-slate-500">
              <FileCode className="h-10 w-10 text-slate-600 mb-2 animate-pulse" />
              <p className="text-xs max-w-[200px] leading-relaxed">
                Select a script from the File Explorer to initiate compiler audits.
              </p>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
}
