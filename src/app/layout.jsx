"use client";
import React from 'react';
import ErrorBoundary from '@/components/ErrorBoundary';
import '../index.css';

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <title>APCRE 4.0 — Autonomous Software Engineering Ecosystem</title>
        <meta name="description" content="A repository-scale autonomous software engineering ecosystem capable of codebase review, ml static audits, and automated repairs." />
      </head>
      <body className="bg-slate-900 text-slate-100 min-h-screen">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}
