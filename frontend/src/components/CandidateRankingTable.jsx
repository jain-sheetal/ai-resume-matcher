import React, { useState, useMemo } from 'react';
import { Award, Search, Download, ArrowUpDown, ChevronRight, Filter, Eye, CheckCircle2, AlertTriangle, Sparkles, UserCheck, ShieldCheck, Scale } from 'lucide-react';
import CandidateComparisonModal from './CandidateComparisonModal';

export default function CandidateRankingTable({
  matchData,
  onSelectCandidate,
  onExportCsv
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [expFilter, setExpFilter] = useState('all'); // 'all' | '1' | '3' | '5'
  const [categoryFilter, setCategoryFilter] = useState('all'); // 'all' | 'strong' | 'good' | 'moderate'
  const [sortField, setSortField] = useState('overall_score'); // 'overall_score' | 'experience_years' | 'name'
  const [sortDirection, setSortDirection] = useState('desc'); // 'asc' | 'desc'
  const [selectedForCompare, setSelectedForCompare] = useState([]); // List of candidate objects
  const [isCompareModalOpen, setIsCompareModalOpen] = useState(false);

  const candidates = matchData?.results || [];
  const engineDiag = matchData?.engine_diagnostics;

  const filteredCandidates = useMemo(() => {
    return candidates
      .filter((c) => {
        // Search filter
        const matchesSearch =
          c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.matched_skills.some(s => s.toLowerCase().includes(searchQuery.toLowerCase())) ||
          (c.email && c.email.toLowerCase().includes(searchQuery.toLowerCase()));

        // Score filter
        const matchesScore = c.overall_score >= minScore;

        // Experience filter
        let matchesExp = true;
        if (expFilter === '1') matchesExp = c.experience_years >= 1.0;
        if (expFilter === '3') matchesExp = c.experience_years >= 3.0;
        if (expFilter === '5') matchesExp = c.experience_years >= 5.0;

        // Category filter
        let matchesCat = true;
        if (categoryFilter === 'strong') matchesCat = c.overall_score >= 80;
        if (categoryFilter === 'good') matchesCat = c.overall_score >= 65 && c.overall_score < 80;
        if (categoryFilter === 'moderate') matchesCat = c.overall_score < 65;

        return matchesSearch && matchesScore && matchesExp && matchesCat;
      })
      .sort((a, b) => {
        let valA = a[sortField];
        let valB = b[sortField];

        if (typeof valA === 'string') {
          return sortDirection === 'asc'
            ? valA.localeCompare(valB)
            : valB.localeCompare(valA);
        }

        return sortDirection === 'asc' ? valA - valB : valB - valA;
      });
  }, [candidates, searchQuery, minScore, expFilter, categoryFilter, sortField, sortDirection]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const toggleSelectForCompare = (cand, e) => {
    e.stopPropagation();
    setSelectedForCompare(prev => {
      const exists = prev.some(c => c.candidate_id === cand.candidate_id);
      if (exists) {
        return prev.filter(c => c.candidate_id !== cand.candidate_id);
      } else {
        if (prev.length >= 2) {
          // Replace second candidate
          return [prev[0], cand];
        }
        return [...prev, cand];
      }
    });
  };

  const getScoreBadge = (score) => {
    if (score >= 80) {
      return {
        bg: 'bg-emerald-50 text-emerald-700 border-emerald-200',
        bar: 'bg-emerald-500',
        label: 'Strong Match'
      };
    }
    if (score >= 65) {
      return {
        bg: 'bg-blue-50 text-blue-700 border-blue-200',
        bar: 'bg-blue-500',
        label: 'Good Fit'
      };
    }
    if (score >= 50) {
      return {
        bg: 'bg-amber-50 text-amber-700 border-amber-200',
        bar: 'bg-amber-500',
        label: 'Moderate'
      };
    }
    return {
      bg: 'bg-slate-100 text-slate-700 border-slate-200',
      bar: 'bg-slate-400',
      label: 'Low Match'
    };
  };

  const getRankBadge = (rank) => {
    if (rank === 1) return <span className="text-base" title="Top Candidate">🥇</span>;
    if (rank === 2) return <span className="text-base" title="Runner Up">🥈</span>;
    if (rank === 3) return <span className="text-base" title="3rd Place">🥉</span>;
    return <span className="text-xs font-bold text-slate-400">#{rank}</span>;
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
      {/* Top Banner & Metrics */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-5 border-b border-slate-100 gap-4">
        <div>
          <div className="flex items-center space-x-2">
            <span className="w-8 h-8 rounded-lg bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold text-sm">
              3
            </span>
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Award className="w-5 h-5 text-emerald-600" />
              Candidate Ranking Dashboard
            </h2>
          </div>
          <p className="text-xs text-slate-500 mt-1 flex items-center gap-2">
            <span>Ranked by AI semantic relevance, technical skill coverage, and experience alignment.</span>
            {engineDiag && (
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold border ${engineDiag.is_fallback ? 'bg-amber-50 text-amber-800 border-amber-200' : 'bg-emerald-50 text-emerald-800 border-emerald-200'}`}>
                Engine: {engineDiag.active_engine}
              </span>
            )}
          </p>
        </div>

        {/* Quick Stats Badges & Compare Button */}
        <div className="flex flex-wrap items-center gap-3">
          <div className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-center">
            <span className="text-[10px] uppercase font-bold text-slate-400 block">Evaluated</span>
            <span className="text-sm font-extrabold text-slate-900">{candidates.length} Resumes</span>
          </div>
          <div className="px-3 py-1.5 bg-blue-50 border border-blue-200 rounded-xl text-center">
            <span className="text-[10px] uppercase font-bold text-blue-500 block">Top Match</span>
            <span className="text-sm font-extrabold text-blue-700">
              {candidates[0]?.overall_score ? `${candidates[0].overall_score}%` : 'N/A'}
            </span>
          </div>
          <div className="px-3 py-1.5 bg-indigo-50 border border-indigo-200 rounded-xl text-center">
            <span className="text-[10px] uppercase font-bold text-indigo-500 block">Avg Score</span>
            <span className="text-sm font-extrabold text-indigo-700">{matchData?.average_score || 0}%</span>
          </div>

          {selectedForCompare.length === 2 && (
            <button
              onClick={() => setIsCompareModalOpen(true)}
              className="flex items-center space-x-1.5 px-3.5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-xl shadow-md transition-all animate-bounce"
            >
              <Scale className="w-3.5 h-3.5" />
              <span>Compare (2)</span>
            </button>
          )}

          <button
            onClick={onExportCsv}
            className="flex items-center space-x-1.5 px-3 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl shadow-sm transition-all"
            title="Export rankings to CSV spreadsheet"
          >
            <Download className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Export CSV</span>
          </button>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="py-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Search */}
        <div className="relative flex-1 max-w-sm">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name, email, or skill..."
            className="w-full pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500"
          />
        </div>

        {/* Multi-Filters */}
        <div className="flex flex-wrap items-center gap-3">
          {/* Experience Filter */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-xl p-1 text-xs">
            <span className="text-slate-400 text-[11px] font-bold px-1.5">Exp:</span>
            {['all', '1', '3', '5'].map(lvl => (
              <button
                key={lvl}
                onClick={() => setExpFilter(lvl)}
                className={`px-2 py-0.5 rounded-lg font-semibold text-[11px] transition-colors ${expFilter === lvl ? 'bg-white text-blue-700 shadow-xs border border-slate-200' : 'text-slate-500 hover:text-slate-800'}`}
              >
                {lvl === 'all' ? 'All' : `${lvl}+ yrs`}
              </button>
            ))}
          </div>

          {/* Category Filter */}
          <div className="flex items-center gap-1 bg-slate-50 border border-slate-200 rounded-xl p-1 text-xs">
            {['all', 'strong', 'good', 'moderate'].map(cat => (
              <button
                key={cat}
                onClick={() => setCategoryFilter(cat)}
                className={`px-2 py-0.5 rounded-lg font-semibold text-[11px] capitalize transition-colors ${categoryFilter === cat ? 'bg-white text-indigo-700 shadow-xs border border-slate-200' : 'text-slate-500 hover:text-slate-800'}`}
              >
                {cat === 'all' ? 'All Tiers' : cat}
              </button>
            ))}
          </div>

          {/* Min Score Slider */}
          <div className="flex items-center space-x-2 text-xs bg-slate-50 px-3 py-1.5 border border-slate-200 rounded-xl">
            <span className="text-slate-500 font-semibold whitespace-nowrap">Min Score:</span>
            <input
              type="range"
              min="0"
              max="90"
              step="5"
              value={minScore}
              onChange={(e) => setMinScore(Number(e.target.value))}
              className="w-20 accent-blue-600"
            />
            <span className="font-extrabold text-blue-700 min-w-8">{minScore}%</span>
          </div>
        </div>
      </div>

      {/* Main Ranking Table */}
      <div className="overflow-x-auto border border-slate-200 rounded-xl">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-slate-50/80 border-b border-slate-200 text-slate-600 text-[11px] font-extrabold uppercase tracking-wider">
              <th className="py-3 px-3 w-10 text-center">Compare</th>
              <th className="py-3 px-3 w-12 text-center">Rank</th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-900" onClick={() => handleSort('name')}>
                <div className="flex items-center space-x-1">
                  <span>Candidate</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-900" onClick={() => handleSort('experience_years')}>
                <div className="flex items-center space-x-1">
                  <span>Experience</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4 cursor-pointer hover:text-slate-900 w-44" onClick={() => handleSort('overall_score')}>
                <div className="flex items-center space-x-1">
                  <span>Overall Match %</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4">Top Matched Skills</th>
              <th className="py-3 px-4 text-center w-24">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 text-xs text-slate-700">
            {filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan="7" className="py-12 text-center text-slate-400 text-sm">
                  No candidates match the current filter criteria.
                </td>
              </tr>
            ) : (
              filteredCandidates.map((cand) => {
                const badge = getScoreBadge(cand.overall_score);
                const isSelected = selectedForCompare.some(c => c.candidate_id === cand.candidate_id);

                return (
                  <tr
                    key={cand.candidate_id}
                    onClick={() => onSelectCandidate(cand)}
                    className="hover:bg-blue-50/40 cursor-pointer transition-colors group"
                  >
                    {/* Compare Checkbox */}
                    <td className="py-3.5 px-3 text-center" onClick={(e) => e.stopPropagation()}>
                      <input
                        type="checkbox"
                        checked={isSelected}
                        onChange={(e) => toggleSelectForCompare(cand, e)}
                        className="rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                        title="Select up to 2 candidates to compare side-by-side"
                      />
                    </td>

                    {/* Rank */}
                    <td className="py-3.5 px-3 text-center font-bold">
                      {getRankBadge(cand.rank)}
                    </td>

                    {/* Candidate Name & Contacts */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="font-extrabold text-slate-900 group-hover:text-blue-600 transition-colors">
                          {cand.name}
                        </span>
                        {cand.confidence?.overall && (
                          <span className={`text-[10px] font-bold px-1.5 py-0.2 rounded border ${cand.confidence.overall === 'High' ? 'bg-emerald-50 text-emerald-700 border-emerald-200' : 'bg-slate-50 text-slate-600 border-slate-200'}`}>
                            {cand.confidence.overall}
                          </span>
                        )}
                      </div>
                      <div className="text-[11px] text-slate-400 mt-0.5 truncate max-w-xs">
                        {cand.email || cand.filename}
                      </div>
                    </td>

                    {/* Experience */}
                    <td className="py-3.5 px-4 whitespace-nowrap">
                      <span className="font-bold text-slate-800">{cand.experience_years}</span>
                      <span className="text-slate-400 text-[11px] ml-1">years</span>
                    </td>

                    {/* Overall Score & Mini Bar */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-base font-black text-slate-900 min-w-10">
                          {cand.overall_score}%
                        </span>
                        <div className="flex-1 max-w-[80px] bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full ${badge.bar} transition-all duration-500 rounded-full`}
                            style={{ width: `${cand.overall_score}%` }}
                          />
                        </div>
                      </div>
                      <span className={`inline-block mt-1 px-2 py-0.5 text-[10px] font-bold rounded-full border ${badge.bg}`}>
                        {badge.label}
                      </span>
                    </td>

                    {/* Matched Skills Chips */}
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1 max-w-md">
                        {cand.matched_skills.slice(0, 4).map((skill) => (
                          <span
                            key={skill}
                            className="px-2 py-0.5 text-[11px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-md"
                          >
                            {skill}
                          </span>
                        ))}
                        {cand.matched_skills.length > 4 && (
                          <span className="px-1.5 py-0.5 text-[10px] font-bold bg-slate-100 text-slate-600 rounded-md">
                            +{cand.matched_skills.length - 4} more
                          </span>
                        )}
                        {cand.matched_skills.length === 0 && (
                          <span className="text-xs text-slate-400 italic">None</span>
                        )}
                      </div>
                    </td>

                    {/* View Button */}
                    <td className="py-3.5 px-4 text-center">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectCandidate(cand);
                        }}
                        className="p-1.5 text-blue-600 hover:text-white hover:bg-blue-600 rounded-lg transition-colors border border-blue-200 hover:border-blue-600"
                        title="View candidate analysis drawer"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      {/* Comparison Modal */}
      {isCompareModalOpen && selectedForCompare.length === 2 && (
        <CandidateComparisonModal
          candidateA={selectedForCompare[0]}
          candidateB={selectedForCompare[1]}
          onClose={() => setIsCompareModalOpen(false)}
        />
      )}
    </div>
  );
}
