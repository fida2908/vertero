import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import './App.css';

function App() {
  const [mode, setMode] = useState('upload'); // 'upload' or 'snapshot'
  const [file, setFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
  const webcamRef = useRef(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setResults([]);
  };

  const handleCaptureSnapshot = () => {
    const imageSrc = webcamRef.current.getScreenshot();
    if (!imageSrc) return;

    // Convert base64 to Blob
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
    setResults([]);
  };

  const handleToggleMode = () => {
    setMode((prev) => (prev === 'upload' ? 'snapshot' : 'upload'));
    setFile(null);
    setResults([]);
  };

  const handleAnalyzePosture = async () => {
    if (!file) {
      alert("Please select a file or take a snapshot.");
      return;
    }

    setIsLoading(true);
    setResults([]);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      setResults(data.results || [{ frame: 0, message: "No results", good: false }]);
    } catch (error) {
      console.error("Error uploading or analyzing:", error);
      setResults([{ frame: 0, message: "Upload failed", good: false }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-wrapper" data-theme="light">
      <header>
        <div className="brand">
          <img src="/logo192.png" alt="logo" className="logo" /> Vertero
        </div>
      </header>

      <main className="main-content">
        <h1>Posture Detection App</h1>
        <button onClick={handleToggleMode} className="mode-btn">
          Switch to {mode === 'upload' ? 'Snapshot Mode' : 'Upload Mode'}
        </button>

        <div className="card">
          {mode === 'upload' ? (
            <div className="upload-container">
              <input type="file" accept="video/*,image/*" onChange={handleFileChange} />
              {file && file.type.startsWith('video') && (
                <video width="640" height="480" controls className="video-preview">
                  <source src={URL.createObjectURL(file)} />
                </video>
              )}
              {file && file.type.startsWith('image') && (
                <img src={URL.createObjectURL(file)} alt="Snapshot" style={{ width: "100%", maxWidth: 640, marginTop: 10 }} />
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
              <button onClick={handleCaptureSnapshot} style={{ marginTop: "10px" }}>
                Capture Snapshot
              </button>
              {file && (
                <img src={URL.createObjectURL(file)} alt="Captured" style={{ width: "100%", maxWidth: 640, marginTop: 10 }} />
              )}
            </div>
          )}

          <button onClick={handleAnalyzePosture} className="analyze-btn" disabled={!file}>
            Analyze Posture
          </button>

          {isLoading && <div className="loading">Analyzing posture...</div>}

          {results.length > 0 && (
            <div className="results">
              <h3>Posture Analysis Results</h3>
              <ul>
                {results.map((r, index) => (
                  <li key={index} className={r.good ? 'good' : 'bad'}>
                    {r.good ? '✅' : '❌'} Frame {r.frame} – {r.message}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </main>

      <footer>
        <p>
          Vertero helps detect poor posture using rule-based logic and computer vision.
          Built for healthy habits at work, gym, or home. Maintain your spine, maintain your shine!
        </p>
      </footer>
    </div>
  );
}

export default App;
