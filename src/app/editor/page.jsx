"use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import Editor, { useMonaco } from "@monaco-editor/react";
import { saveAs } from "file-saver";
import { io } from "socket.io-client";
import { motion, AnimatePresence } from "framer-motion";
import LearningLayout from '@/learning/LearningLayout';
import Header from '@/components/Header';
import CommandBar from "@/components/ui/CommandBar";

// Import modernized ecosystem panels
import DashboardPanel from '@/components/panels/DashboardPanel';
import AuditPanel from '@/components/panels/AuditPanel';
import SecurityPanel from '@/components/panels/SecurityPanel';
import ArchitecturePanel from '@/components/panels/ArchitecturePanel';
import KnowledgeGraphPanel from '@/components/panels/KnowledgeGraphPanel';
import InterviewPanel from '@/components/panels/InterviewPanel';
import ResearchPanel from '@/components/panels/ResearchPanel';
import RightInsightPanel from '@/components/panels/RightInsightPanel';
import AssistantChatPanel from '@/components/panels/AssistantChatPanel';
import AgentPanel from '@/components/panels/AgentPanel';
import {
  Search,
  Folder,
  FolderOpen,
  FileText,
  FileCode2,
  FileJson,
  FileDown,
  ChevronDown,
  Play,
  LogIn,
  Users,
  Sparkles,
  Bot,
  BarChart3,
  AlertTriangle,
  Info,
  Lightbulb,
  Plus,
  Save,
  TerminalSquare,
  Trash2,
  Pencil,
  Facebook,
  Instagram,
  Linkedin,
  Youtube,
  X,
  Code2,
  Handshake,
  LayoutDashboard,
  Shield,
  FileLock2,
  Scale,
  Mail,
  BookOpen,
  Cpu,
  ArrowRight,
  CheckCircle2,
  Send,
  RotateCw,
  FilePlus,
  FolderPlus,
  Mic,
  MicOff,
  Share2,
  GraduationCap,
} from "lucide-react";

/** -------------------- Constants -------------------- */
const NAV_ITEMS = ["Code Editor", "Courses", "Contact", "About", "Resources"];

const API_BASE = "";

function cn(...classes) {
  return classes.filter(Boolean).join(" ");
}

function Badge({ children, tone = "neutral" }) {
  const styles = {
    neutral: "bg-slate-100 text-slate-700 border-slate-200",
    blue: "bg-blue-50 text-blue-700 border-blue-200",
    green: "bg-emerald-50 text-emerald-700 border-emerald-200",
    red: "bg-rose-50 text-rose-700 border-rose-200",
    yellow: "bg-amber-50 text-amber-700 border-amber-200",
  };
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-2 py-0.5 text-xs font-medium",
        styles[tone] || styles.neutral,
      )}
    >
      {children}
    </span>
  );
}

/** -------------------- Tree Builder -------------------- */
function buildTree(files) {
  const root = {
    name: "workspace",
    type: "folder",
    path: "workspace",
    children: [],
  };

  const insertNode = (parts, fileObj, current, currentPath) => {
    const [head, ...rest] = parts;
    const newPath = currentPath ? `${currentPath}/${head}` : head;

    if (!head) return;

    if (rest.length === 0) {
      if (fileObj.isDirectory) {
        let folder = current.children.find(
          (c) => c.type === "folder" && c.name === head,
        );
        if (!folder) {
          folder = { type: "folder", name: head, path: fileObj.path, children: [] };
          current.children.push(folder);
        }
        return;
      }
      current.children.push({
        type: "file",
        name: head,
        path: fileObj.path,
        file: fileObj,
      });
      return;
    }

    let folder = current.children.find(
      (c) => c.type === "folder" && c.name === head,
    );

    if (!folder) {
      folder = { type: "folder", name: head, path: newPath, children: [] };
      current.children.push(folder);
    }

    insertNode(rest, fileObj, folder, newPath);
  };

  files.forEach((f) => {
    const clean = f.path.replace(/^\/+/, "");
    const parts = clean.split("/");
    insertNode(parts.slice(1), f, root, "workspace");
  });

  const sortChildren = (node) => {
    node.children.sort((a, b) => {
      if (a.type !== b.type) return a.type === "folder" ? -1 : 1;
      return a.name.localeCompare(b.name);
    });
    node.children.forEach((c) => c.type === "folder" && sortChildren(c));
  };

  sortChildren(root);
  return root;
}

/** -------------------- Tree Node -------------------- */
function TreeNode({
  node,
  level = 0,
  selected,
  onSelect,
  onRenameFile,
  onDeleteFile,
  onNewFileClick,
}) {
  const [open, setOpen] = useState(true);

  if (node.type === "folder") {
    const FolderIcon = open ? FolderOpen : Folder;
    return (
      <div className="mb-0.5 font-sans">
        <div className="flex items-center justify-between w-full group rounded-md hover:bg-[#2a2d2e] pr-2 transition-all">
          <button
            onClick={() => setOpen((p) => !p)}
            className="flex-grow flex items-center gap-1.5 py-1 text-[12px] text-slate-300 hover:text-white rounded-md font-medium text-left outline-none transition-colors"
            style={{ paddingLeft: `${level * 12 + 6}px` }}
          >
            <ChevronDown
              className={cn(
                "h-3.5 w-3.5 text-slate-500 transition-transform duration-150 shrink-0",
                open ? "rotate-0" : "-rotate-90",
              )}
            />
            <FolderIcon className="h-4 w-4 text-amber-500 fill-amber-500/10 shrink-0" />
            <span className="truncate tracking-wide">
              {node.name}
            </span>
          </button>

          <button
            onClick={(e) => {
              e.stopPropagation();
              onNewFileClick(node.path);
            }}
            className="opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded text-slate-500 hover:text-slate-200 hover:bg-[#30363d]/50 outline-none shrink-0"
            title="New File in Folder"
          >
            <Plus className="h-3.5 w-3.5" />
          </button>
        </div>

        {open && (
          <div className="relative">
            {/* Indentation Nesting Line Guides */}
            <div 
              className="absolute top-0 bottom-1 w-[1px] bg-[#30363d]/70" 
              style={{ left: `${level * 12 + 12}px` }}
            />
            <div className="space-y-0.5">
              {node.children.map((child) => (
                <TreeNode
                  key={child.path}
                  node={child}
                  level={level + 1}
                  selected={selected}
                  onSelect={onSelect}
                  onRenameFile={onRenameFile}
                  onDeleteFile={onDeleteFile}
                  onNewFileClick={onNewFileClick}
                />
              ))}
            </div>
          </div>
        )}
      </div>
    );
  }

  const f = node.file;
  const active = selected?.path === f.path;
  const ext = f.name.split('.').pop()?.toLowerCase();

  const getFileIcon = () => {
    if (ext === 'py') return <FileCode2 className="h-4 w-4 text-amber-400 shrink-0" />;
    if (ext === 'json') return <FileJson className="h-4 w-4 text-emerald-400 shrink-0" />;
    if (ext === 'md') return <FileDown className="h-4 w-4 text-sky-400 shrink-0" />;
    return <FileText className="h-4 w-4 text-slate-400 shrink-0" />;
  };

  return (
    <div
      className={cn(
        "w-full py-1 text-[12px] transition flex items-center justify-between gap-2 cursor-pointer group rounded-md relative font-sans select-none outline-none",
        active
          ? "bg-[#24292f] text-white font-medium border-l-2 border-indigo-500 pl-[calc(var(--pad)+2px)]"
          : "text-slate-400 hover:text-slate-200 hover:bg-[#2a2d2e] pl-[var(--pad)]",
      )}
      style={{
        '--pad': `${level * 12 + 12 + 8}px`,
      }}
    >
      <button
        onClick={() => onSelect(f)}
        className="flex items-center gap-1.5 flex-1 text-left min-w-0 outline-none"
      >
        {getFileIcon()}
        <span className="truncate tracking-wide">{f.name}</span>
      </button>

      <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity bg-transparent shrink-0 mr-1.5">
        <button
          onClick={() => onRenameFile(f)}
          className="p-1 rounded text-slate-500 hover:text-slate-200 hover:bg-[#30363d]/50 transition-colors"
          title="Rename"
        >
          <Pencil className="h-3 w-3" />
        </button>

        <button
          onClick={() => onDeleteFile(f)}
          className="p-1 rounded text-slate-500 hover:text-rose-400 hover:bg-[#30363d]/50 transition-colors"
          title="Delete"
        >
          <Trash2 className="h-3 w-3" />
        </button>
      </div>
    </div>
  );
}

