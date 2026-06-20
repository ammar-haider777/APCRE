import React from "react";
import { AlertTriangle, Sparkles, Terminal, ShieldAlert } from "lucide-react";

export default function RightInsightPanel({
  issues,
  onFixClick,
  selectedFixIssueId,
  setSelectedFixIssueId,
  fixLoading,
  setFixLoading,
  agentRunning,
  agentVisibleLogs,
  agentPrompt,
  agentFilename,
  setAgentPrompt,
  setAgentFilename,
  onRunAgent,
  isListening,
  onToggleSpeech
}) {
  return (
    <div className="space-y-5 h-full flex flex-col justify-between text-slate-300">
      
      {/* 1. Conversational Agent Timeline Console (Top section) */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900/50 p-4 flex flex-col flex-1 min-h-[250px]">
        <h3 className="text-xs font-bold text-white mb-3 flex items-center gap-2 font-mono uppercase tracking-wider">
          <Terminal className="h-4 w-4 text-blue-400" />
          <span>Agent Timeline Console</span>
        </h3>
        
        <div className="flex-1 w-full bg-slate-950/80 border border-slate-850 rounded-xl p-3 font-mono text-[9px] overflow-y-auto max-h-[200px] space-y-1.5 scrollbar-thin select-text">
          {agentVisibleLogs && agentVisibleLogs.length > 0 ? (
            agentVisibleLogs.map((log, idx) => {
              let textClass = "text-slate-400";
              if (log.status === "success") textClass = "text-emerald-400 font-bold";
              else if (log.status === "error") textClass = "text-rose-400 font-bold";
              else if (log.status === "warning") textClass = "text-amber-400 font-bold";

              return (
                <div key={idx} className="flex gap-2 items-start leading-normal">
                  <span className="text-slate-600 shrink-0 select-none">[{log.time}]</span>
                  <span className={textClass}>{log.step}</span>
                </div>
              );
            })
          ) : (
            <div className="h-full flex flex-col items-center justify-center py-12 text-center text-slate-600">
              <Terminal className="h-6 w-6 text-slate-700 mb-1" />
              <span>Console Ready. Launch Agent to stream activities.</span>
            </div>
          )}
          {agentRunning && (
            <div className="flex items-center gap-2 text-blue-400 animate-pulse mt-2 select-none">
              <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping" />
              <span>Agent executing multi-step repair plan...</span>
            </div>
          )}
        </div>
      </div>

      {/* 2. Contextual AI Findings (Middle Section) */}
      <div className="rounded-2xl border border-slate-800 bg-[#111827] p-4 flex flex-col flex-1 min-h-[200px]">
        <h3 className="text-xs font-bold text-white mb-3 flex items-center gap-2 font-mono uppercase tracking-wider">
          <Sparkles className="h-4 w-4 text-amber-500" />
          <span>Active Code Smells ({issues ? issues.length : 0})</span>
        </h3>
        
        <div className="flex-1 overflow-y-auto max-h-[160px] space-y-2 pr-1">
          {issues && issues.length > 0 ? (
            issues.map((issue, idx) => {
              let tagColor = "bg-blue-500/10 text-blue-400 border-blue-500/20";
              if (issue.type === "critical") tagColor = "bg-rose-500/10 text-rose-400 border-rose-500/20";
              else if (issue.type === "warning") tagColor = "bg-amber-500/10 text-amber-400 border-amber-500/20";

              return (
                <div key={idx} className="p-2.5 border border-slate-800/80 rounded-xl bg-slate-950/20 text-[10px] space-y-2">
                  <div className="flex justify-between items-start gap-2">
                    <span className="font-semibold text-slate-200 truncate">{issue.title}</span>
                    <span className={`px-1.5 py-0.5 border text-[8px] font-bold font-mono rounded uppercase shrink-0 ${tagColor}`}>
                      Line {issue.line}
                    </span>
                  </div>
                  <p className="text-slate-400 leading-normal text-[9px]">{issue.desc}</p>
                  
                  <div className="flex items-center justify-between mt-1 pt-1.5 border-t border-slate-800/40">
                    <button
                      onClick={async () => {
                        try {
                          setSelectedFixIssueId(issue.id);
                          setFixLoading(true);
                          await onFixClick(issue);
                        } catch (err) {
                          alert("Failed to fix: " + err.message);
                        } finally {
                          setFixLoading(false);
                          setSelectedFixIssueId(null);
                        }
                      }}
                      disabled={fixLoading}
                      className="px-2 py-1 text-[9px] font-mono font-bold uppercase rounded bg-blue-600 hover:bg-blue-500 text-white disabled:opacity-50 transition"
                    >
                      {fixLoading && selectedFixIssueId === issue.id ? "Fixing..." : "⚡ Quick Fix"}
                    </button>
                  </div>
                </div>
              );
            })
          ) : (
            <div className="h-full flex flex-col items-center justify-center py-12 text-center text-slate-600">
              <CheckCircleSymbol className="h-6 w-6 text-slate-700 mb-1" />
              <span>Clean Codebase. No active structural smells detected.</span>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}

// Simple internal helper SVG components
function CheckCircleSymbol(props) {
  return (
    <svg className={props.className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2">
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}
