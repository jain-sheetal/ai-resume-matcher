import React, { useState, useMemo } from 'react';
import { Award, Search, Download, ArrowUpDown, ChevronRight, Filter, Eye, CheckCircle2, AlertTriangle, Sparkles, UserCheck } from 'lucide-react';

export default function CandidateRankingTable({
  matchData,
  onSelectCandidate,
  onExportCsv
}) {
  const [searchQuery, setSearchQuery] = useState('');
  const [minScore, setMinScore] = useState(0);
  const [sortField, setSortField] = useState('overall_score'); // 'overall_score' | 'experience_years' | 'name'
  const [sortDirection, setSortDirection] = useState('desc'); // 'asc' | 'desc'

  const candidates = matchData?.results || [];

  const filteredCandidates = useMemo(() => {
    return candidates
      .filter((c) => {
        const matchesSearch =
          c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
          c.matched_skills.some(s => s.toLowerCase().includes(searchQuery.toLowerCase())) ||
          (c.email && c.email.toLowerCase().includes(searchQuery.toLowerCase()));

        const matchesScore = c.overall_score >= minScore;
        return matchesSearch && matchesScore;
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
  }, [candidates, searchQuery, minScore, sortField, sortDirection]);

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
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
          <p className="text-xs text-slate-500 mt-1">
            Ranked by AI semantic relevance, technical skill coverage, and experience alignment.
          </p>
        </div>

        {/* Quick Stats Badges */}
        <div className="flex items-center space-x-3">
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
      <div className="mt-4 flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="relative w-full sm:w-72">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search by name, skill, email..."
            className="w-full pl-9 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:bg-white focus:outline-none transition-all placeholder:text-slate-400"
          />
        </div>

        {/* Score threshold slider */}
        <div className="flex items-center space-x-3 w-full sm:w-auto">
          <span className="text-xs text-slate-500 whitespace-nowrap">
            Min Score: <strong className="text-slate-800">{minScore}%</strong>
          </span>
          <input
            type="range"
            min="0"
            max="90"
            step="5"
            value={minScore}
            onChange={(e) => setMinScore(Number(e.target.value))}
            className="w-32 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
          />
        </div>
      </div>

      {/* Main Ranking Table */}
      <div className="mt-4 overflow-x-auto rounded-xl border border-slate-200">
        <table className="w-full text-left text-xs">
          <thead className="bg-slate-50/80 border-b border-slate-200 text-slate-600 uppercase font-bold tracking-wider text-[11px]">
            <tr>
              <th className="py-3 px-4 w-12 text-center">Rank</th>
              <th
                onClick={() => handleSort('name')}
                className="py-3 px-4 cursor-pointer hover:text-slate-900 transition-colors"
              >
                <div className="flex items-center space-x-1">
                  <span>Candidate</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('experience_years')}
                className="py-3 px-4 cursor-pointer hover:text-slate-900 transition-colors"
              >
                <div className="flex items-center space-x-1">
                  <span>Experience</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th
                onClick={() => handleSort('overall_score')}
                className="py-3 px-4 cursor-pointer hover:text-slate-900 transition-colors"
              >
                <div className="flex items-center space-x-1">
                  <span>Match %</span>
                  <ArrowUpDown className="w-3 h-3 text-slate-400" />
                </div>
              </th>
              <th className="py-3 px-4">Matched Skills</th>
              <th className="py-3 px-4 text-right">Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white">
            {filteredCandidates.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-400">
                  No candidates match the selected filters.
                </td>
              </tr>
            ) : (
              filteredCandidates.map((c) => {
                const badge = getScoreBadge(c.overall_score);
                return (
                  <tr
                    key={c.candidate_id}
                    onClick={() => onSelectCandidate(c)}
                    className="hover:bg-blue-50/40 cursor-pointer transition-colors group"
                  >
                    {/* Rank */}
                    <td className="py-3.5 px-4 text-center">
                      <div className="flex items-center justify-center">
                        {getRankBadge(c.rank)}
                      </div>
                    </td>

                    {/* Candidate */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-8 h-8 rounded-full bg-slate-100 group-hover:bg-blue-100 text-slate-700 group-hover:text-blue-700 flex items-center justify-center font-bold text-xs transition-colors">
                          {c.name.split(' ').map(n => n[0]).join('').slice(0, 2)}
                        </div>
                        <div>
                          <p className="font-bold text-slate-900 group-hover:text-blue-700 transition-colors">
                            {c.name}
                          </p>
                          <p className="text-[10px] text-slate-400">
                            {c.email || c.filename}
                          </p>
                        </div>
                      </div>
                    </td>

                    {/* Experience */}
                    <td className="py-3.5 px-4">
                      <span className="font-semibold text-slate-800">
                        {c.experience_years} years
                      </span>
                    </td>

                    {/* Match Score */}
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2.5">
                        <div className="w-16 bg-slate-100 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-2 rounded-full ${badge.bar}`}
                            style={{ width: `${c.overall_score}%` }}
                          />
                        </div>
                        <span className={`px-2 py-0.5 text-xs font-extrabold rounded-md border ${badge.bg}`}>
                          {c.overall_score}%
                        </span>
                      </div>
                    </td>

                    {/* Matched Skills */}
                    <td className="py-3.5 px-4">
                      <div className="flex flex-wrap gap-1 max-w-xs">
                        {c.matched_skills.slice(0, 3).map((skill) => (
                          <span
                            key={skill}
                            className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-md"
                          >
                            {skill}
                          </span>
                        ))}
                        {c.matched_skills.length > 3 && (
                          <span className="px-1.5 py-0.5 text-[10px] font-semibold text-slate-500 bg-slate-100 rounded-md">
                            +{c.matched_skills.length - 3} more
                          </span>
                        )}
                        {c.matched_skills.length === 0 && (
                          <span className="text-[11px] text-slate-400 italic">None</span>
                        )}
                      </div>
                    </td>

                    {/* Action */}
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectCandidate(c);
                        }}
                        className="inline-flex items-center space-x-1 px-3 py-1 text-xs font-semibold text-blue-600 hover:text-blue-800 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors"
                      >
                        <Eye className="w-3.5 h-3.5" />
                        <span>Analysis</span>
                        <ChevronRight className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>

      <div className="mt-3 text-right">
        <span className="text-[11px] text-slate-400">
          Showing {filteredCandidates.length} of {candidates.length} candidates
        </span>
      </div>
    </div>
  );
}
