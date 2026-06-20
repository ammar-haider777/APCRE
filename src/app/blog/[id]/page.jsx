"use client";
import React from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';;
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { blogsData } from '@/data/blogs';
import { ArrowLeft, User, Calendar, Sparkles } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { motion } from 'framer-motion';

export default function BlogPostPage() {
  const { id } = useParams();
  const blog = blogsData.find((b) => b.id === parseInt(id, 10));

  if (!blog) {
    return (
      <div className="min-h-screen bg-[#0B1220] flex flex-col font-sans text-slate-200">
        <Header />
        <main className="flex-grow flex items-center justify-center">
          <div className="text-center space-y-4">
            <h1 className="text-2xl font-bold text-white font-mono">Blog post not found</h1>
            <Link href="/blog" className="text-blue-400 hover:underline inline-flex items-center text-xs font-bold uppercase font-mono tracking-wider">
              <ArrowLeft className="w-4 h-4 mr-2" /> Back to Blog
            </Link>
          </div>
        </main>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#0B1220] flex flex-col font-sans text-slate-200 overflow-x-hidden selection:bg-blue-500/30">
      <Header />
      
      <main className="flex-grow">
        {/* Hero Image Section */}
        <div className="w-full h-[40vh] md:h-[50vh] relative border-b border-slate-800/80">
          <div className="absolute inset-0 bg-black/60 z-10" />
          <img src={blog.image} alt={blog.title} className="w-full h-full object-cover opacity-60" />
          <div className="absolute inset-0 z-20 flex items-center justify-center">
            <div className="max-w-4xl w-full px-8 text-center text-white space-y-4">
              <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-blue-500/5 px-3 py-1 text-[10px] font-bold uppercase font-mono tracking-widest text-blue-400">
                <Sparkles className="h-3 w-3" />
                <span>Reading Article</span>
              </div>
              <h1 className="text-3xl md:text-5xl font-black mb-6 leading-tight">
                {blog.title}
              </h1>
              <div className="flex items-center justify-center space-x-6 text-xs font-bold font-mono uppercase tracking-wider text-slate-400">
                <div className="flex items-center gap-1.5">
                  <User className="w-4 h-4 text-blue-400" /> {blog.author}
                </div>
                <div className="flex items-center gap-1.5">
                  <Calendar className="w-4 h-4 text-emerald-400" /> {blog.date}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Content Section */}
        <div className="max-w-3xl mx-auto px-8 py-16 text-left">
          <Link href="/blog" className="inline-flex items-center text-blue-400 font-bold uppercase font-mono tracking-wider text-[10px] hover:text-blue-300 mb-10 transition">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to all articles
          </Link>
          
          <motion.article 
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            className="prose prose-lg prose-invert max-w-none text-slate-300 leading-relaxed text-sm font-semibold space-y-6"
          >
            <ReactMarkdown>{blog.content}</ReactMarkdown>
          </motion.article>
        </div>
      </main>

      <Footer />
    </div>
  );
}