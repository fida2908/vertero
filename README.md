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
```
---
### Backend (FastAPI + Python)
Inside /backend folder:
```bash
cd backend
pip install -r requirements.txt
```
Start server:
```bash
uvicorn main:app --reload
```

Server will run at: http://127.0.0.1:8000

---
### 🌐 Frontend (React)
Inside /frontend folder:

```bash
cd frontend
npm install
```

Create .env file:
REACT_APP_API_URL=http://127.0.0.1:8000


Start frontend
```bash
npm start
```

React app will run at http://localhost:3000

---
### 📸 Screenshots

<img width="967" height="978" alt="Screenshot 2025-07-10 190715" src="https://github.com/user-attachments/assets/7f3ce371-1ae3-4e9b-93e4-94cbba455ce8" />


<img width="1869" height="895" alt="Screenshot 2025-07-10 190830" src="https://github.com/user-attachments/assets/d7cfdc93-e40b-4e83-94ad-59f82cbef7be" />


<img width="942" height="804" alt="Screenshot 2025-07-10 190737" src="https://github.com/user-attachments/assets/c4a365dc-3cf9-46aa-bec6-b9899055ad03" />

<img width="6" height="21" alt="Screenshot 2025-07-10 190655" src="https://github.com/user-attachments/assets/73573956-f59c-4c99-9a84-a1d2ddd97234" />


---
### Demo Video

https://github.com/fida2908/vertero/assets/demo.mp4

---
### 📁 Folder Structure
📁 backend/
   ├── main.py
   ├── analyze.py
   ├── annotated/         # Annotated outputs
   └── videos/         # Uploaded input videos

📁 frontend/
   ├── src/
   │   ├── App.js
   │   ├── App.css
   │   └── assets/
   └── public/

---
### 🙌 Team / Credits
Developed by:
Fida K A
