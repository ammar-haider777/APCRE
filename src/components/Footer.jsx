"use client";
import React from 'react';
import Link from 'next/link';;
import { Facebook, Instagram, Twitter, Linkedin, Youtube, Github } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="w-full bg-[#111827] border-t border-slate-800/80 pt-16 pb-8 px-8 md:px-16 font-sans">
      <div className="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-5 gap-12 mb-16">
        
        {/* Column 1: Logo & Connect */}
        <div className="flex flex-col space-y-12">
          {/* Logo */}
          <div className="text-xl font-black text-white tracking-wider uppercase flex items-center">
            AP<span className="text-blue-500">CRE</span>
          </div>

          {/* Connect Section */}
          <div>
            <h4 className="font-bold text-white mb-6 text-sm">Connect</h4>
            <ul className="space-y-4 text-xs font-semibold text-slate-400">
              <li><a href="#" className="hover:text-blue-400 transition-colors">Follow on Twitter</a></li>
              <li><a href="#" className="hover:text-blue-400 transition-colors">Follow on GitHub</a></li>
              <li><a href="#" className="hover:text-blue-400 transition-colors">Join Discord</a></li>
              <li><a href="#" className="hover:text-blue-400 transition-colors">Email support</a></li>
              <li><a href="#" className="hover:text-blue-400 transition-colors">Report security</a></li>
            </ul>
          </div>
        </div>

        {/* Column 2: Product */}
        <div>
          <h4 className="font-bold text-white text-sm mb-6">Product</h4>
          <ul className="space-y-4 text-xs font-semibold text-slate-400">
            <li><Link href="/editor" className="hover:text-blue-400 transition-colors">Code editor</Link></li>
            <li><Link href="/courses" className="hover:text-blue-400 transition-colors">Courses</Link></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">AI review</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Collaboration</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Dashboard</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Pricing</a></li>
          </ul>
        </div>

        {/* Column 3: Company */}
        <div>
          <h4 className="font-bold text-white text-sm mb-6">Company</h4>
          <ul className="space-y-4 text-xs font-semibold text-slate-400">
            <li><Link href="/about" className="hover:text-blue-400 transition-colors">About us</Link></li>
            <li><Link href="/contact" className="hover:text-blue-400 transition-colors">Contact</Link></li>
            <li><Link href="/blog" className="hover:text-blue-400 transition-colors">Blog</Link></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Careers</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Press</a></li>
          </ul>
        </div>

        {/* Column 4: Resources */}
        <div>
          <h4 className="font-bold text-white text-sm mb-6">Resources</h4>
          <ul className="space-y-4 text-xs font-semibold text-slate-400">
            <li><Link href="/docs" className="hover:text-blue-400 transition-colors">Documentation</Link></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">API docs</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Community</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Support</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Status</a></li>
          </ul>
        </div>

        {/* Column 5: Legal */}
        <div>
          <h4 className="font-bold text-white text-sm mb-6">Legal</h4>
          <ul className="space-y-4 text-xs font-semibold text-slate-400">
            <li><Link href="/privacy" className="hover:text-blue-400 transition-colors">Privacy policy</Link></li>
            <li><Link href="/terms" className="hover:text-blue-400 transition-colors">Terms of service</Link></li>
            <li><Link href="/cookies" className="hover:text-blue-400 transition-colors">Cookie policy</Link></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Accessibility</a></li>
            <li><a href="#" className="hover:text-blue-400 transition-colors">Security</a></li>
          </ul>
        </div>

      </div>

      {/* Dark Bottom Bar */}
      <div className="max-w-[1400px] mx-auto bg-[#0B1220] text-slate-400 py-6 px-8 rounded-2xl flex flex-col md:flex-row items-center justify-between gap-6 text-xs font-semibold border border-slate-800/60">
        
        {/* Copyright */}
        <div>
          © 2026 APCRE. All rights reserved.
        </div>

        {/* Middle Links */}
        <div className="flex items-center space-x-6">
          <a href="#" className="hover:text-white transition-colors">Privacy policy</a>
          <a href="#" className="hover:text-white transition-colors">Terms of service</a>
          <a href="#" className="hover:text-white transition-colors">Cookie settings</a>
        </div>

        {/* Social Icons */}
        <div className="flex items-center space-x-4">
          <a href="#" className="hover:text-white transition-colors"><Facebook className="w-4 h-4" /></a>
          <a href="#" className="hover:text-white transition-colors"><Instagram className="w-4 h-4" /></a>
          <a href="#" className="hover:text-white transition-colors">
            {/* Custom X matching lucide style */}
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M4 4l11.733 16h4.267l-11.733 -16z"/><path d="M4 20l6.768 -6.768m2.46 -2.46l6.772 -6.772"/></svg>
          </a>
          <a href="#" className="hover:text-white transition-colors"><Linkedin className="w-4 h-4" /></a>
          <a href="#" className="hover:text-white transition-colors"><Youtube className="w-4 h-4" /></a>
        </div>
        
      </div>
    </footer>
  );
}