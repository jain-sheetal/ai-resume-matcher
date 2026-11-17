import React from 'react';
import { X, BookOpen, Cpu, Sparkles, Layers, CheckCircle2 } from 'lucide-react';

export default function DocsModal({ onClose }) {
  return (
    <div className="fixed inset-0 z-50 overflow-hidden bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] shadow-2xl border border-slate-200 overflow-hidden flex flex-col animate-in zoom-in-95">
        {/* Header */}
        <div className="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50">
          <div className="flex items-center space-x-2">
            <BookOpen className="w-5 h-5 text-blue-600" />
            <h3 className="font-extrabold text-slate-900 text-base">
              Matching Algorithm & Technical Architecture
            </h3>
          </div>
          <button onClick={onClose} className="p-1.5 text-slate-400 hover:text-slate-700 rounded-lg">
            <X className="w-4 h-4" />
          </button>
        </div>

        {/* Scrollable Content */}
        <div className="p-6 overflow-y-auto space-y-5 text-xs text-slate-700 leading-relaxed">
          <div>
            <h4 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-1.5">
              <Cpu className="w-4 h-4 text-blue-600" />
              1. Semantic Embedding Engine (Sentence Transformers)
            </h4>
            <p>
              Unlike legacy systems relying strictly on literal keyword matching, MatchPro AI uses <strong>all-MiniLM-L6-v2</strong> from the Sentence Transformers library. It maps the Job Description context and candidate resumes into a 384-dimensional dense vector space, computing semantic cosine similarity:
            </p>
            <div className="my-2 p-2.5 bg-slate-100 rounded-lg font-mono text-[11px] text-slate-800">
              Cosine Similarity = (A · B) / (||A|| · ||B||)
            </div>
            <p>
              This accurately rewards transferable knowledge (e.g. recognizing that experience in <em>"FastAPI microservices and RESTful API design"</em> semantically maps to <em>"Backend Python Engineer"</em> even if exact wording varies).
            </p>
          </div>

          <div>
            <h4 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-1.5">
              <Layers className="w-4 h-4 text-indigo-600" />
              2. Skill Ontology & Synonym Taxonomy
            </h4>
            <p>
              The system maintains a comprehensive canonical taxonomy of over 250+ tech skills with alias mappings:
            </p>
            <ul className="list-disc pl-5 mt-1 space-y-0.5 text-slate-600">
              <li><code>React.js</code>, <code>reactjs</code> &rarr; <strong>React</strong></li>
              <li><code>Postgres</code>, <code>pgsql</code> &rarr; <strong>PostgreSQL</strong></li>
              <li><code>K8s</code> &rarr; <strong>Kubernetes</strong></li>
              <li><code>Amazon Web Services</code> &rarr; <strong>AWS</strong></li>
            </ul>
          </div>

          <div>
            <h4 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-1.5">
              <Sparkles className="w-4 h-4 text-emerald-600" />
              3. Multi-Criteria Composite Evaluation
            </h4>
            <div className="p-3 bg-blue-50/70 border border-blue-200 rounded-xl font-mono text-xs text-blue-900 font-bold">
              Overall Score = Composite(Technical Skills, Semantic Embedding, Experience Duration, Education)
            </div>
            <div className="grid grid-cols-2 gap-2 mt-2">
              <div className="p-2 bg-slate-50 border rounded-lg">
                <strong>Technical Skills:</strong> Matched skills vs Required skills with bonus for additional versatility.
              </div>
              <div className="p-2 bg-slate-50 border rounded-lg">
                <strong>Semantic Similarity:</strong> Dense contextual embedding similarity (0-100%).
              </div>
              <div className="p-2 bg-slate-50 border rounded-lg">
                <strong>Experience:</strong> Chronological tenure vs JD minimum requirement.
              </div>
              <div className="p-2 bg-slate-50 border rounded-lg">
                <strong>Education:</strong> Academic degree level qualification baseline.
              </div>
            </div>
          </div>

          <div>
            <h4 className="font-bold text-sm text-slate-900 mb-1 flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-purple-600" />
              4. Explainable AI (XAI)
            </h4>
            <p>
              Every candidate ranking is backed by clear, human-understandable justifications:
              explicit tenure delta, matched vs missing skill lists, and contextual domain alignment summaries.
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-slate-50 border-t border-slate-100 text-right">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-slate-900 hover:bg-slate-800 text-white text-xs font-semibold rounded-xl"
          >
            Got It
          </button>
        </div>
      </div>
    </div>
  );
}
