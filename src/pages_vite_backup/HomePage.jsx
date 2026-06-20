import React, { useRef, useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import Footer from "../components/Footer";
import Header from "../components/Header";
import { motion } from "framer-motion";
import { 
  ChevronRight, 
  Star,
  Smartphone,
  Shield,
  Download,
  Users,
  Code,
  Sparkles,
  Bot,
  Play,
  Terminal,
  Activity,
  CheckCircle2,
  HelpCircle,
  FolderGit2
} from "lucide-react";

export default function HomePage() {
  const scrollRef = useRef(null);
  const navigate = useNavigate();

  const CAROUSEL_IMAGES = [
    "https://images.unsplash.com/photo-1573164713988-8665fc963095?auto=format&fit=crop&w=600&h=600&q=80",
    "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=600&h=600&q=80",
    "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?auto=format&fit=crop&w=600&h=600&q=80",
    "https://images.unsplash.com/photo-1517048676732-d65bc937f952?auto=format&fit=crop&w=600&h=600&q=80",
  ];

  const extendedImages = Array(20).fill(CAROUSEL_IMAGES).flat();

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollLeft = scrollRef.current.scrollWidth / 2;
    }
  }, []);

  const handleScrollBounds = () => {
    const el = scrollRef.current;
    if (!el) return;
    if (el.scrollLeft <= 500) {
      el.scrollLeft = (el.scrollWidth / 2) - 500;
    } else if (el.scrollLeft >= el.scrollWidth - el.clientWidth - 500) {
      el.scrollLeft = (el.scrollWidth / 2) + 500;
    }
  };

  const scrollLeft = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: -420, behavior: 'smooth' });
    }
  };

  const scrollRight = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({ left: 420, behavior: 'smooth' });
    }
  };

  const [activeFaq, setActiveFaq] = useState(null);

  return (
    <div className="font-sans min-h-screen bg-[#0B1220] text-slate-100 selection:bg-blue-500/30 overflow-x-hidden">
      
      {/* 1. HEADER */}
      <Header />

      {/* 2. PREMIUM HERO SECTION */}
      <section className="relative pt-24 pb-32 px-8 md:px-16 max-w-7xl mx-auto flex flex-col lg:flex-row items-center gap-12">
        {/* Background glow effects */}
        <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] bg-blue-500/10 rounded-full blur-[120px] pointer-events-none select-none" />
        <div className="absolute top-1/3 right-1/4 -translate-y-1/2 w-[400px] h-[400px] bg-indigo-500/10 rounded-full blur-[140px] pointer-events-none select-none" />

        <div className="lg:w-1/2 z-10 space-y-6 text-left">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-blue-500/5 px-3 py-1 text-[10px] font-bold uppercase font-mono tracking-widest text-blue-400">
            <Sparkles className="h-3 w-3" />
            <span>Next-Gen Autonomous Code Review</span>
          </div>

          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-black text-white leading-none tracking-tight">
            Write better <br/>
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              Python Code
            </span> <br/>
            with AI Agent
          </h1>

          <p className="text-sm sm:text-base text-slate-400 max-w-lg leading-relaxed font-semibold">
            APCRE brings real-time autonomous AST reviews, OWASP vulnerability diagnostics, 
            Wilcoxon t-test research, and WebRTC interactive pairing right inside your browser.
          </p>

          <div className="flex flex-wrap gap-4 pt-2">
            <Link to="/editor">
              <button className="px-6 py-3 text-xs font-extrabold uppercase font-mono tracking-wider text-white bg-blue-600 hover:bg-blue-500 shadow-lg hover:shadow-blue-500/20 rounded-xl transition-all duration-300">
                Start Coding Free
              </button>
            </Link>
            <Link to="/login">
              <button className="px-6 py-3 text-xs font-extrabold uppercase font-mono tracking-wider text-slate-300 border border-slate-800 rounded-xl hover:bg-slate-800 hover:text-white transition-all duration-300">
                Log In Portal
              </button>
            </Link>
          </div>
        </div>

        {/* Hero mockup frame */}
        <div className="lg:w-1/2 w-full mt-8 lg:mt-0 z-10">
          <div className="w-full h-[320px] sm:h-[420px] border border-slate-800 rounded-2xl overflow-hidden shadow-2xl relative bg-slate-950/80 p-1.5 backdrop-blur-md">
            <div className="h-[28px] w-full bg-[#111827] rounded-t-xl border-b border-slate-800/80 flex items-center px-4 justify-between select-none">
              <div className="flex gap-1.5">
                <span className="w-2.5 h-2.5 rounded-full bg-rose-500" />
                <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              </div>
              <span className="text-[10px] font-mono text-slate-500">APCRE / workspace_diagnostics.py</span>
              <span className="w-4 h-4" />
            </div>
            <img 
              src="https://images.unsplash.com/photo-1542831371-29b0f74f9713?auto=format&fit=crop&q=80&w=800&h=600" 
              alt="Editor IDE" 
              className="w-full h-[calc(100%-28px)] object-cover rounded-b-xl opacity-80" 
            />
          </div>
        </div>
      </section>

      {/* 3. CAPABILITIES GRIDS */}
      <section className="py-24 border-t border-slate-800/80 px-8 bg-[#111827]/40 relative">
        <div className="max-w-7xl mx-auto text-center space-y-4 mb-16">
          <p className="text-xs font-bold uppercase tracking-widest text-blue-500 font-mono">Platform Capabilities</p>
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">
            Designed for Autonomous Intelligence
          </h2>
          <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
            Catch architectural anti-patterns, test dynamic loops, and collaborate remotely in seconds.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-7xl mx-auto">
          {[
            { 
              label: "DEVELOPMENT", title: "Monaco Python IDE", 
              desc: "Full inline autocomplete, rich syntax coloring, and monospaced diagnostic timelines.", 
              img: "https://images.unsplash.com/photo-1542831371-29b0f74f9713?auto=format&fit=crop&w=400&q=80" 
            },
            { 
              label: "INTELLIGENCE", title: "Deep AI Review", 
              desc: "catch complex dynamic programming bounds, OOP violations, and recursion faults instantly.", 
              img: "https://images.unsplash.com/photo-1573164574572-cb89e39749b4?auto=format&fit=crop&w=400&q=80" 
            },
            { 
              label: "MULTIPLAYER", title: "WebRTC Live Rooms", 
              desc: "Pair program natively with video feeds, screen sharing, and socket sync logic.", 
              img: "https://images.unsplash.com/photo-1522071820081-009f0129c71c?auto=format&fit=crop&w=400&q=80" 
            },
            { 
              label: "AUDITING", title: "OWASP Security", 
              desc: "Comprehensive CWE diagnostics, risk categorizations, and detailed automated repairs.", 
              img: "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=400&q=80" 
            }
          ].map((item, i) => (
            <div key={i} className="flex flex-col justify-between border border-slate-800 bg-[#111827] rounded-2xl overflow-hidden hover:border-blue-500/40 hover:shadow-xl hover:shadow-blue-500/5 transition-all duration-300 group">
              <div className="p-6">
                <p className="text-[10px] font-bold text-blue-400 font-mono tracking-wider mb-2">{item.label}</p>
                <h3 className="text-lg font-bold text-white mb-2 leading-tight">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed mb-6">{item.desc}</p>
                <Link to="/editor" className="text-xs font-bold font-mono uppercase tracking-wider text-slate-300 group-hover:text-blue-400 transition-colors flex items-center gap-1.5">
                  <span>Start Testing</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
              </div>
              <div className="h-36 overflow-hidden bg-slate-900 border-t border-slate-800/80">
                <img src={item.img} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 opacity-60" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 4. WORKFLOW TIMELINE */}
      <section className="py-24 border-t border-slate-800/80 px-8 max-w-7xl mx-auto">
        <div className="text-center space-y-4 mb-16">
          <p className="text-xs font-bold uppercase tracking-widest text-emerald-500 font-mono">Workflow</p>
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">How APCRE Operates</h2>
          <p className="text-slate-400 text-sm max-w-md mx-auto leading-relaxed">
            From single scripts to full-fledged K-fold empirical validations, intelligence is native.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {[
            { 
              step: "01", title: "Write Scripts", 
              desc: "Input python code into the workspace terminal or load local folders instantly." 
            },
            { 
              step: "02", title: "Review Findings", 
              desc: "Deep AST models run syntax, OOP complexity, and security scans." 
            },
            { 
              step: "03", title: "AI Assistant Help", 
              desc: "Tutor chat with speech dictation resolves logic bottlenecks." 
            },
            { 
              step: "04", title: "Wilcoxon Validation", 
              desc: "Evaluate precision-recall matrices and export standardized thesis PDFs." 
            }
          ].map((item, i) => (
            <div key={i} className="p-6 rounded-2xl border border-slate-800 bg-[#111827] shadow-lg flex flex-col justify-between hover:border-slate-700 transition duration-300">
              <div>
                <div className="text-3xl font-extrabold font-mono text-emerald-400 mb-4">{item.step}</div>
                <h3 className="text-base font-bold text-white mb-2">{item.title}</h3>
                <p className="text-xs text-slate-400 leading-relaxed">{item.desc}</p>
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* 5. VISUAL DEMONSTRATION CAROUSEL */}
      <section className="py-24 border-t border-slate-800/80 px-8 text-center bg-[#111827]/20 relative overflow-hidden">
        <h2 className="text-3xl font-extrabold text-white mb-2">See It In Action</h2>
        <p className="text-slate-400 text-sm mb-12">Dynamic previews from the interactive workspace</p>
        
        <div className="relative max-w-5xl mx-auto flex items-center justify-center">
          <button 
            onClick={scrollLeft}
            className="absolute -left-6 z-20 w-10 h-10 border border-slate-800 bg-[#111827] hover:bg-slate-800 hover:text-white rounded-full flex items-center justify-center shadow-lg transition"
          >
             <ChevronRight className="w-5 h-5 rotate-180 text-slate-300" />
          </button>
          
          <div 
            ref={scrollRef}
            onScroll={handleScrollBounds}
            className="flex space-x-6 overflow-x-auto snap-x snap-mandatory py-4 px-2 hide-scrollbar scroll-smooth w-full select-none"
          >
            {extendedImages.map((img, i) => (
              <div key={i} className="snap-center min-w-[280px] sm:min-w-[400px] h-[220px] sm:h-[300px] rounded-2xl overflow-hidden shadow-2xl border border-slate-800 bg-slate-950 flex-shrink-0 relative group">
                <img src={img} className="w-full h-full object-cover opacity-60 group-hover:scale-102 transition duration-500" alt={`Editor ${i}`} />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300 flex items-end p-4">
                  <div className="text-left text-xs text-white font-mono">Active reviewing module enabled</div>
                </div>
              </div>
            ))}
          </div>

          <button 
            onClick={scrollRight}
            className="absolute -right-6 z-20 w-10 h-10 border border-slate-800 bg-[#111827] hover:bg-slate-800 hover:text-white rounded-full flex items-center justify-center shadow-lg transition"
          >
             <ChevronRight className="w-5 h-5 text-slate-300" />
          </button>
        </div>
      </section>

      {/* 6. ADVANTAGES SECTION */}
      <section className="py-24 border-t border-slate-800/80 px-8 bg-[#111827]/40">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row gap-12 items-center">
          <div className="lg:w-1/3 text-left space-y-4">
            <p className="text-xs font-bold uppercase tracking-widest text-indigo-500 font-mono">Academic Excellence</p>
            <h2 className="text-3xl font-extrabold text-white leading-tight">Why Researchers <br/>Trust APCRE</h2>
            <p className="text-slate-400 text-sm leading-relaxed font-semibold">
              APCRE integrates deep language-server telemetry with trained classifiers to measure absolute code quality boundaries.
            </p>
            <div className="pt-2">
              <Link to="/about">
                <button className="px-5 py-2 text-xs font-extrabold uppercase font-mono tracking-wider text-slate-300 border border-slate-800 rounded-xl hover:bg-slate-850 transition">
                  About Team
                </button>
              </Link>
            </div>
          </div>

          <div className="lg:w-2/3 grid grid-cols-1 sm:grid-cols-2 gap-6 w-full">
            {[
              { icon: <Shield className="h-5 w-5 text-rose-400" />, title: "Precision Metrics", text: "Evaluate true semantic quality via Wilcoxon signed-rank matrices showing 94.59% accuracy." },
              { icon: <Users className="h-5 w-5 text-blue-400" />, title: "Live Pair Rooms", text: "Multiplayer pairing lets instructors directly audit students code in active sandboxes." },
              { icon: <Code className="h-5 w-5 text-cyan-400" />, title: "Structural Smells", text: "捕获 recursion loops, decoupled dependencies, and complexity index errors." },
              { icon: <Smartphone className="h-5 w-5 text-emerald-400" />, title: "Online Testing", text: "Compile and execute python files securely without local compiler installations." }
            ].map((adv, idx) => (
              <div key={idx} className="p-5 border border-slate-800 bg-[#111827] rounded-2xl flex items-start gap-4">
                <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 shrink-0">
                  {adv.icon}
                </div>
                <div className="text-left space-y-1">
                  <h4 className="font-bold text-white text-sm">{adv.title}</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">{adv.text}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* 7. FAQ SECTION */}
      <section className="py-24 border-t border-slate-800/80 px-8 max-w-4xl mx-auto">
        <div className="text-center space-y-4 mb-16">
          <p className="text-xs font-bold uppercase tracking-widest text-blue-500 font-mono">Questions</p>
          <h2 className="text-3xl font-extrabold text-white">Ecosystem FAQs</h2>
          <p className="text-slate-400 text-sm">Everything you need to know about the APCRE workspace.</p>
        </div>

        <div className="space-y-4 text-left">
          {[
            { q: "How does APCRE review code?", a: "APCRE runs structural AST analyzers alongside custom language-tutors to extract syntax trees, decouple indexes, and highlight performance issues." },
            { q: "Can I collaborate live?", a: "Yes. Use 'Collaboration Room' from the sidebar navigation to spin up instantaneous peer-coding sandboxes with audio/video feeds." },
            { q: "Is the compiler fully local?", a: "All processes compile on our secure Node and Flask backend environments, running code seamlessly without requiring local python dependencies." }
          ].map((faq, idx) => (
            <div 
              key={idx} 
              className="rounded-2xl border border-slate-800 bg-[#111827] overflow-hidden transition-all duration-300"
            >
              <button 
                onClick={() => setActiveFaq(activeFaq === idx ? null : idx)}
                className="w-full flex items-center justify-between p-5 text-sm font-bold text-white focus:outline-none"
              >
                <span>{faq.q}</span>
                <span className={`text-slate-400 transition-transform duration-300 ${activeFaq === idx ? "rotate-180" : ""}`}>▼</span>
              </button>
              {activeFaq === idx && (
                <div className="px-5 pb-5 text-xs text-slate-400 leading-relaxed border-t border-slate-850 pt-3">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </section>

      {/* 8. NEWSLETTER */}
      <section className="py-16 px-8 border-t border-slate-800/80 bg-[#111827]/30">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="text-center md:text-left">
            <h4 className="font-bold text-white text-lg mb-1">Stay in the Loop</h4>
            <p className="text-xs text-slate-400 font-semibold">Get updates on new academic features and model retrains.</p>
          </div>
          <div className="flex w-full md:w-auto items-center gap-2 max-w-sm">
            <input 
              type="email" 
              placeholder="e.g. ammar@apcre.dev" 
              className="w-full sm:w-64 bg-[#0B1220] border border-slate-800 text-slate-200 text-xs px-4 py-2.5 rounded-xl outline-none focus:border-blue-500/50 transition-all font-mono"
            />
            <button className="px-5 py-2.5 text-xs font-extrabold uppercase font-mono tracking-wider text-white bg-blue-600 hover:bg-blue-500 rounded-xl transition whitespace-nowrap shadow-md">
              Subscribe
            </button>
          </div>
        </div>
      </section>

      {/* 9. GLOBAL FOOTER */}
      <Footer />

    </div>
  );
}