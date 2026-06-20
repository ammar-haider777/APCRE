"use client";
import React from "react";
import Link from 'next/link';;
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { motion } from "framer-motion";
import { ChevronRight, Github, Linkedin, Globe, Sparkles, Bot, Shield, Trophy } from "lucide-react";
import mudassarImg from '@/assets/Mudassar.png';
import ammarImg from '@/assets/Ammar.png';
import muneerImg from '@/assets/Muneer.png';
import mariyamImg from '@/assets/mariyam.png';

export default function AboutPage() {
  return (
    <div className="font-sans min-h-screen bg-[#0B1220] text-slate-200 overflow-x-hidden selection:bg-blue-500/30">
      <Header />

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 px-8 text-center max-w-4xl mx-auto space-y-6">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-blue-500/5 rounded-full blur-[100px] pointer-events-none select-none" />
        
        <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-blue-500/5 px-3 py-1 text-[10px] font-bold uppercase font-mono tracking-widest text-blue-400">
          <Sparkles className="h-3 w-3" />
          <span>About Ecosystem</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-black text-white tracking-tight">
          Code Review <br/>
          <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Reimagined</span>
        </h1>
        
        <p className="text-sm text-slate-400 max-w-xl mx-auto leading-relaxed font-semibold">
          APCRE brings artificial intelligence to Python development, catching complex bugs and anti-patterns before they matter.
        </p>

        <div className="flex justify-center gap-4 pt-2">
          <Link href="/editor">
            <button className="px-5 py-2.5 text-xs font-extrabold uppercase font-mono tracking-wider text-white bg-blue-600 hover:bg-blue-500 shadow-md hover:shadow-blue-500/25 rounded-xl transition-all duration-300">
              Start Reviewing
            </button>
          </Link>
          <Link href="/contact">
            <button className="px-5 py-2.5 text-xs font-extrabold uppercase font-mono tracking-wider text-slate-300 border border-slate-800 rounded-xl hover:bg-slate-800 transition duration-300">
              Contact Team
            </button>
          </Link>
        </div>
      </section>

      {/* Why APCRE exists */}
      <section className="bg-[#111827]/40 py-24 px-8 border-t border-slate-800/80">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <p className="text-xs font-bold uppercase tracking-widest text-blue-400 font-mono">Purpose</p>
          <h2 className="text-3xl md:text-4xl font-extrabold text-white tracking-tight">Why APCRE Exists</h2>
          <p className="text-xs sm:text-sm text-slate-400 max-w-2xl mx-auto leading-relaxed font-semibold">
            Python developers face a simple problem. Code reviews take time, mistakes slip through, and learning best practices happens too late. APCRE solves this by embedding artificial intelligence directly into the editor, catching issues in real time and teaching better patterns as you write.
          </p>
          
          <div className="flex justify-center items-center gap-6 pt-4">
            <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="text-xs font-bold font-mono uppercase tracking-wider text-slate-300 hover:text-blue-400 transition-colors flex items-center gap-1.5">
              <span>Explore GitHub Repository</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </a>
          </div>

          <div className="rounded-3xl overflow-hidden shadow-2xl relative max-w-4xl mx-auto border border-slate-800 bg-[#0B1220] p-1.5 mt-12">
            <img 
              src="https://images.unsplash.com/photo-1542831371-29b0f74f9713?auto=format&fit=crop&w=1200&q=80" 
              alt="Editor Interface" 
              className="w-full h-auto object-cover opacity-60 rounded-2xl" 
            />
          </div>
        </div>
      </section>

      {/* Team Section */}
      <section className="py-24 px-8 border-t border-slate-800/80 max-w-6xl mx-auto">
        <div className="space-y-12">
          {/* Header section stacked on top */}
          <div className="text-center max-w-2xl mx-auto space-y-4">
            <p className="text-xs font-bold uppercase tracking-widest text-blue-400 font-mono">Team</p>
            <h2 className="text-3xl md:text-4xl font-extrabold text-white leading-tight">Meet the Builders</h2>
            <p className="text-xs sm:text-sm text-slate-400 font-semibold leading-relaxed">
              Three developers working to make code review intelligent, collaborative, and accessible.
            </p>
          </div>

          {/* 3-column Grid for Horizontal layout */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            
            {/* Person 1 (Mudassir) */}
            <div className="rounded-3xl border border-slate-800 bg-[#111827]/40 p-6 flex flex-col items-center text-center space-y-4 shadow-xl backdrop-blur-md hover:border-slate-750 bg-slate-900/30 transition-all duration-300">
              <div className="w-28 h-28 rounded-full overflow-hidden bg-[#E2B671] border-2 border-slate-800 shrink-0 shadow-md">
                <img src={mudassarImg.src} alt="Muhammad Mudassar" className="w-full h-full object-cover object-top" />
              </div>
              <div className="space-y-2 flex-grow">
                <h3 className="text-lg font-bold text-white">Muhammad Mudassar</h3>
                <p className="text-[10px] text-blue-400 font-semibold font-mono uppercase tracking-wider h-8 flex items-center justify-center">Frontend Architect & UI/UX Designer</p>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Designed and implemented the core visual system, and optimized standard layouts for consistent SaaS user experience.
                </p>
              </div>
              <div className="flex justify-center space-x-3 text-slate-400 pt-3 border-t border-slate-800/60 w-full">
                <a href="https://www.linkedin.com/in/muhammad-mudassar3/" className="hover:text-blue-400 transition"><Linkedin className="w-4 h-4" /></a>
                <a href="https://github.com/mudassar-durvaish" className="hover:text-blue-400 transition"><Github className="w-4 h-4" /></a>
                <a href="https://mudassardurvaish.me/" className="hover:text-blue-400 transition"><Globe className="w-4 h-4" /></a>
              </div>
            </div>

            {/* Person 2 (Ammar) */}
            <div className="rounded-3xl border border-slate-800 bg-[#111827]/40 p-6 flex flex-col items-center text-center space-y-4 shadow-xl backdrop-blur-md hover:border-slate-750 bg-slate-900/30 transition-all duration-300">
              <div className="w-28 h-28 rounded-full overflow-hidden bg-slate-800 border-2 border-slate-800 shrink-0 shadow-md">
                <img src={ammarImg.src} alt="Ammar Haider" className="w-full h-full object-cover object-top" />
              </div>
              <div className="space-y-2 flex-grow">
                <h3 className="text-lg font-bold text-white">Ammar Haider</h3>
                <p className="text-[10px] text-blue-400 font-semibold font-mono uppercase tracking-wider h-8 flex items-center justify-center">Backend Lead & Systems Engineer</p>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Engineered core backend routing protocols, WebRTC call coordination, and socket multiplayer layers.
                </p>
              </div>
              <div className="flex justify-center space-x-3 text-slate-400 pt-3 border-t border-slate-800/60 w-full">
                <a href="https://www.linkedin.com/in/ammar-haider777/" className="hover:text-blue-400 transition"><Linkedin className="w-4 h-4" /></a>
                <a href="https://github.com/Mrhacker011" className="hover:text-blue-400 transition"><Github className="w-4 h-4" /></a>
                <a href="#" className="hover:text-blue-400 transition"><Globe className="w-4 h-4" /></a>
              </div>
            </div>

            {/* Person 3 (Muneer) */}
            <div className="rounded-3xl border border-slate-800 bg-[#111827]/40 p-6 flex flex-col items-center text-center space-y-4 shadow-xl backdrop-blur-md hover:border-slate-750 bg-slate-900/30 transition-all duration-300">
              <div className="w-28 h-28 rounded-full overflow-hidden bg-slate-800 border-2 border-slate-800 shrink-0 shadow-md">
                <img src={muneerImg.src} alt="Muneer Hussain" className="w-full h-full object-cover object-top" />
              </div>
              <div className="space-y-2 flex-grow">
                <h3 className="text-lg font-bold text-white">Muneer Hussain</h3>
                <p className="text-[10px] text-blue-400 font-semibold font-mono uppercase tracking-wider h-8 flex items-center justify-center">ML Engineer & Model Assessor</p>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Trained deep code representation embeddings, and implemented empirical cross-validations and Wilcoxon sign checks.
                </p>
              </div>
              <div className="flex justify-center space-x-3 text-slate-400 pt-3 border-t border-slate-800/60 w-full">
                <a href="https://www.linkedin.com/in/muneer-hussain/overlay/contact-info/" className="hover:text-blue-400 transition"><Linkedin className="w-4 h-4" /></a>
                <a href="http://github.com/MuneerHussain01" className="hover:text-blue-400 transition"><Github className="w-4 h-4" /></a>
                <a href="https://67fbe3ed6f60535a0ddd0a74--delightful-kheer-89cf8e.netlify.app/" className="hover:text-blue-400 transition"><Globe className="w-4 h-4" /></a>
              </div>
            </div>

          </div>
        </div>
      </section>

      {/* Supervisor section */}
      <section className="bg-[#111827]/40 py-24 px-8 border-t border-slate-800/80 max-w-6xl mx-auto rounded-3xl mb-16">
        <div className="max-w-4xl mx-auto text-left space-y-12">
          <div className="space-y-4">
            <div className="text-[10px] font-bold text-blue-400 uppercase tracking-widest font-mono">Academic Advising</div>
            <h3 className="text-2xl md:text-4xl font-extrabold text-white leading-tight max-w-2xl">
              Project Supervised by Dr. Maryam Nawaz
            </h3>
            <p className="text-xs sm:text-sm text-slate-400 leading-relaxed font-semibold max-w-xl">
              Guidance on ML evaluations, AST parsers, and thesis methodology was provided by faculty advisor Dr. Maryam Nawaz.
            </p>
          </div>
          
          <div className="flex flex-col sm:flex-row items-center gap-6 text-center sm:text-left">
            <div className="w-24 h-24 rounded-full overflow-hidden bg-slate-800 border border-slate-850 shrink-0 shadow-lg">
              <img src={mariyamImg.src} alt="Dr. Maryam Nawaz" className="w-full h-full object-cover object-top" />
            </div>
            <div className="space-y-1.5">
              <h4 className="text-lg font-bold text-white">Dr. Maryam Nawaz</h4>
              <p className="text-xs text-slate-500 font-semibold font-mono uppercase">Project Supervisor • Faculty Advisor</p>
              <div className="flex justify-center sm:justify-start space-x-3 text-slate-400 pt-1">
                <a href="https://scholar.google.com/citations?user=Cor7r8AAAAAJ&hl=en" className="hover:text-blue-400 transition"><Globe className="w-4 h-4" /></a>
                <a href="https://www.linkedin.com/in/marriam-nawaz-ab9644a4/" className="hover:text-blue-400 transition"><Linkedin className="w-4 h-4" /></a>
              </div>
            </div>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}