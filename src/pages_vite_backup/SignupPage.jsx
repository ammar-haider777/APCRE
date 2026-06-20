import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { Sparkles, Mail, Key, User, Camera } from 'lucide-react';

export default function SignupPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
  });
  const [avatar, setAvatar] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setAvatar(e.target.files[0]);
    }
  };

  const handleSignup = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const data = new FormData();
      data.append('firstName', formData.firstName);
      data.append('lastName', formData.lastName);
      data.append('email', formData.email);
      data.append('password', formData.password);
      if (avatar) {
        data.append('avatar', avatar);
      }

      const res = await fetch('/api/signup', {
        method: 'POST',
        body: data,
      });
      const result = await res.json();
      
      if (!res.ok) throw new Error(result.error || 'Signup failed');

      localStorage.setItem('user', JSON.stringify(result.user));
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
            <h1 className="text-2xl font-black text-white uppercase tracking-wider font-mono">Create account</h1>
            <p className="text-xs text-slate-400 leading-relaxed font-semibold">Set up your profile to begin auditing</p>
          </div>

          {error && (
            <div className="p-3 border border-rose-500/20 bg-rose-500/10 text-rose-400 text-xs rounded-xl font-mono mb-6">
              {error}
            </div>
          )}

          <form onSubmit={handleSignup} className="space-y-4">
            <div className="space-y-1.5 text-left">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <Camera className="h-3.5 w-3.5" />
                <span>Profile Picture</span>
              </label>
              <input 
                type="file" 
                accept="image/*" 
                onChange={handleFileChange} 
                className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-400 px-3 py-2 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono file:mr-4 file:py-1 file:px-3 file:rounded-xl file:border-0 file:text-[10px] file:font-extrabold file:uppercase file:bg-blue-600 file:text-white hover:file:bg-blue-500 cursor-pointer" 
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-1.5 text-left">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5" />
                  <span>First name</span>
                </label>
                <input 
                  required 
                  type="text" 
                  value={formData.firstName} 
                  onChange={(e) => setFormData({...formData, firstName: e.target.value})} 
                  className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" 
                  placeholder="Ammar"
                />
              </div>
              <div className="space-y-1.5 text-left">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono flex items-center gap-1.5">
                  <User className="h-3.5 w-3.5" />
                  <span>Last name</span>
                </label>
                <input 
                  required 
                  type="text" 
                  value={formData.lastName} 
                  onChange={(e) => setFormData({...formData, lastName: e.target.value})} 
                  className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" 
                  placeholder="Haider"
                />
              </div>
            </div>

            <div className="space-y-1.5 text-left">
              <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono flex items-center gap-1.5">
                <Mail className="h-3.5 w-3.5" />
                <span>Email address</span>
              </label>
              <input 
                required 
                type="email" 
                value={formData.email} 
                onChange={(e) => setFormData({...formData, email: e.target.value})} 
                className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" 
                placeholder="ammar@apcre.dev"
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
                value={formData.password} 
                onChange={(e) => setFormData({...formData, password: e.target.value})} 
                className="w-full bg-[#070a13] border border-slate-800 text-xs text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" 
                placeholder="••••••••"
              />
            </div>

            <button 
              type="submit" 
              disabled={loading} 
              className="w-full rounded-xl bg-blue-600 hover:bg-blue-700 py-3 text-xs font-bold uppercase font-mono tracking-wider text-white shadow-md hover:shadow-lg transition-all duration-300 mt-4 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Sign up'}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-slate-400 font-semibold">
            Already have an account? <Link to="/login" className="text-blue-400 hover:underline">Log in</Link>
          </p>
        </motion.div>
      </main>

      <Footer />
    </div>
  );
}