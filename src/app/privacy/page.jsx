"use client";
import React from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function PrivacyPolicyPage() {
  return (
    <div className="font-sans min-h-screen bg-white flex flex-col">
      <Header />
      <main className="flex-grow max-w-4xl mx-auto py-32 px-8 text-gray-800">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-8 tracking-tight">Privacy Policy</h1>
        <div className="prose prose-blue max-w-none text-gray-700 space-y-6">
          <p className="text-lg font-medium leading-relaxed">
            At APCRE, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website or use our services.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. Information We Collect</h2>
          <p>
            We may collect personal information that you voluntarily provide to us when you register on the platform, express an interest in obtaining information about us, or otherwise contact us.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. How We Use Your Information</h2>
          <p>
            Having accurate information about you permits us to provide you with a smooth, efficient, and customized experience. Specifically, we may use information collected about you via the platform to:
          </p>
          <ul className="list-disc pl-6 space-y-2">
            <li>Create and manage your account.</li>
            <li>Compile anonymous statistical data and analysis for use internally or with third parties.</li>
            <li>Deliver targeted advertising, newsletters, and other information regarding promotions.</li>
            <li>Increase the efficiency and operation of the platform.</li>
          </ul>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. Disclosure of Your Information</h2>
          <p>
            We may share information we have collected about you in certain situations. Your information may be disclosed as follows: By Law or to Protect Rights, Business Transfers, or with your consent.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. Contact Us</h2>
          <p>
            If you have questions or comments about this Privacy Policy, please contact us at: mudassardurvaish@gmail.com.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}