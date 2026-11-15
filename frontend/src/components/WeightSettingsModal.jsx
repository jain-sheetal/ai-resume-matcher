import React, { useState } from 'react';
import { X, Sliders, RotateCcw, Check, AlertCircle } from 'lucide-react';

export default function WeightSettingsModal({ weights, onSaveWeights, onClose }) {
  const [localWeights, setLocalWeights] = useState({
    skills: Math.round((weights.skills || 0.40) * 100),
    semantic: Math.round((weights.semantic || 0.35) * 100),
    experience: Math.round((weights.experience || 0.20) * 100),
    education: Math.round((weights.education || 0.05) * 100),
  });

  const total = localWeights.skills + localWeights.semantic + localWeights.experience + localWeights.education;
  const isValid = total === 100;

  const handleReset = () => {
    setLocalWeights({
      skills: 40,
      semantic: 35,
      experience: 20,
      education: 5
    });
  };

  const handleSave = () => {
    if (!isValid) return;
    onSaveWeights({
      skills: localWeights.skills / 100.0,
      semantic: localWeights.semantic / 100.0,
      experience: localWeights.experience / 100.0,
      education: localWeights.education / 100.0,
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-md w-full shadow-2xl border border-slate-200 overflow-hidden animate-in zoom-in-95">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-2">
            <Sliders className="w-5 h-5 text-indigo-600" />
            <h3 className="font-extrabold text-slate-900 text-base">Customize Scoring Weights</h3>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-5">
          <p className="text-xs text-slate-600">
            Tune how the AI calculates candidate match scores according to your hiring priorities. Total weights must sum to 100%.
          </p>

          {/* Skill Weight */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-800 mb-1">
              <span>Technical Skills Overlap</span>
              <span className="text-blue-600">{localWeights.skills}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={localWeights.skills}
              onChange={(e) => setLocalWeights({ ...localWeights, skills: Number(e.target.value) })}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-blue-600"
            />
            <span className="text-[10px] text-slate-400">Strict keyword and taxonomy matching</span>
          </div>

          {/* Semantic Weight */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-800 mb-1">
              <span>Semantic Similarity (Sentence Transformers)</span>
              <span className="text-indigo-600">{localWeights.semantic}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={localWeights.semantic}
              onChange={(e) => setLocalWeights({ ...localWeights, semantic: Number(e.target.value) })}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-indigo-600"
            />
            <span className="text-[10px] text-slate-400">Contextual embedding cosine similarity</span>
          </div>

          {/* Experience Weight */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-800 mb-1">
              <span>Experience & Tenure</span>
              <span className="text-emerald-600">{localWeights.experience}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={localWeights.experience}
              onChange={(e) => setLocalWeights({ ...localWeights, experience: Number(e.target.value) })}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-emerald-600"
            />
            <span className="text-[10px] text-slate-400">Comparison of candidate years vs required years</span>
          </div>

          {/* Education Weight */}
          <div>
            <div className="flex justify-between text-xs font-bold text-slate-800 mb-1">
              <span>Education & Degree</span>
              <span className="text-purple-600">{localWeights.education}%</span>
            </div>
            <input
              type="range"
              min="0"
              max="100"
              step="5"
              value={localWeights.education}
              onChange={(e) => setLocalWeights({ ...localWeights, education: Number(e.target.value) })}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-purple-600"
            />
            <span className="text-[10px] text-slate-400">Degree qualification requirements</span>
          </div>

          {/* Total Validation */}
          <div className={`p-3 rounded-xl flex items-center justify-between text-xs font-bold ${
            isValid ? 'bg-emerald-50 text-emerald-800 border border-emerald-200' : 'bg-red-50 text-red-700 border border-red-200'
          }`}>
            <div className="flex items-center gap-1.5">
              {!isValid && <AlertCircle className="w-4 h-4 flex-shrink-0" />}
              <span>Total Weight:</span>
            </div>
            <span>{total}% {isValid ? '(Valid)' : '(Must equal 100%)'}</span>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <button
            onClick={handleReset}
            className="flex items-center space-x-1 text-xs font-semibold text-slate-500 hover:text-slate-800"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>
          <div className="flex items-center space-x-2">
            <button
              onClick={onClose}
              className="px-3 py-1.5 text-xs font-semibold text-slate-600 hover:bg-slate-200/60 rounded-xl transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={!isValid}
              className="px-4 py-1.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white text-xs font-bold rounded-xl transition-all shadow-sm"
            >
              Apply Weights
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
