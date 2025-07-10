# 🧍‍♂️ Vertero - Posture Detection System

> A real-time posture assessment tool using computer vision (MediaPipe + OpenCV), FastAPI backend, and a React.js frontend. Supports video/image uploads, snapshots, and live webcam recording.

---

## 🚀 Features

- 🎥 Upload, snapshot, or record posture input  
- 🤖 Detects posture types: **Squat** and **Desk Sitting**  
- ✅ Summarizes key insights from posture  
- 🖼️ Annotated output (image/video) with visual feedback  
- 📄 Export feedback as a downloadable PDF report  
- 🔁 Real-time web-based interface  

---

## 🧩 Tech Stack

### Frontend (React.js)
- React Webcam  
- jsPDF   
- Fetch API (POST upload)  

### Backend (FastAPI)
- Python 3.9+ 
- OpenCV  
- MediaPipe  
- FFmpeg (for webm to mp4 conversion)  

---

## 🛠️ Setup Instructions

### ✅ Clone the Repository
```bash
git clone https://github.com/fida2908/vertero.git
cd vertero
