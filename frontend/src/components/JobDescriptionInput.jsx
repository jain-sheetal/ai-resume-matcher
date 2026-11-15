import React, { useState } from 'react';
import { Briefcase, Upload, FileText, Sparkles, CheckCircle2, ChevronRight, AlertCircle, RefreshCw } from 'lucide-react';
import { api } from '../services/api';

export default function JobDescriptionInput({
  parsedJd,
  setParsedJd,
  sampleJds,
  isLoading,
  setIsLoading
}) {
  const [activeTab, setActiveTab] = useState('paste'); // 'paste' | 'upload'
  const [jdText, setJdText] = useState('');
  const [selectedSampleId, setSelectedSampleId] = useState('');
  const [error, setError] = useState(null);

  const handleSelectSample = (sample) => {
    setSelectedSampleId(sample.id);
    setJdText(sample.description);
    handleParseText(sample.description, sample.title);
  };

  const handleParseText = async (textToParse = jdText, customTitle = null) => {
    if (!textToParse.trim()) {
      setError('Please provide or paste a Job Description.');
      return;
    }
    setError(null);
    setIsLoading(true);
    try {
      const parsed = await api.parseJd({
        text: textToParse,
        title: customTitle || "Job Position"
      });
      setParsedJd(parsed);
    } catch (err) {
      setError(err.message || 'Failed to parse Job Description');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setError(null);
    setIsLoading(true);
    try {
      const parsed = await api.uploadJdFile(file);
      setParsedJd(parsed);
      setJdText(parsed.raw_text);
    } catch (err) {
      setError(err.message || 'Failed to upload and parse file');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-blue-100 text-blue-700 flex items-center justify-center font-bold text-sm">
            1
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-blue-600" />
              Job Description Input
            </h2>
            <p className="text-xs text-slate-500">Paste text, upload a JD file, or select a sample benchmark</p>
          </div>
        </div>

        {/* Preset quick buttons */}
        <div className="flex items-center space-x-1.5 overflow-x-auto pb-1 sm:pb-0">
          <span className="text-xs font-semibold text-slate-400 mr-1 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-500" /> Presets:
          </span>
          {sampleJds.map((sample) => (
            <button
              key={sample.id}
              onClick={() => handleSelectSample(sample)}
              className={`px-2.5 py-1 text-xs font-medium rounded-lg border transition-all whitespace-nowrap ${
                selectedSampleId === sample.id
                  ? 'bg-blue-600 text-white border-blue-600 shadow-sm'
                  : 'bg-slate-50 text-slate-700 border-slate-200 hover:bg-slate-100'
              }`}
            >
              {sample.title.split('(')[0].trim()}
            </button>
          ))}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Input Mode Selector */}
      <div className="mt-4 flex items-center space-x-3 border-b border-slate-100 pb-3">
        <button
          onClick={() => setActiveTab('paste')}
          className={`flex items-center space-x-1.5 text-xs font-semibold pb-1 border-b-2 transition-all ${
            activeTab === 'paste'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <FileText className="w-3.5 h-3.5" />
          <span>Paste Job Description</span>
        </button>
        <button
          onClick={() => setActiveTab('upload')}
          className={`flex items-center space-x-1.5 text-xs font-semibold pb-1 border-b-2 transition-all ${
            activeTab === 'upload'
              ? 'border-blue-600 text-blue-600'
              : 'border-transparent text-slate-500 hover:text-slate-800'
          }`}
        >
          <Upload className="w-3.5 h-3.5" />
          <span>Upload File (.pdf, .docx, .txt)</span>
        </button>
      </div>

      {/* Input Controls */}
      <div className="mt-4">
        {activeTab === 'paste' ? (
          <div>
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Paste job description here (responsibilities, required skills, min experience, etc.)..."
              rows={5}
              className="w-full p-3 text-xs sm:text-sm font-sans bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white focus:outline-none transition-all placeholder:text-slate-400"
            />
            <div className="mt-2 flex justify-between items-center">
              <span className="text-xs text-slate-400">
                {jdText ? `${jdText.split(/\s+/).filter(Boolean).length} words` : 'Empty JD'}
              </span>
              <button
                onClick={() => handleParseText()}
                disabled={isLoading || !jdText.trim()}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-semibold rounded-xl shadow-sm transition-all flex items-center space-x-1.5"
              >
                {isLoading ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    <span>Extracting...</span>
                  </>
                ) : (
                  <>
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Extract Requirements</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div className="border-2 border-dashed border-slate-200 hover:border-blue-400 rounded-2xl p-6 text-center transition-colors bg-slate-50/50">
            <Upload className="w-8 h-8 text-slate-400 mx-auto mb-2" />
            <p className="text-xs font-semibold text-slate-700">Drag & drop JD file or browse</p>
            <p className="text-[11px] text-slate-400 mt-1">Supports PDF, DOCX, and TXT files</p>
            <label className="mt-3 inline-block px-4 py-2 bg-white border border-slate-300 hover:bg-slate-50 text-slate-700 text-xs font-semibold rounded-xl cursor-pointer shadow-sm transition-colors">
              Browse File
              <input
                type="file"
                accept=".pdf,.docx,.doc,.txt"
                onChange={handleFileUpload}
                className="hidden"
              />
            </label>
          </div>
        )}
      </div>

      {/* Extracted JD Info Card */}
      {parsedJd && (
        <div className="mt-5 p-4 bg-gradient-to-r from-blue-50/60 to-indigo-50/40 border border-blue-100 rounded-xl">
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-blue-100">
            <div className="flex items-center space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              <span className="text-xs font-bold uppercase tracking-wider text-blue-900">
                Extracted Job Requirements
              </span>
            </div>
            <span className="text-xs px-2.5 py-0.5 font-bold rounded-full bg-blue-600 text-white shadow-xs">
              Min Exp: {parsedJd.min_experience_years} {parsedJd.min_experience_years === 1 ? 'Year' : 'Years'}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <div>
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Position Role</span>
              <p className="text-xs font-bold text-slate-900 mt-0.5">{parsedJd.title}</p>
            </div>
            <div>
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">Education Expectation</span>
              <p className="text-xs font-medium text-slate-800 mt-0.5">{parsedJd.required_education}</p>
            </div>
            <div>
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                Required Skills ({parsedJd.required_skills.length})
              </span>
              <div className="flex flex-wrap gap-1 mt-1 max-h-20 overflow-y-auto pr-1">
                {parsedJd.required_skills.map((skill) => (
                  <span
                    key={skill}
                    className="px-2 py-0.5 text-[11px] font-semibold bg-white text-blue-800 border border-blue-200 rounded-md shadow-2xs"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
