import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Cpu, Terminal, Mic, MicOff, Play, CheckCircle2, ShieldAlert, FileCode2 } from "lucide-react";

export default function AgentPanel({
  isPro,
  agentRunning,
  agentVisibleLogs,
  agentPrompt,
  agentFilename,
  setAgentPrompt,
  setAgentFilename,
  onRunAgent,
  isListening,
  onToggleSpeech,
  onShowCheckout
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35 }}
      className="space-y-6 text-slate-200"
    >
      {/* 1. Header */}
      <div className="border-b border-slate-800/80 pb-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Cpu className="h-6 w-6 text-blue-500 animate-pulse" />
            <span>Autonomous Repair & Coding Agent (ADA)</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">Multi-step autonomous agent running static audit, code generation, sandboxed test execution, and traceback self-repair loops.</p>
        </div>
      </div>

      <AnimatePresence mode="wait">
        {!isPro ? (
          /* SaaS Lock Screen */
          <motion.div
            key="lock-screen"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.98 }}
            className="max-w-md mx-auto rounded-2xl border border-slate-850 bg-[#111827] p-6 shadow-xl flex flex-col items-center text-center space-y-6"
          >
            <div className="p-4 rounded-full bg-gradient-to-tr from-blue-500 to-indigo-600 text-white shadow-lg animate-pulse">
              <Cpu className="h-8 w-8" />
            </div>
            <div>
              <h2 className="text-lg font-bold text-white">APCRE Pro Feature</h2>
              <p className="text-xs text-slate-400 mt-2 leading-relaxed">
                Upgrade to Pro to unlock local autonomous coding agents capable of analyzing directories, executing unit tests inside safe sandbox subprocesses, and patching runtime exceptions.
              </p>
            </div>
            <button
              onClick={onShowCheckout}
              className="w-full rounded-xl bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 text-xs font-bold text-white shadow-md hover:from-blue-750 hover:to-indigo-750 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5"
            >
              Start 2-Month Free Trial
            </button>
          </motion.div>
        ) : (
          /* Active Coder Agent Workspace */
          <motion.div
            key="agent-workspace"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            className="grid grid-cols-1 lg:grid-cols-5 gap-6"
          >
            {/* Left Controls (2 cols) */}
            <div className="lg:col-span-2 space-y-4">
              
              {/* Instructions Prompt */}
              <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg space-y-4">
                <div className="text-xs font-bold text-white font-mono uppercase tracking-wider">Agent Assignment Prompt</div>
                
                <div className="relative">
                  <textarea
                    value={agentPrompt}
                    onChange={(e) => setAgentPrompt(e.target.value)}
                    placeholder="Enter task (e.g., 'Calculate average of custom numbers', 'example of dynamic programming data structure'...)"
                    className="w-full bg-slate-950/60 border border-slate-850 rounded-xl px-4 py-3 text-xs text-slate-200 placeholder-slate-500 focus:border-blue-500/50 focus:outline-none resize-none h-[110px] font-mono leading-relaxed"
                  />
                  
                  {/* Voice Input Toggle Button */}
                  <button
                    onClick={onToggleSpeech}
                    className={`absolute bottom-3.5 right-3.5 p-2 rounded-xl border transition ${
                      isListening
                        ? "bg-rose-500/10 border-rose-500/20 text-rose-400 animate-pulse"
                        : "bg-slate-900 border-slate-850 text-slate-400 hover:text-white"
                    }`}
                    title={isListening ? "Listening... Click to stop" : "Voice dictation"}
                  >
                    {isListening ? <Mic className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
                  </button>
                </div>

                {/* Target filename field */}
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">
                    Output Target File Name
                  </label>
                  <input
                    value={agentFilename}
                    onChange={(e) => setAgentFilename(e.target.value)}
                    className="w-full bg-slate-950/60 border border-slate-850 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono"
                    placeholder="automation_agent.py"
                  />
                </div>

                <button
                  onClick={onRunAgent}
                  disabled={agentRunning || !agentPrompt.trim()}
                  className="w-full flex items-center justify-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-700 py-3 text-xs font-bold text-white shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50"
                >
                  <Play className="h-4 w-4" />
                  <span>{agentRunning ? "Agent Running..." : "Launch Coder Agent"}</span>
                </button>
              </div>

              {/* Status Info Box */}
              <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg flex items-start gap-3">
                <CheckCircle2 className="h-5 w-5 text-emerald-400 shrink-0 mt-0.5" />
                <div className="text-[11px] leading-relaxed text-slate-400">
                  <span className="font-bold text-slate-200 block mb-1">Stateful Sandbox Subprocess</span>
                  Tasks compile and run in a safe local environment with an absolute 10.0-second safety timeout limit to intercept and prevent infinite loop freezes.
                </div>
              </div>

            </div>

            {/* Right Live Activity Log Timeline (3 cols) */}
            <div className="lg:col-span-3 rounded-2xl border border-slate-800 bg-[#111827] p-5 shadow-lg flex flex-col min-h-[350px]">
              <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-mono uppercase tracking-wider">
                <Terminal className="h-4 w-4 text-blue-400 animate-pulse" />
                <span>Agent Live Activity Timeline Console</span>
              </h3>
              
              <div className="flex-grow w-full bg-slate-950/80 border border-slate-850 rounded-xl p-4 font-mono text-xs overflow-y-auto max-h-[320px] space-y-2 scrollbar-thin select-text">
                {agentVisibleLogs && agentVisibleLogs.length > 0 ? (
                  agentVisibleLogs.map((log, idx) => {
                    let textClass = "text-slate-400";
                    if (log.status === "success") textClass = "text-emerald-400 font-bold";
                    else if (log.status === "error") textClass = "text-rose-400 font-bold";
                    else if (log.status === "warning") textClass = "text-amber-400 font-bold";

                    return (
                      <div key={idx} className="flex gap-2.5 items-start leading-relaxed">
                        <span className="text-slate-600 shrink-0 select-none">[{log.time}]</span>
                        <span className={textClass}>{log.step}</span>
                      </div>
                    );
                  })
                ) : (
                  <div className="h-full flex flex-col items-center justify-center py-20 text-center text-slate-650">
                    <Terminal className="h-8 w-8 text-slate-700 mb-2" />
                    <span>Console ready. Input a goal prompt and launch the coder agent to begin.</span>
                  </div>
                )}
                {agentRunning && (
                  <div className="flex items-center gap-2 text-blue-400 animate-pulse mt-3 select-none">
                    <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping" />
                    <span>Executing self-debugging repair pipeline...</span>
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
