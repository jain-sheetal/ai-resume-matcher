const API_BASE = '/api';

export const api = {
  // Job Description endpoints
  async getSampleJds() {
    const res = await fetch(`${API_BASE}/jd/samples`);
    if (!res.ok) throw new Error('Failed to load sample job descriptions');
    return res.json();
  },

  async parseJd(payload) {
    const res = await fetch(`${API_BASE}/jd/parse`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to parse JD' }));
      throw new Error(err.detail || 'Failed to parse JD');
    }
    return res.json();
  },

  async uploadJdFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${API_BASE}/jd/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to upload JD file' }));
      throw new Error(err.detail || 'Failed to upload JD file');
    }
    return res.json();
  },

  // Resume endpoints
  async uploadResumes(files) {
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }
    const res = await fetch(`${API_BASE}/resumes/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to process resumes' }));
      throw new Error(err.detail || 'Failed to process resumes');
    }
    return res.json();
  },

  async getSampleResumes() {
    const res = await fetch(`${API_BASE}/resumes/samples`);
    if (!res.ok) throw new Error('Failed to load sample resumes');
    return res.json();
  },

  // Match and Rank
  async evaluateCandidates(payload) {
    const res = await fetch(`${API_BASE}/match/evaluate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: 'Failed to evaluate candidates' }));
      throw new Error(err.detail || 'Failed to evaluate candidates');
    }
    return res.json();
  },

  async exportCsv(payload) {
    const res = await fetch(`${API_BASE}/match/export-csv`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error('Failed to export CSV');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Candidate_Rankings_${new Date().toISOString().slice(0, 10)}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  }
};
