import React from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { FileText, Terminal, Shield, HelpCircle, BookOpen } from 'lucide-react';

export default function DocsPage() {
  return (
    <div className="min-h-screen bg-[#0B1220] flex flex-col font-sans text-slate-200">
      <Header />
      
      <main className="flex-grow max-w-7xl mx-auto px-8 py-16 flex w-full gap-8 relative">
        <div className="absolute top-1/4 left-1/4 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-blue-500/5 rounded-full blur-[100px] pointer-events-none select-none" />

        {/* Sidebar Nav */}
        <aside className="w-1/4 hidden md:block flex-shrink-0">
          <div className="sticky top-8 bg-[#111827] p-6 rounded-2xl border border-slate-800/80 shadow-xl space-y-4">
            <h3 className="font-bold text-white uppercase tracking-wider text-xs font-mono flex items-center gap-2">
              <BookOpen className="h-4 w-4 text-blue-400" />
              <span>APCRE Docs</span>
            </h3>
            <ul className="space-y-3 text-xs font-semibold text-slate-400">
              <li><a href="#getting-started" className="text-blue-400 hover:text-blue-300 font-bold block transition">Getting Started</a></li>
              <li><a href="#api-reference" className="hover:text-white block transition">API Reference</a></li>
              <li><a href="#ml-models" className="hover:text-white block transition">ML Models Setup</a></li>
              <li><a href="#troubleshooting" className="hover:text-white block transition">Troubleshooting</a></li>
            </ul>
          </div>
        </aside>

        {/* Content */}
        <motion.article 
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex-1 bg-[#111827] p-10 rounded-2xl border border-slate-800/80 shadow-2xl space-y-6 text-left"
        >
          <div className="border-b border-slate-800 pb-4">
            <h1 id="getting-started" className="text-3xl font-extrabold text-white flex items-center gap-2.5">
              <FileText className="h-7 w-7 text-blue-500" />
              <span>Platform Documentation</span>
            </h1>
            <p className="text-xs text-slate-400 mt-2 font-semibold">
              Welcome to the official documentation for APCRE (Academic Python Code Review Environment).
            </p>
          </div>

          <p className="text-xs text-slate-300 leading-relaxed font-semibold">
            This guide will walk you through setting up your workspace, leveraging AI reviews, and navigating our interactive codebase.
          </p>

          <hr className="border-slate-800" />

          <div className="space-y-3">
            <h2 id="api-reference" className="text-lg font-bold text-white flex items-center gap-2 font-mono uppercase tracking-wider">
              <Terminal className="h-4 w-4 text-blue-400" />
              <span>1. API Reference</span>
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed font-semibold">
              The APCRE backend handles executions natively safely in isolated containers (or via child processes depending on configuration).
            </p>
            <pre className="bg-[#070a13] border border-slate-850 p-4 rounded-xl text-xs overflow-x-auto text-emerald-400 font-mono">
<code>{`// Example Execution Payload
fetch('/api/run', {
  method: 'POST',
  body: JSON.stringify({ code: "print('Hello World')" })
})`}</code>
            </pre>
          </div>

          <div className="space-y-3">
            <h2 id="ml-models" className="text-lg font-bold text-white flex items-center gap-2 font-mono uppercase tracking-wider">
              <Shield className="h-4 w-4 text-emerald-400" />
              <span>2. Machine Learning Model Integration</span>
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed font-semibold">
              APCRE relies on a pre-trained ML model (<code>ml_model.pkl</code>) combined with LLM checkpoints to categorize coding flaws into distinct categories: <code>Syntax</code>, <code>Logic</code>, <code>Security</code>, and <code>Performance</code>.
            </p>
            <ul className="list-disc pl-5 text-xs text-slate-400 leading-relaxed font-semibold space-y-1">
              <li>Ensure <code>ml_model.pkl</code> is placed in your backend root.</li>
              <li>Python Flask serves endpoints over <code>/api/review</code> allowing for instantaneous static/dynamic checks.</li>
            </ul>
          </div>

          <div className="space-y-3">
            <h2 id="troubleshooting" className="text-lg font-bold text-white flex items-center gap-2 font-mono uppercase tracking-wider">
              <HelpCircle className="h-4 w-4 text-amber-500" />
              <span>3. Troubleshooting</span>
            </h2>
            <p className="text-xs text-slate-400 leading-relaxed font-semibold">
              If you're encountering timeout errors during execution, ensure the system resources limit isn't being reached. Max execution timeout defaults to 10s.
            </p>
          </div>
        </motion.article>

      </main>
      <Footer />
    </div>
  );
}