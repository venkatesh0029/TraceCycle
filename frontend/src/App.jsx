import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Recycle,
  ShieldCheck,
  BarChart3,
  Cpu,
  ArrowRight,
  Menu,
  X,
  Github,
  LayoutDashboard
} from 'lucide-react';
import { ethers } from 'ethers';
import Dashboard from './components/Dashboard';
import Analytics from './components/Analytics';
import { Web3Provider } from './context/Web3Context';

const Navbar = ({ onViewChange, currentView }) => {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <nav className="fixed w-full z-50 glass-panel border-b border-white/5 bg-dark-900/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div
            className="flex items-center gap-2 cursor-pointer"
            onClick={() => onViewChange('landing')}
          >
            <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center">
              <Recycle className="text-white w-5 h-5" />
            </div>
            <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-500 to-indigo-500">
              TraceCycle
            </span>
          </div>

          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <button
                onClick={() => onViewChange('landing')}
                className={`px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentView === 'landing' ? 'text-primary-500' : 'hover:text-primary-500'}`}
              >
                Home
              </button>
              {currentView === 'landing' && (
                <a href="#features" className="hover:text-primary-500 px-3 py-2 rounded-md text-sm font-medium transition-colors">Features</a>
              )}
              <button
                onClick={() => onViewChange('analytics')}
                className={`flex items-center gap-2 px-3 py-2 rounded-md text-sm font-medium transition-colors ${currentView === 'analytics' ? 'text-primary-500' : 'hover:text-primary-500'}`}
              >
                Analytics
              </button>
              <button
                onClick={() => onViewChange('dashboard')}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${currentView === 'dashboard' ? 'bg-primary-600/20 text-primary-400 border border-primary-500/30' : 'bg-primary-600 hover:bg-primary-700 text-white'}`}
              >
                {currentView === 'dashboard' ? (
                  <>
                    <LayoutDashboard className="w-4 h-4" /> Dashboard Active
                  </>
                ) : (
                  <>
                    Launch App
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="-mr-2 flex md:hidden">
            <button onClick={() => setIsOpen(!isOpen)} className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-white/10 focus:outline-none">
              {isOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {isOpen && (
        <div className="md:hidden glass-panel mt-2 mx-2">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <button onClick={() => { onViewChange('landing'); setIsOpen(false); }} className="block w-full text-left px-3 py-2 rounded-md text-base font-medium hover:bg-white/10 hover:text-primary-500">Home</button>
            <button onClick={() => { onViewChange('analytics'); setIsOpen(false); }} className="block w-full text-left px-3 py-2 rounded-md text-base font-medium hover:bg-white/10 hover:text-primary-500">Analytics</button>
            <button onClick={() => { onViewChange('dashboard'); setIsOpen(false); }} className="block w-full text-center mt-4 px-4 py-3 rounded-lg bg-primary-600 hover:bg-primary-700 text-white font-medium">
              Launch App
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

const Hero = ({ onStart }) => {
  return (
    <div id="home" className="relative pt-32 pb-20 sm:pt-40 sm:pb-24 overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-96 h-96 rounded-full bg-primary-500/20 blur-3xl"></div>
        <div className="absolute top-40 -left-20 w-72 h-72 rounded-full bg-indigo-500/20 blur-3xl"></div>
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center z-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <span className="inline-block py-1 px-3 rounded-full bg-primary-500/10 border border-primary-500/20 text-primary-400 text-sm font-medium mb-6">
            Blockchain-Powered Waste Management
          </span>
          <h1 className="text-5xl sm:text-7xl font-extrabold tracking-tight mb-8">
            Constructing a <br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-primary-400 via-indigo-400 to-primary-400 animate-gradient">
              Transparent Future
            </span>
          </h1>
          <p className="mt-4 text-xl text-slate-400 max-w-2xl mx-auto mb-10">
            TraceCycle leverages blockchain technology and AI to ensure complete transparency, security, and efficiency in waste lifecycle management.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onStart}
              className="px-8 py-4 rounded-xl bg-gradient-to-r from-primary-600 to-indigo-600 text-white font-bold text-lg shadow-lg shadow-primary-500/25 flex items-center justify-center gap-2"
            >
              Get Started <ArrowRight className="w-5 h-5" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="px-8 py-4 rounded-xl glass-panel text-white font-bold text-lg hover:bg-white/10 transition-colors"
            >
              Read Docs
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

const FeatureCard = ({ icon: Icon, title, description, delay }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay, duration: 0.5 }}
    className="glass-panel p-8 hover:bg-white/10 transition-colors group"
  >
    <div className="w-12 h-12 rounded-lg bg-primary-500/10 flex items-center justify-center mb-6 group-hover:bg-primary-500/20 transition-colors">
      <Icon className="w-6 h-6 text-primary-400" />
    </div>
    <h3 className="text-xl font-bold mb-4 text-white">{title}</h3>
    <p className="text-slate-400 leading-relaxed">
      {description}
    </p>
  </motion.div>
);

const Features = () => {
  return (
    <div id="features" className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">Why Choose TraceCycle?</h2>
          <p className="text-slate-400 max-w-2xl mx-auto text-lg">
            Our platform combines cutting-edge technologies to revolutionize waste management logistics and accountability.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <FeatureCard
            icon={ShieldCheck}
            title="Immutable Records"
            description="Every transaction is recorded on the blockchain, creating a tamper-proof history of waste movement from generation to disposal."
            delay={0.1}
          />
          <FeatureCard
            icon={Cpu}
            title="AI-Driven Analytics"
            description="Advanced machine learning algorithms optimize collection routes and predict waste generation patterns for smarter logistics."
            delay={0.2}
          />
          <FeatureCard
            icon={BarChart3}
            title="Real-time Tracking"
            description="Monitor waste flow in real-time with comprehensive dashboards and instant alerts for anomalies or delays."
            delay={0.3}
          />
        </div>
      </div>
    </div>
  );
};

const Footer = () => (
  <footer className="border-t border-white/5 bg-dark-800/50 py-12">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row justify-between items-center gap-6">
      <div className="flex items-center gap-2">
        <div className="w-8 h-8 rounded-lg bg-primary-500 flex items-center justify-center">
          <Recycle className="text-white w-5 h-5" />
        </div>
        <span className="text-xl font-bold text-slate-200">TraceCycle</span>
      </div>
      <p className="text-slate-500 text-sm">
        © 2024 TraceCycle. All rights reserved. Built for a sustainable future.
      </p>
      <div className="flex gap-4">
        <a href="#" className="text-slate-400 hover:text-white transition-colors">
          <Github className="w-5 h-5" />
        </a>
      </div>
    </div>
  </footer>
);

function App() {
  const [blockNumber, setBlockNumber] = useState(null);
  const [view, setView] = useState('landing'); // 'landing' or 'dashboard'

  useEffect(() => {
    // Simple improved blockchain check
    const checkConnection = async () => {
      if (window.ethereum) {
        try {
          const provider = new ethers.BrowserProvider(window.ethereum);
          const block = await provider.getBlockNumber();
          setBlockNumber(block);
        } catch (err) {
          console.log("Ethereum connection failed or not authorized yet");
        }
      }
    };
    checkConnection();
  }, []);

  return (
    <Web3Provider>
      <div className="min-h-screen bg-dark-900 text-white selection:bg-primary-500/30">
        <Navbar onViewChange={setView} currentView={view} />

        {view === 'landing' && (
          <>
            <Hero onStart={() => setView('dashboard')} />
            <Features />
            <Footer />
          </>
        )}

        {view === 'dashboard' && <Dashboard />}

        {view === 'analytics' && <Analytics />}

        {/* Status Bar */}
        <div className="fixed bottom-4 right-4 z-50">
          <div className={`px-4 py-2 rounded-full glass-panel text-xs font-mono flex items-center gap-2 border ${blockNumber ? 'border-green-500/30 text-green-400' : 'border-red-500/30 text-red-400'}`}>
            <div className={`w-2 h-2 rounded-full ${blockNumber ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`}></div>
            {blockNumber ? `Block: ${blockNumber}` : 'Disconnected'}
          </div>
        </div>
      </div>
    </Web3Provider>
  );
}

export default App;
