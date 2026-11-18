import React from 'react';
import { X, CheckCircle2, AlertTriangle, Briefcase, GraduationCap, Award, Sparkles } from 'lucide-react';

export default function CandidateComparisonModal({ candidateA, candidateB, onClose }) {
  if (!candidateA || !candidateB) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] shadow-2xl border border-slate-200 flex flex-col animate-in zoom-in-95">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-2">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <h3 className="font-extrabold text-slate-900 text-base">
              Head-to-Head Candidate Comparison
            </h3>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Comparison Content */}
        <div className="p-6 overflow-y-auto space-y-6 text-xs text-slate-700">
          {/* Top Summary Cards */}
          <div className="grid grid-cols-2 gap-4">
            {/* Candidate A */}
            <div className="p-4 rounded-xl border-2 border-indigo-200 bg-indigo-50/30">
              <span className="text-[10px] font-bold uppercase tracking-wider text-indigo-600 block">Candidate A (Rank #{candidateA.rank})</span>
              <h4 className="text-lg font-black text-slate-900 mt-0.5">{candidateA.name}</h4>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-black text-indigo-700">{candidateA.overall_score}%</span>
                <span className="text-xs font-semibold text-slate-500">Overall Match</span>
              </div>
            </div>

            {/* Candidate B */}
            <div className="p-4 rounded-xl border-2 border-blue-200 bg-blue-50/30">
              <span className="text-[10px] font-bold uppercase tracking-wider text-blue-600 block">Candidate B (Rank #{candidateB.rank})</span>
              <h4 className="text-lg font-black text-slate-900 mt-0.5">{candidateB.name}</h4>
              <div className="flex items-baseline gap-2 mt-2">
                <span className="text-3xl font-black text-blue-700">{candidateB.overall_score}%</span>
                <span className="text-xs font-semibold text-slate-500">Overall Match</span>
              </div>
            </div>
          </div>

          {/* Metric Comparison Table */}
          <div className="border border-slate-200 rounded-xl overflow-hidden">
            <table className="w-full text-left border-collapse text-xs">
              <thead>
                <tr className="bg-slate-100/70 border-b border-slate-200 text-slate-600 font-bold uppercase text-[10px]">
                  <th className="p-3 w-1/3">Evaluation Metric</th>
                  <th className="p-3 w-1/3 text-indigo-900">{candidateA.name}</th>
                  <th className="p-3 w-1/3 text-blue-900">{candidateB.name}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                <tr>
                  <td className="p-3 font-semibold text-slate-700">Total Experience</td>
                  <td className={`p-3 font-bold ${candidateA.experience_years >= candidateB.experience_years ? 'text-emerald-700 font-extrabold' : 'text-slate-700'}`}>
                    {candidateA.experience_years} Years
                  </td>
                  <td className={`p-3 font-bold ${candidateB.experience_years >= candidateA.experience_years ? 'text-emerald-700 font-extrabold' : 'text-slate-700'}`}>
                    {candidateB.experience_years} Years
                  </td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-700">Technical Skill Score</td>
                  <td className="p-3 font-bold text-slate-800">{candidateA.score_breakdown.skills_score}%</td>
                  <td className="p-3 font-bold text-slate-800">{candidateB.score_breakdown.skills_score}%</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-700">Semantic AI Score</td>
                  <td className="p-3 font-bold text-slate-800">{candidateA.score_breakdown.semantic_score}%</td>
                  <td className="p-3 font-bold text-slate-800">{candidateB.score_breakdown.semantic_score}%</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-700">Experience Score</td>
                  <td className="p-3 font-bold text-slate-800">{candidateA.score_breakdown.experience_score}%</td>
                  <td className="p-3 font-bold text-slate-800">{candidateB.score_breakdown.experience_score}%</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-700">Extraction Confidence</td>
                  <td className="p-3 font-bold text-emerald-700">{candidateA.confidence?.overall || 'High'}</td>
                  <td className="p-3 font-bold text-emerald-700">{candidateB.confidence?.overall || 'High'}</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-700">Matched Skills Count</td>
                  <td className="p-3 font-bold text-slate-800">{candidateA.matched_skills.length} skills</td>
                  <td className="p-3 font-bold text-slate-800">{candidateB.matched_skills.length} skills</td>
                </tr>
                <tr>
                  <td className="p-3 font-semibold text-slate-700">Missing Skills Count</td>
                  <td className="p-3 font-bold text-rose-700">{candidateA.missing_skills.length} skills</td>
                  <td className="p-3 font-bold text-rose-700">{candidateB.missing_skills.length} skills</td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Side by side skills */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                {candidateA.name}'s Matched Skills:
              </span>
              <div className="flex flex-wrap gap-1 p-2 bg-slate-50 rounded-lg border border-slate-200 min-h-[48px]">
                {candidateA.matched_skills.map(s => (
                  <span key={s} className="px-2 py-0.5 bg-white border border-emerald-200 text-emerald-800 rounded text-[11px] font-semibold">
                    {s}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-slate-500 block mb-1">
                {candidateB.name}'s Matched Skills:
              </span>
              <div className="flex flex-wrap gap-1 p-2 bg-slate-50 rounded-lg border border-slate-200 min-h-[48px]">
                {candidateB.matched_skills.map(s => (
                  <span key={s} className="px-2 py-0.5 bg-white border border-blue-200 text-blue-800 rounded text-[11px] font-semibold">
                    {s}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl"
          >
            Close Comparison
          </button>
        </div>
      </div>
    </div>
  );
}
