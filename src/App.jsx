import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import HomePage from './pages/HomePage';
import Editor from './Editor';
import AboutPage from './pages/AboutPage';
import ContactPage from './pages/ContactPage';
import PrivacyPolicyPage from './pages/PrivacyPolicyPage';
import TermsOfServicePage from './pages/TermsOfServicePage';
import CookiePolicyPage from './pages/CookiePolicyPage';
import SignupPage from './pages/SignupPage';
import LoginPage from './pages/LoginPage';
import BlogPage from './pages/BlogPage';
import BlogPostPage from './pages/BlogPostPage';
import DocsPage from './pages/DocsPage';
import NotFoundPage from './pages/NotFoundPage';
import LearningLayout from './learning/LearningLayout';
import ErrorBoundary from './components/ErrorBoundary';
import Header from './components/Header';
import Footer from './components/Footer';
import './App.css';

function App() {
  return (
    <BrowserRouter>
      <ErrorBoundary>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/editor" element={<Editor />} />
          <Route path="/signup" element={<SignupPage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/blog" element={<BlogPage />} />
          <Route path="/blog/:id" element={<BlogPostPage />} />
          <Route path="/docs" element={<DocsPage />} />
          <Route path="/courses" element={
            <div className="min-h-screen bg-slate-50 flex flex-col">
              <Header />
              <main className="flex-grow">
                <LearningLayout />
              </main>
            </div>
          } />
          <Route path="/about" element={<AboutPage />} />
          <Route path="/contact" element={<ContactPage />} />
          <Route path="/privacy" element={<PrivacyPolicyPage />} />
          <Route path="/terms" element={<TermsOfServicePage />} />
          <Route path="/cookies" element={<CookiePolicyPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </ErrorBoundary>
    </BrowserRouter>
  );
}

export default App;