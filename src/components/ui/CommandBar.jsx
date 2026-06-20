import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Search,
  Code2,
  ShieldAlert,
  FolderKanban,
  MessageSquareCode,
  GraduationCap,
  FileText,
  Terminal,
  Zap,
} from "lucide-react";

const COMMANDS = [
  {
    id: "review",
    title: "Run Quality & SMELL Review",
    subtitle: "Triggers local 20-class ensemble neural code linter",
    icon: Code2,
    shortcut: "/review",
    category: "Developer Core",
  },
  {
    id: "security",
    title: "Audit CWE & OWASP Security",
    subtitle: "Scan repository for dangerous injections and secrets",
    icon: ShieldAlert,
    shortcut: "/security",
    category: "Developer Core",
  },
  {
    id: "graph",
    title: "Focus Dependency Knowledge Graph",
    subtitle: "Render local module dependencies and coupling links",
    icon: FolderKanban,
    shortcut: "/graph",
    category: "Visualization",
  },
  {
    id: "chat",
    title: "Open Autonomous AI Assistant Chat",
    subtitle: "Discuss AST structure and class refactoring plans",
    icon: MessageSquareCode,
    shortcut: "/chat",
    category: "AI Agentic",
  },
  {
    id: "courses",
    title: "Navigate Interactive Academy",
    subtitle: "Launch local interactive coding tutorials and lessons",
    icon: GraduationCap,
    shortcut: "/courses",
    category: "Education",
  },
  {
    id: "docs",
    title: "Read Developer Specifications",
    subtitle: "View comprehensive offline API reference guides",
    icon: FileText,
    shortcut: "/docs",
    category: "Education",
  },
];

export default function CommandBar({ isOpen, onClose, onExecuteCommand }) {
  const [search, setSearch] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef(null);

  // Focus input when opened
  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      setSearch("");
      setSelectedIndex(0);
    }
  }, [isOpen]);

  // Handle global key events
  useEffect(() => {
    if (!isOpen) return;

    const handleKeyDown = (e) => {
      if (e.key === "Escape") {
        e.preventDefault();
        onClose();
      } else if (e.key === "ArrowDown") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredCommands.length);
      } else if (e.key === "ArrowUp") {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % filteredCommands.length);
      } else if (e.key === "Enter") {
        e.preventDefault();
        if (filteredCommands[selectedIndex]) {
          handleExecute(filteredCommands[selectedIndex]);
        }
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isOpen, search, selectedIndex]);

  const filteredCommands = COMMANDS.filter(
    (cmd) =>
      cmd.title.toLowerCase().includes(search.toLowerCase()) ||
      cmd.subtitle.toLowerCase().includes(search.toLowerCase()) ||
      cmd.shortcut.toLowerCase().includes(search.toLowerCase())
  );

  const handleExecute = (cmd) => {
    onExecuteCommand(cmd.id);
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh]">
          {/* Transparent Backdrop Blur overlay */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-slate-950/70 backdrop-blur-md"
          />

          {/* Dialog Container */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="relative z-10 w-full max-w-xl overflow-hidden rounded-2xl border border-slate-800 bg-slate-900/80 shadow-2xl backdrop-blur-xl"
          >
            {/* Search Input HUD */}
            <div className="flex items-center border-b border-slate-800/80 px-4 py-3.5">
              <Search className="mr-3 h-5 w-5 text-slate-400 shrink-0" />
              <input
                ref={inputRef}
                type="text"
                placeholder="Type a command or search workspace..."
                value={search}
                onChange={(e) => {
                  setSearch(e.target.value);
                  setSelectedIndex(0);
                }}
                className="w-full bg-transparent text-sm text-slate-200 outline-none placeholder:text-slate-500"
              />
              <span className="rounded bg-slate-800 px-2 py-0.5 font-mono text-[10px] text-slate-400">
                ESC
              </span>
            </div>

            {/* List Results */}
            <div className="max-h-[340px] overflow-y-auto p-2">
              {filteredCommands.length > 0 ? (
                <div className="space-y-1">
                  {filteredCommands.map((cmd, idx) => {
                    const isSelected = idx === selectedIndex;
                    const Icon = cmd.icon;
                    return (
                      <div
                        key={cmd.id}
                        onClick={() => handleExecute(cmd)}
                        className={`flex items-center justify-between rounded-xl px-3.5 py-3 cursor-pointer transition-all duration-150 ${
                          isSelected
                            ? "bg-slate-800/80 border-slate-700/60 shadow-inner"
                            : "hover:bg-slate-800/30"
                        }`}
                      >
                        <div className="flex items-center gap-3">
                          <div
                            className={`flex h-9 w-9 items-center justify-center rounded-lg border ${
                              isSelected
                                ? "bg-indigo-500/10 border-indigo-500/30 text-indigo-400"
                                : "bg-slate-800/50 border-slate-700/50 text-slate-400"
                            }`}
                          >
                            <Icon className="h-4.5 w-4.5" />
                          </div>
                          <div>
                            <span className="block text-xs font-semibold text-slate-200">
                              {cmd.title}
                            </span>
                            <span className="block text-[10px] text-slate-400 mt-0.5">
                              {cmd.subtitle}
                            </span>
                          </div>
                        </div>

                        {/* Shortcuts badge */}
                        <div className="flex items-center gap-2">
                          <span className="rounded bg-slate-800/90 border border-slate-700/50 px-2 py-0.5 font-mono text-[9px] text-slate-400">
                            {cmd.shortcut}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <Terminal className="h-8 w-8 text-slate-500 mb-2" />
                  <span className="text-xs text-slate-400">No matching commands found.</span>
                </div>
              )}
            </div>

            {/* Premium Console Footer info */}
            <div className="flex items-center justify-between border-t border-slate-800/80 bg-slate-950/40 px-4 py-2 text-[10px] text-slate-400">
              <div className="flex items-center gap-2">
                <span>↑↓ navigate</span>
                <span>•</span>
                <span>enter select</span>
              </div>
              <div className="flex items-center gap-1">
                <Zap className="h-3 w-3 text-amber-400" />
                <span>APCRE HUD v4.0</span>
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
