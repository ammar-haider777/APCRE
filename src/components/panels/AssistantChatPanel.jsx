import React, { useEffect, useRef } from "react";
import { motion } from "framer-motion";
import { Bot, Send, User, Mic, MicOff } from "lucide-react";

export default function AssistantChatPanel({
  assistantMessages,
  assistantInput,
  assistantLoading,
  setAssistantInput,
  sendAssistantMessage,
  isListening,
  onToggleSpeech
}) {
  const containerRef = useRef(null);

  // Auto scroll to bottom
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [assistantMessages, assistantLoading]);

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -15 }}
      transition={{ duration: 0.35 }}
      className="flex flex-col h-[calc(100vh-120px)] text-slate-200"
    >
      {/* 1. Header */}
      <div className="border-b border-slate-800/80 pb-4 shrink-0 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight flex items-center gap-2.5">
            <Bot className="h-6 w-6 text-blue-500 animate-pulse" />
            <span>APCRE AI Programming Assistant</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">Senior pedagogical mentor offering deep-dives, compiler dry-runs, and SQL compliance guidance.</p>
        </div>
      </div>

      {/* 2. Chat Bubbles Panel */}
      <div
        ref={containerRef}
        className="flex-grow overflow-y-auto p-4 space-y-4 my-4 bg-slate-950/40 border border-slate-850 rounded-2xl scrollbar-thin max-h-[calc(100vh-260px)]"
      >
        {assistantMessages && assistantMessages.length > 0 ? (
          assistantMessages.map((m, idx) => {
            const isUser = m.role === "user";
            return (
              <div
                key={idx}
                className={`flex gap-3 max-w-[85%] ${isUser ? "ml-auto flex-row-reverse" : "mr-auto"}`}
              >
                {/* Avatar Icon */}
                <div className={`p-2 rounded-xl h-8 w-8 shrink-0 flex items-center justify-center border ${
                  isUser ? "bg-blue-500/10 border-blue-500/20 text-blue-400" : "bg-slate-900 border-slate-800 text-slate-400"
                }`}>
                  {isUser ? <User className="h-4 w-4" /> : <Bot className="h-4 w-4" />}
                </div>

                {/* Bubble card */}
                <div className={`rounded-2xl px-4 py-3 text-xs leading-relaxed border font-sans whitespace-pre-wrap ${
                  isUser 
                    ? "bg-blue-600/10 border-blue-500/30 text-slate-200"
                    : "bg-[#111827] border-slate-800/80 text-slate-300"
                }`}>
                  {m.text}
                </div>
              </div>
            );
          })
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-center py-20 text-slate-600">
            <Bot className="h-10 w-10 text-slate-700 mb-2 animate-bounce" />
            <span className="text-xs max-w-[240px] leading-relaxed">
              Workspace Mentor Active. Paste code or ask about linked lists, trees, complexity, or design patterns to begin!
            </span>
          </div>
        )}

        {assistantLoading && (
          <div className="flex gap-3 max-w-[80%] mr-auto">
            <div className="p-2 rounded-xl bg-slate-900 border border-slate-800 text-slate-400 h-8 w-8 shrink-0 flex items-center justify-center">
              <Bot className="h-4 w-4 animate-spin text-blue-400" />
            </div>
            <div className="rounded-2xl px-4 py-3 text-xs bg-[#111827] border border-slate-800/80 text-slate-500 animate-pulse font-mono font-semibold">
              Evaluating parameters...
            </div>
          </div>
        )}
      </div>

      {/* 3. Chat Input Box */}
      <div className="shrink-0 flex items-center gap-3 bg-[#111827] border border-slate-800/80 rounded-2xl p-3 shadow-lg">
        <input
          value={assistantInput}
          onChange={(e) => setAssistantInput(e.target.value)}
          placeholder="Ask me to explain code, dry-run pointers, or give a quiz..."
          className="flex-grow bg-transparent text-xs text-slate-200 outline-none placeholder:text-slate-500 font-mono px-2"
          onKeyDown={(e) => {
            if (e.key === "Enter") {
              sendAssistantMessage();
            }
          }}
        />
        
        {/* Speech Recognition Toggle */}
        <button
          onClick={onToggleSpeech}
          className={`p-2 rounded-xl border transition ${
            isListening
              ? "bg-rose-500/10 border-rose-500/20 text-rose-400 animate-pulse"
              : "bg-slate-900 border-slate-800 text-slate-400 hover:text-white"
          }`}
          title={isListening ? "Listening... Click to stop" : "Voice dictation"}
        >
          {isListening ? <Mic className="h-4 w-4" /> : <Mic className="h-4 w-4" />}
        </button>

        <button
          onClick={sendAssistantMessage}
          disabled={assistantLoading || !assistantInput.trim()}
          className="rounded-xl bg-blue-600 hover:bg-blue-700 px-4 py-2.5 text-xs font-bold text-white shadow-md hover:shadow-lg transition-all duration-300 disabled:opacity-50 flex items-center gap-1.5"
        >
          <Send className="h-3.5 w-3.5" />
          <span>Send</span>
        </button>
      </div>
    </motion.div>
  );
}
