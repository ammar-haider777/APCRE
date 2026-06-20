"use client";
import React, { useState, useEffect } from "react";
import Link from 'next/link';
import { useRouter } from 'next/navigation';;
import { ChevronDown } from "lucide-react";

export default function Header() {
  const [user, setUser] = useState(null);
  const navigate = useRouter();

  useEffect(() => {
    const loadUser = () => {
      const stored = localStorage.getItem("user");
      if (stored) {
        setUser(JSON.parse(stored));
      } else {
        setUser(null);
      }
    };
    loadUser();
    window.addEventListener('user-login', loadUser);
    return () => window.removeEventListener('user-login', loadUser);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("user");
    setUser(null);
    navigate("/");
  };

  return (
    <nav className="flex items-center justify-between px-8 py-3 bg-[#111827] border-b border-slate-800/80 font-sans w-full select-none shrink-0 h-[56px] z-40">
      <div className="flex items-center space-x-12">
        {/* Logo (clickable to go home) */}
        <Link href="/" className="text-lg font-black text-white tracking-wider uppercase flex items-center hover:opacity-90 transition-opacity">
          AP<span className="text-blue-500">CRE</span>
        </Link>

        {/* Links */}
        <div className="hidden md:flex space-x-6 text-xs font-semibold text-slate-400">
          <Link href="/editor" className="hover:text-white transition-colors">Code Editor</Link>
          <Link href="/courses" className="hover:text-white transition-colors">Courses</Link>
          <Link href="/blog" className="hover:text-white transition-colors">Blog</Link>
          <Link href="/docs" className="hover:text-white transition-colors">Docs</Link>
          <Link href="/contact" className="hover:text-white transition-colors">Contact</Link>
          <Link href="/about" className="hover:text-white transition-colors">About</Link>
          <Link href="/privacy" className="hover:text-white transition-colors">Privacy</Link>
        </div>
      </div>
      
      {/* Buttons / User */}
      <div className="flex items-center space-x-4">
        {user ? (
          <div className="flex items-center space-x-4">
            <Link href="/editor">
              <button className="px-4 py-1.5 text-xs font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 shadow-md hover:shadow-lg transition-all duration-300 flex items-center space-x-2">
                <span>Start Editor</span>
              </button>
            </Link>
            <div className="flex items-center space-x-2 cursor-pointer group" onClick={handleLogout} title="Click to logout">
              <img src={user.avatar} alt="Avatar" className="w-8 h-8 rounded-full border-2 border-slate-700 shadow-sm object-cover group-hover:opacity-80 transition-opacity" />
            </div>
          </div>
        ) : (
          <>
            <Link href="/login">
              <button className="px-4 py-1.5 text-xs font-bold text-slate-300 border border-slate-800 rounded-xl hover:bg-slate-800 hover:text-white transition-all bg-transparent">
                Sign in
              </button>
            </Link>
            <Link href="/signup">
              <button className="px-4 py-1.5 text-xs font-bold text-white bg-blue-600 rounded-xl hover:bg-blue-700 shadow-md hover:shadow-lg transition-all duration-300">
                Sign up
              </button>
            </Link>
          </>
        )}
      </div>
    </nav>
  );
}