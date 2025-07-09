import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import jsPDF from 'jspdf';
import './App.css';

function App() {
  const [mode, setMode] = useState('upload');
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [summary, setSummary] = useState([]);
  const [annotatedMediaUrl, setAnnotatedMediaUrl] = useState(null);
  const [isVideoResult, setIsVideoResult] = useState(false);
  const webcamRef = useRef(null);

  const handleFileChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setSummary([]);
    setAnnotatedMediaUrl(null);
  };

  const handleCaptureSnapshot = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    const byteString = atob(imageSrc.split(',')[1]);
    const mimeString = imageSrc.split(',')[0].split(':')[1].split(';')[0];
    const ab = new ArrayBuffer(byteString.length);
    const ia = new Uint8Array(ab);
    for (let i = 0; i < byteString.length; i++) {
      ia[i] = byteString.charCodeAt(i);
    }
    const blob = new Blob([ab], { type: mimeString });
    const imageFile = new File([blob], 'snapshot.png', { type: mimeString });

    setFile(imageFile);
    setSummary([]);
    setAnnotatedMediaUrl(null);
  };

  const handleToggleMode = () => {
    setMode((prev) => (prev === 'upload' ? 'snapshot' : 'upload'));
    setFile(null);
    setSummary([]);
    setAnnotatedMediaUrl(null);
  };

  const handleAnalyzePosture = async () => {
    if (!file) {
      alert("Please select a file or take a snapshot.");
      return;
    }

    setIsLoading(true);
    setSummary([]);
    setAnnotatedMediaUrl(null);
    setIsVideoResult(false);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setSummary(data.summary || []);

      if (data.annotated_image) {
        setAnnotatedMediaUrl(`http://127.0.0.1:8000/${data.annotated_image}`);
        setIsVideoResult(false);
      } else if (data.annotated_video) {
        setAnnotatedMediaUrl(`http://127.0.0.1:8000/${data.annotated_video}`);
        setIsVideoResult(true);
      } else {
        setAnnotatedMediaUrl(null);
      }
    } catch (error) {
      console.error("❌ Error analyzing:", error);
      setSummary(["❌ Upload or analysis failed."]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPDF = () => {
    const doc = new jsPDF();
    doc.setFontSize(16);
    doc.text("📋 Posture Detection Summary", 20, 20);

    doc.setFontSize(12);
    let y = 35;
    summary.forEach((item) => {
      doc.text(`• ${item}`, 20, y);
      y += 10;
      if (y > 270) {
        doc.addPage();
        y = 20;
      }
    });

    doc.save("posture_report.pdf");
  };

  return (
    <div className="app-wrapper" data-theme="light">
      <header>
        <div className="brand">
          <img src="/verter_logo.png" alt="Vertero Logo" className="logo" /> Vertero
        </div>
      </header>

      <main className="main-content">
        <h1>Your Daily Guide to Better Posture</h1>

        <div className="card">
          <button onClick={handleToggleMode} className="mode-btn">
            Switch to {mode === 'upload' ? 'Snapshot Mode' : 'Upload Mode'}
          </button>

          {mode === 'upload' ? (
            <div className="upload-container">
              <input type="file" accept="video/*,image/*" onChange={handleFileChange} />
              {file && file.type?.startsWith('video') && (
                <video width="100%" height="auto" controls className="video-preview">
                  <source src={URL.createObjectURL(file)} />
                </video>
              )}
              {file && file.type?.startsWith('image') && (
                <img
                  src={URL.createObjectURL(file)}
                  alt="Uploaded Preview"
                  style={{ width: "100%", maxWidth: 640, marginTop: 10 }}
                />
              )}
            </div>
          ) : (
            <div className="snapshot-container">
              <Webcam
                ref={webcamRef}
                audio={false}
                screenshotFormat="image/png"
                videoConstraints={{ facingMode: 'user' }}
                mirrored
                style={{ width: "100%", maxWidth: 640 }}
              />
              <button onClick={handleCaptureSnapshot} className="snapshot-btn">
                📸 Capture Snapshot
              </button>

              {file && (
                <img
                  src={URL.createObjectURL(file)}
                  alt="Snapshot Preview"
                  style={{ width: "100%", maxWidth: 640, marginTop: 10 }}
                />
              )}
            </div>
          )}

          <button onClick={handleAnalyzePosture} className="analyze-btn" disabled={!file}>
            Analyze Posture
          </button>

          {isLoading && (
            <div className="loading">
              Analyzing posture <span className="spinner" />
            </div>
          )}

          {annotatedMediaUrl && (
            <div style={{ marginTop: "20px", textAlign: "center" }}>
              <h3>📌 Annotated Posture</h3>
              {isVideoResult ? (
                <video
                  src={annotatedMediaUrl}
                  controls
                  style={{ width: "100%", maxWidth: 640, borderRadius: 8, border: "2px solid #ccc" }}
                />
              ) : (
                <img
                  src={annotatedMediaUrl}
                  alt="Annotated Posture Result"
                  style={{ width: "100%", maxWidth: 640, borderRadius: 8, border: "2px solid #ccc" }}
                />
              )}
            </div>
          )}

          {summary.length > 0 && (
            <>
              <div className="results summary">
                <h3>📝 Summary Insights</h3>
                <ul>
                  {summary.map((s, idx) => (
                    <li key={idx}>
                      {s.startsWith("✅") ? (
                        <span className="good-posture">{s}</span>
                      ) : (
                        `🕒 ${s}`
                      )}
                    </li>
                  ))}
                </ul>
              </div>

              <div className="download-btn-wrapper">
                <button className="download-btn" onClick={handleDownloadPDF}>
                  ⬇️ Download Report (PDF)
                </button>
              </div>
            </>
          )}
        </div>
      </main>

      <div className="tip-box">
        <span className="tip-icon">ℹ️</span>
        <strong>Tips:</strong> Make sure your full body is visible
      </div>

      <footer>
        <p>
          Vertero helps detect poor posture using rule-based logic and computer vision.
          Built for healthy habits at work, gym or home. Maintain your spine, maintain your shine!
        </p>
      </footer>
    </div>
  );
}

export default App;
