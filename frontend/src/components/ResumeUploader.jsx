import React, { useState, useRef } from 'react';
import { UploadCloud, Files, FileText, CheckCircle, Trash2, Sparkles, User, Briefcase, RefreshCw, AlertCircle } from 'lucide-react';
import { api } from '../services/api';

export default function ResumeUploader({
  resumes,
  setResumes,
  isLoading,
  setIsLoading,
  onTriggerMatch,
  canMatch,
  isMatching
}) {
  const [dragActive, setDragActive] = useState(false);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFiles = async (fileList) => {
    if (!fileList || fileList.length === 0) return;

    setError(null);
    setIsLoading(true);
    try {
      const parsedResumes = await api.uploadResumes(fileList);
      // Append without duplicating by filename
      setResumes(prev => {
        const existingNames = new Set(prev.map(r => r.filename));
        const newOnes = parsedResumes.filter(r => !existingNames.has(r.filename));
        return [...prev, ...newOnes];
      });
    } catch (err) {
      setError(err.message || 'Error processing uploaded resumes');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer?.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleLoadSampleResumes = async () => {
    setError(null);
    setIsLoading(true);
    try {
      const samples = await api.getSampleResumes();
      setResumes(samples);
    } catch (err) {
      setError(err.message || 'Failed to load sample resumes');
    } finally {
      setIsLoading(false);
    }
  };

  const removeResume = (id) => {
    setResumes(prev => prev.filter(r => r.id !== id));
  };

  const clearAll = () => {
    setResumes([]);
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-100 gap-3">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-indigo-100 text-indigo-700 flex items-center justify-center font-bold text-sm">
            2
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Files className="w-5 h-5 text-indigo-600" />
              Batch Resume Upload
            </h2>
            <p className="text-xs text-slate-500">
              Upload at least 10+ resumes in batch (PDF and DOCX supported)
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center space-x-2">
          <button
            onClick={handleLoadSampleResumes}
            disabled={isLoading}
            className="flex items-center space-x-1.5 px-3 py-1.5 text-xs font-semibold bg-gradient-to-r from-indigo-50 to-blue-50 hover:from-indigo-100 hover:to-blue-100 text-indigo-700 border border-indigo-200 rounded-xl transition-all shadow-xs"
            title="Load 12 pre-generated synthetic PDF & DOCX resumes instantly"
          >
            <Sparkles className="w-3.5 h-3.5 text-indigo-600" />
            <span>Load 12 Sample Resumes (PDF & DOCX)</span>
          </button>

          {resumes.length > 0 && (
            <button
              onClick={clearAll}
              className="p-1.5 text-slate-400 hover:text-red-600 rounded-lg hover:bg-red-50 transition-colors"
              title="Clear all uploaded resumes"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {/* Drag & Drop Box */}
      <div
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
        onClick={() => inputRef.current?.click()}
        className={`mt-4 border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
          dragActive
            ? 'border-indigo-500 bg-indigo-50/50 scale-[1.005]'
            : 'border-slate-200 hover:border-indigo-400 bg-slate-50/50'
        }`}
      >
        <input
          ref={inputRef}
          type="file"
          multiple
          accept=".pdf,.docx,.doc"
          onChange={(e) => handleFiles(e.target.files)}
          className="hidden"
        />
        <UploadCloud className="w-10 h-10 text-indigo-500 mx-auto mb-2" />
        <h3 className="text-sm font-bold text-slate-800">
          Drop multiple candidate resumes here, or <span className="text-indigo-600 underline">browse</span>
        </h3>
        <p className="text-xs text-slate-400 mt-1">
          Supports multi-file selection of PDF & DOCX (Upload 10, 20, or more)
        </p>
      </div>

      {/* Extracted Resumes List */}
      {resumes.length > 0 && (
        <div className="mt-5">
          <div className="flex items-center justify-between pb-2 mb-3 border-b border-slate-100">
            <span className="text-xs font-bold text-slate-700 uppercase tracking-wider">
              Uploaded Resumes ({resumes.length} ready)
            </span>
            <span className="text-xs text-slate-500">
              {resumes.filter(r => r.filename.endsWith('.pdf')).length} PDFs, {resumes.filter(r => r.filename.endsWith('.docx')).length} DOCXs
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 max-h-64 overflow-y-auto pr-1">
            {resumes.map((r) => (
              <div
                key={r.id}
                className="p-3 bg-slate-50 hover:bg-slate-100/80 border border-slate-200 rounded-xl transition-all relative group"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-center space-x-2">
                    <div className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold ${
                      r.filename.toLowerCase().endsWith('.pdf')
                        ? 'bg-red-100 text-red-700'
                        : 'bg-blue-100 text-blue-700'
                    }`}>
                      {r.filename.toLowerCase().endsWith('.pdf') ? 'PDF' : 'DOC'}
                    </div>
                    <div>
                      <p className="text-xs font-bold text-slate-900 truncate max-w-[150px]">
                        {r.contact.name}
                      </p>
                      <p className="text-[10px] text-slate-400 truncate max-w-[150px]">
                        {r.filename}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeResume(r.id);
                    }}
                    className="opacity-0 group-hover:opacity-100 text-slate-400 hover:text-red-500 transition-opacity p-1"
                    title="Remove resume"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>

                <div className="mt-2.5 pt-2 border-t border-slate-200/60 flex items-center justify-between text-[11px] text-slate-600">
                  <span className="font-semibold text-slate-800">
                    {r.experience.total_years} yrs exp
                  </span>
                  <span className="bg-white px-2 py-0.5 rounded-md border border-slate-200 text-indigo-700 font-medium">
                    {r.extracted_skills.length} skills found
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Primary Matching Button Trigger */}
      <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between">
        <div className="text-xs text-slate-500">
          {!canMatch ? (
            <span className="text-amber-600 font-medium flex items-center gap-1.5">
              <AlertCircle className="w-3.5 h-3.5" />
              Provide a Job Description and at least 1 resume to compute match scores.
            </span>
          ) : (
            <span className="text-emerald-700 font-medium flex items-center gap-1.5">
              <CheckCircle className="w-3.5 h-3.5" />
              Ready to execute AI semantic matching & candidate ranking!
            </span>
          )}
        </div>

        <button
          onClick={onTriggerMatch}
          disabled={!canMatch || isLoading || isMatching}
          className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed text-white text-xs sm:text-sm font-bold rounded-xl shadow-md shadow-indigo-500/20 hover:shadow-indigo-500/30 transition-all flex items-center space-x-2"
        >
          {isMatching ? (
            <>
              <RefreshCw className="w-4 h-4 animate-spin" />
              <span>Analyzing & Ranking...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Match & Rank Candidates ({resumes.length})</span>
            </>
          )}
        </button>
      </div>
    </div>
  );
}
