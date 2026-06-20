import React from 'react';
import { Link } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-[#EDF3FC] flex flex-col font-sans">
      <Header />
      <main className="flex-grow flex items-center justify-center py-16 px-4">
        <div className="text-center">
          <h1 className="text-8xl font-extrabold text-blue-600 mb-4">404</h1>
          <h2 className="text-3xl font-bold text-gray-900 mb-4">Page not found</h2>
          <p className="text-gray-600 mb-8 max-w-md mx-auto">
            The page you're looking for doesn't exist or has been moved.
          </p>
          <div className="flex justify-center space-x-4">
            <Link to="/">
              <button className="px-6 py-3 text-sm font-semibold text-white bg-blue-600 rounded-lg hover:bg-blue-700 shadow-sm transition-all">
                Go home
              </button>
            </Link>
            <Link to="/editor">
              <button className="px-6 py-3 text-sm font-semibold text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-all bg-white">
                Open editor
              </button>
            </Link>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
