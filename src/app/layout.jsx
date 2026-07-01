"use client";
import React, { useEffect } from 'react';
import ErrorBoundary from '@/components/ErrorBoundary';
import '../index.css';

export default function RootLayout({ children }) {
  useEffect(() => {
    const handleUnhandledRejection = (event) => {
      const reason = event.reason;
      if (!reason) return;

      const isMonacoCancel = 
        reason.type === "cancelation" || 
        reason.type === "cancellation" ||
        reason.message === "Canceled" ||
        reason.message === "Cancelled" ||
        reason.name === "CancelationError" ||
        reason.name === "CancellationError" ||
        reason.isCancellationError === true ||
        (typeof reason === "object" && (
          reason.msg === "operation is manually canceled" ||
          (reason.message && reason.message.includes("Canceled")) ||
          (Object.keys(reason).length === 0 && reason.constructor === Object)
        ));

      if (isMonacoCancel) {
        event.preventDefault();
        event.stopPropagation();
      }
    };

    window.addEventListener("unhandledrejection", handleUnhandledRejection);
    return () => {
      window.removeEventListener("unhandledrejection", handleUnhandledRejection);
    };
  }, []);

  return (
    <html lang="en">
      <head>
        <title>APCRE 4.0 — Autonomous Software Engineering Ecosystem</title>
        <meta name="description" content="A repository-scale autonomous software engineering ecosystem capable of codebase review, ml static audits, and automated repairs." />
        <script dangerouslySetInnerHTML={{ __html: `
          window.addEventListener('unhandledrejection', function(event) {
            var reason = event.reason;
            if (!reason) return;
            var isMonacoCancel = 
              reason.type === "cancelation" || 
              reason.type === "cancellation" ||
              reason.message === "Canceled" ||
              reason.message === "Cancelled" ||
              reason.name === "CancelationError" ||
              reason.name === "CancellationError" ||
              reason.isCancellationError === true ||
              (typeof reason === "object" && (
                reason.msg === "operation is manually canceled" ||
                (reason.message && reason.message.indexOf("Canceled") !== -1) ||
                (Object.keys(reason).length === 0 && reason.constructor === Object)
              ));
            if (isMonacoCancel) {
              event.preventDefault();
              event.stopPropagation();
              event.stopImmediatePropagation();
            }
          });
        ` }} />
      </head>
      <body className="bg-slate-900 text-slate-100 min-h-screen">
        <ErrorBoundary>
          {children}
        </ErrorBoundary>
      </body>
    </html>
  );
}

