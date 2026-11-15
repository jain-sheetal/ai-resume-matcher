import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import JobDescriptionInput from './components/JobDescriptionInput';
import ResumeUploader from './components/ResumeUploader';
import CandidateRankingTable from './components/CandidateRankingTable';
import CandidateDetailDrawer from './components/CandidateDetailDrawer';
import WeightSettingsModal from './components/WeightSettingsModal';
import DocsModal from './components/DocsModal';
import { api } from './services/api';
import { Sparkles, CheckCircle2, AlertCircle } from 'lucide-react';

export default function App() {
  const [sampleJds, setSampleJds] = useState([]);
  const [parsedJd, setParsedJd] = useState(null);
  const [resumes, setResumes] = useState([]);
  const [matchData, setMatchData] = useState(null);
  const [selectedCandidate, setSelectedCandidate] = useState(null);

  const [weights, setWeights] = useState({
    skills: 0.40,
    semantic: 0.35,
    experience: 0.20,
    education: 0.05
  });

  const [isJdLoading, setIsJdLoading] = useState(false);
  const [isResumeLoading, setIsResumeLoading] = useState(false);
  const [isMatchingLoading, setIsMatchingLoading] = useState(false);
  const [isWeightsOpen, setIsWeightsOpen] = useState(false);
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
        resumes: resumes,
        weights: weights
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
        resumes: resumes,
        weights: weights
      });
    } catch (err) {
      alert("Failed to export CSV: " + err.message);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col">
      <Navbar
        onOpenWeights={() => setIsWeightsOpen(true)}
        onOpenDocs={() => setIsDocsOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Hero Section */}
        <div className="text-center max-w-3xl mx-auto space-y-2">
          <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-blue-50 border border-blue-200 text-blue-700 text-xs font-bold">
            <Sparkles className="w-3.5 h-3.5 text-blue-600" />
            <span>AI-Driven Resume Screening & Semantic Ranking</span>
          </div>
          <h1 className="text-2xl sm:text-4xl font-extrabold text-slate-900 tracking-tight">
            Match Candidates to Job Descriptions in Seconds
          </h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Powered by Sentence Transformers neural embeddings, automated experience comparison, and skill ontology matching.
          </p>
        </div>

        {matchError && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{matchError}</span>
          </div>
        )}

        {/* Top Split: Module 1 & Module 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-start">
          {/* Module 1: Job Description Input */}
          <JobDescriptionInput
            parsedJd={parsedJd}
            setParsedJd={setParsedJd}
            sampleJds={sampleJds}
            isLoading={isJdLoading}
            setIsLoading={setIsJdLoading}
          />

          {/* Module 2: Resume Batch Upload */}
          <ResumeUploader
            resumes={resumes}
            setResumes={setResumes}
            isLoading={isResumeLoading || isMatchingLoading}
            setIsLoading={setIsResumeLoading}
            onTriggerMatch={handleTriggerMatch}
            canMatch={Boolean(parsedJd && resumes.length > 0)}
          />
        </div>

        {/* Module 4: Candidate Ranking Dashboard */}
        {matchData && (
          <div id="results-section" className="animate-in fade-in duration-500">
            <CandidateRankingTable
              matchData={matchData}
              onSelectCandidate={(candidate) => setSelectedCandidate(candidate)}
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

        {/* Custom Scoring Weights Modal */}
        {isWeightsOpen && (
          <WeightSettingsModal
            weights={weights}
            onSaveWeights={(newWeights) => {
              setWeights(newWeights);
              // Re-evaluate if matchData is active
              if (parsedJd && resumes.length > 0) {
                handleTriggerMatch();
              }
            }}
            onClose={() => setIsWeightsOpen(false)}
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
