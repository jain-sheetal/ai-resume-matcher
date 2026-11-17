import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResumeUploader from './components/ResumeUploader';
import CandidateRankingTable from './components/CandidateRankingTable';
import CandidateDetailDrawer from './components/CandidateDetailDrawer';
import DocsModal from './components/DocsModal';
import { api } from './services/api';
import { Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export default function App() {
  const [sampleJds, setSampleJds] = useState([]);
  const [parsedJd, setParsedJd] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [matchData, setMatchData] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const [isJdLoading, setIsJdLoading] = useState(false);
  const [isResumeLoading, setIsResumeLoading] = useState(false);
  const [isMatchingLoading, setIsMatchingLoading] = useState(false);
  const [isDocsOpen, setIsDocsOpen] = useState(false);
  const [matchError, setMatchError] = useState(null);

  // Load sample JDs and optionally load sample resumes initially
  useEffect(() => {
    async function loadInitialData() {
      try {
        const jds = await api.getSampleJds();
        setSampleJds(jds);
        if (jds && jds.length > 0) {
          // Pre-populate with first sample JD for immediate interactive testing
          const first = jds[0];
          const parsed = await api.parseJd({ text: first.description, title: first.title });
          setParsedJd(parsed);
        }
      } catch (err) {
        console.error("Failed to load initial sample JDs", err);
      }
    }
    loadInitialData();
  }, []);

  const handleTriggerMatch = async () => {
    if (!parsedJd || resumes.length === 0) return;

    setMatchError(null);
    setIsMatchingLoading(true);
    try {
      const response = await api.evaluateCandidates({
        job_description: parsedJd,
        resumes: resumes
      });
      setMatchData(response);

      // Smooth scroll down to results table
      setTimeout(() => {
        window.scrollTo({
          top: document.body.scrollHeight / 2,
          behavior: 'smooth'
        });
      }, 100);
    } catch (err) {
      setMatchError(err.message || 'Failed to match and rank candidates');
    } finally {
      setIsMatchingLoading(false);
    }
  };

  const handleExportCsv = async () => {
    if (!parsedJd || resumes.length === 0) return;
    try {
      await api.exportCsv({
        job_description: parsedJd,
        resumes: resumes
      });
    } catch (err) {
      alert("Failed to export CSV: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar
        onOpenDocs={() => setIsDocsOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto pt-2 pb-1">
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-semibold mb-3">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI / Full Stack Intern Assignment Submission</span>
          </div>
          <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
            AI-Based Resume Matching & Candidate Ranking
          </h1>
          <p className="mt-3 text-sm sm:text-base text-slate-600 leading-relaxed">
            Upload Job Descriptions and batch candidate resumes (PDF & DOCX) to generate intelligent semantic rankings, skill gap analyses, and Explainable AI candidate profiles.
          </p>
        </div>

        {/* Error notification banner */}
        {matchError && (
          <div className="p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3 text-red-800 text-xs">
            <AlertCircle className="w-4 h-4 text-red-600 shrink-0 mt-0.5" />
            <div>
              <strong className="font-bold">Evaluation Notice:</strong> {matchError}
            </div>
          </div>
        )}

        {/* Top Grid: Module 1 (JD) & Module 2 (Resumes) */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          <div className="lg:col-span-6">
            <JobDescriptionInput
              sampleJds={sampleJds}
              parsedJd={parsedJd}
              setParsedJd={setParsedJd}
              isLoading={isJdLoading}
              setIsLoading={setIsJdLoading}
            />
          </div>

          <div className="lg:col-span-6">
            <ResumeUploader
              resumes={resumes}
              setResumes={setResumes}
              isLoading={isResumeLoading}
              setIsLoading={setIsResumeLoading}
              onTriggerMatch={handleTriggerMatch}
              canMatch={Boolean(parsedJd && resumes.length > 0)}
              isMatching={isMatchingLoading}
            />
          </div>
        </div>

        {/* Module 3 trigger: Big Action Match Bar */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className={`w-3 h-3 rounded-full ${parsedJd && resumes.length > 0 ? 'bg-emerald-500 animate-pulse' : 'bg-slate-300'}`} />
            <div>
              <p className="text-xs font-bold text-slate-800">
                {parsedJd && resumes.length > 0
                  ? `Ready to evaluate ${resumes.length} candidates against ${parsedJd.title || 'Job Description'}`
                  : 'Please complete Job Description and upload at least 1 resume to run matching'
                }
              </p>
              <p className="text-[11px] text-slate-500">
                Executes Sentence-BERT embeddings, canonical skill taxonomy, and tenure alignment.
              </p>
            </div>
          </div>

          <button
            onClick={handleTriggerMatch}
            disabled={!parsedJd || resumes.length === 0 || isMatchingLoading}
            className={`w-full sm:w-auto px-6 py-3 rounded-xl font-bold text-xs uppercase tracking-wider flex items-center justify-center space-x-2 shadow-md transition-all ${
              !parsedJd || resumes.length === 0 || isMatchingLoading
                ? 'bg-slate-200 text-slate-400 cursor-not-allowed shadow-none'
                : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-blue-500/25 hover:shadow-lg'
            }`}
          >
            {isMatchingLoading ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                <span>Processing AI Matching...</span>
              </>
            ) : (
              <>
                <Sparkles className="w-4 h-4" />
                <span>Match & Rank Candidates</span>
              </>
            )}
          </button>
        </div>

        {/* Module 4: Candidate Ranking Dashboard */}
        {matchData && (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-300">
            <CandidateRankingTable
              matchData={matchData}
              jobDescription={parsedJd}
              onSelectCandidate={(cand) => setSelectedCandidate(cand)}
              onExportCsv={handleExportCsv}
            />
          </div>
        )}

        {/* Module 5: Candidate-Level Analysis Drawer */}
        {selectedCandidate && (
          <CandidateDetailDrawer
            candidate={selectedCandidate}
            jobDescription={parsedJd}
            onClose={() => setSelectedCandidate(null)}
          />
        )}

        {/* Algorithm Docs Modal */}
        {isDocsOpen && (
          <DocsModal onClose={() => setIsDocsOpen(false)} />
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-500">
        <p>MatchPro AI • AI / Full Stack Developer Practical Development Assignment</p>
        <p className="text-[11px] text-slate-400 mt-1">
          FastAPI Backend • React 18 + Tailwind CSS • Sentence Transformers (all-MiniLM-L6-v2)
        </p>
      </footer>
    </div>
  );
}
