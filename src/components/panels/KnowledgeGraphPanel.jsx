import React, { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Share2, ZoomIn, ZoomOut, RotateCcw, Info, CheckSquare } from "lucide-react";

export default function KnowledgeGraphPanel({ files }) {
  const [zoom, setZoom] = useState(1);
  const [panX, setPanX] = useState(0);
  const [panY, setPanY] = useState(0);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [selectedNode, setSelectedNode] = useState(null);

  // Fallback defaults if no files are loaded
  const defaultNodes = [
    { id: "apcre_api", label: "apcre_api.py", type: "module", x: 200, y: 150, details: "The core Flask gateway server orchestrating code reviews, AST parsing, and AI features." },
    { id: "design_review", label: "DesignReviewEngine", type: "class", x: 100, y: 70, details: "AST-based analyzer verifying SOLID parameters, Gang of Four (GoF) patterns, and technical debt." },
    { id: "coin_change", label: "coin_change()", type: "function", x: 300, y: 80, details: "Dynamic Programming memoized algorithm template compiled by the offline agent." },
    { id: "sqlite3", label: "SQLite Memory DB", type: "library", x: 320, y: 220, details: "Offline SQL repository storing agent repair logs and software engineering knowledge graphs." },
    { id: "decorator", label: "GoF Singleton Pattern", type: "pattern", x: 80, y: 220, details: "Structural design pattern checking class instances across execution paths." }
  ];

  const defaultLinks = [
    { source: "apcre_api", target: "design_review" },
    { source: "apcre_api", target: "coin_change" },
    { source: "apcre_api", target: "sqlite3" },
    { source: "design_review", target: "decorator" }
  ];

  // Dynamic code structure parser (AST/Regex Simulation on active workspace)
  const { nodes, links } = useMemo(() => {
    const pyFiles = files ? files.filter(f => f.name && f.name.endsWith(".py")) : [];
    
    if (pyFiles.length === 0) {
      return { nodes: defaultNodes, links: defaultLinks };
    }

    const parsedNodes = [];
    const parsedLinks = [];
    const totalFiles = pyFiles.length;

    // Anchor SQLite DB in the absolute center
    const hasDB = pyFiles.some(f => {
      const code = f.content || "";
      return code.includes("sqlite3") || code.includes("connect(") || code.includes("apcre_memory.db");
    });

    if (hasDB) {
      parsedNodes.push({
        id: "lib_sqlite",
        label: "SQLite Memory DB",
        type: "library",
        x: 200,
        y: 150,
        details: "SQLite persistent storage boundary. Direct connections initialized here cause High SQL Coupling smells."
      });
    }

    pyFiles.forEach((file, fIdx) => {
      const fileId = `mod_${file.name.replace(/\./g, "_")}`;
      const angle = (fIdx * 2 * Math.PI) / totalFiles;
      
      // Arrange modules in a circle around the center
      const modX = 200 + Math.cos(angle) * 80;
      const modY = 150 + Math.sin(angle) * 80;

      parsedNodes.push({
        id: fileId,
        label: file.name,
        type: "module",
        x: modX,
        y: modY,
        details: `Active workspace script parsed statically in real-time. Size: ${(file.content || "").length} bytes.`
      });

      if (hasDB && (file.content || "").includes("sqlite3")) {
        parsedLinks.push({ source: fileId, target: "lib_sqlite" });
      }

      const code = file.content || "";

      // 1. Dynamic Class Parser
      const classRegex = /class\s+(\w+)/g;
      let match;
      let cCount = 0;
      while ((match = classRegex.exec(code)) !== null) {
        const className = match[1];
        const classId = `class_${fileId}_${className}`;
        
        // Arrange classes slightly offset from their parent module
        const classAngle = angle + (cCount + 1) * 0.5;
        const clsX = modX + Math.cos(classAngle) * 55;
        const clsY = modY + Math.sin(classAngle) * 55;

        parsedNodes.push({
          id: classId,
          label: className,
          type: "class",
          x: clsX,
          y: clsY,
          details: `Class definition found inside ${file.name}. Performs structural operations and handles data context.`
        });
        parsedLinks.push({ source: fileId, target: classId });

        // GoF Singleton pattern check
        if (code.includes("get_instance") || code.includes("_instance")) {
          const patId = `pat_${classId}_singleton`;
          parsedNodes.push({
            id: patId,
            label: "GoF Singleton Pattern",
            type: "pattern",
            x: clsX + Math.cos(classAngle + 0.3) * 40,
            y: clsY + Math.sin(classAngle + 0.3) * 40,
            details: "Creational design pattern ensuring a single object instance. Its hand-rolled implementation violates DIP."
          });
          parsedLinks.push({ source: classId, target: patId });
        }
        cCount++;
      }

      // 2. Dynamic Function Parser
      const funcRegex = /def\s+(\w+)\s*\(/g;
      let fCount = 0;
      while ((match = funcRegex.exec(code)) !== null) {
        const funcName = match[1];
        if (funcName.startsWith("__") || fCount >= 4) continue; // skip init methods & limit function explosion
        
        const funcId = `func_${fileId}_${funcName}`;
        const funcAngle = angle - (fCount + 1) * 0.4;
        
        parsedNodes.push({
          id: funcId,
          label: `${funcName}()`,
          type: "function",
          x: modX + Math.cos(funcAngle) * 45,
          y: modY + Math.sin(funcAngle) * 45,
          details: `Algorithm method or service endpoint parsed inside ${file.name}.`
        });
        parsedLinks.push({ source: fileId, target: funcId });
        fCount++;
      }
    });

    return { nodes: parsedNodes, links: parsedLinks };
  }, [files]);

  // Mouse handlers for dragging/panning
  const handleMouseDown = (e) => {
    setIsDragging(true);
    setDragStart({ x: e.clientX - panX, y: e.clientY - panY });
  };

  const handleMouseMove = (e) => {
    if (!isDragging) return;
    setPanX(e.clientX - dragStart.x);
    setPanY(e.clientY - dragStart.y);
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleZoomIn = () => setZoom(prev => Math.min(2.5, prev + 0.15));
  const handleZoomOut = () => setZoom(prev => Math.max(0.4, prev - 0.15));
  const handleReset = () => {
    setZoom(1);
    setPanX(0);
    setPanY(0);
    setSelectedNode(null);
  };

  const getNodeColor = (type) => {
    switch (type) {
      case "module": return "fill-blue-500 stroke-blue-400";
      case "class": return "fill-purple-500 stroke-purple-400";
      case "function": return "fill-amber-500 stroke-amber-400";
      case "library": return "fill-indigo-500 stroke-indigo-400";
      case "pattern": return "fill-rose-500 stroke-rose-400";
      default: return "fill-slate-500 stroke-slate-400";
    }
  };

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
            <Share2 className="h-6 w-6 text-indigo-500" />
            <span>Interactive Repository Knowledge Graph</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">Audit coupling bounds and map your code's path to clean, decoupled Hexagonal architectures.</p>
        </div>
      </div>

      {/* 2. Main Graph Column Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        
        {/* SVG Viewport (3 cols) */}
        <div className="lg:col-span-3 flex flex-col rounded-2xl border border-slate-800 bg-slate-950/60 p-4 shadow-lg min-h-[380px] select-none relative overflow-hidden">
          
          {/* Zoom/Pan overlay widgets */}
          <div className="absolute top-4 right-4 z-20 flex items-center gap-2 rounded-xl bg-slate-900/80 border border-slate-800 p-1.5 backdrop-blur-sm">
            <button onClick={handleZoomIn} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors" title="Zoom In">
              <ZoomIn className="h-3.5 w-3.5" />
            </button>
            <button onClick={handleZoomOut} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors" title="Zoom Out">
              <ZoomOut className="h-3.5 w-3.5" />
            </button>
            <button onClick={handleReset} className="p-2 hover:bg-slate-800 rounded-lg text-slate-400 hover:text-white transition-colors" title="Reset Viewport">
              <RotateCcw className="h-3.5 w-3.5" />
            </button>
          </div>

          {/* Legend widget overlay */}
          <div className="absolute bottom-4 left-4 z-20 flex flex-wrap gap-2 text-[9px] font-mono tracking-wide rounded-xl bg-slate-900/80 border border-slate-800 p-2 backdrop-blur-sm">
            <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-blue-500" /> <span>Module</span></div>
            <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-purple-500" /> <span>Class</span></div>
            <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-amber-500" /> <span>Function</span></div>
            <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-indigo-500" /> <span>Library</span></div>
            <div className="flex items-center gap-1.5"><span className="w-1.5 h-1.5 rounded-full bg-rose-500" /> <span>Pattern</span></div>
          </div>

          {/* SVG Canvas */}
          <div
            onMouseDown={handleMouseDown}
            onMouseMove={handleMouseMove}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseUp}
            className={`flex-1 w-full h-full cursor-grab active:cursor-grabbing overflow-hidden ${isDragging ? "active" : ""}`}
          >
            <svg
              className="w-full h-full min-h-[340px]"
              viewBox="0 0 400 300"
            >
              <g transform={`translate(${panX}, ${panY}) scale(${zoom})`}>
                
                {/* SVG Links */}
                {links.map((link, idx) => {
                  const srcNode = nodes.find(n => n.id === link.source);
                  const tgtNode = nodes.find(n => n.id === link.target);
                  if (!srcNode || !tgtNode) return null;
                  return (
                    <line
                      key={idx}
                      x1={srcNode.x}
                      y1={srcNode.y}
                      x2={tgtNode.x}
                      y2={tgtNode.y}
                      stroke="#334155"
                      strokeWidth="1"
                      strokeDasharray="2,2"
                    />
                  );
                })}

                {/* SVG Nodes */}
                {nodes.map((node, idx) => {
                  const isSelected = selectedNode && selectedNode.id === node.id;
                  return (
                    <g
                      key={idx}
                      transform={`translate(${node.x}, ${node.y})`}
                      onClick={(e) => {
                        e.stopPropagation();
                        setSelectedNode(node);
                      }}
                      className="cursor-pointer group"
                    >
                      {/* Selection Glow */}
                      {isSelected && (
                        <circle
                          r="14"
                          className="fill-blue-500/10 stroke-blue-500/30 stroke-2 animate-pulse"
                        />
                      )}
                      
                      {/* Node Shape */}
                      <circle
                        r="8"
                        className={`stroke-2 transition-all duration-300 hover:scale-[1.15] ${getNodeColor(node.type)}`}
                      />

                      {/* Node Label Text */}
                      <text
                        y="18"
                        textAnchor="middle"
                        className="fill-slate-300 text-[7px] font-bold font-mono tracking-tight transition-colors group-hover:fill-white select-none"
                      >
                        {node.label}
                      </text>
                    </g>
                  );
                })}
              </g>
            </svg>
          </div>
        </div>

        {/* Node details panel inspector (2 cols) */}
        <div className="rounded-2xl border border-slate-800 bg-[#111827] p-5 lg:col-span-2 shadow-lg flex flex-col min-h-[380px]">
          <h3 className="text-sm font-bold text-white mb-4 flex items-center gap-2 font-mono uppercase tracking-wider">
            <Info className="h-4 w-4 text-blue-400" />
            <span>Graph Component Inspector</span>
          </h3>
          {selectedNode ? (
            <div className="flex-1 flex flex-col justify-between">
              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800/80 font-mono">
                  <div className="text-[10px] text-slate-400 uppercase tracking-wider">Indexed Node</div>
                  <div className="text-sm font-extrabold text-white mt-1">{selectedNode.label}</div>
                  <div className="text-[9px] uppercase tracking-wider text-slate-500 mt-2 font-bold flex items-center gap-1.5">
                    <span className="w-1.5 h-1.5 rounded-full bg-blue-500" />
                    <span>Type: {selectedNode.type}</span>
                  </div>
                </div>

                <div className="p-4 rounded-xl border border-slate-800/80 bg-slate-950/20 text-xs leading-relaxed text-slate-400">
                  <span className="font-bold text-slate-200 block mb-2 font-mono uppercase tracking-wider text-[10px]">Description Summary</span>
                  {selectedNode.details}
                </div>
              </div>

              <div className="p-4 rounded-xl bg-indigo-500/5 border border-indigo-500/10 flex items-start gap-3 mt-6">
                <CheckSquare className="h-5 w-5 text-indigo-400 shrink-0 mt-0.5" />
                <div className="text-[11px] leading-relaxed text-slate-400">
                  <span className="font-bold text-slate-200 block">SE-Knowledge Graph Reasoning</span>
                  Relations are parsed statically from active workspace code content. Clicking dependencies highlights optimization tracks.
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-grow flex flex-col items-center justify-center text-center py-16 text-slate-500">
              <Share2 className="h-10 w-10 text-slate-600 mb-2 animate-pulse" />
              <p className="text-xs max-w-[200px] leading-relaxed">
                Click a graph node in the map panel to inspect components, coupling links, and optimization schemas.
              </p>
            </div>
          )}
        </div>

      </div>
    </motion.div>
  );
}
