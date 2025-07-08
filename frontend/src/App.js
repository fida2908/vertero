import React, { useState, useRef } from 'react';
import Webcam from 'react-webcam';
import './App.css';

function App() {
  const [mode, setMode] = useState('webcam'); // 'webcam' or 'upload'
  const [videoFile, setVideoFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [results, setResults] = useState([]);
  const webcamRef = useRef(null);

  const handleFileChange = (e) => {
    setVideoFile(e.target.files[0]);
    setResults([]);
  };

  const handleToggleMode = () => {
    setMode((prev) => (prev === 'webcam' ? 'upload' : 'webcam'));
    setVideoFile(null);
    setResults([]);
  };

  const handleAnalyzePosture = async () => {
    setIsLoading(true);
    setResults([]);

    try {
      const formData = new FormData();

      if (mode === 'upload' && videoFile) {
        // Case: user uploads a video file
        formData.append("file", videoFile);
      } else if (mode === 'webcam' && webcamRef.current) {
        // Case: capture webcam screenshot
        const screenshot = webcamRef.current.getScreenshot();

        if (!screenshot) {
          alert("Unable to capture webcam image.");
          setIsLoading(false);
          return;
        }

        const blob = await fetch(screenshot).then(res => res.blob());
        const file = new File([blob], "webcam.jpg", { type: "image/jpeg" });
        formData.append("file", file);
      } else {
        alert("No input provided.");
        setIsLoading(false);
        return;
      }

      // Send to FastAPI backend
      const response = await fetch("http://127.0.0.1:8000/upload/", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error("Upload failed");
      }

      const data = await response.json();

      // Use actual analysis result if returned
      if (data.results) {
        setResults(data.results);
      } else {
        setResults([
          { frame: 1, message: `Uploaded: ${data.filename}`, good: true }
        ]);
      }
    } catch (error) {
      console.error("Error uploading or analyzing file:", error);
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
          Switch to {mode === 'webcam' ? 'Upload Mode' : 'Webcam Mode'}
        </button>

        <div className="card">
          {mode === 'webcam' ? (
            <div className="video-container">
              <Webcam
                ref={webcamRef}
                width={640}
                height={480}
                className="webcam-preview"
                videoConstraints={{ facingMode: 'user' }}
              />
            </div>
          ) : (
            <div className="upload-container">
              <input type="file" accept="video/*" onChange={handleFileChange} />
              {videoFile && (
                <video width="640" height="480" controls className="video-preview">
                  <source src={URL.createObjectURL(videoFile)} type="video/mp4" />
                  Your browser does not support the video tag.
                </video>
              )}
            </div>
          )}

          <button onClick={handleAnalyzePosture} className="analyze-btn">
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
