"use client";
import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';;
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { motion } from 'framer-motion';
import { LogIn, Key, Mail, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useRouter();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });
      const result = await res.json();
      
      if (!res.ok) throw new Error(result.error || 'Login failed');

      localStorage.setItem('user', JSON.stringify(result.user));
      window.dispatchEvent(new Event('user-login'));
      navigate('/editor');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B1220] flex flex-col font-sans text-slate-200">
      <Header />
      
      <main className="flex-grow flex items-center justify-center py-16 px-4 relative">
        {/* Decorative background glows */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-blue-500/10 rounded-full blur-[100px] pointer-events-none select-none" />

        <motion.div 
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.35 }}
          className="max-w-md w-full bg-[#111827] rounded-2xl shadow-2xl p-8 border border-slate-800/80 z-10"
        >
          <div className="text-center mb-8 space-y-2">
            <div className="mx-auto w-10 h-10 rounded-xl bg-blue-500/10 border border-blue-500/20 text-blue-400 flex items-center justify-center">
              <Sparkles className="h-5 w-5" />
            </div>
            <h1 className="text-2xl font-black text-white uppercase tracking-wider font-mono">Sign in to APCRE</h1>
            <p className="text-xs text-slate-400 leading-relaxed font-semibold">Enter your credentials to access the code editor.</p>
          </div>

          {error && (
            <div className="p-3 border border-rose-500/20 bg-rose-500/10 text-rose-400 text-xs rounded-xl font-mono mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleLogin} className="space-y-5">
            <div className="space-y-1.5 text-left">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <Mail className="h-3.5 w-3.5" />
                <span>Email address</span>
              </label>
              <input 
                required 
                type="email" 
                value={email} 
                onChange={(e) => setEmail(e.target.value)} 
                className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" 
                placeholder="e.g. ammar@apcre.dev"
              />
            </div>

            <div className="space-y-1.5 text-left">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <Key className="h-3.5 w-3.5" />
                <span>Password</span>
              </label>
              <input 
                required 
                type="password" 
                value={password} 
                onChange={(e) => setPassword(e.target.value)} 
                className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" 
                placeholder="••••••••"
              />
            </div>

            <button 
              type="submit" 
              disabled={loading} 
              className="w-full rounded-xl bg-blue-600 hover:bg-blue-700 py-3 text-xs font-bold uppercase font-mono tracking-wider text-white shadow-md hover:shadow-lg transition-all duration-300 mt-4 disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Login'}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-slate-400 font-semibold">
            New here? <Link href="/signup" className="text-blue-400 hover:underline">Create an account</Link>
          </p>
        </motion.div>
      </main>

      <Footer />
    </div>
  );
}