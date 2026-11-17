import React, { useState } from 'react';
import { X, Award, CheckCircle2, AlertTriangle, Briefcase, GraduationCap, Mail, Phone, FileText, Sparkles, ChevronDown, ChevronUp, Layers, Check } from 'lucide-react';

export default function CandidateDetailDrawer({ candidate, jobDescription, onClose }) {
  const [showRawText, setShowRawText] = useState(false);

  if (!candidate) return null;

  const { score_breakdown: sb, explanation: exp } = candidate;

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (score >= 65) return 'text-blue-600 bg-blue-50 border-blue-200';
    if (score >= 50) return 'text-amber-600 bg-amber-50 border-amber-200';
    return 'text-slate-600 bg-slate-100 border-slate-200';
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex justify-end">
      <div className="w-full max-w-2xl bg-white h-full shadow-2xl flex flex-col transform transition-transform duration-300 ease-in-out animate-in slide-in-from-right">
        {/* Header */}
        <div className="p-5 border-b border-slate-200 flex items-start justify-between bg-slate-50/70">
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-black px-2 py-0.5 rounded-md bg-blue-600 text-white">
                Rank #{candidate.rank}
              </span>
              <h2 className="text-xl font-extrabold text-slate-900">{candidate.name}</h2>
            </div>
            <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-slate-500">
              {candidate.email && (
                <span className="flex items-center gap-1">
                  <Mail className="w-3.5 h-3.5 text-slate-400" />
                  {candidate.email}
                </span>
              )}
              {candidate.phone && (
                <span className="flex items-center gap-1">
                  <Phone className="w-3.5 h-3.5 text-slate-400" />
                  {candidate.phone}
                </span>
              )}
              <span className="flex items-center gap-1">
                <FileText className="w-3.5 h-3.5 text-slate-400" />
                {candidate.filename}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-slate-700 hover:bg-slate-200/60 rounded-xl transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Hero Score Card */}
          <div className="p-5 rounded-2xl bg-gradient-to-br from-slate-900 to-indigo-950 text-white shadow-lg relative overflow-hidden">
            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 relative z-10">
              <div>
                <span className="text-xs uppercase font-bold tracking-wider text-indigo-300 block">
                  Overall Match Score
                </span>
                <div className="flex items-baseline space-x-2 mt-1">
                  <span className="text-4xl font-extrabold">{candidate.overall_score}%</span>
                  <span className="text-xs font-semibold px-2.5 py-0.5 rounded-full bg-indigo-500/30 border border-indigo-400/40 text-indigo-200">
                    {exp.verdict}
                  </span>
                </div>
                <p className="text-xs text-slate-300 mt-2 max-w-sm">
                  Calculated using Sentence Transformers neural embeddings, skill ontology taxonomy, and experience duration evaluation.
                </p>
              </div>

              {/* Mini breakdown chips */}
              <div className="grid grid-cols-2 gap-2 w-full sm:w-auto">
                <div className="p-2.5 bg-white/10 rounded-xl text-center backdrop-blur-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-300 block">Skills</span>
                  <span className="text-sm font-bold text-white">{sb.skills_score}%</span>
                </div>
                <div className="p-2.5 bg-white/10 rounded-xl text-center backdrop-blur-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-300 block">Semantic</span>
                  <span className="text-sm font-bold text-white">{sb.semantic_score}%</span>
                </div>
                <div className="p-2.5 bg-white/10 rounded-xl text-center backdrop-blur-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-300 block">Experience</span>
                  <span className="text-sm font-bold text-white">{sb.experience_score}%</span>
                </div>
                <div className="p-2.5 bg-white/10 rounded-xl text-center backdrop-blur-xs">
                  <span className="text-[10px] uppercase font-bold text-slate-300 block">Education</span>
                  <span className="text-sm font-bold text-white">{sb.education_score}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Experience Comparison */}
          <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl">
            <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5 mb-3">
              <Briefcase className="w-4 h-4 text-blue-600" />
              Experience Evaluation
            </h3>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 text-center">
              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Candidate Has</span>
                <span className="text-base font-extrabold text-slate-900">{candidate.experience_years} Years</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-lg">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">JD Requires</span>
                <span className="text-base font-extrabold text-blue-700">{jobDescription?.min_experience_years || 2} Years</span>
              </div>
              <div className="p-3 bg-white border border-slate-200 rounded-lg col-span-2 sm:col-span-1">
                <span className="text-[10px] uppercase font-bold text-slate-400 block">Tenure Delta</span>
                <span className={`text-base font-extrabold ${candidate.experience_years >= (jobDescription?.min_experience_years || 2) ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {candidate.experience_years >= (jobDescription?.min_experience_years || 2) ? '+' : ''}
                  {(candidate.experience_years - (jobDescription?.min_experience_years || 2)).toFixed(1)} Yrs
                </span>
              </div>
            </div>
            <p className="text-xs text-slate-600 mt-2.5 bg-white p-2.5 rounded-lg border border-slate-100">
              {exp.experience_analysis}
            </p>
          </div>

          {/* Matched vs Missing Skills */}
          <div className="space-y-4">
            {/* Matched Skills */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Matched Skills ({candidate.matched_skills.length})
                </span>
                <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  Covered in Resume
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 p-3 bg-emerald-50/50 border border-emerald-100 rounded-xl min-h-[48px]">
                {candidate.matched_skills.length === 0 ? (
                  <span className="text-xs text-slate-400 italic">No direct required skills matched.</span>
                ) : (
                  candidate.matched_skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2.5 py-1 text-xs font-semibold bg-white text-emerald-800 border border-emerald-200 rounded-lg shadow-2xs flex items-center gap-1"
                    >
                      <Check className="w-3 h-3 text-emerald-600" />
                      {skill}
                    </span>
                  ))
                )}
              </div>
            </div>

            {/* Missing Skills */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-amber-600" />
                  Missing Skills ({candidate.missing_skills.length})
                </span>
                <span className="text-[11px] font-semibold text-amber-700 bg-amber-50 px-2 py-0.5 rounded-full border border-amber-200">
                  Required in JD
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 p-3 bg-amber-50/50 border border-amber-100 rounded-xl min-h-[48px]">
                {candidate.missing_skills.length === 0 ? (
                  <span className="text-xs text-emerald-700 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> All required skills are matched!
                  </span>
                ) : (
                  candidate.missing_skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2.5 py-1 text-xs font-semibold bg-white text-amber-800 border border-amber-200 rounded-lg shadow-2xs flex items-center gap-1"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
                      {skill}
                    </span>
                  ))
                )}
              </div>
            </div>

            {/* Additional Skills */}
            {candidate.additional_skills.length > 0 && (
              <div>
                <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5 mb-2">
                  <Layers className="w-3.5 h-3.5 text-indigo-500" />
                  Additional Valued Skills ({candidate.additional_skills.length})
                </span>
                <div className="flex flex-wrap gap-1.5 p-3 bg-slate-50 border border-slate-200 rounded-xl max-h-24 overflow-y-auto">
                  {candidate.additional_skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2 py-0.5 text-[11px] font-medium bg-white text-slate-700 border border-slate-200 rounded-md"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Explainable AI: Reasons Behind Score */}
          <div className="p-5 bg-gradient-to-br from-indigo-50/40 via-blue-50/30 to-purple-50/40 border border-indigo-100 rounded-2xl space-y-4">
            <div className="flex items-center space-x-2">
              <Sparkles className="w-4 h-4 text-indigo-600" />
              <h3 className="text-xs font-bold text-indigo-900 uppercase tracking-wider">
                Explainable AI Rationale & Decision Factors
              </h3>
            </div>

            {/* Strengths */}
            <div>
              <span className="text-xs font-bold text-emerald-800 block mb-1.5">
                Key Strengths Identified
              </span>
              <ul className="space-y-1.5">
                {exp.strengths.map((s, idx) => (
                  <li key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5" />
                    <span>{s}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Gaps */}
            {exp.gaps.length > 0 && (
              <div>
                <span className="text-xs font-bold text-amber-800 block mb-1.5">
                  Identified Gaps & Risk Flags
                </span>
                <ul className="space-y-1.5">
                  {exp.gaps.map((g, idx) => (
                    <li key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                      <AlertTriangle className="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5" />
                      <span>{g}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Semantic Context */}
            <div className="pt-2 border-t border-indigo-100">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wider block">
                Contextual Embedding Similarity
              </span>
              <p className="text-xs text-slate-700 mt-1">
                {exp.semantic_alignment}
              </p>
            </div>
          </div>

          {/* Collapsible Raw Text Snippet */}
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowRawText(!showRawText)}
              className="w-full p-3.5 bg-slate-50 hover:bg-slate-100 text-left flex items-center justify-between text-xs font-bold text-slate-700 transition-colors"
            >
              <div className="flex items-center space-x-2">
                <FileText className="w-4 h-4 text-slate-500" />
                <span>Extracted Resume Text Preview</span>
              </div>
              {showRawText ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            {showRawText && (
              <div className="p-4 bg-slate-900 text-slate-200 font-mono text-[11px] max-h-60 overflow-y-auto whitespace-pre-wrap">
                {candidate.raw_text_snippet || 'No raw text snippet available.'}
              </div>
            )}
          </div>
        </div>

        {/* Footer Actions */}
        <div className="p-4 border-t border-slate-200 bg-slate-50 flex items-center justify-between">
          <span className="text-xs text-slate-500">
            Candidate ID: <code className="text-slate-800">{candidate.candidate_id}</code>
          </span>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl transition-colors"
          >
            Close Analysis
          </button>
        </div>
      </div>
    </div>
  );
}
