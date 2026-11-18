import React, { useState } from 'react';
import { X, Award, CheckCircle2, AlertTriangle, Briefcase, GraduationCap, Mail, Phone, FileText, Sparkles, ChevronDown, ChevronUp, Layers, Check, ShieldCheck, HelpCircle } from 'lucide-react';

export default function CandidateDetailDrawer({ candidate, jobDescription, onClose }) {
  const [showRawText, setShowRawText] = useState(false);
  const [filterTier, setFilterTier] = useState('all'); // 'all' | 'Strong Match' | 'Missing'

  if (!candidate) return null;

  const { score_breakdown: sb, explanation: exp, confidence } = candidate;
  const evidences = candidate.skill_evidences || [];

  const filteredEvidences = evidences.filter(e => {
    if (filterTier === 'all') return true;
    return e.result === filterTier;
  });

  const getTierBadge = (result) => {
    switch (result) {
      case 'Strong Match':
        return 'bg-emerald-50 text-emerald-800 border-emerald-200';
      case 'Partial Match':
        return 'bg-blue-50 text-blue-800 border-blue-200';
      case 'Related Skill':
        return 'bg-purple-50 text-purple-800 border-purple-200';
      case 'Missing':
        return 'bg-rose-50 text-rose-800 border-rose-200';
      default:
        return 'bg-slate-50 text-slate-700 border-slate-200';
    }
  };

  const getConfidenceBadge = (level) => {
    if (level === 'High') return 'bg-emerald-100 text-emerald-800 border-emerald-300';
    if (level === 'Medium') return 'bg-amber-100 text-amber-800 border-amber-300';
    return 'bg-rose-100 text-rose-800 border-rose-300';
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
              {confidence && (
                <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border flex items-center gap-1 ${getConfidenceBadge(confidence.overall)}`}>
                  <ShieldCheck className="w-3 h-3" />
                  {confidence.overall} Confidence
                </span>
              )}
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
                  Evaluated with Sentence-BERT embeddings, contextual skill ontology, and non-overlapping tenure intervals.
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

          {/* Contextual Requirement Evidence Table */}
          {evidences.length > 0 && (
            <div className="p-4 bg-white border border-slate-200 rounded-xl space-y-3">
              <div className="flex items-center justify-between">
                <h3 className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <Award className="w-4 h-4 text-indigo-600" />
                  Requirement-by-Requirement Evidence ({evidences.length})
                </h3>
                <div className="flex items-center gap-1 text-[11px]">
                  <button
                    onClick={() => setFilterTier('all')}
                    className={`px-2 py-0.5 rounded-md font-semibold ${filterTier === 'all' ? 'bg-slate-900 text-white' : 'text-slate-500 hover:bg-slate-100'}`}
                  >
                    All
                  </button>
                  <button
                    onClick={() => setFilterTier('Strong Match')}
                    className={`px-2 py-0.5 rounded-md font-semibold ${filterTier === 'Strong Match' ? 'bg-emerald-600 text-white' : 'text-slate-500 hover:bg-slate-100'}`}
                  >
                    Strong
                  </button>
                  <button
                    onClick={() => setFilterTier('Missing')}
                    className={`px-2 py-0.5 rounded-md font-semibold ${filterTier === 'Missing' ? 'bg-rose-600 text-white' : 'text-slate-500 hover:bg-slate-100'}`}
                  >
                    Missing
                  </button>
                </div>
              </div>

              <div className="divide-y divide-slate-100 border border-slate-100 rounded-lg max-h-72 overflow-y-auto">
                {filteredEvidences.map((evi) => (
                  <div key={evi.requirement} className="p-2.5 hover:bg-slate-50/70 transition-colors">
                    <div className="flex items-center justify-between gap-2">
                      <div className="flex items-center space-x-1.5">
                        <span className="font-bold text-xs text-slate-900">{evi.requirement}</span>
                        <span className={`text-[10px] font-semibold px-1.5 py-0.2 rounded border ${getTierBadge(evi.result)}`}>
                          {evi.result}
                        </span>
                      </div>
                      <span className="text-[10px] font-medium text-slate-400">
                        {evi.category}
                      </span>
                    </div>
                    {evi.evidence_snippet ? (
                      <p className="mt-1 text-[11px] text-slate-600 italic bg-slate-50 p-1.5 rounded border border-slate-100">
                        "{evi.evidence_snippet}"
                      </p>
                    ) : (
                      <p className="mt-0.5 text-[10px] text-rose-500 italic">
                        No direct mention found in candidate resume.
                      </p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Matched vs Missing Skills Badges */}
          <div className="space-y-4">
            {/* Matched Skills */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs font-bold text-slate-900 uppercase tracking-wider flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Matched Skills ({candidate.matched_skills.length})
                </span>
                <span className="text-[11px] font-semibold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-200">
                  Verified in Resume
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
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                  Missing Skills ({candidate.missing_skills.length})
                </span>
                <span className="text-[11px] font-semibold text-rose-700 bg-rose-50 px-2 py-0.5 rounded-full border border-rose-200">
                  Required in JD
                </span>
              </div>
              <div className="flex flex-wrap gap-1.5 p-3 bg-rose-50/40 border border-rose-100 rounded-xl min-h-[48px]">
                {candidate.missing_skills.length === 0 ? (
                  <span className="text-xs text-emerald-700 font-semibold flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> All required skills are matched!
                  </span>
                ) : (
                  candidate.missing_skills.map((skill) => (
                    <span
                      key={skill}
                      className="px-2.5 py-1 text-xs font-semibold bg-white text-rose-800 border border-rose-200 rounded-lg shadow-2xs flex items-center gap-1"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
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
                {exp.strengths.map((str, idx) => (
                  <li key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                    <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600 shrink-0 mt-0.5" />
                    <span>{str}</span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Gaps */}
            {exp.gaps.length > 0 && (
              <div>
                <span className="text-xs font-bold text-rose-800 block mb-1.5">
                  Deductions & Identified Gaps
                </span>
                <ul className="space-y-1.5">
                  {exp.gaps.map((gap, idx) => (
                    <li key={idx} className="text-xs text-slate-700 flex items-start gap-2">
                      <AlertTriangle className="w-3.5 h-3.5 text-rose-600 shrink-0 mt-0.5" />
                      <span>{gap}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <div className="pt-2 border-t border-indigo-100 text-[11px] text-slate-500">
              <p><strong>Semantic Context:</strong> {exp.semantic_alignment}</p>
            </div>
          </div>

          {/* Raw Text Preview */}
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <button
              onClick={() => setShowRawText(!showRawText)}
              className="w-full px-4 py-2.5 bg-slate-100 hover:bg-slate-200/80 text-slate-700 text-xs font-bold flex items-center justify-between transition-colors"
            >
              <span className="flex items-center gap-1.5">
                <FileText className="w-3.5 h-3.5 text-slate-500" />
                Inspect Extracted Text Stream
              </span>
              {showRawText ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            </button>
            {showRawText && (
              <div className="p-4 bg-slate-900 text-slate-100 font-mono text-[11px] max-h-60 overflow-y-auto whitespace-pre-wrap leading-relaxed">
                {candidate.raw_text_snippet}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
