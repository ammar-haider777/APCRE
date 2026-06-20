"use client";
import React from 'react';
import Header from '@/components/Header';
import Footer from '@/components/Footer';

export default function CookiePolicyPage() {
  return (
    <div className="font-sans min-h-screen bg-white flex flex-col">
      <Header />
      <main className="flex-grow max-w-4xl mx-auto py-32 px-8 text-gray-800">
        <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-8 tracking-tight">Cookie Policy</h1>
        <div className="prose prose-blue max-w-none text-gray-700 space-y-6">
          <p className="text-lg font-medium leading-relaxed">
            This Cookie Policy explains what cookies are and how APCRE uses them. You should read this policy to understand what types of cookies we use, the information we collect using cookies, and how that information is used.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">1. What are Cookies?</h2>
          <p>
            Cookies are small text files that are placed on your computer or mobile device when you visit a website. They are widely used in order to make websites work, or work more efficiently, as well as to provide information to the owners of the site.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">2. How we use Cookies</h2>
          <p>
            We use cookies for a variety of reasons detailed below. Unfortunately, in most cases, there are no industry standard options for disabling cookies without completely disabling the functionality and features they add to this site. We recommend that you leave on all cookies if you are not sure whether you need them or not, in case they are used to provide a service that you use.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">3. The Cookies we set</h2>
          <ul className="list-disc pl-6 space-y-2">
            <li><strong>Account related cookies:</strong> If you create an account with us, we will use cookies for the management of the signup process and general administration.</li>
            <li><strong>Login related cookies:</strong> We use cookies when you are logged in so that we can remember this fact to prevent you from having to log in every single time you visit a new page.</li>
            <li><strong>Email newsletters related cookies:</strong> This site offers a newsletter or email subscription service and cookies may be used to remember if you are already registered and whether to show certain notifications unique to subscribed or unsubscribed users.</li>
          </ul>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">4. Third-Party Cookies</h2>
          <p>
            In some special cases, we also use cookies provided by trusted third parties. This site uses analytics solutions to help us understand how you use the site and ways that we can improve your experience. These cookies may track things such as how long you spend on the site and the pages that you visit so we can continue to produce engaging content.
          </p>
          <h2 className="text-2xl font-bold text-gray-900 mt-8 mb-4">5. More Information</h2>
          <p>
            Hopefully, that has clarified things for you. As previously mentioned, if there is something you aren't sure whether you need or not, it's usually safer to leave cookies enabled in case it does interact with one of the features you use on our site.
          </p>
        </div>
      </main>
      <Footer />
    </div>
  );
}