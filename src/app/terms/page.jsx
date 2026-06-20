"use client";
import React from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function TermsOfServicePage() {
  return (
    <div className="font-sans min-h-screen bg-white flex flex-col">
      <Header />
      <main className="flex-grow max-w-4xl mx-auto py-32 px-8 text-gray-800">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-8 tracking-tight">Terms of Service</h1>
        <div className="prose prose-blue max-w-none text-gray-700 space-y-6">
          <p className="text-lg font-medium leading-relaxed">
            Welcome to APCRE. These Terms of Service govern your use of our website, software, and services. By accessing or using APCRE, you agree to be bound by these Terms.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. Acceptance of Terms</h2>
          <p>
            By registering for and/or using the services in any manner, including but not limited to visiting or browsing the Site, you agree to these Terms of Service and all other operating rules, policies, and procedures that may be published from time to time on the Site by us.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. Description of Service</h2>
          <p>
            APCRE provides an intelligent platform for real-time Python development, code review, and learning. Our services are continually evolving, and the form or nature of the services we provide may change from time to time without prior notice to you.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. User Conduct</h2>
          <p>
            You are exclusively responsible for your conduct within our platform. You agree not to use the services for any unlawful purpose or in any way that interrupts, damages, or impairs the services. We reserve the right to suspend or terminate your account if we determine that you have violated these Terms.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. Intellectual Property</h2>
          <p>
            The service and its original content, features, and functionality are and will remain the exclusive property of APCRE and its licensors. You may not reproduce, duplicate, copy, sell, resell or exploit any portion of the service without express written permission by us.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">5. Disclaimer of Warranties</h2>
          <p>
            Your use of the service is at your sole risk. The service is provided on an "AS IS" and "AS AVAILABLE" basis. The service is provided without warranties of any kind, whether express or implied.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}