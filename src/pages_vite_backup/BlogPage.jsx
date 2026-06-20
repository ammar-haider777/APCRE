import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { blogsData } from '../data/blogs';
import { motion } from 'framer-motion';
import { FileText, Calendar, User, ArrowRight, Sparkles } from 'lucide-react';

export default function BlogPage() {
  return (
    <div className="min-h-screen bg-[#0B1220] flex flex-col font-sans text-slate-200">
      <Header />
      
      <main className="flex-grow max-w-7xl mx-auto px-8 py-16 w-full relative">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[350px] h-[350px] bg-blue-500/5 rounded-full blur-[110px] pointer-events-none select-none" />

        <div className="text-center mb-16 space-y-4">
          <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-blue-500/5 px-3 py-1 text-[10px] font-bold uppercase font-mono tracking-widest text-blue-400">
            <Sparkles className="h-3 w-3" />
            <span>Developer Insights</span>
          </div>
          <h1 className="text-3xl sm:text-5xl font-black text-white tracking-tight">APCRE Blog</h1>
          <p className="text-sm text-slate-400 max-w-2xl mx-auto font-semibold leading-relaxed">
            Insights, updates, and tutorials from the team behind the ultimate AI-assisted academic code review environment.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 z-10 relative">
          {blogsData.map((blog) => (
            <motion.div 
              key={blog.id} 
              initial={{ opacity: 0, scale: 0.98 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.3 }}
              className="bg-[#111827] rounded-2xl border border-slate-800/80 overflow-hidden flex flex-col hover:border-slate-700 hover:shadow-xl hover:shadow-blue-500/5 transition-all duration-300 group"
            >
              <div className="h-48 overflow-hidden bg-slate-900 border-b border-slate-800/80">
                <img 
                  src={blog.image} 
                  alt={blog.title} 
                  className="w-full h-full object-cover group-hover:scale-102 transition duration-500 opacity-60"
                />
              </div>
              <div className="p-6 flex flex-col flex-grow text-left space-y-3">
                <div className="flex items-center gap-3 text-[10px] font-mono text-slate-500 font-bold uppercase select-none">
                  <span className="flex items-center gap-1"><Calendar className="w-3.5 h-3.5" />{blog.date}</span>
                  <span className="flex items-center gap-1"><User className="w-3.5 h-3.5" />{blog.author}</span>
                </div>
                <h2 className="text-lg font-bold text-white line-clamp-2 leading-tight">
                  <Link to={`/blog/${blog.id}`} className="hover:text-blue-400 transition-colors">
                    {blog.title}
                  </Link>
                </h2>
                <p className="text-xs text-slate-400 flex-grow line-clamp-3 leading-relaxed">
                  {blog.summary}
                </p>
                <Link 
                  to={`/blog/${blog.id}`} 
                  className="inline-flex items-center gap-1.5 mt-4 text-blue-400 font-bold uppercase font-mono text-[10px] tracking-wider hover:text-blue-300 transition-colors"
                >
                  <span>Read full article</span>
                  <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </motion.div>
          ))}
        </div>
      </main>

      <Footer />
    </div>
  );
}