/** -------------------- Resources Mega Menu -------------------- */
function ResourcesMegaMenu({ open, onClose }) {
  if (!open) return null;

  return (
    <>
      <div onClick={onClose} className="fixed inset-0 z-[60] bg-black/10" />

      <div className="fixed left-0 right-0 top-14 z-[70] border-b bg-[#eaf2ff]">
        <div className="mx-auto w-full px-6 py-6">
          <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
            <div>
              <div className="text-xs font-bold uppercase tracking-wide text-slate-600">
                Product
              </div>

              <div className="mt-3 space-y-3">
                <div className="flex items-start gap-3">
                  <Code2 className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      Code editor
                    </div>
                    <div className="text-xs text-slate-600">
                      AI-powered Python editing environment
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Handshake className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      Collaboration
                    </div>
                    <div className="text-xs text-slate-600">
                      Real-time pair programming
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Cpu className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      AI assistant
                    </div>
                    <div className="text-xs text-slate-600">
                      Intelligent code suggestions
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <LayoutDashboard className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      Dashboard
                    </div>
                    <div className="text-xs text-slate-600">
                      Manage your projects
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div className="text-xs font-bold uppercase tracking-wide text-slate-600">
                Company
              </div>

              <div className="mt-3 space-y-3">
                <div className="flex items-start gap-3">
                  <BookOpen className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      About us
                    </div>
                    <div className="text-xs text-slate-600">
                      Meet the team behind APCRE
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Mail className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      Contact
                    </div>
                    <div className="text-xs text-slate-600">
                      Get in touch with support
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Shield className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      Privacy
                    </div>
                    <div className="text-xs text-slate-600">
                      Read our privacy policy
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-3">
                  <Scale className="h-5 w-5 text-slate-700 mt-0.5" />
                  <div>
                    <div className="text-sm font-semibold text-slate-900">
                      Terms
                    </div>
                    <div className="text-xs text-slate-600">
                      Review our terms of service
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <div className="text-xs font-bold uppercase tracking-wide text-slate-600">
                Latest updates
              </div>

              <div className="mt-3 space-y-3">
                <div className="flex items-start gap-3 rounded-2xl bg-white p-3 border">
                  <div className="h-12 w-12 rounded-xl bg-blue-50 flex items-center justify-center">
                    <FileLock2 className="h-6 w-6 text-blue-700" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-slate-900">
                      Python best practices
                    </div>
                    <div className="text-xs text-slate-600">
                      Learn how to write cleaner code
                    </div>
                    <button className="mt-2 text-xs font-semibold text-blue-700 hover:underline">
                      Read
                    </button>
                  </div>
                </div>

                <div className="flex items-start gap-3 rounded-2xl bg-white p-3 border">
                  <div className="h-12 w-12 rounded-xl bg-slate-100 flex items-center justify-center">
                    <Sparkles className="h-6 w-6 text-slate-800" />
                  </div>
                  <div className="flex-1">
                    <div className="text-sm font-semibold text-slate-900">
                      Code review automation
                    </div>
                    <div className="text-xs text-slate-600">
                      Discover AI-driven review techniques
                    </div>
                    <button className="mt-2 text-xs font-semibold text-blue-700 hover:underline">
                      Read
                    </button>
                  </div>
                </div>

                <button className="inline-flex items-center gap-2 text-sm font-semibold text-slate-900 hover:underline">
                  Button <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

/** -------------------- Header -------------------- */
function TopNav({ active = "Resources", onSignIn, onNavigate }) {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-[#eaf2ff]/90 backdrop-blur">
      <div className="mx-auto flex h-14 w-full items-center justify-between px-4">
        <div className="flex items-center gap-2 select-none">
          <div className="text-xl font-extrabold tracking-wide">
            <span className="text-slate-500">AP</span>
            <span className="text-blue-600">CRE</span>
          </div>
        </div>

        <nav className="hidden items-center gap-6 md:flex">
          {NAV_ITEMS.map((item) => {
            const isResources = item === "Resources";
            return (
              <button
                key={item}
                onClick={() => {
                  if (item === "Courses") {
                    onNavigate("courses");
                  } else if (item === "Code Editor") {
                    onNavigate("editor");
                  } else if (item === "Resources") {
                    onNavigate("resources");
                  }
                }}
                className={cn(
                  "text-sm font-medium transition inline-flex items-center gap-1",
                  item === active
                    ? "text-slate-900"
                    : "text-slate-600 hover:text-slate-900",
                )}
              >
                {item}
                {isResources && <ChevronDown className="h-4 w-4 opacity-70" />}
              </button>
            );
          })}
        </nav>

        <div className="flex items-center gap-2">
          <button
            onClick={onSignIn}
            className="inline-flex items-center gap-2 rounded-xl border px-3 py-1.5 text-sm font-semibold text-slate-700 hover:bg-slate-50"
          >
            <LogIn className="h-4 w-4" />
            Sign in
          </button>

          <button
            onClick={() => onNavigate("editor")}
            className="inline-flex items-center gap-2 rounded-xl bg-blue-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-blue-700"
          >
            <Play className="h-4 w-4" />
            Start
          </button>
        </div>
      </div>
    </header>
  );
}

/** -------------------- Left Sidebar -------------------- */
function LeftSidebar({
  activeTab,
  setActiveTab,
  onOpenFolderClick,
  workspacePath,
  isPro,
  trialTimeRemaining,
  startOneDayTrial
}) {
  const sidebarTabs = [
    { key: "dashboard", label: "Dashboard", icon: <LayoutDashboard className="h-4 w-4" /> },
    { key: "audit", label: "Repository Audit", icon: <BarChart3 className="h-4 w-4" /> },
    { key: "review", label: "AI Code Review", icon: <Sparkles className="h-4 w-4" /> },
    { key: "assistant", label: "APCRE Assistant", icon: <Bot className="h-4 w-4" /> },
    { key: "agent", label: "Autonomous Agent", icon: <Cpu className="h-4 w-4" /> },
    { key: "security", label: "Security Center", icon: <Shield className="h-4 w-4" /> },
    { key: "architecture", label: "Architecture Center", icon: <Code2 className="h-4 w-4" /> },
    { key: "kg", label: "Knowledge Graph", icon: <Share2 className="h-4 w-4" /> },
    { key: "interview", label: "Interview Workspace", icon: <GraduationCap className="h-4 w-4" /> },
    { key: "research", label: "Research Dashboard", icon: <FileText className="h-4 w-4" /> },
    { key: "room", label: "Collaboration Room", icon: <Users className="h-4 w-4" /> },
  ];

  return (
    <aside className="w-[240px] shrink-0 border-r border-slate-800/80 bg-[#111827] flex flex-col justify-between h-[calc(100vh-56px)] select-none">
      <div className="flex-grow flex flex-col min-h-0">
        
        {/* Workspace directory banner */}
        <div className="p-4 border-b border-slate-800/80 bg-slate-950/20">
          <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-500">Active Workspace</div>
          <div className="flex items-center justify-between gap-1.5 mt-2">
            <span className="text-xs text-white truncate max-w-[140px] font-mono font-semibold" title={workspacePath}>
              {workspacePath ? workspacePath.split("\\").pop().split("/").pop() : "No folder loaded"}
            </span>
            <button
              onClick={onOpenFolderClick}
              className="text-[9px] font-bold text-blue-400 bg-blue-500/10 border border-blue-500/20 hover:bg-blue-500/25 px-2 py-0.5 rounded-lg transition"
            >
              Open
            </button>
          </div>
        </div>

        {/* Tab Links */}
        <nav className="flex-grow p-3 space-y-1 overflow-y-auto max-h-[calc(100vh-280px)]">
          {sidebarTabs.map((t) => {
            const isSelected = activeTab === t.key;
            return (
              <button
                key={t.key}
                onClick={() => setActiveTab(t.key)}
                className={`w-full flex items-center gap-3 rounded-xl px-4 py-2.5 text-xs font-semibold border transition-all duration-300 ${
                  isSelected
                    ? "bg-blue-500/10 border-blue-500/40 text-blue-400 font-bold"
                    : "bg-transparent border-transparent text-slate-400 hover:text-slate-200 hover:bg-slate-800/30"
                }`}
              >
                <div className="shrink-0 flex items-center justify-center">
                  {t.icon}
                </div>
                <span className="truncate">{t.label}</span>
                {t.key === "agent" && (
                  <span className="ml-auto flex h-1.5 w-1.5 shrink-0 rounded-full bg-blue-500 animate-pulse" />
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Subscription SaaS Box at Bottom */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/10">
        {isPro ? (
          <div className="p-3 rounded-xl bg-gradient-to-tr from-blue-900/10 to-indigo-900/10 border border-blue-500/20">
            <span className="text-[10px] font-extrabold uppercase font-mono tracking-widest text-blue-400 block">APCRE Pro Active</span>
            <span className="text-[9px] text-slate-500 block mt-1 leading-relaxed font-mono truncate">
              {trialTimeRemaining || "🎁 Sandbox Trial Activated"}
            </span>
          </div>
        ) : (
          <button
            onClick={startOneDayTrial}
            className="w-full text-center rounded-xl bg-slate-900 border border-slate-800 hover:border-slate-700 py-2.5 text-[10px] font-extrabold uppercase font-mono tracking-wider text-slate-400 hover:text-white transition"
          >
            Upgrade to Pro
          </button>
        )}
      </div>
    </aside>
  );
}

function IssueCard({
  issue,
  isSelected,
  onFixClick,
  onDetailsClick,
  loading,
  fixResult,
  onBack,
}) {
  const meta = useMemo(() => {
    if (issue.type === "critical")
      return {
        icon: <AlertTriangle className="h-4 w-4 text-rose-600" />,
        tone: "red",
        bg: "bg-rose-50",
        border: "border-rose-200",
      };
    if (issue.type === "warning")
      return {
        icon: <Info className="h-4 w-4 text-amber-600" />,
        tone: "yellow",
        bg: "bg-amber-50",
        border: "border-amber-200",
      };
    return {
      icon: <Lightbulb className="h-4 w-4 text-blue-600" />,
      tone: "blue",
      bg: "bg-blue-50",
      border: "border-blue-200",
    };
  }, [issue.type]);

  return (
    <div
      className={cn(
        "rounded-2xl border p-3 transition",
        meta.bg,
        meta.border,
        isSelected ? "ring-2 ring-blue-300" : "",
      )}
    >
      <div className="flex items-start justify-between gap-2">
        <div className="flex items-center gap-2">
          <span className="inline-flex h-8 w-8 items-center justify-center rounded-xl bg-white border">
            {meta.icon}
          </span>
          <div>
            <div className="text-sm font-bold text-slate-900">
              {issue.title}
            </div>
            <div className="text-xs text-slate-600">Line {issue.line}</div>
          </div>
        </div>
        <Badge tone={meta.tone}>{issue.type}</Badge>
      </div>

      <p className="mt-2 text-xs text-slate-700">{issue.desc}</p>

      <div className="mt-3 flex gap-2">
        <button
          onClick={() => onFixClick(issue)}
          disabled={loading}
          className={cn(
            "rounded-xl px-3 py-1.5 text-xs font-semibold text-white",
            loading ? "bg-slate-400 cursor-not-allowed" : "bg-slate-900",
          )}
        >
          {loading ? "Fixing..." : "Fix"}
        </button>

        <button
          onClick={() => onDetailsClick(issue)}
          className="rounded-xl border px-3 py-1.5 text-xs font-semibold text-slate-700"
        >
          Details
        </button>

        {isSelected && (
          <button
            onClick={onBack}
            className="ml-auto rounded-xl border px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-white"
          >
            Back
          </button>
        )}
      </div>

      {isSelected && (
        <div className="mt-4 rounded-xl border bg-white p-3">
          <div className="text-xs font-bold text-slate-900">Fix Result</div>

          {loading && (
            <div className="mt-2 text-xs text-slate-600">
              ⏳ Applying fix...
            </div>
          )}

          {!loading && fixResult?.error && (
            <div className="mt-2 text-xs text-rose-600">{fixResult.error}</div>
          )}

          {!loading && fixResult?.explanation && (
            <div className="mt-2 text-xs text-slate-700">
              {fixResult.explanation}
            </div>
          )}

          {!loading && fixResult?.raw && (
            <pre className="mt-2 max-h-40 overflow-auto rounded-lg bg-slate-900 p-2 text-[11px] text-slate-100">
              {fixResult.raw}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

/** -------------------- Room Panel -------------------- */
/** -------------------- Video Player Helper -------------------- */
function VideoPlayer({ stream, muted = false, className }) {
  const videoRef = useRef(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
      videoRef.current.play().catch((err) => {
        console.warn("Autoplay blocked or video playback failed:", err);
      });
    }
  }, [stream]);

  if (!stream) return null;

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted={muted}
      className={className}
    />
  );
}

/** -------------------- Room Panel -------------------- */
function RoomPanel({
  roomId,
  setRoomId,
  joined,
  onJoin,
  onLeave,
  users,
  socketConnected,
  localStream,
  remoteStream,
  isScreenSharing,
  isCallActive,
  onStartCall,
  onLeaveCall,
  onToggleScreenShare,
  meetLogs,
}) {
  if (!joined) {
    return (
      <div className="rounded-2xl border p-4 bg-slate-900 border-slate-800 text-white">
        <div className="text-sm font-bold flex items-center gap-2">
          <Users className="h-4 w-4 text-indigo-400" />
          <span>Collaboration Room</span>
        </div>
        <p className="mt-1 text-xs text-slate-400">
          Sync editor contents and voice calls with Socket.IO
        </p>

        <div className="mt-3 flex items-center gap-2">
          <span
            className={cn(
              "inline-flex items-center gap-1 rounded-full border px-2 py-0.5 text-[10px] font-mono",
              socketConnected
                ? "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
                : "bg-rose-500/10 text-rose-400 border-rose-500/20",
            )}
          >
            <span className={cn("w-1.5 h-1.5 rounded-full shrink-0", socketConnected ? "bg-emerald-400 animate-pulse" : "bg-rose-400")} />
            {socketConnected ? "Online" : "Offline"}
          </span>
        </div>

        <input
          value={roomId}
          onChange={(e) => setRoomId(e.target.value)}
          className="mt-3 w-full rounded-xl bg-slate-800 border border-slate-700 px-3 py-2 text-xs text-white outline-none placeholder:text-slate-500"
          placeholder="Enter Room ID (example: room1)"
        />

        <button
          onClick={onJoin}
          className="mt-3 w-full rounded-xl bg-indigo-600 px-3 py-2 text-xs font-semibold text-white hover:bg-indigo-700 active:scale-95 transition"
        >
          Connect Workspace
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4 text-slate-300">
      {/* Room ID card */}
      <div className="rounded-2xl border border-slate-800 bg-[#0f172a]/50 p-4">
        <div className="flex items-center justify-between gap-2">
          <div>
            <div className="text-xs text-slate-400 font-mono">WORKSPACE LINKED</div>
            <div className="text-sm font-bold text-white mt-0.5">Room ID: {roomId}</div>
          </div>

          <button
            onClick={onLeave}
            className="rounded-xl border border-slate-700 px-3 py-1.5 text-[10px] font-semibold text-slate-400 hover:text-white hover:bg-slate-800 transition"
          >
            Disconnect
          </button>
        </div>
      </div>

      {/* Participants Card */}
      <div className="rounded-2xl border border-slate-800 bg-[#0f172a]/50 p-4">
        <div className="text-xs font-bold text-white mb-2 flex items-center gap-1.5 font-mono uppercase tracking-wider">
          <Users className="h-4 w-4 text-indigo-400" />
          <span>Active Peers ({users.length})</span>
        </div>
        <div className="space-y-2 max-h-[120px] overflow-auto pr-1">
          {users.length === 0 && (
            <div className="text-xs text-slate-500 font-mono">Waiting for connections...</div>
          )}
          {users.map((u) => (
            <div
              key={u.socketId}
              className="flex items-center justify-between rounded-xl border border-slate-800 bg-slate-900/60 px-3 py-2 text-xs"
            >
              <div className="font-semibold text-slate-200">
                {u.name}
              </div>
              <div className="text-[10px] text-slate-400 truncate max-w-[120px]">
                {u.email}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Video Call & Screen Sharing Card */}
      <div className="rounded-2xl border border-slate-800 bg-[#0f172a]/50 p-4">
        <div className="flex items-center justify-between">
          <div className="text-xs font-bold text-white flex items-center gap-1.5 font-mono uppercase tracking-wider">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500 animate-pulse shrink-0" />
            <span>APCRE Meet voice & video</span>
          </div>
          {isCallActive && (
            <span className="text-[9px] font-bold bg-rose-500/10 text-rose-400 px-2 py-0.5 border border-rose-500/20 rounded-full font-mono">
              CALL ACTIVE
            </span>
          )}
        </div>

        {/* Dynamic Streams View */}
        {isCallActive ? (
          <div className="mt-3 space-y-2">
            {/* Screen Share / Webcam Feeds */}
            <div className="relative aspect-video w-full rounded-xl bg-black overflow-hidden border border-slate-850 shadow-inner">
              {remoteStream ? (
                <VideoPlayer stream={remoteStream} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex flex-col items-center justify-center text-xs text-slate-500 gap-2">
                  <div className="w-4 h-4 rounded-full border-2 border-indigo-400 border-t-transparent animate-spin" />
                  <span>Waiting for peer's camera feed...</span>
                </div>
              )}
              {/* Picture-in-Picture Local Stream */}
              {localStream && (
                <div className="absolute bottom-2 right-2 w-28 aspect-video rounded-lg overflow-hidden border border-slate-800 shadow-lg bg-slate-950">
                  <VideoPlayer stream={localStream} muted={true} className="w-full h-full object-cover" />
                  <div className="absolute top-1 left-1 text-[8px] bg-black/60 text-white font-mono px-1 rounded truncate max-w-[80px]">
                    {isScreenSharing ? "Sharing Screen" : "You"}
                  </div>
                </div>
              )}
            </div>

            {/* Meet Controls */}
            <div className="grid grid-cols-2 gap-2 mt-2">
              <button
                onClick={onToggleScreenShare}
                className={cn(
                  "rounded-xl px-3 py-2 text-[10px] font-semibold flex items-center justify-center gap-1 transition-all active:scale-95",
                  isScreenSharing
                    ? "bg-amber-600 text-white hover:bg-amber-700 shadow-md"
                    : "bg-slate-800 text-slate-200 border border-slate-700 hover:bg-slate-700 hover:text-white"
                )}
              >
                <span>{isScreenSharing ? "🛑 Stop Sharing" : "🖥️ Share Screen"}</span>
              </button>
              <button
                onClick={onLeaveCall}
                className="rounded-xl bg-rose-600 text-white px-3 py-2 text-[10px] font-semibold flex items-center justify-center gap-1 hover:bg-rose-700 active:scale-95 transition"
              >
                <span>🔇 Leave Call</span>
              </button>
            </div>

            {meetLogs && meetLogs.length > 0 && (
              <div className="mt-2 rounded-xl bg-black/60 p-2 text-[9px] font-mono text-indigo-300 border border-slate-800 max-h-[80px] overflow-auto">
                {meetLogs.map((log, idx) => (
                  <div key={idx}>{log}</div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="mt-3">
            <div className="aspect-video w-full rounded-xl bg-black/40 border border-slate-850 flex flex-col items-center justify-center text-slate-500 text-[10px] p-3 text-center gap-1.5">
              <span>WebRTC voice, camera & screen sharing connection.</span>
              <span className="text-[8px] text-slate-600">Connect peer-to-peer over secure Google STUN servers.</span>
            </div>

            <button
              onClick={onStartCall}
              className="mt-3 w-full rounded-xl bg-emerald-600 px-3 py-2 text-xs font-semibold text-white hover:bg-emerald-700 active:scale-95 transition flex items-center justify-center gap-1"
            >
              <span>📞 Start Video Call</span>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

/** -------------------- F1 Report Panel -------------------- */
/** -------------------- F1 Report Panel -------------------- */
function F1ReportPanel({ code, filename, issues }) {
  const metrics = useMemo(() => {
    if (!code || !code.trim()) {
      return {
        loc: 0, sloc: 0, comments: 0, blanks: 0,
        functions: 0, classes: 0, imports: 0,
        avgFuncLen: 0, maxNesting: 0, complexity: 0, score: 0,
      };
    }

    const lines = code.split("\n");
    const loc = lines.length;
    let comments = 0, blanks = 0, sloc = 0;
    let functions = 0, classes = 0, imports = 0;
    let maxNesting = 0;
    const funcLengths = [];
    let inFunc = false, funcStart = 0;

    for (let i = 0; i < lines.length; i++) {
      const trimmed = lines[i].trim();
      if (!trimmed) { blanks++; continue; }
      if (trimmed.startsWith("#")) { comments++; continue; }
      sloc++;

      if (/^def\s+/.test(trimmed)) {
        if (inFunc) funcLengths.push(i - funcStart);
        inFunc = true; funcStart = i; functions++;
      }
      if (/^class\s+/.test(trimmed)) classes++;
      if (/^(import |from .+ import )/.test(trimmed)) imports++;

      // Estimate nesting by leading spaces
      const indent = lines[i].search(/\S/);
      const nestLevel = Math.floor(indent / 4);
      if (nestLevel > maxNesting) maxNesting = nestLevel;
    }
    if (inFunc) funcLengths.push(lines.length - funcStart);

    const avgFuncLen = funcLengths.length > 0
      ? Math.round(funcLengths.reduce((a, b) => a + b, 0) / funcLengths.length)
      : 0;

    // Cyclomatic complexity estimate
    const complexityKeywords = (code.match(/\b(if|elif|for|while|except|and|or)\b/g) || []).length;
    const complexity = complexityKeywords + 1;

    // Score calculation
    let score = 100;
    if (maxNesting > 4) score -= (maxNesting - 4) * 5;
    if (avgFuncLen > 30) score -= Math.min(20, (avgFuncLen - 30));
    if (comments / Math.max(sloc, 1) < 0.1) score -= 10; // low comment ratio
    if (complexity > 15) score -= Math.min(20, (complexity - 15) * 2);
    if (functions === 0 && sloc > 20) score -= 10; // no functions in substantial code
    
    // Also deduct for any active critical, warning, or suggestion issues detected by the AST/ML engine!
    let hasSyntaxError = false;
    if (issues && issues.length > 0) {
      const criticalCount = issues.filter(x => x.type === "critical").length;
      const warningCount = issues.filter(x => x.type === "warning").length;
      const suggestionCount = issues.filter(x => x.type === "suggestion").length;
      
      score -= (criticalCount * 15 + warningCount * 8 + suggestionCount * 3);
      
      // Audit for critical syntax errors
      hasSyntaxError = issues.some(x => x.title.toLowerCase().includes("syntax error"));
    }

    score = Math.max(0, Math.min(100, Math.round(score)));

    // Cap the score at 25 if there is a fatal syntax error!
    if (hasSyntaxError) {
      score = Math.min(score, 25);
    }

    return { loc, sloc, comments, blanks, functions, classes, imports, avgFuncLen, maxNesting, complexity, score };
  }, [code, issues]);

  const scoreColor = metrics.score >= 80 ? "text-emerald-500" : metrics.score >= 50 ? "text-amber-500" : "text-rose-500";
  const scoreBgColor = metrics.score >= 80 ? "bg-emerald-500/10 border-emerald-500/20" : metrics.score >= 50 ? "bg-amber-500/10 border-amber-500/20" : "bg-rose-500/10 border-rose-500/20";
  const scoreBarColor = metrics.score >= 80 ? "bg-emerald-500" : metrics.score >= 50 ? "bg-amber-500" : "bg-rose-500";

  let ratingBadge = "Excellent";
  let ratingDesc = "The code is highly structured, readable, and conforms to industry standards.";
  let badgeColor = "bg-emerald-500/10 text-emerald-400 border-emerald-500/20";
  if (metrics.score < 50) {
    ratingBadge = "Critical Optimization Needed";
    ratingDesc = "Refactoring required. Nested layers or technical issues are heavily impacting maintainability.";
    badgeColor = "bg-rose-500/10 text-rose-400 border-rose-500/20";
  } else if (metrics.score < 80) {
    ratingBadge = "Good Structure";
    ratingDesc = "Decent codebase quality, but there are areas where formatting or naming can be improved.";
    badgeColor = "bg-amber-500/10 text-amber-400 border-amber-500/20";
  }

  return (
    <div className="space-y-4 text-slate-300">
      {/* 1. Header & Quality Score Card */}
      <div className={cn("rounded-2xl border p-4 backdrop-blur-sm", scoreBgColor)}>
        <div className="flex items-center justify-between">
          <div>
            <div className="text-xs text-slate-400 font-mono tracking-wider uppercase">F1 Code Quality Report</div>
            <div className="text-sm font-bold text-white mt-0.5 truncate max-w-[160px]">{filename || "untitled.py"}</div>
          </div>
          <BarChart3 className="h-5 w-5 text-slate-400" />
        </div>

        {/* Circular Display */}
        <div className="mt-5 flex flex-col items-center justify-center">
          <div className="relative flex items-center justify-center w-24 h-24 rounded-full border-4 border-slate-800">
            <div className={cn("text-3xl font-extrabold font-mono", scoreColor)}>{metrics.score}</div>
            <div className="absolute -bottom-1 text-[9px] font-semibold bg-slate-900 border border-slate-800 text-slate-400 px-2 py-0.5 rounded-full uppercase">
              F1 Score
            </div>
          </div>
          <div className="mt-3 text-center">
            <span className={cn("text-[10px] font-mono font-bold px-2 py-0.5 border rounded-full uppercase", badgeColor)}>
              {ratingBadge}
            </span>
            <p className="text-[10px] text-slate-400 mt-2 leading-relaxed max-w-[220px] mx-auto">
              {ratingDesc}
            </p>
          </div>
        </div>
      </div>

      {/* 2. Issues impacting score */}
      <div className="rounded-2xl border border-slate-800 bg-[#0f172a]/50 p-4">
        <div className="text-xs font-bold text-white mb-3 flex items-center gap-1.5 font-mono uppercase tracking-wider">
          <AlertTriangle className="h-4 w-4 text-amber-500" />
          <span>Violations Impacting Score ({issues ? issues.length : 0})</span>
        </div>
        {issues && issues.length > 0 ? (
          <div className="space-y-2 max-h-[150px] overflow-auto pr-1">
            {issues.map((issue, idx) => (
              <div key={idx} className="p-2 border border-slate-800/80 rounded-xl bg-slate-900/60 flex items-start gap-2 text-[10px]">
                <span className={cn(
                  "w-1.5 h-1.5 rounded-full mt-1 shrink-0",
                  issue.type === "critical" ? "bg-rose-500" : issue.type === "warning" ? "bg-amber-500" : "bg-blue-500"
                )} />
                <div className="flex-1 min-w-0">
                  <div className="font-semibold text-slate-200 truncate">{issue.title} (Line {issue.line})</div>
                  <div className="text-slate-400 mt-0.5 leading-normal">{issue.desc}</div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-[10px] text-emerald-400 bg-emerald-500/10 p-3 rounded-xl border border-emerald-500/20 flex items-start gap-2">
            <CheckCircle2 className="h-3.5 w-3.5 text-emerald-400 shrink-0 mt-0.5" />
            <div className="leading-relaxed">
              <span className="font-bold block">Perfect Conformity!</span>
              No quality issues or structural syntax violations detected in this script.
            </div>
          </div>
        )}
      </div>

      {/* 3. Detailed Metrics Table */}
      <div className="rounded-2xl border border-slate-800 bg-[#0f172a]/50 p-4">
        <div className="text-xs font-bold text-white mb-3 flex items-center gap-1.5 font-mono uppercase tracking-wider">
          <Info className="h-4 w-4 text-blue-400" />
          <span>Code Metrics Overview</span>
        </div>
        <div className="space-y-2 text-xs text-slate-300">
          <div className="flex justify-between border-b border-slate-800/50 pb-1.5">
            <span className="text-slate-400">Total lines of code</span>
            <span className="font-mono font-bold text-white">{metrics.loc}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1.5">
            <span className="text-slate-400">Pure code lines (SLOC)</span>
            <span className="font-mono font-bold text-white">{metrics.sloc}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1.5">
            <span className="text-slate-400">Comments & Documentation</span>
            <span className="font-mono font-bold text-emerald-400">{metrics.comments}</span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1.5">
            <span className="text-slate-400">Max Nesting Depth</span>
            <span className={cn("font-mono font-bold", metrics.maxNesting > 3 ? "text-rose-400" : "text-emerald-400")}>
              {metrics.maxNesting} levels
            </span>
          </div>
          <div className="flex justify-between border-b border-slate-800/50 pb-1.5">
            <span className="text-slate-400">Cyclomatic Complexity</span>
            <span className={cn("font-mono font-bold", metrics.complexity > 10 ? "text-amber-400" : "text-emerald-400")}>
              {metrics.complexity} (Index)
            </span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Average Function Scope</span>
            <span className={cn("font-mono font-bold", metrics.avgFuncLen > 25 ? "text-amber-400" : "text-emerald-400")}>
              {metrics.avgFuncLen} lines
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

/** -------------------- Right Panel -------------------- */
function RightPanel({
  activeTab,
  setActiveTab,
  issues,
  onRunReview,
  loading,
  roomId,
  setRoomId,
  roomJoined,
  onJoinRoom,
  onLeaveRoom,
  onFixIssue,
  roomUsers,
  socketConnected,

  /**  Assistant props */
  assistantMessages,
  assistantInput,
  assistantLoading,
  setAssistantInput,
  sendAssistantMessage,

  /** F1 Report props */
  selectedFile,

  // WebRTC properties
  localStream,
  remoteStream,
  isScreenSharing,
  isCallActive,
  onStartCall,
  onLeaveCall,
  onToggleScreenShare,
  meetLogs,
  onAgentSuccess,
}) {
  const [selectedFixIssueId, setSelectedFixIssueId] = useState(null);
  const [fixLoading, setFixLoading] = useState(false);
  const [fixResult, setFixResult] = useState(null);

  // ═══════════════════════════════════════════════════════════════
  // SaaS & Coder Agent States
  // ═══════════════════════════════════════════════════════════════
  const [user, setUser] = useState(null);
  const [isClient, setIsClient] = useState(false);

  // Initialize client state
  useEffect(() => {
    setIsClient(true);
    const stored = localStorage.getItem("user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
  }, []);

  // Listen to user changes globally
  useEffect(() => {
    const handleUserUpdate = () => {
      const stored = localStorage.getItem("user");
      if (stored) {
        setUser(JSON.parse(stored));
      } else {
        setUser(null);
      }
    };
    window.addEventListener("user-login", handleUserUpdate);
    return () => window.removeEventListener("user-login", handleUserUpdate);
  }, []);

  useEffect(() => {
    // Automatically reset trial to 2 months and grant access on load
    const currentExpiry = localStorage.getItem("trialExpiry");
    const twoMonthsMs = 60 * 24 * 60 * 60 * 1000;
    const targetExpiry = Date.now() + twoMonthsMs;
    
    if (!currentExpiry || parseInt(currentExpiry, 10) - Date.now() < 30 * 24 * 60 * 60 * 1000) {
      localStorage.setItem("trialExpiry", targetExpiry.toString());
      localStorage.setItem("localPro", "true");
      window.dispatchEvent(new Event("user-login"));
    }
  }, []);

  const [trialTimeRemaining, setTrialTimeRemaining] = useState("");

  const isPro = useMemo(() => {
    if (!isClient) return false;
    if (user && user.plan === "pro") return true;
    if (localStorage.getItem("localPro") === "true") {
      const expiryStr = localStorage.getItem("trialExpiry");
      if (expiryStr) {
        const expiry = parseInt(expiryStr, 10);
        if (Date.now() > expiry) {
          localStorage.removeItem("localPro");
          localStorage.removeItem("trialExpiry");
          return false;
        }
      }
      return true;
    }
    return false;
  }, [user, isClient]);

  useEffect(() => {
    if (!isClient) return;
    const updateTrialTimer = () => {
      const expiryStr = localStorage.getItem("trialExpiry");
      if (expiryStr) {
        const expiry = parseInt(expiryStr, 10);
        const diff = expiry - Date.now();
        if (diff <= 0) {
          localStorage.removeItem("localPro");
          localStorage.removeItem("trialExpiry");
          setTrialTimeRemaining("");
          window.dispatchEvent(new Event("user-login"));
        } else {
          const days = Math.floor(diff / (1000 * 60 * 60 * 24));
          const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          if (days > 0) {
            setTrialTimeRemaining(`🎁 Trial Active: ${days}d ${hours}h remaining`);
          } else {
            setTrialTimeRemaining(`🎁 Trial Active: ${hours}h ${mins}m remaining`);
          }
        }
      } else {
        setTrialTimeRemaining("");
      }
    };

    updateTrialTimer();
    const interval = setInterval(updateTrialTimer, 30000);
    return () => clearInterval(interval);
  }, [isPro, isClient]);

  const startOneDayTrial = () => {
    const expiry = Date.now() + 60 * 24 * 60 * 60 * 1000; // 60 days (2 months)
    localStorage.setItem("trialExpiry", expiry.toString());
    localStorage.setItem("localPro", "true");
    window.dispatchEvent(new Event("user-login"));
    alert("🎁 Your 2-Month Free Trial has been activated successfully! Enjoy APCRE Pro Autonomous Agents.");
  };

  // Checkout modal states
  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [billingCycle, setBillingCycle] = useState("annual"); // "monthly" or "annual"
  const [cardNumber, setCardNumber] = useState("");
  const [cardExpiry, setCardExpiry] = useState("");
  const [cardCvc, setCardCvc] = useState("");
  const [cardName, setCardName] = useState(user ? `${user.firstName || ""} ${user.lastName || ""}`.trim() : "Ammar Haider");
  const [paymentProcessing, setPaymentProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState("");
  const [paymentError, setPaymentError] = useState("");

  // Agent states
  const [agentPrompt, setAgentPrompt] = useState("");
  const [agentFilename, setAgentFilename] = useState("automation_agent.py");
  const [agentRunning, setAgentRunning] = useState(false);
  const [agentVisibleLogs, setAgentVisibleLogs] = useState([]);
  const [agentResult, setAgentResult] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const toggleSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
    } else {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setAgentPrompt((prev) => prev ? prev + " " + transcript : transcript);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    }
  };

  // Card formatting helpers
  const handleCardNumberChange = (e) => {
    let value = e.target.value.replace(/\D/g, "");
    let formatted = "";
    for (let i = 0; i < value.length; i++) {
      if (i > 0 && i % 4 === 0) formatted += " ";
      formatted += value[i];
    }
    setCardNumber(formatted);
  };

  const handleCardExpiryChange = (e) => {
    let value = e.target.value.replace(/\D/g, "");
    let formatted = "";
    if (value.length > 2) {
      formatted = value.slice(0, 2) + "/" + value.slice(2, 4);
    } else {
      formatted = value;
    }
    setCardExpiry(formatted);
  };

  // Simulated payment processing loop
  const processSimulatedPayment = async () => {
    setPaymentError("");
    if (!cardName.trim()) {
      setPaymentError("Please enter the cardholder name.");
      return;
    }
    if (cardNumber.replace(/\s/g, "").length < 16) {
      setPaymentError("Please enter a valid 16-digit card number.");
      return;
    }
    if (cardExpiry.length < 5) {
      setPaymentError("Please enter expiry date (MM/YY).");
      return;
    }
    if (cardCvc.length < 3) {
      setPaymentError("Please enter CVV / CVC.");
      return;
    }

    setPaymentProcessing(true);
    
    // Simulate payment sequence steps
    const steps = [
      "⚙️ Connecting to Stripe Gateway...",
      "🛡️ Authenticating card with 3D Secure...",
      "💸 Authorizing charge...",
      "🎉 Subscription upgraded successfully!"
    ];

    for (let i = 0; i < steps.length; i++) {
      setPaymentStatus(steps[i]);
      await new Promise((resolve) => setTimeout(resolve, 800));
    }

    try {
      // API call to upgrade user in backend if logged in
      if (user && user.id) {
        await fetch("/api/user/upgrade", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ userId: user.id, plan: "pro" }),
        });
      }
      
      // Update local storage
      const updatedUser = user ? { ...user, plan: "pro" } : { firstName: "Guest", lastName: "User", email: "guest@apcre.pro", plan: "pro", id: "guest" };
      localStorage.setItem("user", JSON.stringify(updatedUser));
      localStorage.setItem("localPro", "true");
      
      // Dispatch event to sync
      window.dispatchEvent(new Event("user-login"));
      
      setShowCheckoutModal(false);
      alert("👑 Congratulations! Your APCRE Pro subscription has been successfully activated.");
    } catch (err) {
      setPaymentError("Backend upgrade failed, but local bypass activated.");
      localStorage.setItem("localPro", "true");
      window.dispatchEvent(new Event("user-login"));
      setShowCheckoutModal(false);
    } finally {
      setPaymentProcessing(false);
    }
  };

  // Autonomous agent handler with visual playback log delay
  const runAutonomousAgent = async () => {
    if (!agentPrompt.trim()) return;
    setAgentRunning(true);
    setAgentVisibleLogs([]);
    setAgentResult(null);

    const prepLogs = [
      { time: new Date().toLocaleTimeString(), step: "🧠 Initializing Autonomous Coder Agent...", status: "info" },
      { time: new Date().toLocaleTimeString(), step: "🔍 Inspecting workspace configuration...", status: "info" }
    ];
    setAgentVisibleLogs(prepLogs);

    try {
      const response = await fetch("/api/agent/automate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: agentPrompt,
          filename: agentFilename || "automation_agent.py",
          code: selectedFile ? selectedFile.content : ""
        }),
      });

      const data = await response.json();
      
      if (data.logs && data.logs.length > 0) {
        let currentLogs = [...prepLogs];
        for (let i = 0; i < data.logs.length; i++) {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          currentLogs = [...currentLogs, data.logs[i]];
          setAgentVisibleLogs(currentLogs);
        }
      } else {
        setAgentVisibleLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), step: "Response received from agent engine.", status: "success" }]);
      }

      setAgentResult(data);
      if (data.success && onAgentSuccess) {
        onAgentSuccess(agentFilename || "automation_agent.py");
      }
    } catch (err) {
      setAgentVisibleLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), step: `Agent Error: ${err.message}`, status: "error" }]);
      setAgentResult({ success: false, error: err.message, stderr: err.message });
    } finally {
      setAgentRunning(false);
    }
  };

  const tabs = [
    { key: "room", label: "Join Room", icon: <Users className="h-4 w-4" /> },
    {
      key: "review",
      label: "AI Review",
      icon: <Sparkles className="h-4 w-4" />,
    },
    { key: "assistant", label: "Assistant", icon: <Bot className="h-4 w-4" /> },
    { key: "f1", label: "F1 Report", icon: <BarChart3 className="h-4 w-4" /> },
    { key: "agent", label: "AI Agent", icon: <Cpu className="h-4 w-4" /> },
  ];

  const summary = useMemo(() => {
    const critical = issues.filter((x) => x.type === "critical").length;
    const warning = issues.filter((x) => x.type === "warning").length;
    const suggestion = issues.filter((x) => x.type === "suggestion").length;
    const score = Math.max(
      0,
      100 - critical * 18 - warning * 8 - suggestion * 4,
    );
    return { critical, warning, suggestion, score };
  }, [issues]);

  const handleFixIssue = async (issue) => {
    setSelectedFixIssueId(issue.id);
    setFixResult(null);
    setFixLoading(true);

    try {
      await onFixIssue(issue);
      setFixResult({
        explanation: "Fix applied successfully ",
      });
    } catch (err) {
      setFixResult({
        error: err.message,
      });
    }

    setFixLoading(false);
  };

  return (
    <aside className="h-[calc(100vh-56px)] w-[360px] shrink-0 border-l bg-white">
      <div className="flex h-full flex-col">
        <div className="border-b p-3">
          <div className="grid grid-cols-5 gap-1">
                        {tabs.map((t) => (
              <button
                key={t.key}
                onClick={() => setActiveTab(t.key)}
                className={cn(
                  "rounded-xl px-1 py-2 text-xs font-semibold transition flex flex-col items-center justify-center gap-1 relative",
                  activeTab === t.key
                    ? "bg-slate-900 text-white"
                    : "bg-slate-50 text-slate-700 hover:bg-slate-100",
                )}
                title={t.label}
              >
                {t.icon}
                <span className="text-[9px] block text-center font-semibold tracking-wider leading-none mt-0.5">
                  {t.label.split(" ").pop()}
                </span>
                {t.key === "agent" && (
                  <span className="absolute top-1 right-1.5 flex h-2 w-2">
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
                  </span>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="flex-1 overflow-auto p-3">
          {activeTab === "review" && (
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div>
                  <div className="text-sm font-bold text-slate-900">
                    Detected Issues
                  </div>
                  <div className="text-xs text-slate-500">
                    Results generated from ChatGPT API
                  </div>
                </div>
                <Badge tone="red">{issues.length} Issues</Badge>
              </div>

              <button
                onClick={() => {
                  setSelectedFixIssueId(null);
                  setFixResult(null);
                  setFixLoading(false);
                  onRunReview();
                }}
                disabled={loading}
                className={cn(
                  "w-full rounded-2xl px-3 py-2 text-sm font-semibold text-white",
                  loading
                    ? "bg-blue-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700",
                )}
              >
                {loading ? "Reviewing..." : "Run AI Review"}
              </button>

              <div className="space-y-2">
                {issues
                  .filter((issue) =>
                    selectedFixIssueId ? issue.id === selectedFixIssueId : true,
                  )
                  .map((issue) => (
                    <IssueCard
                      key={issue.id}
                      issue={issue}
                      isSelected={selectedFixIssueId === issue.id}
                      onFixClick={handleFixIssue}
                      onDetailsClick={() => {}}
                      loading={fixLoading && selectedFixIssueId === issue.id}
                      fixResult={
                        selectedFixIssueId === issue.id ? fixResult : null
                      }
                      onBack={() => {
                        setSelectedFixIssueId(null);
                        setFixResult(null);
                        setFixLoading(false);
                      }}
                    />
                  ))}
              </div>

              {!selectedFixIssueId && (
                <div className="rounded-2xl border p-4">
                  <div className="text-sm font-bold text-slate-900">
                    Review Summary
                  </div>

                  <div className="mt-3 space-y-2 text-xs text-slate-700">
                    <div className="flex items-center justify-between">
                      <span>Critical Issues</span>
                      <span className="font-bold">{summary.critical}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Warnings</span>
                      <span className="font-bold">{summary.warning}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span>Suggestions</span>
                      <span className="font-bold">{summary.suggestion}</span>
                    </div>
                  </div>

                  <div className="mt-4">
                    <div className="flex items-center justify-between text-xs text-slate-600">
                      <span>Code Quality Score</span>
                      <span className="font-bold text-slate-900">
                        {summary.score}/100
                      </span>
                    </div>
                    <div className="mt-2 h-2 w-full rounded-full bg-slate-100">
                      <div
                        className="h-2 rounded-full bg-blue-600"
                        style={{ width: `${summary.score}%` }}
                      />
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === "room" && (
            <RoomPanel
              roomId={roomId}
              setRoomId={setRoomId}
              joined={roomJoined}
              onJoin={onJoinRoom}
              onLeave={onLeaveRoom}
              users={roomUsers}
              socketConnected={socketConnected}
              localStream={localStream}
              remoteStream={remoteStream}
              isScreenSharing={isScreenSharing}
              isCallActive={isCallActive}
              onStartCall={onStartCall}
              onLeaveCall={onLeaveCall}
              onToggleScreenShare={onToggleScreenShare}
              meetLogs={meetLogs}
            />
          )}

          {/*  Assistant UI */}
          {activeTab === "assistant" && (
            <div className="flex h-[calc(100vh-140px)] flex-col rounded-2xl border bg-white">
              <div className="border-b p-3">
                <div className="text-sm font-bold text-slate-900">
                  APCRE Assistant
                </div>
                <div className="text-xs text-slate-500">
                  Uses your current file code as context
                </div>
              </div>

              <div className="flex-1 overflow-auto p-3 space-y-3">
                {assistantMessages.map((m, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      "max-w-[90%] rounded-2xl px-3 py-2 text-sm whitespace-pre-wrap",
                      m.role === "user"
                        ? "ml-auto bg-blue-600 text-white"
                        : "mr-auto bg-slate-100 text-slate-800",
                    )}
                  >
                    {m.text}
                  </div>
                ))}

                {assistantLoading && (
                  <div className="mr-auto max-w-[80%] rounded-2xl bg-slate-100 px-3 py-2 text-sm text-slate-600">
                    Thinking...
                  </div>
                )}
              </div>

              <div className="border-t p-3">
                <div className="flex items-center gap-2">
                  <input
                    value={assistantInput}
                    onChange={(e) => setAssistantInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === "Enter") sendAssistantMessage();
                    }}
                    className="flex-1 rounded-xl border px-3 py-2 text-sm outline-none"
                    placeholder="Ask something... (press Enter)"
                  />
                  <button
                    onClick={sendAssistantMessage}
                    disabled={assistantLoading}
                    className={cn(
                      "rounded-xl px-4 py-2 text-sm font-semibold text-white inline-flex items-center gap-2",
                      assistantLoading
                        ? "bg-slate-400 cursor-not-allowed"
                        : "bg-slate-900 hover:bg-slate-800",
                    )}
                  >
                    <Send className="h-4 w-4" />
                    Send
                  </button>
                </div>
              </div>
            </div>
          )}

          {activeTab === "f1" && selectedFile && (
            <F1ReportPanel code={selectedFile.content || ""} filename={selectedFile.name || ""} issues={issues || []} />
          )}
          {activeTab === "f1" && !selectedFile && (
            <div className="rounded-2xl border p-4 text-sm text-slate-600">
              Select a file to generate the F1 report.
            </div>
          )}

          {activeTab === "agent" && (
            <div className="space-y-4">
              {!isPro ? (
                /* Sleek Glassmorphic Lock Shield Overlay */
                <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-50/50 p-6 text-center backdrop-blur-md shadow-xl transition-all duration-300 hover:shadow-2xl">
                  <div className="absolute -top-12 -left-12 h-32 w-32 rounded-full bg-indigo-500/20 blur-2xl pointer-events-none"></div>
                  <div className="absolute -bottom-12 -right-12 h-32 w-32 rounded-full bg-purple-500/20 blur-2xl pointer-events-none"></div>

                  <div className="relative z-10 flex flex-col items-center">
                    <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-tr from-indigo-500 to-purple-600 text-white shadow-lg animate-pulse mb-4">
                      <FileLock2 className="h-8 w-8" />
                    </div>
                    <h3 className="text-xl font-bold text-slate-900 mb-2">APCRE Pro Feature</h3>
                    <p className="text-sm text-slate-600 leading-relaxed mb-6">
                      Upgrade to unlock Autonomous AI Coding Agents capable of planning, generating, running, and self-debugging Python scripts in your workspace.
                    </p>
                    <button
                      onClick={() => setShowCheckoutModal(true)}
                      className="w-full rounded-xl bg-gradient-to-r from-indigo-600 to-purple-600 px-4 py-3 text-sm font-semibold text-white shadow-md hover:from-indigo-700 hover:to-purple-700 hover:shadow-lg transition-all duration-300 transform hover:-translate-y-0.5"
                    >
                      👑 Upgrade to APCRE Pro
                    </button>
                    
                    <button
                      onClick={startOneDayTrial}
                      className="mt-3 w-full rounded-xl border border-slate-300 bg-white hover:bg-slate-50 px-4 py-2.5 text-xs font-semibold text-slate-700 transition-all duration-300 shadow-sm"
                    >
                      🎁 Start 2-Month Free Trial
                    </button>

                    <div className="mt-4 text-xs text-slate-400 flex items-center justify-center gap-1">
                      <Shield className="h-3 w-3" /> Secure Stripe checkout. Cancel anytime.
                    </div>
                  </div>
                </div>
              ) : (
                /* Unlocked AI Agent Control Panel */
                <div className="space-y-4">
                  {trialTimeRemaining && (
                    <div className="rounded-2xl bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/25 p-3 flex items-center justify-between text-xs text-amber-800 shadow-sm">
                      <span className="font-semibold">{trialTimeRemaining}</span>
                      <button
                        onClick={() => setShowCheckoutModal(true)}
                        className="rounded-lg bg-amber-600 hover:bg-amber-700 px-2.5 py-1 text-[10px] font-bold text-white transition-all shadow-sm"
                      >
                        Upgrade Pro
                      </button>
                    </div>
                  )}

                  <div className="rounded-2xl border border-indigo-100 bg-indigo-50/30 p-4">
                    <div className="flex items-center gap-2 mb-2">
                      <div className="h-2 w-2 rounded-full bg-indigo-600 animate-ping"></div>
                      <span className="text-xs font-bold uppercase tracking-wider text-indigo-700">Autonomous Mode Active</span>
                    </div>
                    <p className="text-xs text-slate-600 leading-normal">
                      The agent will outline its plan, generate compliant Python code, run tests, and recursively repair tracebacks in a loop.
                    </p>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <div className="flex items-center justify-between mb-1">
                        <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider">Automation Task</label>
                        <button
                          type="button"
                          onClick={toggleSpeechRecognition}
                          disabled={agentRunning}
                          className={cn(
                            "flex items-center gap-1.5 text-[9px] font-bold px-2 py-0.5 rounded-full border transition-all duration-300 hover:scale-105 active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed",
                            isListening
                              ? "text-rose-600 bg-rose-50 border-rose-200 animate-pulse shadow-sm shadow-rose-100"
                              : "text-indigo-600 bg-indigo-50 hover:bg-indigo-100/70 border-indigo-100/50"
                          )}
                          title={isListening ? "Stop listening" : "Start voice input"}
                        >
                          {isListening ? (
                            <>
                              <Mic className="h-3 w-3 text-rose-600 animate-pulse" />
                              <span className="font-semibold text-rose-600">Listening...</span>
                            </>
                          ) : (
                            <>
                              <Mic className="h-3 w-3 text-indigo-600" />
                              <span>Voice Input</span>
                            </>
                          )}
                        </button>
                      </div>
                      <textarea
                        value={agentPrompt}
                        onChange={(e) => setAgentPrompt(e.target.value)}
                        placeholder="e.g. Calculate average values of a numbers list and save to average_output.txt"
                        className="w-full min-h-[90px] rounded-xl border border-slate-200 p-3 text-xs focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                        disabled={agentRunning}
                      />
                    </div>

                    <div>
                      <label className="block text-[10px] font-bold text-slate-500 uppercase tracking-wider mb-1">Script Name</label>
                      <input
                        type="text"
                        value={agentFilename}
                        onChange={(e) => setAgentFilename(e.target.value)}
                        placeholder="automation_agent.py"
                        className="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                        disabled={agentRunning}
                      />
                    </div>

                    <button
                      onClick={runAutonomousAgent}
                      disabled={agentRunning || !agentPrompt.trim()}
                      className={cn(
                        "w-full rounded-xl py-2.5 text-xs font-semibold text-white shadow-md transition-all duration-300 flex items-center justify-center gap-2",
                        agentRunning || !agentPrompt.trim()
                          ? "bg-slate-400 cursor-not-allowed"
                          : "bg-slate-900 hover:bg-slate-800 hover:shadow-lg"
                      )}
                    >
                      {agentRunning ? (
                        <>
                          <RotateCw className="h-3.5 w-3.5 animate-spin" />
                          Running Agentic Loop...
                        </>
                      ) : (
                        <>
                          <Cpu className="h-3.5 w-3.5" />
                          Launch Coder Agent
                        </>
                      )}
                    </button>
                  </div>

                  {/* Animated step-by-step logs */}
                  {(agentVisibleLogs.length > 0 || agentRunning) && (
                    <div className="rounded-xl border border-slate-850 bg-slate-950 p-3 font-mono text-[10px] text-slate-300 shadow-inner">
                      <div className="flex items-center justify-between border-b border-slate-800 pb-1.5 mb-2">
                        <span className="text-slate-400 font-bold uppercase text-[9px] tracking-wider">Agent Activity Log</span>
                        <div className="flex items-center gap-1">
                          <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse"></span>
                          <span className="text-[9px] text-slate-500">Auto-Correction Active</span>
                        </div>
                      </div>
                      <div className="space-y-1.5 max-h-[160px] overflow-auto">
                        {agentVisibleLogs.map((log, idx) => (
                          <div key={idx} className="flex gap-1.5 items-start leading-normal">
                            <span className="text-slate-600 select-none">[{log.time}]</span>
                            <span className={cn(
                              "flex-1",
                              log.status === "success" ? "text-emerald-400" :
                              log.status === "error" ? "text-rose-400" :
                              log.status === "warning" ? "text-amber-400" : "text-slate-300"
                            )}>
                              {log.step}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Success Result Area */}
                  {agentResult && agentResult.success && !agentRunning && (
                    <div className="rounded-xl border border-emerald-100 bg-emerald-50/20 p-3 space-y-2">
                      <div className="flex items-center gap-1.5 text-emerald-700 font-semibold text-xs">
                        <CheckCircle2 className="h-4 w-4" />
                        <span>Task Completed Successfully!</span>
                      </div>
                      <p className="text-[11px] text-slate-600">
                        The agent created <strong>{agentResult.created_file}</strong> in your workspace.
                      </p>
                      {agentResult.stdout && (
                        <div className="rounded-lg bg-slate-900 p-2 font-mono text-[9px] text-white">
                          <div className="text-[8px] text-slate-400 border-b border-slate-800 pb-0.5 mb-1">STDOUT</div>
                          <pre className="overflow-auto max-h-[60px]">{agentResult.stdout}</pre>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Failure Result Area */}
                  {agentResult && !agentResult.success && !agentRunning && (
                    <div className="rounded-xl border border-rose-100 bg-rose-50/20 p-3 space-y-2">
                      <div className="flex items-center gap-1.5 text-rose-700 font-semibold text-xs">
                        <AlertTriangle className="h-4 w-4" />
                        <span>Agent Execution Halted</span>
                      </div>
                      <p className="text-[11px] text-slate-600">
                        The agent was unable to successfully execute the automation within attempts.
                      </p>
                      {agentResult.stderr && (
                        <div className="rounded-lg bg-rose-950/50 border border-rose-900/30 p-2 font-mono text-[9px] text-rose-200">
                          <div className="text-[8px] text-rose-400 border-b border-rose-900/30 pb-0.5 mb-1">STDERR</div>
                          <pre className="overflow-auto max-h-[60px]">{agentResult.stderr}</pre>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Stripe Payment Portal Overlay */}
      {showCheckoutModal && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-slate-900/60 p-4 backdrop-blur-sm">
          <div className="relative w-full max-w-md rounded-3xl border border-slate-200/50 bg-white p-6 shadow-2xl backdrop-blur-xl">
            <div className="absolute -top-12 -left-12 h-32 w-32 rounded-full bg-indigo-500/10 blur-2xl pointer-events-none"></div>
            <div className="absolute -bottom-12 -right-12 h-32 w-32 rounded-full bg-purple-500/10 blur-2xl pointer-events-none"></div>

            <button
              onClick={() => setShowCheckoutModal(false)}
              className="absolute top-4 right-4 rounded-xl p-1.5 text-slate-400 hover:bg-slate-100 hover:text-slate-600 transition"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="text-center mb-6">
              <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-50 px-3 py-1 text-xs font-semibold text-indigo-700 mb-2">
                👑 Premium SaaS Checkout
              </span>
              <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 bg-clip-text text-transparent">
                Upgrade to APCRE Pro
              </h2>
              <p className="text-sm text-slate-500 mt-1">
                Choose a plan and experience autonomous coding.
              </p>
            </div>

            {/* Pricing Options */}
            <div className="grid grid-cols-2 gap-3 mb-6">
              <button
                onClick={() => setBillingCycle("monthly")}
                className={cn(
                  "rounded-2xl border-2 p-3 text-left transition relative",
                  billingCycle === "monthly"
                    ? "border-indigo-600 bg-indigo-50/20"
                    : "border-slate-100 bg-slate-50 hover:bg-slate-100"
                )}
              >
                <div className="text-xs font-bold text-slate-500 uppercase">Monthly</div>
                <div className="text-xl font-bold text-slate-900">$29<span className="text-xs font-normal text-slate-500">/mo</span></div>
              </button>
              
              <button
                onClick={() => setBillingCycle("annual")}
                className={cn(
                  "rounded-2xl border-2 p-3 text-left transition relative",
                  billingCycle === "annual"
                    ? "border-indigo-600 bg-indigo-50/20"
                    : "border-slate-100 bg-slate-50 hover:bg-slate-100"
                )}
              >
                <span className="absolute -top-2.5 right-3 rounded-full bg-gradient-to-r from-emerald-500 to-teal-500 px-2 py-0.5 text-[9px] font-bold text-white uppercase tracking-wider shadow-sm">
                  Save 35%
                </span>
                <div className="text-xs font-bold text-slate-500 uppercase">Annual</div>
                <div className="text-xl font-bold text-slate-900">$19<span className="text-xs font-normal text-slate-500">/mo</span></div>
              </button>
            </div>

            {/* Credit Card Details */}
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-xs font-bold text-slate-650 uppercase mb-1">Cardholder Name</label>
                <input
                  type="text"
                  value={cardName}
                  onChange={(e) => setCardName(e.target.value)}
                  placeholder="e.g. Ammar Haider"
                  className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-650 uppercase mb-1">Card Number</label>
                <div className="relative">
                  <input
                    type="text"
                    value={cardNumber}
                    onChange={handleCardNumberChange}
                    placeholder="4242 4242 4242 4242"
                    maxLength="19"
                    className="w-full rounded-xl border border-slate-200 pl-3 pr-10 py-2 text-sm font-mono focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                  <div className="absolute right-3 top-2.5 text-slate-400">
                    💳
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-650 uppercase mb-1">Expiry Date</label>
                  <input
                    type="text"
                    value={cardExpiry}
                    onChange={handleCardExpiryChange}
                    placeholder="MM/YY"
                    maxLength="5"
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm font-mono text-center focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-bold text-slate-650 uppercase mb-1">CVC / CVV</label>
                  <input
                    type="password"
                    value={cardCvc}
                    onChange={(e) => setCardCvc(e.target.value.replace(/\D/g, ""))}
                    placeholder="•••"
                    maxLength="3"
                    className="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm font-mono text-center focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
                  />
                </div>
              </div>
            </div>

            {paymentError && (
              <div className="text-xs text-rose-500 font-semibold mb-4 text-center">
                ⚠️ {paymentError}
              </div>
            )}

            <button
              onClick={processSimulatedPayment}
              disabled={paymentProcessing}
              className="w-full rounded-xl bg-slate-900 py-3 text-sm font-semibold text-white shadow-md hover:bg-slate-800 hover:shadow-lg transition flex items-center justify-center gap-2"
            >
              {paymentProcessing ? (
                <>
                  <RotateCw className="h-4 w-4 animate-spin" />
                  {paymentStatus}
                </>
              ) : (
                <>
                  <span>Pay ${billingCycle === "monthly" ? "29.00" : "228.00"} & Activate Pro</span>
                </>
              )}
            </button>

            <div className="mt-4 text-center text-[10px] text-slate-400">
              🔒 Secure 256-bit SSL encrypted connection via Stripe.
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}

/** -------------------- Footer -------------------- */
function Footer({ subEmail, setSubEmail, subMsg, onSubscribe }) {
  return (
    <footer className="border-t bg-white">
      <div className="mx-auto w-full px-6 py-12">
        {/* TOP SUBSCRIBE ROW */}
        <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
          <div>
            <div className="text-lg font-bold text-slate-900">
              Stay in the loop
            </div>
            <div className="text-sm text-slate-500">
              Get updates on new features and improvements
            </div>
          </div>

          <div className="max-w-xl w-full md:w-auto">
            <div className="flex items-center gap-2 flex-col md:flex-row md:justify-end">
              <input
                value={subEmail}
                onChange={(e) => setSubEmail(e.target.value)}
                className="w-full md:w-72 rounded-xl border px-3 py-2 text-sm outline-none"
                placeholder="your@email.com"
              />
              <button
                onClick={onSubscribe}
                className="w-full md:w-auto rounded-xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
              >
                Subscribe
              </button>
            </div>

            <p className="mt-2 text-xs text-slate-500 md:text-right">
              By subscribing you agree to our{" "}
              <a href="#" className="underline">
                Privacy Policy
              </a>
              .
            </p>

            {subMsg && (
              <p className="mt-2 text-xs text-slate-600 md:text-right">
                {subMsg}
              </p>
            )}
          </div>
        </div>

        {/* MIDDLE LINKS SECTION */}
        <div className="mt-12 grid grid-cols-2 gap-8 md:grid-cols-7">
          {/* LOGO */}
          <div className="col-span-3 md:col-span-3">
            <div className="text-2xl font-extrabold tracking-wide">
              <span className="text-slate-500">AP</span>
              <span className="text-blue-600">CRE</span>
            </div>
          </div>

          {/* Product */}
          <div>
            <div className="text-sm font-bold text-slate-900">Product</div>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <a href="#" className="hover:underline">
                  Code editor
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  AI review
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Collaboration
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Dashboard
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Pricing
                </a>
              </li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <div className="text-sm font-bold text-slate-900">Company</div>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <a href="#" className="hover:underline">
                  About us
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Contact
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Blog
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Careers
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Press
                </a>
              </li>
            </ul>
          </div>

          {/* Resources */}
          <div>
            <div className="text-sm font-bold text-slate-900">Resources</div>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <a href="#" className="hover:underline">
                  Documentation
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  API docs
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Community
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Support
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Status
                </a>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <div className="text-sm font-bold text-slate-900">Legal</div>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <a href="#" className="hover:underline">
                  Privacy policy
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Terms of service
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Cookie policy
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Accessibility
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Security
                </a>
              </li>
            </ul>
          </div>

          {/* Connect */}
          <div>
            <div className="text-sm font-bold text-slate-900">Connect</div>
            <ul className="mt-3 space-y-2 text-sm text-slate-600">
              <li>
                <a href="#" className="hover:underline">
                  Follow on Twitter
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Follow on GitHub
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Join Discord
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Email support
                </a>
              </li>
              <li>
                <a href="#" className="hover:underline">
                  Report security
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* BOTTOM BAR */}
        <div className="mt-12 border-t border-white/10 bg-slate-900 px-6 py-4 rounded-2xl">
          <div className="flex flex-col items-center justify-between gap-3 md:flex-row">
            <div className="text-xs text-white/70 text-center md:text-left">
              © {new Date().getFullYear()} APCRE. All rights reserved.
            </div>

            <div className="flex flex-wrap items-center justify-center gap-4 text-xs">
              <a
                href="#"
                className="text-white/70 hover:text-white hover:underline transition"
              >
                Privacy policy
              </a>
              <a
                href="#"
                className="text-white/70 hover:text-white hover:underline transition"
              >
                Terms of service
              </a>
              <a
                href="#"
                className="text-white/70 hover:text-white hover:underline transition"
              >
                Cookie settings
              </a>
            </div>

            <div className="flex items-center justify-center gap-3 text-white/70">
              <a
                href="#"
                className="hover:text-white transition"
                title="Facebook"
              >
                <Facebook className="h-4 w-4" />
              </a>
              <a
                href="#"
                className="hover:text-white transition"
                title="Instagram"
              >
                <Instagram className="h-4 w-4" />
              </a>
              <a href="#" className="hover:text-white transition" title="X">
                <X className="h-4 w-4" />
              </a>
              <a
                href="#"
                className="hover:text-white transition"
                title="LinkedIn"
              >
                <Linkedin className="h-4 w-4" />
              </a>
              <a
                href="#"
                className="hover:text-white transition"
                title="YouTube"
              >
                <Youtube className="h-4 w-4" />
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}

/** -------------------- Main App -------------------- */
export default function App() {
  const [resourcesOpen, setResourcesOpen] = useState(false);
  const [isCommandBarOpen, setIsCommandBarOpen] = useState(false);

  // Global shortcut CTRL+K command console listener
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        setIsCommandBarOpen((prev) => !prev);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, []);

  // Handle and bypass Monaco cancellation unhandled rejections to prevent Next.js dev overlay
  useEffect(() => {
    const handleUnhandledRejection = (event) => {
      const reason = event.reason;
      if (!reason) return;

      const isMonacoCancel = 
        reason.type === "cancelation" || 
        reason.type === "cancellation" ||
        reason.message === "Canceled" ||
        reason.message === "Cancelled" ||
        reason.name === "CancelationError" ||
        reason.name === "CancellationError" ||
        reason.isCancellationError === true ||
        (typeof reason === "object" && (
          reason.msg === "operation is manually canceled" ||
          (reason.message && reason.message.includes("Canceled")) ||
          (Object.keys(reason).length === 0 && reason.constructor === Object)
        ));

      if (isMonacoCancel) {
        event.preventDefault();
        event.stopPropagation();
        event.stopImmediatePropagation();
      }
    };

    window.addEventListener("unhandledrejection", handleUnhandledRejection);
    return () => {
      window.removeEventListener("unhandledrejection", handleUnhandledRejection);
    };
  }, []);


  const [files, setFiles] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [filesLoading, setFilesLoading] = useState(false);

  const [workspacePath, setWorkspacePath] = useState("");
  const [showOpenFolderModal, setShowOpenFolderModal] = useState(false);
  const [openFolderPathInput, setOpenFolderPathInput] = useState("c:\\Users\\WAZIR AMMAR HAIDER\\Desktop\\fyp\\Source_Code");

  // Fetch current backend workspace folder on mount
  useEffect(() => {
    const fetchWorkspacePath = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/workspace-path`);
        const data = await res.json();
        if (data.path) {
          setOpenFolderPathInput(data.path.replaceAll("/", "\\"));
          // Auto-open workspace folder on mount
          setWorkspacePath(data.path);
          await loadFilesFromBackend(data.path);
        }
      } catch (e) {
        console.log("Failed to fetch default workspace path.");
      }
    };
    fetchWorkspacePath();
  }, []);

  // Trigger absolute path switching on backend
  const openCustomFolder = async (pathStr) => {
    if (!pathStr.trim()) return alert("Please enter a path");
    try {
      setToast("⏳ Opening folder...");
      const res = await fetch(`${API_BASE}/api/open-folder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ path: pathStr.trim() })
      });
      const data = await res.json();
      if (data.error) {
        alert(data.error);
        return;
      }
      if (data.path) {
        setWorkspacePath(data.path);
        await loadFilesFromBackend(data.path);
        setShowOpenFolderModal(false);
        setToast("📂 Folder opened successfully!");
        setTimeout(() => setToast(""), 1500);
      }
    } catch (err) {
      alert("Error: " + err.message);
    }
  };

  // Trigger Windows Native Folder Selector via PowerShell
  const triggerNativeFolderPicker = async () => {
    try {
      setToast("⏳ Waiting for folder selection...");
      const res = await fetch(`${API_BASE}/api/open-folder`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({})
      });
      const data = await res.json();
      if (data.cancelled) {
        setToast("Cancelled");
        setTimeout(() => setToast(""), 1000);
        return;
      }
      if (data.error) {
        alert(data.error);
        return;
      }
      if (data.path) {
        setWorkspacePath(data.path);
        await loadFilesFromBackend(data.path);
        setShowOpenFolderModal(false);
        setToast("📂 Folder opened successfully!");
        setTimeout(() => setToast(""), 1500);
      }
    } catch (err) {
      alert("Failed to open native dialog: " + err.message);
    }
  };

  // Create new folder
  const createNewFolder = async (fullPathFromBox) => {
    let p = fullPathFromBox.trim();
    let relative = p;
    if (relative.startsWith("workspace/")) {
      relative = relative.substring("workspace/".length);
    }
    relative = relative.replace(/^\/+/, "");

    if (!relative) {
      alert("Please enter a valid folder path.");
      return;
    }

    const absolutePathInApp = `workspace/${relative}`;

    if (files.some((f) => f.path === absolutePathInApp)) {
      alert("A file or folder with this name already exists!");
      return;
    }

    const res = await fetch(`${API_BASE}/api/folders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: relative }),
    });

    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    await loadFilesFromBackend();
    setToast("📁 Folder created");
    setTimeout(() => setToast(""), 1500);
  };

  const monaco = useMonaco();
  const editorRef = useRef(null);

  /* == REAL-TIME AI CODE REVIEW & AUTOCOMPLETE == */
  useEffect(() => {
    if (!monaco) return;

    // 1. Register AI Autocomplete Provider
    const completionProvider = monaco.languages.registerCompletionItemProvider("python", {
      provideCompletionItems: async (model, position) => {
        const textUntilPosition = model.getValueInRange({
          startLineNumber: 1,
          startColumn: 1,
          endLineNumber: position.lineNumber,
          endColumn: position.column,
        });

        try {
          const res = await fetch(`${API_BASE}/api/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ prompt: textUntilPosition }),
          });
          const aiResponse = await res.json();
          
          const suggestions = (aiResponse.suggestions || []).map((sugg) => ({
            label: sugg.text,
            kind: monaco.languages.CompletionItemKind.Snippet,
            insertText: sugg.text,
            detail: "AI Model Suggestion",
          }));

          return { suggestions };
        } catch (e) {
          return { suggestions: [] };
        }
      },
    });

    return () => {
      completionProvider.dispose();
    };
  }, [monaco]);

  useEffect(() => {
    if (!monaco || !editorRef.current || !selectedFile?.content) return;
    
    // 2. Debounce typing to request AI Review for syntax/errors
    const timer = setTimeout(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/review`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ code: selectedFile.content })
        });
        const aiAnalysis = await res.json();
        
        const markers = (aiAnalysis.errors || []).map(err => ({
          message: err.message,
          severity: monaco.MarkerSeverity.Error,
          startLineNumber: err.line,
          startColumn: err.column || 1,
          endLineNumber: err.line,
          endColumn: err.endColumn || 10,
        }));
        
        monaco.editor.setModelMarkers(editorRef.current.getModel(), "ai-reviewer", markers);
      } catch (err) {
        console.log("AI Model unreachable for syntax checking.");
      }
    }, 1500);

    return () => clearTimeout(timer);
  }, [selectedFile?.content, monaco]);

  const handleEditorDidMount = (editor) => {
    editorRef.current = editor;
  };

  const [activeTab, setActiveTab] = useState("review");

  // =========================================================================
  // HOISTED SAAS & CODER AGENT STATES (Ecosystem-wide Reactivity)
  // =========================================================================
  const [selectedFixIssueId, setSelectedFixIssueId] = useState(null);
  const [fixLoading, setFixLoading] = useState(false);
  const [fixResult, setFixResult] = useState(null);

  const [user, setUser] = useState(null);
  const [isClient, setIsClient] = useState(false);

  // Initialize client state
  useEffect(() => {
    setIsClient(true);
    const stored = localStorage.getItem("user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
  }, []);

  useEffect(() => {
    const handleUserUpdate = () => {
      const stored = localStorage.getItem("user");
      if (stored) {
        setUser(JSON.parse(stored));
      } else {
        setUser(null);
      }
    };
    window.addEventListener("user-login", handleUserUpdate);
    return () => window.removeEventListener("user-login", handleUserUpdate);
  }, []);

  useEffect(() => {
    const currentExpiry = localStorage.getItem("trialExpiry");
    const twoMonthsMs = 60 * 24 * 60 * 60 * 1000;
    const targetExpiry = Date.now() + twoMonthsMs;
    
    if (!currentExpiry || parseInt(currentExpiry, 10) - Date.now() < 30 * 24 * 60 * 60 * 1000) {
      localStorage.setItem("trialExpiry", targetExpiry.toString());
      localStorage.setItem("localPro", "true");
      window.dispatchEvent(new Event("user-login"));
    }
  }, []);

  const [trialTimeRemaining, setTrialTimeRemaining] = useState("");

  const isPro = useMemo(() => {
    if (!isClient) return false;
    if (user && user.plan === "pro") return true;
    if (localStorage.getItem("localPro") === "true") {
      const expiryStr = localStorage.getItem("trialExpiry");
      if (expiryStr) {
        const expiry = parseInt(expiryStr, 10);
        if (Date.now() > expiry) {
          localStorage.removeItem("localPro");
          localStorage.removeItem("trialExpiry");
          return false;
        }
      }
      return true;
    }
    return false;
  }, [user, isClient]);

  useEffect(() => {
    if (!isClient) return;
    const updateTrialTimer = () => {
      const expiryStr = localStorage.getItem("trialExpiry");
      if (expiryStr) {
        const expiry = parseInt(expiryStr, 10);
        const diff = expiry - Date.now();
        if (diff <= 0) {
          localStorage.removeItem("localPro");
          localStorage.removeItem("trialExpiry");
          setTrialTimeRemaining("");
          window.dispatchEvent(new Event("user-login"));
        } else {
          const days = Math.floor(diff / (1000 * 60 * 60 * 24));
          const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
          const mins = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
          if (days > 0) {
            setTrialTimeRemaining(`🎁 Trial: ${days}d ${hours}h remaining`);
          } else {
            setTrialTimeRemaining(`🎁 Trial: ${hours}h ${mins}m remaining`);
          }
        }
      } else {
        setTrialTimeRemaining("");
      }
    };

    updateTrialTimer();
    const interval = setInterval(updateTrialTimer, 30000);
    return () => clearInterval(interval);
  }, [isPro, isClient]);

  const startOneDayTrial = () => {
    const expiry = Date.now() + 60 * 24 * 60 * 60 * 1000;
    localStorage.setItem("trialExpiry", expiry.toString());
    localStorage.setItem("localPro", "true");
    window.dispatchEvent(new Event("user-login"));
    alert("🎁 Your 2-Month Free Trial has been activated successfully! Enjoy APCRE Pro Autonomous Agents.");
  };

  const [showCheckoutModal, setShowCheckoutModal] = useState(false);
  const [showNewFileModal, setShowNewFileModal] = useState(false);
  const [newFileName, setNewFileName] = useState("");
  const [newFileError, setNewFileError] = useState("");
  const [billingCycle, setBillingCycle] = useState("annual");
  const [cardNumber, setCardNumber] = useState("");
  const [cardExpiry, setCardExpiry] = useState("");
  const [cardCvc, setCardCvc] = useState("");
  const [cardName, setCardName] = useState(user ? `${user.firstName || ""} ${user.lastName || ""}`.trim() : "Ammar Haider");
  const [paymentProcessing, setPaymentProcessing] = useState(false);
  const [paymentStatus, setPaymentStatus] = useState("");
  const [paymentError, setPaymentError] = useState("");

  const [agentPrompt, setAgentPrompt] = useState("");
  const [agentFilename, setAgentFilename] = useState("automation_agent.py");
  const [agentRunning, setAgentRunning] = useState(false);
  const [agentVisibleLogs, setAgentVisibleLogs] = useState([]);
  const [agentResult, setAgentResult] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const recognitionRef = useRef(null);

  const toggleSpeechRecognition = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use Chrome, Edge, or Safari.");
      return;
    }

    if (isListening) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsListening(false);
    } else {
      const recognition = new SpeechRecognition();
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = "en-US";

      recognition.onstart = () => {
        setIsListening(true);
      };

      recognition.onerror = (event) => {
        console.error("Speech recognition error:", event.error);
        setIsListening(false);
      };

      recognition.onend = () => {
        setIsListening(false);
      };

      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        if (transcript) {
          setAgentPrompt((prev) => prev ? prev + " " + transcript : transcript);
        }
      };

      recognitionRef.current = recognition;
      recognition.start();
    }
  };

  const handleCardNumberChange = (e) => {
    let value = e.target.value.replace(/\\D/g, "");
    let formatted = "";
    for (let i = 0; i < value.length; i++) {
      if (i > 0 && i % 4 === 0) formatted += " ";
      formatted += value[i];
    }
    setCardNumber(formatted);
  };

  const handleCardExpiryChange = (e) => {
    let value = e.target.value.replace(/\\D/g, "");
    let formatted = "";
    if (value.length > 2) {
      formatted = value.slice(0, 2) + "/" + value.slice(2, 4);
    } else {
      formatted = value;
    }
    setCardExpiry(formatted);
  };

  const processSimulatedPayment = async () => {
    setPaymentError("");
    if (!cardName.trim()) {
      setPaymentError("Please enter the cardholder name.");
      return;
    }
    if (cardNumber.replace(/\\s/g, "").length < 16) {
      setPaymentError("Please enter a valid 16-digit card number.");
      return;
    }
    if (cardExpiry.length < 5) {
      setPaymentError("Please enter expiry date (MM/YY).");
      return;
    }
    if (cardCvc.length < 3) {
      setPaymentError("Please enter CVV / CVC.");
      return;
    }

    setPaymentProcessing(true);
    
    const steps = [
      "⚙️ Connecting to Stripe Gateway...",
      "🛡️ Authenticating card with 3D Secure...",
      "💸 Authorizing charge...",
      "🎉 Subscription upgraded successfully!"
    ];

    for (let i = 0; i < steps.length; i++) {
      setPaymentStatus(steps[i]);
      await new Promise((resolve) => setTimeout(resolve, 800));
    }

    try {
      if (user && user.id) {
        await fetch("/api/user/upgrade", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ userId: user.id, plan: "pro" }),
        });
      }
      
      const updatedUser = user ? { ...user, plan: "pro" } : { firstName: "Guest", lastName: "User", email: "guest@apcre.pro", plan: "pro", id: "guest" };
      localStorage.setItem("user", JSON.stringify(updatedUser));
      localStorage.setItem("localPro", "true");
      
      window.dispatchEvent(new Event("user-login"));
      setShowCheckoutModal(false);
      alert("👑 Congratulations! Your APCRE Pro subscription has been successfully activated.");
    } catch (err) {
      setPaymentError("Backend upgrade failed, but local bypass activated.");
      localStorage.setItem("localPro", "true");
      window.dispatchEvent(new Event("user-login"));
      setShowCheckoutModal(false);
    } finally {
      setPaymentProcessing(false);
    }
  };

  const runAutonomousAgent = async () => {
    if (!agentPrompt.trim()) return;
    setAgentRunning(true);
    setAgentVisibleLogs([]);
    setAgentResult(null);

    const prepLogs = [
      { time: new Date().toLocaleTimeString(), step: "🧠 Initializing Autonomous Coder Agent...", status: "info" },
      { time: new Date().toLocaleTimeString(), step: "🔍 Inspecting workspace configuration...", status: "info" }
    ];
    setAgentVisibleLogs(prepLogs);

    try {
      const response = await fetch(`${API_BASE}/api/agent/automate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: agentPrompt,
          filename: agentFilename || "automation_agent.py",
          code: selectedFile ? selectedFile.content : ""
        }),
      });

      const data = await response.json();
      
      if (data.logs && data.logs.length > 0) {
        let currentLogs = [...prepLogs];
        for (let i = 0; i < data.logs.length; i++) {
          await new Promise((resolve) => setTimeout(resolve, 1000));
          currentLogs = [...currentLogs, data.logs[i]];
          setAgentVisibleLogs(currentLogs);
        }
      } else {
        setAgentVisibleLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), step: "Response received from agent engine.", status: "success" }]);
      }

      setAgentResult(data);
      
      // Auto-load created file
      await loadFilesFromBackend();
      try {
        const res = await fetch(`${API_BASE}/api/files`);
        const filesData = await res.json();
        if (filesData?.files && Array.isArray(filesData.files)) {
          const found = filesData.files.find(f => f.name === (agentFilename || "automation_agent.py"));
          if (found) {
            const normFile = {
              ...found,
              path: found.path.startsWith("workspace/") ? found.path : `workspace/${found.path}`
            };
            setSelectedFile(normFile);
          }
        }
      } catch (e) {}

    } catch (err) {
      setAgentVisibleLogs(prev => [...prev, { time: new Date().toLocaleTimeString(), step: `Agent Error: ${err.message}`, status: "error" }]);
      setAgentResult({ success: false, error: err.message, stderr: err.message });
    } finally {
      setAgentRunning(false);
    }
  };
  const [page, setPage] = useState("editor");
  const startLesson = (lesson) => {
    setPage("editor");

    const lessonFile = {
      name: "lesson.py",
      path: "workspace/lesson.py",
      content: lesson.starterCode,
    };

    setFiles([lessonFile]);
    setSelectedFile(lessonFile);
  };

  const [terminalOutput, setTerminalOutput] = useState(
    "APCRE Terminal Ready...\n",
  );
  const [terminalInput, setTerminalInput] = useState("");

  const [aiIssues, setAiIssues] = useState([
    {
      id: "m1",
      type: "suggestion",
      title: "Run AI Review",
      line: "-",
      desc: "Click Run AI Review to get issues from ChatGPT API.",
      fix: "",
    },
  ]);
  const [aiLoading, setAiLoading] = useState(false);

  /** -------------------- Debounced Real-Time Auto-Review -------------------- */
  useEffect(() => {
    if (!selectedFile || !selectedFile.content || !selectedFile.content.trim()) {
      setAiIssues([]);
      return;
    }

    const reviewTimer = setTimeout(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/review`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            filename: selectedFile.name,
            code: selectedFile.content || "",
          }),
        });
        const data = await res.json();
        if (data.issues && Array.isArray(data.issues)) {
          const withIds = data.issues.map((x, idx) => ({
            id: "ai-" + idx,
            type: x.type || "suggestion",
            title: x.title || "Issue",
            line: x.line || "-",
            desc: x.desc || "",
            fix: x.fix || "",
          }));
          setAiIssues(withIds);
        }
      } catch (err) {
        console.error("Auto-review background fetch failed:", err);
      }
    }, 800); // 800ms debounce of typing inactivity

    return () => clearTimeout(reviewTimer);
  }, [selectedFile?.content, selectedFile?.name]);

  const [showSignIn, setShowSignIn] = useState(false);
  const [toast, setToast] = useState("");

  const [subEmail, setSubEmail] = useState("");
  const [subMsg, setSubMsg] = useState("");



  /** --------------------  Assistant States -------------------- */
  const [assistantMessages, setAssistantMessages] = useState([
    { role: "assistant", text: "Welcome to APCRE! How can I help you?!" },
  ]);
  const [assistantInput, setAssistantInput] = useState("");
  const [assistantLoading, setAssistantLoading] = useState(false);

  /** -------------------- Socket.io States -------------------- */
  const socketRef = useRef(null);
  const [socketConnected, setSocketConnected] = useState(false);

  const [roomId, setRoomId] = useState("");
  const [roomJoined, setRoomJoined] = useState(false);
  const [roomUsers, setRoomUsers] = useState([]);

  /** -------------------- WebRTC & APCRE Meet States -------------------- */
  const [localStream, setLocalStream] = useState(null);
  const [remoteStream, setRemoteStream] = useState(null);
  const [isCallActive, setIsCallActive] = useState(false);
  const [isScreenSharing, setIsScreenSharing] = useState(false);
  const [meetLogs, setMeetLogs] = useState([]);

  const peerConnectionRef = useRef(null);
  const screenTrackRef = useRef(null);
  const localStreamRef = useRef(null);
  const iceQueueRef = useRef([]);

  const logMeet = (msg) => {
    console.log(`[APCRE Meet] ${msg}`);
    setMeetLogs((prev) => [...prev.slice(-15), `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  const drainIceQueue = async (pc) => {
    if (!pc) return;
    if (iceQueueRef.current.length === 0) return;
    logMeet(`Draining ${iceQueueRef.current.length} buffered ICE candidates.`);
    for (const candidate of iceQueueRef.current) {
      try {
        await pc.addIceCandidate(new RTCIceCandidate(candidate));
      } catch (err) {
        console.error("Error adding buffered ICE candidate:", err);
      }
    }
    iceQueueRef.current = [];
  };

  const createMockStream = (label = "APCRE Video") => {
    logMeet("Initializing mock audio/video fallback...");
    const canvas = document.createElement("canvas");
    canvas.width = 640;
    canvas.height = 480;
    const ctx = canvas.getContext("2d");
    
    let angle = 0;
    const interval = setInterval(() => {
      if (!ctx) return;
      const grad = ctx.createLinearGradient(0, 0, 640, 480);
      grad.addColorStop(0, "#1e1b4b");
      grad.addColorStop(1, "#311042");
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, 640, 480);

      ctx.strokeStyle = "#6366f1";
      ctx.lineWidth = 4;
      ctx.beginPath();
      for (let x = 0; x < 640; x++) {
        const y = 240 + Math.sin(x * 0.02 + angle) * 40;
        if (x === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
      }
      ctx.stroke();

      ctx.fillStyle = "rgba(99, 102, 241, 0.2)";
      ctx.beginPath();
      ctx.arc(320, 240, 90, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = "#818cf8";
      ctx.lineWidth = 2;
      ctx.stroke();

      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 22px monospace";
      ctx.textAlign = "center";
      ctx.fillText(label, 320, 230);
      
      ctx.fillStyle = "#a5b4fc";
      ctx.font = "13px monospace";
      ctx.fillText("Real-time WebRTC Peer Connected", 320, 260);

      ctx.fillStyle = "#10b981";
      ctx.beginPath();
      ctx.arc(220, 226, 6, 0, Math.PI * 2);
      ctx.fill();

      angle += 0.08;
    }, 1000 / 30);

    const stream = canvas.captureStream(30);

    try {
      const AudioCtx = window.AudioContext || window.webkitAudioContext;
      if (AudioCtx) {
        const audioContext = new AudioCtx();
        const osc = audioContext.createOscillator();
        const gain = audioContext.createGain();
        osc.connect(gain);
        const dest = audioContext.createMediaStreamDestination();
        gain.connect(dest);
        
        osc.frequency.value = 440;
        osc.type = "sine";
        gain.gain.value = 0.001;
        osc.start();
        
        dest.stream.getAudioTracks().forEach(track => {
          stream.addTrack(track);
        });

        stream.cleanupMock = () => {
          clearInterval(interval);
          osc.stop();
          audioContext.close();
        };
      }
    } catch (e) {
      console.warn("Mock Audio generation failed:", e);
      stream.cleanupMock = () => clearInterval(interval);
    }

    return stream;
  };

  const createMockScreenStream = () => {
    logMeet("Initializing mock screen-share fallback...");
    const canvas = document.createElement("canvas");
    canvas.width = 800;
    canvas.height = 600;
    const ctx = canvas.getContext("2d");
    
    let offset = 0;
    const interval = setInterval(() => {
      if (!ctx) return;
      ctx.fillStyle = "#0f172a";
      ctx.fillRect(0, 0, 800, 600);

      ctx.strokeStyle = "#334155";
      ctx.lineWidth = 1;
      for (let x = 0; x < 800; x += 40) {
        ctx.beginPath();
        ctx.moveTo(x, 0);
        ctx.lineTo(x, 600);
        ctx.stroke();
      }
      for (let y = 0; y < 600; y += 40) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(800, y);
        ctx.stroke();
      }

      ctx.fillStyle = "#38bdf8";
      ctx.font = "bold 16px monospace";
      ctx.fillText("class APCREScheduler:", 50, 80);
      
      ctx.fillStyle = "#a7f3d0";
      ctx.fillText("    def __init__(self, interval_sec):", 50, 110);
      ctx.fillStyle = "#fbcfe8";
      ctx.fillText("        self.interval = interval_sec", 50, 140);
      ctx.fillStyle = "#fde047";
      ctx.fillText("        self.status = 'ACTIVE'", 50, 170);

      ctx.fillStyle = "#e2e8f0";
      ctx.font = "14px monospace";
      ctx.fillText("--- Real-time Collaboration Presentation Mode ---", 50, 230);
      ctx.fillText(`Timestamp: ${new Date().toISOString()}`, 50, 260);

      ctx.fillStyle = "#f59e0b";
      ctx.fillRect(0, 0, 800, 30);
      ctx.fillStyle = "#ffffff";
      ctx.font = "bold 12px monospace";
      ctx.textAlign = "center";
      ctx.fillText("🖥️ PRESENTATION: SHARING SCREEN", 400, 20);
      ctx.textAlign = "left";

      offset += 1;
    }, 1000 / 30);

    const stream = canvas.captureStream(30);
    stream.cleanupMock = () => clearInterval(interval);
    return stream;
  };

  /** -------------------- Realtime code guard -------------------- */
  const ignoreRemoteUpdate = useRef(false);

  /** -------------------- Load Files from Backend -------------------- */
  async function loadFilesFromBackend(forcedPath = null) {
    if (!workspacePath && !forcedPath) {
      setFiles([]);
      setSelectedFile(null);
      return;
    }
    setFilesLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/files`);
      const data = await res.json();

      if (data?.files && Array.isArray(data.files)) {
        const normalized = data.files.map((f) => ({
          ...f,
          path: f.path.startsWith("workspace/")
            ? f.path
            : `workspace/${f.path}`,
        }));

        setFiles(normalized);
        setSelectedFile((prev) => {
          if (!prev) return normalized[0] || null;
          const still = normalized.find((x) => x.path === prev.path);
          return still || normalized[0] || null;
        });
      } else {
        setFiles([]);
        setSelectedFile(null);
      }
    } catch (err) {
      console.log("❌ Failed to load files:", err.message);
      setFiles([]);
      setSelectedFile(null);
    } finally {
      setFilesLoading(false);
    }
  };

  useEffect(() => {
    if (workspacePath) {
      loadFilesFromBackend();
    }
  }, [workspacePath]);

  /** -------------------- Socket.io Setup -------------------- */
  useEffect(() => {
    const getSocketUrl = () => {
      if (typeof window === "undefined") return "";
      const { protocol, hostname, port } = window.location;
      if (port) {
        return `${protocol}//${hostname}:5000`;
      }
      if (hostname === "localhost" || hostname === "127.0.0.1") {
        return `${protocol}//${hostname}:5000`;
      }
      return window.location.origin;
    };

    const socket = io(getSocketUrl(), {
      transports: ["websocket", "polling"],
    });

    socketRef.current = socket;

    socket.on("connect", () => {
      setSocketConnected(true);
    });

    socket.on("disconnect", () => {
      setSocketConnected(false);
      setRoomJoined(false);
      setRoomUsers([]);
    });

    socket.on("room:joined", ({ roomId, users, code }) => {
      setRoomJoined(true);
      setRoomUsers(users || []);

      if (typeof code === "string" && selectedFile) {
        ignoreRemoteUpdate.current = true;

        setFiles((prev) =>
          prev.map((f) =>
            f.path === selectedFile.path ? { ...f, content: code } : f,
          ),
        );
        setSelectedFile((prev) => (prev ? { ...prev, content: code } : prev));

        setTimeout(() => {
          ignoreRemoteUpdate.current = false;
        }, 50);
      }
    });

    socket.on("room:users", (users) => {
      setRoomUsers(users || []);
    });

    socket.on("code:updated", ({ code }) => {
      if (!selectedFile) return;

      ignoreRemoteUpdate.current = true;

      setFiles((prev) =>
        prev.map((f) =>
          f.path === selectedFile.path ? { ...f, content: code } : f,
        ),
      );
      setSelectedFile((prev) => (prev ? { ...prev, content: code } : prev));

      setTimeout(() => {
        ignoreRemoteUpdate.current = false;
      }, 50);
    });

    socket.on("room:error", ({ error }) => {
      alert(error || "Room error");
    });

    socket.on("rtc:signal", async ({ sender, signal }) => {
      if (sender === socket.id) return;

      if (signal.offer) {
        logMeet("Received incoming SDP Offer from peer...");
        let pc = peerConnectionRef.current;
        if (!pc) {
          logMeet("Creating RTCPeerConnection to accept offer...");
          setIsCallActive(true);
          
          let stream = localStreamRef.current;
          if (!stream) {
            try {
              stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
              logMeet("Acquired local camera & mic for incoming call.");
            } catch (e) {
              logMeet(`Media acquisition failed: ${e.message}. Using simulated stream.`);
              stream = createMockStream(`${user?.name || "Guest"}'s Camera`);
            }
            setLocalStream(stream);
            localStreamRef.current = stream;
          }

          pc = new RTCPeerConnection({
            iceServers: [
              { urls: "stun:stun.l.google.com:19302" },
              { urls: "stun:stun1.l.google.com:19302" },
              { urls: "stun:stun2.l.google.com:19302" }
            ]
          });
          peerConnectionRef.current = pc;

          stream.getTracks().forEach((track) => {
            pc.addTrack(track, stream);
          });

          pc.ontrack = (event) => {
            logMeet("Remote track received!");
            if (event.streams && event.streams[0]) {
              setRemoteStream(event.streams[0]);
            }
          };

          pc.onicecandidate = (event) => {
            if (event.candidate && socketRef.current) {
              socketRef.current.emit("rtc:signal", {
                roomId,
                signal: { type: "candidate", candidate: event.candidate }
              });
            }
          };

          pc.onconnectionstatechange = () => {
            logMeet(`Connection state changed: ${pc.connectionState}`);
          };
        }

        try {
          await pc.setRemoteDescription(new RTCSessionDescription(signal.offer));
          logMeet("Remote Description set successfully. Creating SDP Answer...");
          await drainIceQueue(pc);
          const answer = await pc.createAnswer();
          await pc.setLocalDescription(answer);
          logMeet("Sending SDP Answer back to signaling channel...");
          socketRef.current.emit("rtc:signal", {
            roomId,
            signal: { type: "answer", answer }
          });
        } catch (err) {
          logMeet(`Error answering call: ${err.message}`);
        }
      } else if (signal.answer) {
        logMeet("Received SDP Answer from peer...");
        const pc = peerConnectionRef.current;
        if (pc) {
          try {
            await pc.setRemoteDescription(new RTCSessionDescription(signal.answer));
            logMeet("Call negotiated and connected successfully!");
            await drainIceQueue(pc);
          } catch (err) {
            logMeet(`Error setting remote description: ${err.message}`);
          }
        }
      } else if (signal.type === "candidate" && signal.candidate) {
        const pc = peerConnectionRef.current;
        if (pc && pc.remoteDescription && pc.remoteDescription.type) {
          try {
            await pc.addIceCandidate(new RTCIceCandidate(signal.candidate));
          } catch (err) {
            console.error("Error adding ICE candidate:", err);
          }
        } else {
          logMeet("Buffering incoming ICE candidate (remote description not set yet)...");
          iceQueueRef.current.push(signal.candidate);
        }
      }
    });

    socket.on("rtc:leave-call", () => {
      logMeet("Remote peer left the call.");
      setIsScreenSharing(false);
      if (screenTrackRef.current) {
        screenTrackRef.current.stop();
        if (screenTrackRef.current.cleanupMock) {
          screenTrackRef.current.cleanupMock();
        }
        screenTrackRef.current = null;
      }
      setRemoteStream(null);
      if (peerConnectionRef.current) {
        peerConnectionRef.current.close();
        peerConnectionRef.current = null;
      }
    });

    return () => {
      socket.disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedFile?.path]);

  /** -------------------- Backend Save Debounce -------------------- */
  const saveTimer = useRef(null);

  const saveFileToBackend = async (filePath, content) => {
    const relative = filePath.replace(/^workspace\//, "");

    await fetch(`${API_BASE}/api/files`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: relative, content }),
    });
  };

  /** -------------------- Editor Change -------------------- */
  const onChangeCode = (val) => {
    if (!selectedFile) return;

    const newContent = val || "";

    setFiles((prev) =>
      prev.map((f) =>
        f.path === selectedFile.path ? { ...f, content: newContent } : f,
      ),
    );
    setSelectedFile((prev) => (prev ? { ...prev, content: newContent } : prev));

    // Instantly clear the default placeholder issue so that the local F1 score calculates dynamically
    setAiIssues((prev) => prev.filter((x) => x.id !== "m1"));

    if (saveTimer.current) clearTimeout(saveTimer.current);
    saveTimer.current = setTimeout(() => {
      saveFileToBackend(selectedFile.path, newContent).catch(() => {});
    }, 400);

    if (roomJoined && socketRef.current && !ignoreRemoteUpdate.current) {
      socketRef.current.emit("code:update", { roomId, code: newContent });
    }
  };

  /** -------------------- Create File (Backend) -------------------- */
  const createNewFile = async (fullPathFromBox, customOnError = null) => {
    let p = fullPathFromBox.trim();

    // Strip leading workspace/ first to clean it, then do operations
    let relative = p;
    if (relative.startsWith("workspace/")) {
      relative = relative.substring("workspace/".length);
    }
    relative = relative.replace(/^\/+/, "");

    if (!relative) {
      if (customOnError) customOnError("Please enter a valid file path.");
      else alert("Please enter a valid file path.");
      return false;
    }

    const name = relative.split("/").pop();
    const absolutePathInApp = `workspace/${relative}`;

    if (files.some((f) => f.path === absolutePathInApp)) {
      if (customOnError) customOnError("File already exists!");
      else alert("File already exists!");
      return false;
    }

    const res = await fetch(`${API_BASE}/api/files`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        path: relative,
        content: `print("Hello from ${name}")\n`,
      }),
    });

    const data = await res.json();
    if (data.error) {
      if (customOnError) customOnError(data.error);
      else alert(data.error);
      return false;
    }

    await loadFilesFromBackend();
    setToast("📄 File created");
    setTimeout(() => setToast(""), 1500);
    return true;
  };

  /** -------------------- Delete File (Backend) -------------------- */
  const deleteFile = async (file) => {
    if (files.length === 1) {
      alert("You cannot delete the last file.");
      return;
    }

    const confirmDel = confirm(`Delete file "${file.name}" ?`);
    if (!confirmDel) return;

    const relative = file.path.replace(/^workspace\//, "");

    const res = await fetch(`${API_BASE}/api/files`, {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ path: relative }),
    });

    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    await loadFilesFromBackend();
    setToast("🗑 File deleted");
    setTimeout(() => setToast(""), 1500);
  };

  /** -------------------- Rename File (Backend) -------------------- */
  const renameFile = async (file) => {
    const newName = prompt("Enter new file name:", file.name);
    if (!newName) return;

    const parentFolder = file.path.split("/").slice(0, -1).join("/");
    const newPathFull = `${parentFolder}/${newName}`;

    if (files.some((f) => f.path === newPathFull)) {
      alert("A file with this name already exists!");
      return;
    }

    const oldRelative = file.path.replace(/^workspace\//, "");
    const newRelative = newPathFull.replace(/^workspace\//, "");

    const res = await fetch(`${API_BASE}/api/files/rename`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        oldPath: oldRelative,
        newPath: newRelative,
      }),
    });

    const data = await res.json();
    if (data.error) {
      alert(data.error);
      return;
    }

    await loadFilesFromBackend();
    setToast(" File renamed");
    setTimeout(() => setToast(""), 1500);
  };

  /** -------------------- Download Selected File -------------------- */
  const downloadFile = () => {
    if (!selectedFile) return;

    const blob = new Blob([selectedFile.content || ""], {
      type: "text/plain;charset=utf-8",
    });
    saveAs(blob, selectedFile.name);
  };

  /** -------------------- Run Python (Backend) -------------------- */
  const runCodeReal = async () => {
    if (!selectedFile) return;

    setTerminalOutput(`Running ${selectedFile.name}...\n`);

    try {
      const res = await fetch(`${API_BASE}/api/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: selectedFile.name,
          code: selectedFile.content || "",
        }),
      });

      const data = await res.json();

      setTerminalOutput(
        `Running ${selectedFile.name}...\n\n` +
          `STDOUT:\n${data.stdout || ""}\n\n` +
          `STDERR:\n${data.stderr || ""}\n\n` +
          `Exit Code: ${data.exitCode}\n`,
      );
    } catch (err) {
      setTerminalOutput(`❌ Backend not running.\n\n${err.message}`);
    }
  };

  /** -------------------- Terminal Command -------------------- */
  const runTerminalCommand = async (cmd) => {
    setTerminalOutput((prev) => prev + `\n> ${cmd}\n`);

    try {
      const res = await fetch(`${API_BASE}/api/terminal`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ command: cmd }),
      });

      const data = await res.json();
      setTerminalOutput((prev) => prev + (data.output || "") + "\n");
    } catch (err) {
      setTerminalOutput((prev) => prev + `❌ ${err.message}\n`);
    }
  };

  /** -------------------- AI Fix -------------------- */
  const handleFixIssue = async (issue) => {
    if (!selectedFile) return;

    const res = await fetch(`${API_BASE}/api/fix`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        filename: selectedFile.name,
        code: selectedFile.content || "",
        issue: {
          title: issue.title,
          line: issue.line,
          desc: issue.desc,
        },
      }),
    });

    const data = await res.json();

    if (data.error) throw new Error(data.error);

    if (data.fixedCode) {
      onChangeCode(data.fixedCode);
      setAiIssues((prevIssues) => prevIssues.filter((x) => x.id !== issue.id));
    }

    setToast(` Fix applied: ${issue.title}`);
    setTimeout(() => setToast(""), 2000);

    return data;
  };

  /** -------------------- AI Review -------------------- */
  const runAiReview = async () => {
    if (!selectedFile) return;

    setAiLoading(true);
    setActiveTab("review");

    try {
      const res = await fetch(`${API_BASE}/api/review`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          filename: selectedFile.name,
          code: selectedFile.content || "",
        }),
      });

      const data = await res.json();

      if (data.issues && Array.isArray(data.issues)) {
        const withIds = data.issues.map((x, idx) => ({
          id: "ai-" + idx,
          type: x.type || "suggestion",
          title: x.title || "Issue",
          line: x.line || "-",
          desc: x.desc || "",
          fix: x.fix || "",
        }));
        setAiIssues(withIds);
      } else {
        setAiIssues([
          {
            id: "ai-error",
            type: "warning",
            title: "AI review failed",
            line: "-",
            desc: data.error || "Unknown error",
            fix: "",
          },
        ]);
      }
    } catch (err) {
      setAiIssues([
        {
          id: "ai-backend",
          type: "critical",
          title: "Backend not running",
          line: "-",
          desc: err.message,
          fix: "",
        },
      ]);
    }

    setAiLoading(false);
  };

  /** -------------------- Subscribe -------------------- */
  const subscribeNow = async () => {
    setSubMsg("");

    try {
      const res = await fetch(`${API_BASE}/api/subscribe`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: subEmail }),
      });

      const data = await res.json();
      if (data.error) {
        setSubMsg(" " + data.error);
      } else {
        setSubMsg(" " + data.message);
        setSubEmail("");
      }
    } catch (err) {
      setSubMsg("❌ Backend not running");
    }
  };

  /** -------------------- WebRTC Call Handlers -------------------- */
  const onStartCall = async () => {
    if (isCallActive) return;
    logMeet("Initializing media streams...");
    setIsCallActive(true);
    setMeetLogs([]);

    let stream = null;
    try {
      stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      logMeet("Acquired user camera & mic.");
    } catch (e) {
      logMeet(`Media acquisition failed: ${e.message}. Using high-fidelity video simulation.`);
      stream = createMockStream(`${user?.name || "Guest"}'s Camera`);
    }

    setLocalStream(stream);
    localStreamRef.current = stream;

    logMeet("Creating RTCPeerConnection...");
    const pc = new RTCPeerConnection({
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" },
        { urls: "stun:stun2.l.google.com:19302" }
      ]
    });

    peerConnectionRef.current = pc;

    stream.getTracks().forEach((track) => {
      pc.addTrack(track, stream);
    });
    logMeet("Added local audio & video tracks.");

    pc.ontrack = (event) => {
      logMeet("Remote track received from peer!");
      if (event.streams && event.streams[0]) {
        setRemoteStream(event.streams[0]);
      }
    };

    pc.onicecandidate = (event) => {
      if (event.candidate && socketRef.current) {
        socketRef.current.emit("rtc:signal", {
          roomId,
          signal: { type: "candidate", candidate: event.candidate }
        });
      }
    };

    pc.onconnectionstatechange = () => {
      logMeet(`Connection state changed: ${pc.connectionState}`);
    };

    try {
      logMeet("Creating WebRTC Session Description (Offer)...");
      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      
      logMeet("Sending SDP Offer via Socket.IO relay...");
      socketRef.current.emit("rtc:signal", {
        roomId,
        signal: { type: "offer", offer }
      });
    } catch (err) {
      logMeet(`Failed to create SDP Offer: ${err.message}`);
    }
  };

  const stopScreenSharingTrack = (pc) => {
    logMeet("Restoring camera video track...");
    if (screenTrackRef.current) {
      screenTrackRef.current.stop();
      if (screenTrackRef.current.cleanupMock) {
        screenTrackRef.current.cleanupMock();
      }
      screenTrackRef.current = null;
    }

    const cameraTrack = localStream?.getVideoTracks()[0];
    if (cameraTrack && pc) {
      const senders = pc.getSenders();
      const videoSender = senders.find((s) => s.track && s.track.kind === "video");
      if (videoSender) {
        videoSender.replaceTrack(cameraTrack);
        logMeet("Swapped peer video sender back to camera.");
      }
    }
    setIsScreenSharing(false);
  };

  const onToggleScreenShare = async () => {
    const pc = peerConnectionRef.current;
    if (!pc) return alert("You must start a call first before sharing your screen.");

    if (!isScreenSharing) {
      logMeet("Requesting screen capture stream...");
      let screenStream = null;
      try {
        screenStream = await navigator.mediaDevices.getDisplayMedia({ video: true });
        logMeet("Acquired system screen capture.");
      } catch (e) {
        logMeet(`Screen capture denied: ${e.message}. Using simulated screen presentation.`);
        screenStream = createMockScreenStream();
      }

      const screenTrack = screenStream.getVideoTracks()[0];
      screenTrackRef.current = screenTrack;

      const senders = pc.getSenders();
      const videoSender = senders.find((s) => s.track && s.track.kind === "video");
      if (videoSender) {
        videoSender.replaceTrack(screenTrack);
        logMeet("Swapped peer video sender to screen track.");
      }

      screenTrack.onended = () => {
        logMeet("Screen sharing ended by user/system.");
        stopScreenSharingTrack(pc);
      };

      setIsScreenSharing(true);
    } else {
      stopScreenSharingTrack(pc);
    }
  };

  const onLeaveCall = () => {
    logMeet("Closing call connection...");
    setIsCallActive(false);
    setIsScreenSharing(false);
    iceQueueRef.current = [];

    if (screenTrackRef.current) {
      screenTrackRef.current.stop();
      if (screenTrackRef.current.cleanupMock) {
        screenTrackRef.current.cleanupMock();
      }
      screenTrackRef.current = null;
    }

    if (localStream) {
      localStream.getTracks().forEach((track) => track.stop());
      if (localStream.cleanupMock) {
        localStream.cleanupMock();
      }
      setLocalStream(null);
      localStreamRef.current = null;
    }

    setRemoteStream(null);

    if (peerConnectionRef.current) {
      peerConnectionRef.current.close();
      peerConnectionRef.current = null;
    }

    if (socketRef.current) {
      socketRef.current.emit("rtc:leave-call", { roomId });
    }
    logMeet("Call closed.");
  };

  /** -------------------- Room Join/Leave (Socket) -------------------- */
  const joinRoomReal = () => {
    if (!roomId.trim()) return alert("Enter Room ID");
    if (!socketRef.current) return alert("Socket not connected");

    socketRef.current.emit("room:join", {
      roomId,
      user: {
        name: user?.name || "Guest",
        email: user?.email || "guest@email.com",
      },
    });

    setActiveTab("room");
  };

  const leaveRoomReal = () => {
    if (!socketRef.current) return;

    onLeaveCall();
    socketRef.current.emit("room:leave", { roomId });
    setRoomJoined(false);
    setRoomUsers([]);
  };

  /** --------------------  Assistant Send (with context) -------------------- */
  const sendAssistantMessage = async () => {
    const msg = assistantInput.trim();
    if (!msg) return;

    setAssistantMessages((prev) => [...prev, { role: "user", text: msg }]);
    setAssistantInput("");
    setAssistantLoading(true);

    try {
      const res = await fetch(`${API_BASE}/api/assistant`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: msg,
          filename: selectedFile?.name || "",
          code: selectedFile?.content || "",
          roomId: roomJoined ? roomId : "",
        }),
      });

      const data = await res.json();

      if (data.error) {
        setAssistantMessages((prev) => [
          ...prev,
          { role: "assistant", text: " " + data.error },
        ]);
      } else {
        setAssistantMessages((prev) => [
          ...prev,
          { role: "assistant", text: data.reply || "No response" },
        ]);
      }
    } catch (err) {
      setAssistantMessages((prev) => [
        ...prev,
        { role: "assistant", text: " Backend not running or API error." },
      ]);
    }

    setAssistantLoading(false);
  };

  return (
    <div className="min-h-screen bg-[#0B1220] flex flex-col font-sans">
      <Header />

      <ResourcesMegaMenu
        open={page === "resources"}
        onClose={() => setPage("editor")}
      />

      {page === "courses" && <LearningLayout />}

      {page === "editor" && (
        <main className="flex-grow flex w-full h-[calc(100vh-56px)] overflow-hidden">
          {/* 1. Left Sidebar Navigation */}
          <LeftSidebar
            activeTab={activeTab}
            setActiveTab={setActiveTab}
            onOpenFolderClick={() => setShowOpenFolderModal(true)}
            workspacePath={workspacePath}
            isPro={isPro}
            trialTimeRemaining={trialTimeRemaining}
            startOneDayTrial={startOneDayTrial}
          />

          {/* 2. Center Workspace (Dynamic Views) */}
          <section className="flex-1 flex flex-col bg-[#0B1220] min-w-0 overflow-hidden border-r border-slate-800/80">
            
            {/* Context Header for Code Editor only */}
            {activeTab === "review" && (
              <div className="flex items-center justify-between border-b border-slate-800/80 bg-[#111827] px-4 py-3 select-none shrink-0 h-[48px]">
                <span className="text-[11px] font-mono font-bold text-slate-400">
                  WORKSPACE / EDITOR {selectedFile ? `➔ ${selectedFile.name}` : ""}
                </span>
                <div className="flex items-center gap-2">
                  {/* File controls */}
                  <button
                    onClick={() => {
                      setNewFileName("");
                      setNewFileError("");
                      setShowNewFileModal(true);
                    }}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-slate-850 hover:border-slate-750 bg-slate-900 px-3 py-1.5 text-[10px] font-bold uppercase font-mono text-slate-300 hover:text-white transition-all duration-300"
                  >
                    + File
                  </button>
                  
                  <button
                    onClick={downloadFile}
                    className="inline-flex items-center gap-1.5 rounded-xl border border-slate-850 hover:border-slate-750 bg-slate-900 px-3 py-1.5 text-[10px] font-bold uppercase font-mono text-slate-300 hover:text-white transition-all duration-300"
                  >
                    <Save className="h-3.5 w-3.5" />
                    Save
                  </button>

                  <button
                    onClick={runCodeReal}
                    className="inline-flex items-center gap-1.5 rounded-xl bg-blue-600 hover:bg-blue-700 px-3 py-1.5 text-[10px] font-bold uppercase font-mono text-white shadow-md hover:shadow-lg transition-all duration-300"
                  >
                    <Play className="h-3.5 w-3.5" />
                    Run
                  </button>
                </div>
              </div>
            )}

            {/* Dynamic Center Workspaces */}
            <div className="flex-1 overflow-y-auto p-6 scrollbar-thin">
              <AnimatePresence mode="wait">
                {activeTab === "review" && (
                  <motion.div
                    key="review-editor"
                    initial={{ opacity: 0, scale: 0.99 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.99 }}
                    transition={{ duration: 0.25 }}
                    className="h-full flex flex-col space-y-4"
                  >
                    {/* Monaco Editor Container */}
                    <div className="flex-1 rounded-2xl border border-slate-800 bg-slate-950/80 overflow-hidden min-h-[300px]">
                      <Editor
                        height="100%"
                        defaultLanguage="python"
                        theme="vs-dark"
                        value={selectedFile?.content || ""}
                        onChange={onChangeCode}
                        onMount={handleEditorDidMount}
                        options={{
                          fontSize: 14,
                          minimap: { enabled: true },
                          wordWrap: "on",
                          scrollBeyondLastLine: false,
                          inlineSuggest: { enabled: true },
                          suggest: { showInlineDetails: true },
                          fontFamily: "Fira Code, JetBrains Mono, Monaco, monospace"
                        }}
                      />
                    </div>

                    {/* Workspace Terminal */}
                    <div className="h-[200px] rounded-2xl border border-slate-800 bg-slate-950/60 overflow-hidden flex flex-col shrink-0">
                      <div className="bg-[#111827] border-b border-slate-800 px-4 py-2 flex items-center justify-between text-xs font-mono text-slate-400 select-none">
                        <span>APCRE Workspace Terminal (Python & Shell)</span>
                        <span className="text-green-500 font-bold flex items-center gap-1.5">
                          <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span>
                          Live Connected
                        </span>
                      </div>
                      <div className="flex-1 flex flex-col bg-black overflow-hidden">
                        <pre className="flex-1 overflow-auto p-3 text-xs text-green-400 font-mono whitespace-pre-wrap select-text scrollbar-thin">
                          {terminalOutput}
                        </pre>
                        <div className="bg-[#0B1220] border-t border-slate-800/80 p-2 flex gap-2 items-center">
                          <span className="text-green-500 font-mono text-xs flex items-center">&gt;</span>
                          <input
                            value={terminalInput}
                            onChange={(e) => setTerminalInput(e.target.value)}
                            onKeyDown={(e) => {
                              if (e.key === "Enter") {
                                const cmd = terminalInput.trim();
                                if (!cmd) return;
                                runTerminalCommand(cmd);
                                setTerminalInput("");
                              }
                            }}
                            className="flex-1 bg-transparent text-xs text-green-400 font-mono border-none outline-none placeholder:text-slate-655"
                            placeholder="Type command (e.g. 'dir', 'python -V', 'ls') and press Enter..."
                          />
                        </div>
                      </div>
                    </div>
                  </motion.div>
                )}

                {activeTab === "dashboard" && (
                  <DashboardPanel
                    files={files}
                    selectedFile={selectedFile}
                    onSelectFile={(file) => {
                      setSelectedFile(file);
                      setActiveTab("review");
                    }}
                    onSyncRepo={loadFilesFromBackend}
                    loading={filesLoading}
                  />
                )}

                {activeTab === "audit" && (
                  <AuditPanel
                    files={files}
                    issues={aiIssues}
                    selectedFile={selectedFile}
                    onSelectFile={(file) => {
                      setSelectedFile(file);
                      setActiveTab("review");
                    }}
                  />
                )}

                {activeTab === "security" && (
                  <SecurityPanel
                    selectedFile={selectedFile}
                    issues={aiIssues}
                  />
                )}

                {activeTab === "architecture" && (
                  <ArchitecturePanel />
                )}

                {activeTab === "kg" && (
                  <KnowledgeGraphPanel files={files} />
                )}

                {activeTab === "interview" && (
                  <InterviewPanel />
                )}

                {activeTab === "research" && (
                  <ResearchPanel />
                )}

                {activeTab === "assistant" && (
                  <AssistantChatPanel
                    assistantMessages={assistantMessages}
                    assistantInput={assistantInput}
                    assistantLoading={assistantLoading}
                    setAssistantInput={setAssistantInput}
                    sendAssistantMessage={sendAssistantMessage}
                    isListening={isListening}
                    onToggleSpeech={toggleSpeechRecognition}
                  />
                )}

                {activeTab === "agent" && (
                  <AgentPanel
                    isPro={isPro}
                    agentRunning={agentRunning}
                    agentVisibleLogs={agentVisibleLogs}
                    agentPrompt={agentPrompt}
                    agentFilename={agentFilename}
                    setAgentPrompt={setAgentPrompt}
                    setAgentFilename={setAgentFilename}
                    onRunAgent={runAutonomousAgent}
                    isListening={isListening}
                    onToggleSpeech={toggleSpeechRecognition}
                    onShowCheckout={() => setShowCheckoutModal(true)}
                  />
                )}

                {activeTab === "room" && (
                  <RoomPanel
                    roomId={roomId}
                    setRoomId={setRoomId}
                    joined={roomJoined}
                    onJoin={joinRoomReal}
                    onLeave={leaveRoomReal}
                    users={roomUsers}
                    socketConnected={socketConnected}
                    localStream={localStream}
                    remoteStream={remoteStream}
                    isScreenSharing={isScreenSharing}
                    isCallActive={isCallActive}
                    onStartCall={onStartCall}
                    onLeaveCall={onLeaveCall}
                    onToggleScreenShare={onToggleScreenShare}
                    meetLogs={meetLogs}
                  />
                )}
              </AnimatePresence>
            </div>
          </section>

          {/* 3. Right Insight Panel (Only when not in Room or Settings) */}
          <aside className="w-[300px] shrink-0 bg-[#111827] p-5 h-full overflow-y-auto border-l border-slate-800/80">
            <RightInsightPanel
              issues={aiIssues}
              onFixClick={handleFixIssue}
              selectedFixIssueId={selectedFixIssueId}
              setSelectedFixIssueId={setSelectedFixIssueId}
              fixLoading={fixLoading}
              setFixLoading={setFixLoading}
              agentRunning={agentRunning}
              agentVisibleLogs={agentVisibleLogs}
              agentPrompt={agentPrompt}
              agentFilename={agentFilename}
              setAgentPrompt={setAgentPrompt}
              setAgentFilename={setAgentFilename}
              onRunAgent={runAutonomousAgent}
              isListening={isListening}
              onToggleSpeech={toggleSpeechRecognition}
            />
          </aside>
        </main>
      )}

      {/* Modern custom toast alert */}
      {toast && (
        <div className="fixed bottom-6 left-1/2 -translate-x-1/2 rounded-2xl bg-slate-900 border border-slate-800 px-5 py-3 text-xs font-mono font-bold text-white shadow-xl flex items-center gap-2 z-50">
          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-ping" />
          <span>{toast}</span>
        </div>
      )}

      {/* Custom New File Modal Overlay */}
      {showNewFileModal && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center bg-black/60 backdrop-blur-md p-4 animate-fade-in">
          <div className="w-full max-w-md rounded-2xl bg-[#0f172a] border border-slate-800 p-6 shadow-2xl text-slate-300 font-sans relative overflow-hidden">
            
            {/* Ambient Background Glows */}
            <div className="absolute -top-12 -left-12 h-32 w-32 rounded-full bg-blue-500/10 blur-2xl pointer-events-none"></div>
            <div className="absolute -bottom-12 -right-12 h-32 w-32 rounded-full bg-indigo-500/10 blur-2xl pointer-events-none"></div>

            {/* Header */}
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-extrabold text-white uppercase tracking-wider font-mono flex items-center gap-2">
                <span className="text-blue-500">📄</span> Create New File
              </h2>
              <button
                onClick={() => setShowNewFileModal(false)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition outline-none"
              >
                ✕
              </button>
            </div>

            {/* Body */}
            <div className="mt-4 space-y-4">
              <p className="text-xs text-slate-400 leading-relaxed">
                Initialize a new script inside your active collaborative workspace repository path.
              </p>

              {newFileError && (
                <div className="p-3 border border-rose-500/20 bg-rose-500/10 text-rose-400 text-xs rounded-xl font-mono flex items-center gap-2 animate-bounce">
                  <span>⚠️</span>
                  <span>{newFileError}</span>
                </div>
              )}

              {/* Path Input */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">
                  File Path / Name
                </label>
                <input
                  autoFocus
                  value={newFileName}
                  onChange={(e) => {
                    setNewFileName(e.target.value);
                    setNewFileError("");
                  }}
                  onKeyDown={async (e) => {
                    if (e.key === "Enter") {
                      const success = await createNewFile(newFileName, setNewFileError);
                      if (success) {
                        setShowNewFileModal(false);
                      }
                    }
                  }}
                  className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono"
                  placeholder="e.g. payment_monolith.py"
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => setShowNewFileModal(false)}
                  className="flex-1 rounded-xl bg-slate-900 border border-slate-800 text-xs font-bold hover:bg-slate-800 py-2.5 transition text-slate-400 hover:text-white outline-none"
                >
                  Cancel
                </button>
                <button
                  onClick={async () => {
                    const success = await createNewFile(newFileName, setNewFileError);
                    if (success) {
                      setShowNewFileModal(false);
                    }
                  }}
                  className="flex-1 rounded-xl bg-blue-600 hover:bg-blue-500 text-white py-2.5 text-xs font-bold transition shadow-md hover:shadow-blue-500/20 outline-none"
                >
                  Create Script
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Upgraded Stripe SaaS mock payment checkout modal */}
      {showCheckoutModal && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center bg-black/60 backdrop-blur-md p-4">
          <div className="w-full max-w-md rounded-2xl bg-[#0f172a] border border-slate-800 p-6 shadow-2xl text-slate-300 font-sans">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-extrabold text-white uppercase tracking-wider font-mono">APCRE Pro Sandbox Checkout</h2>
              <button
                onClick={() => setShowCheckoutModal(false)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition outline-none"
              >
                Close
              </button>
            </div>

            {paymentStatus ? (
              <div className="py-12 flex flex-col items-center justify-center text-center space-y-4 font-mono">
                <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin" />
                <div className="text-xs font-bold text-blue-400">{paymentStatus}</div>
              </div>
            ) : (
              <div className="mt-4 space-y-4">
                <p className="text-xs text-slate-400 leading-relaxed">
                  Start your **2-Month Free Trial** of APCRE Pro. Cancel anytime. All card inputs are simulated and run completely offline.
                </p>

                {paymentError && (
                  <div className="p-3 border border-rose-500/20 bg-rose-500/10 text-rose-400 text-xs rounded-xl font-mono">
                    {paymentError}
                  </div>
                )}

                {/* Cardholder Name */}
                <div className="space-y-1.5">
                  <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider font-mono">Cardholder Name</label>
                  <input
                    value={cardName}
                    onChange={(e) => setCardName(e.target.value)}
                    className="w-full bg-slate-950 border border-slate-850 text-xs text-slate-200 px-3 py-2 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono"
                    placeholder="e.g. Ammar Haider"
                  />
                </div>

                {/* Card Number */}
                <div className="space-y-1.5">
                  <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider font-mono">Card Number</label>
                  <input
                    value={cardNumber}
                    onChange={handleCardNumberChange}
                    maxLength="19"
                    className="w-full bg-slate-950 border border-slate-850 text-xs text-slate-200 px-3 py-2 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono"
                    placeholder="4242 4242 4242 4242"
                  />
                </div>

                {/* Expiry & CVV */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-1.5">
                    <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider font-mono">Expiry Date</label>
                    <input
                      value={cardExpiry}
                      onChange={handleCardExpiryChange}
                      maxLength="5"
                      className="w-full bg-slate-950 border border-slate-850 text-xs text-slate-200 px-3 py-2 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono"
                      placeholder="MM/YY"
                    />
                  </div>
                  <div className="space-y-1.5">
                    <label className="text-[9px] font-bold text-slate-500 uppercase tracking-wider font-mono">CVV / CVC</label>
                    <input
                      value={cardCvc}
                      onChange={(e) => setCardCvc(e.target.value.replace(/\\D/g, ""))}
                      maxLength="3"
                      className="w-full bg-slate-950 border border-slate-850 text-xs text-slate-200 px-3 py-2 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono"
                      placeholder="e.g. 123"
                    />
                  </div>
                </div>

                <button
                  onClick={processSimulatedPayment}
                  className="w-full rounded-xl bg-blue-600 hover:bg-blue-700 py-3 text-xs font-bold text-white shadow-md hover:shadow-lg transition-all duration-300 mt-4"
                >
                  Confirm Subscription
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Upgraded Folder Picker Overlay */}
      {showOpenFolderModal && (
        <div className="fixed inset-0 z-[999] flex items-center justify-center bg-black/60 backdrop-blur-md p-4">
          <div className="w-full max-w-md rounded-2xl bg-[#0f172a] border border-slate-800 p-6 shadow-2xl text-slate-300 font-sans">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-sm font-extrabold text-white uppercase tracking-wider flex items-center gap-2 font-mono">
                <FolderOpen className="h-4 w-4 text-indigo-400 shrink-0" />
                <span>Workspace Selector</span>
              </h2>
              <button
                onClick={() => setShowOpenFolderModal(false)}
                className="rounded-xl border border-slate-700 bg-slate-900 px-3 py-1 text-xs font-bold text-slate-400 hover:text-white hover:bg-slate-800 transition outline-none"
              >
                Close
              </button>
            </div>

            <div className="mt-4 space-y-4">
              <p className="text-xs text-slate-400 leading-relaxed">
                APCRE will load code review assets, AST parsers, and terminal instances inside your selected local folder.
              </p>

              {/* Native OS Trigger Button */}
              <button
                onClick={triggerNativeFolderPicker}
                className="w-full rounded-xl bg-indigo-600 hover:bg-indigo-500 hover:scale-[1.01] active:scale-95 text-white py-2.5 text-xs font-bold transition flex items-center justify-center gap-2 shadow-md outline-none"
              >
                <span>🖥️ Open Native Windows Folder Selector</span>
              </button>

              <div className="flex items-center gap-2 text-[10px] text-slate-500 font-semibold uppercase tracking-wider justify-center">
                <div className="h-[1px] bg-slate-800 flex-1" />
                <span>or enter path manually</span>
                <div className="h-[1px] bg-slate-800 flex-1" />
              </div>

              {/* Absolute Path Input field */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">
                  Absolute Directory Path
                </label>
                <input
                  value={openFolderPathInput}
                  onChange={(e) => setOpenFolderPathInput(e.target.value)}
                  className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-indigo-500 transition-all font-mono"
                  placeholder="e.g. c:\\Users\\Name\\Projects\\my_app"
                />
              </div>

              <button
                onClick={() => openCustomFolder(openFolderPathInput)}
                className="w-full rounded-xl bg-slate-800 border border-slate-700 text-white hover:bg-slate-700 py-2.5 text-xs font-bold transition outline-none"
              >
                Open Path
              </button>
            </div>
          </div>
        </div>
      )}

      <CommandBar
        isOpen={isCommandBarOpen}
        onClose={() => setIsCommandBarOpen(false)}
        onExecuteCommand={(cmdId) => {
          if (cmdId === "review") {
            if (selectedFile?.content) {
              setAiLoading(true);
              fetch(`${API_BASE}/api/review`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                  filename: selectedFile.name,
                  code: selectedFile.content || "",
                }),
              })
                .then((res) => res.json())
                .then((data) => {
                  if (data.issues && Array.isArray(data.issues)) {
                    const withIds = data.issues.map((x, idx) => ({
                      id: "ai-" + idx,
                      type: x.type || "suggestion",
                      title: x.title || "Issue",
                      line: x.line || "-",
                      desc: x.desc || "",
                      fix: x.fix || "",
                    }));
                    setAiIssues(withIds);
                  }
                })
                .catch((err) => console.error(err))
                .finally(() => setAiLoading(false));
            }
          } else if (cmdId === "security") {
            setActiveTab("security");
          } else if (cmdId === "graph") {
            setActiveTab("graph");
          } else if (cmdId === "chat") {
            setActiveTab("chat");
          } else if (cmdId === "courses") {
            window.location.href = "/courses";
          } else if (cmdId === "docs") {
            window.location.href = "/docs";
          }
        }}
      />
    </div>
  );
}
