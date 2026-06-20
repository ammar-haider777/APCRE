import React, { useState } from 'react';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { Mail, Phone, MapPin, Sparkles, Send } from 'lucide-react';

export default function ContactPage() {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    topic: '',
    helpType: 'General inquiry',
    message: '',
    agreePolicy: false
  });

  const [formStatus, setFormStatus] = useState('');
  
  const [subscribeEmail, setSubscribeEmail] = useState('');
  const [subscribeStatus, setSubscribeStatus] = useState('');

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleFormSubmit = async (e) => {
    e.preventDefault();
    setFormStatus('Sending...');
    try {
      const response = await fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (response.ok) {
        setFormStatus('Success! We will get back to you shortly.');
        setFormData({
          firstName: '', lastName: '', email: '', phone: '',
          topic: '', helpType: 'General inquiry', message: '', agreePolicy: false
        });
      } else {
        setFormStatus(data.error || 'An error occurred.');
      }
    } catch (error) {
      setFormStatus('Network error.');
    }
  };

  const handleSubscribe = async (e) => {
    e.preventDefault();
    if (!subscribeEmail) return;
    setSubscribeStatus('Subscribing...');
    try {
      const response = await fetch('/api/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: subscribeEmail })
      });
      if (response.ok) {
        setSubscribeStatus('Subscribed successfully!');
        setSubscribeEmail('');
      } else {
        setSubscribeStatus('Failed to subscribe.');
      }
    } catch (err) {
      setSubscribeStatus('Network error.');
    }
  };

  return (
    <div className="font-sans min-h-screen bg-[#0B1220] text-slate-200 overflow-x-hidden selection:bg-blue-500/30">
      <Header />

      {/* Hero Section */}
      <section className="relative pt-24 pb-20 text-center max-w-4xl mx-auto space-y-6 px-8">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] bg-blue-500/5 rounded-full blur-[100px] pointer-events-none select-none" />

        <div className="inline-flex items-center gap-1.5 rounded-full border border-blue-500/20 bg-blue-500/5 px-3 py-1 text-[10px] font-bold uppercase font-mono tracking-widest text-blue-400">
          <Sparkles className="h-3 w-3" />
          <span>Connect with Us</span>
        </div>

        <h1 className="text-4xl md:text-6xl font-black text-white tracking-tight">
          Get in <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">Touch</span>
        </h1>
        
        <p className="text-sm text-slate-400 max-w-md mx-auto leading-relaxed font-semibold">
          Have questions or feedback? Send us a message and our development team will respond quickly.
        </p>
      </section>

      {/* Message / Form Section */}
      <section className="py-16 px-8 max-w-6xl mx-auto border-t border-slate-800/80">
        <div className="flex flex-col lg:flex-row gap-16">
          <div className="lg:w-1/3 text-left space-y-6">
            <div className="space-y-2">
              <div className="text-[10px] font-bold text-blue-400 uppercase tracking-widest font-mono">Contact Details</div>
              <h2 className="text-2xl font-black text-white leading-tight">Send Us Your Thoughts</h2>
            </div>
            
            <p className="text-xs text-slate-400 leading-relaxed font-semibold">
              Reach out via forms or use direct channels below:
            </p>
            
            <div className="space-y-4 text-xs font-semibold text-slate-300 font-mono">
              <div className="flex items-center">
                <Mail className="w-4 h-4 mr-3 text-slate-500" />
                <a href="mailto:apcreteam@gmail.com" className="underline hover:text-blue-400 transition underline-offset-4">apcreteam@gmail.com</a>
              </div>
              <div className="flex items-center">
                <Phone className="w-4 h-4 mr-3 text-slate-500" />
                <a href="tel:+923475702720" className="underline hover:text-blue-400 transition underline-offset-4">+92 347 570 2720</a>
              </div>
              <div className="flex items-center">
                <MapPin className="w-4 h-4 mr-3 text-slate-500" />
                <span>UET Taxila, Rawalpindi Pakistan</span>
              </div>
            </div>
          </div>

          <div className="lg:w-2/3 max-w-2xl w-full">
            <form onSubmit={handleFormSubmit} className="space-y-5 text-left text-xs font-semibold text-slate-400">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">First name</label>
                  <input type="text" name="firstName" value={formData.firstName} onChange={handleInputChange} className="w-full bg-[#111827] border border-slate-800 text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" required />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">Last name</label>
                  <input type="text" name="lastName" value={formData.lastName} onChange={handleInputChange} className="w-full bg-[#111827] border border-slate-800 text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" />
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">Email</label>
                  <input type="email" name="email" value={formData.email} onChange={handleInputChange} className="w-full bg-[#111827] border border-slate-800 text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" required />
                </div>
                <div className="space-y-1.5">
                  <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">Phone number</label>
                  <input type="tel" name="phone" value={formData.phone} onChange={handleInputChange} className="w-full bg-[#111827] border border-slate-800 text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono" />
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">What's this about?</label>
                <select name="topic" value={formData.topic} onChange={handleInputChange} className="w-full bg-[#111827] border border-slate-800 text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono">
                  <option value="">Select one...</option>
                  <option value="sales">Sales</option>
                  <option value="support">Support</option>
                  <option value="press">Press</option>
                </select>
              </div>

              <div className="space-y-2">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">How can we help you?</label>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {[
                    "General inquiry", "Technical support", 
                    "Feature request", "Bug report", 
                    "Partnership", "Other"
                  ].map((type) => (
                    <label key={type} className="flex items-center space-x-3 cursor-pointer text-slate-300">
                      <input 
                        type="radio" 
                        name="helpType" 
                        value={type} 
                        checked={formData.helpType === type}
                        onChange={handleInputChange} 
                        className="w-4 h-4 text-blue-600 border-slate-800 bg-[#111827] focus:ring-blue-500"
                      />
                      <span>{type}</span>
                    </label>
                  ))}
                </div>
              </div>

              <div className="space-y-1.5">
                <label className="text-[10px] font-bold text-slate-500 uppercase tracking-wider font-mono">Message</label>
                <textarea name="message" value={formData.message} onChange={handleInputChange} rows="4" placeholder="Tell us more..." className="w-full bg-[#111827] border border-slate-800 text-slate-200 px-3.5 py-2.5 outline-none rounded-xl focus:border-blue-500/50 transition-all font-mono resize-none" required></textarea>
              </div>

              <div className="flex items-center mt-2">
                <input type="checkbox" name="agreePolicy" checked={formData.agreePolicy} onChange={handleInputChange} id="agreePolicy" className="w-4 h-4 text-blue-600 bg-[#111827] border-slate-850 rounded focus:ring-blue-500" required />
                <label htmlFor="agreePolicy" className="ml-3 text-xs text-slate-400">I agree to the privacy policy</label>
              </div>

              <div className="pt-2">
                <button type="submit" className="flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-700 px-6 py-2.5 text-xs font-bold uppercase font-mono tracking-wider text-white shadow-md hover:shadow-lg transition-all duration-300">
                  <Send className="h-3.5 w-3.5" />
                  <span>Send Message</span>
                </button>
                {formStatus && <p className="mt-3 text-xs font-semibold text-blue-400 font-mono">{formStatus}</p>}
              </div>
            </form>
          </div>
        </div>
      </section>

      {/* Subscribe Section */}
      <section className="max-w-6xl mx-auto px-8 mb-24">
        <div className="relative rounded-3xl overflow-hidden bg-slate-950 py-24 px-8 text-center border border-slate-850">
           <div className="relative z-10 space-y-6">
              <h2 className="text-3xl font-extrabold text-white">Stay Updated on APCRE</h2>
              <p className="text-slate-400 max-w-sm mx-auto text-xs font-semibold leading-relaxed">Get active notifications about code review features, model releases, and retrains.</p>
              
              <form onSubmit={handleSubscribe} className="flex flex-col sm:flex-row justify-center items-center gap-3 max-w-md mx-auto mb-4">
                <input 
                  type="email" 
                  placeholder="e.g. ammar@apcre.dev" 
                  value={subscribeEmail}
                  onChange={(e) => setSubscribeEmail(e.target.value)}
                  className="w-full sm:w-auto flex-1 bg-[#111827] border border-slate-800 text-slate-200 text-xs px-4 py-2.5 rounded-xl outline-none focus:border-blue-500/50 transition-all font-mono"
                  required
                />
                <button type="submit" className="w-full sm:w-auto px-5 py-2.5 text-xs font-extrabold uppercase font-mono tracking-wider text-white bg-blue-600 hover:bg-blue-500 rounded-xl transition whitespace-nowrap shadow-md">
                  Subscribe
                </button>
              </form>
              {subscribeStatus && <p className="text-blue-400 text-xs font-semibold font-mono">{subscribeStatus}</p>}
           </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}