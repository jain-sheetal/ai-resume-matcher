import React from 'react';
import { Target, Cpu, BookOpen } from 'lucide-react';

export default function Navbar({ onOpenDocs }) {
  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center text-white shadow-md shadow-blue-500/20">
            <Target className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-xl tracking-tight text-slate-900">
                MatchPro <span className="text-blue-600">AI</span>
              </span>
              <span className="text-xs px-2 py-0.5 font-semibold bg-blue-50 text-blue-700 border border-blue-200 rounded-full">
                v1.0
              </span>
            </div>
            <p className="text-xs text-slate-500 hidden sm:block">
              AI-Powered Resume Matching & Candidate Ranking Engine
            </p>
          </div>
        </div>

        {/* Center / Right controls */}
        <div className="flex items-center space-x-3">
          <div className="hidden md:flex items-center space-x-1.5 px-3 py-1 bg-slate-100 rounded-full text-xs font-medium text-slate-700 border border-slate-200">
            <Cpu className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
            <span>Embedding: <strong className="text-slate-900">all-MiniLM-L6-v2</strong></span>
          </div>

          <button
            onClick={onOpenDocs}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-blue-700 hover:text-blue-900 bg-blue-50 hover:bg-blue-100 border border-blue-200 transition-colors"
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Algorithm Docs</span>
          </button>
        </div>
      </div>
    </header>
  );
}
