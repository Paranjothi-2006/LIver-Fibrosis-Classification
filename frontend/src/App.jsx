import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [patient, setPatient] = useState({
    name: 'Jothi',
    patient_id: 'P10023',
    age: 25,
    gender: 'Male'
  });

  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const stageDetails = {
    'F0': { title: 'F0: Normal Parenchyma', severity: 'Healthy', desc: 'No histologic evidence of liver fibrosis. Normal ultrasound echogenicity.', color: '#16A34A', bg: '#F0FDF4' },
    'F1': { title: 'F1: Mild Fibrosis', severity: 'Mild', desc: 'Slight periportal fibrosis expansion without septa formation.', color: '#0284C7', bg: '#F0F9FF' },
    'F2': { title: 'F2: Moderate Fibrosis', severity: 'Moderate', desc: 'Periportal fibrosis with rare portal-to-portal septa.', color: '#CA8A04', bg: '#FEFCE8' },
    'F3': { title: 'F3: Severe Fibrosis', severity: 'Severe', desc: 'Bridging fibrosis with numerous septa distorting hepatic architecture.', color: '#EA580C', bg: '#FFF7ED' },
    'F4': { title: 'F4: Cirrhosis', severity: 'Critical', desc: 'Advanced nodular transformation with established fibrous bands.', color: '#DC2626', bg: '#FEF2F2' }
  };

  const handleInputChange = (e) => {
    setPatient({ ...patient, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!selectedFile) {
      alert("Please select or upload a valid B-mode liver ultrasound scan.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('name', patient.name);
    formData.append('patient_id', patient.patient_id);
    formData.append('age', patient.age);
    formData.append('gender', patient.gender);

    try {
      const response = await axios.post('http://localhost:8000/api/predict', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(response.data);
    } catch (error) {
      console.error("Diagnostic execution error:", error);
      alert("Backend service unavailable. Ensure FastAPI server is active on port 8000.");
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    if (result && result.report_filename) {
      window.open(`http://localhost:8000/api/download-report/${result.report_filename}`, '_blank');
    }
  };

  const currentStage = result ? stageDetails[result.predicted_stage] || stageDetails['F0'] : null;

  return (
    <div className="clinical-app">
      {/* Hospital Workstation Top Header */}
      <header className="hospital-header">
        <div className="header-brand">
          <div className="brand-logo-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
          </div>
          <div>
            <h1 className="brand-title">Hepatology Workstation</h1>
            <p className="brand-subtitle">AI-Assisted B-Mode Ultrasound Liver Fibrosis Staging</p>
          </div>
        </div>

        <div className="header-meta">
          <div className="meta-item">
            <span className="meta-label">Department</span>
            <span className="meta-value">Radiology & Hepatology</span>
          </div>
          <div className="meta-divider"></div>
          <div className="meta-item">
            <span className="meta-label">Neural Engine</span>
            <span className="meta-value status-online">
              <span className="status-indicator"></span> MobileNetV3-Large + ViT Active
            </span>
          </div>
        </div>
      </header>

      {/* Main Clinical Grid */}
      <main className="clinical-layout">
        {/* Left Workflow Panel: Patient Demographics & Image Ingestion */}
        <aside className="panel panel-left">
          <div className="panel-header">
            <span className="panel-step">01</span>
            <h2>Patient Registration & Scan Ingestion</h2>
          </div>

          <form onSubmit={handleSubmit} className="clinical-form">
            <div className="form-section">
              <span className="section-title">Demographic Records</span>
              
              <div className="field-group">
                <label htmlFor="name">Patient Full Name</label>
                <input 
                  type="text" 
                  id="name"
                  name="name" 
                  value={patient.name} 
                  onChange={handleInputChange} 
                  placeholder="e.g. Paranjothi P" 
                  required 
                />
              </div>

              <div className="field-group">
                <label htmlFor="patient_id">Medical Record Number (PID)</label>
                <input 
                  type="text" 
                  id="patient_id"
                  name="patient_id" 
                  value={patient.patient_id} 
                  onChange={handleInputChange} 
                  placeholder="e.g. P10023" 
                  required 
                />
              </div>

              <div className="field-grid-2">
                <div className="field-group">
                  <label htmlFor="age">Age (Yrs)</label>
                  <input 
                    type="number" 
                    id="age"
                    name="age" 
                    value={patient.age} 
                    onChange={handleInputChange} 
                    min="1" 
                    max="110" 
                    required 
                  />
                </div>

                <div className="field-group">
                  <label htmlFor="gender">Gender</label>
                  <select id="gender" name="gender" value={patient.gender} onChange={handleInputChange}>
                    <option value="Male">Male</option>
                    <option value="Female">Female</option>
                    <option value="Other">Other</option>
                  </select>
                </div>
              </div>
            </div>

            <div className="form-section">
              <span className="section-title">Scan Acquisition</span>
              
              <div className="upload-box">
                <input type="file" id="ultrasound-file" accept="image/*" onChange={handleFileChange} />
                <label htmlFor="ultrasound-file" className="upload-label">
                  <div className="upload-icon-wrapper">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                      <polyline points="17 8 12 3 7 8"/>
                      <line x1="12" y1="3" x2="12" y2="15"/>
                    </svg>
                  </div>
                  <div className="upload-text">
                    <span className="upload-primary">{selectedFile ? selectedFile.name : "Select Ultrasound DICOM / Image"}</span>
                    <span className="upload-secondary">Click or drag scan file here (JPG, PNG)</span>
                  </div>
                </label>
              </div>

              {previewUrl && (
                <div className="preview-container">
                  <div className="preview-header">
                    <span>Input Ultrasound Ingested</span>
                    <span className="file-size">{selectedFile?.size ? `${(selectedFile.size / 1024).toFixed(1)} KB` : ''}</span>
                  </div>
                  <div className="preview-viewport">
                    <img src={previewUrl} alt="Ingested Ultrasound Scan" />
                  </div>
                </div>
              )}
            </div>

            <button type="submit" className="btn-submit" disabled={loading}>
              {loading ? (
                <span className="btn-loading">
                  <span className="clinical-spinner"></span> Running Deep Neural Assessment...
                </span>
              ) : (
                "Run Diagnostic Evaluation"
              )}
            </button>
          </form>
        </aside>

        {/* Right Panel: Diagnostic Results & Explainable AI */}
        <section className="panel panel-right">
          <div className="panel-header">
            <span className="panel-step">02</span>
            <h2>Clinical Assessment & XAI Localization</h2>
          </div>

          {result ? (
            <div className="assessment-results">
              {/* Primary Assessment Summary Card */}
              <div className="summary-card" style={{ backgroundColor: currentStage.bg, borderColor: `${currentStage.color}40` }}>
                <div className="summary-main">
                  <div className="stage-pill" style={{ backgroundColor: currentStage.color }}>
                    {result.predicted_stage} Classification
                  </div>
                  <h3 className="stage-title" style={{ color: currentStage.color }}>{currentStage.title}</h3>
                  <p className="stage-description">{currentStage.desc}</p>
                </div>

                <div className="confidence-box">
                  <span className="confidence-num" style={{ color: currentStage.color }}>{result.confidence.toFixed(1)}%</span>
                  <span className="confidence-sub">Diagnostic Certainty</span>
                </div>
              </div>

              {/* Side-by-Side Dual Viewport */}
              <div className="viewport-grid">
                <div className="viewport-card">
                  <div className="viewport-top">
                    <span className="viewport-title">Raw B-Mode Ultrasound</span>
                    <span className="viewport-tag">Acoustic Input</span>
                  </div>
                  <div className="image-frame">
                    <img src={previewUrl} alt="Original Clinical Ultrasound" />
                  </div>
                </div>

                <div className="viewport-card">
                  <div className="viewport-top">
                    <span className="viewport-title">Grad-CAM XAI Heatmap</span>
                    <span className="viewport-tag tag-xai">Feature Attention Overlay</span>
                  </div>
                  <div className="image-frame">
                    <img src={result.overlay_image} alt="Explainable AI Attention Overlay" />
                  </div>
                </div>
              </div>

              {/* Stage Probability Distribution Table & Progress */}
              <div className="distribution-card">
                <div className="distribution-header">
                  <h4>Multiclass Probability Distribution (METAVIR Scale)</h4>
                  <span className="scale-info">F0 (No Fibrosis) $\rightarrow$ F4 (Cirrhosis)</span>
                </div>

                <div className="distribution-list">
                  {Object.entries(result.probabilities).map(([stage, prob]) => {
                    const stageMeta = stageDetails[stage];
                    const isSelected = stage === result.predicted_stage;

                    return (
                      <div key={stage} className={`dist-item ${isSelected ? 'selected-stage' : ''}`}>
                        <div className="dist-meta">
                          <span className="dist-code" style={{ color: stageMeta.color }}>{stage}</span>
                          <span className="dist-name">{stageMeta.severity} Stage</span>
                          <span className="dist-percent">{prob.toFixed(2)}%</span>
                        </div>
                        <div className="progress-track">
                          <div 
                            className="progress-fill" 
                            style={{ 
                              width: `${prob}%`, 
                              backgroundColor: stageMeta.color 
                            }}
                          ></div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Action Toolbar */}
              <div className="action-toolbar">
                <div className="clinical-disclaimer">
                  * Generated assessment is intended for clinical decision support and radiologist verification.
                </div>
                <button onClick={handleDownloadPDF} className="btn-pdf-download">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                    <polyline points="14 2 14 8 20 8"/>
                    <line x1="12" y1="18" x2="12" y2="12"/>
                    <polyline points="9 15 12 18 15 15"/>
                  </svg>
                  Export Diagnostic PDF Report
                </button>
              </div>
            </div>
          ) : (
            <div className="empty-workstation">
              <div className="empty-illustration">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" strokeWidth="1.5">
                  <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
                </svg>
              </div>
              <h3>Awaiting Scan Input</h3>
              <p>Complete patient demographics on the left panel and ingest a B-mode ultrasound scan to generate stage classification and feature localization maps.</p>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;