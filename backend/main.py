from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import subprocess
from analyze import analyze_posture, analyze_image_posture

app = FastAPI()

# ✅ Enable CORS for frontend (React dev server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Ensure folders exist
os.makedirs("videos", exist_ok=True)
os.makedirs("annotated", exist_ok=True)

# 🖼️ Serve annotated images as static files
app.mount("/annotated", StaticFiles(directory="annotated"), name="annotated")

# 🎥 WebM to MP4 (for OpenCV compatibility)
def convert_webm_to_mp4(input_path, output_path):
    try:
        command = [
            "ffmpeg", "-i", input_path,
            "-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
            output_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"🎥 Converted {input_path} to {output_path}")
    except Exception as e:
        print("❌ FFmpeg conversion error:", e)

# 📤 Upload endpoint
@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        filename = file.filename
        ext = filename.lower().split('.')[-1]
        valid_exts = ["mp4", "webm", "jpg", "jpeg", "png", "avi", "mov"]
        if ext not in valid_exts:
            raise ValueError(f"Unsupported file type: .{ext}")

        # 📝 Save uploaded file
        file_path = os.path.join("videos", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved to: {file_path}")

        # 🔄 Convert webm
        if ext == "webm":
            mp4_path = file_path.replace(".webm", ".mp4")
            convert_webm_to_mp4(file_path, mp4_path)
            file_path = mp4_path

        # 🧠 Analyze posture
        if ext in ["jpg", "jpeg", "png"]:
            result = analyze_image_posture(file_path)
        else:
            result = analyze_posture(file_path)

        print(f"✅ Analyzed {filename}: {len(result['results'])} results, {len(result['summary'])} insights")

        # 📦 Return results + annotated image path
        return {
            "filename": filename,
            "status": "Analyzed successfully",
            "results": result["results"],
            "summary": result["summary"],
            "annotated_image": result.get("annotated_image")  # 🔗 Relative static URL
        }

    except Exception as e:
        print("❌ Error during upload or analysis:", e)
        return {
            "filename": file.filename if file else "unknown",
            "status": "Failed to analyze",
            "results": [{"frame": 0, "message": str(e), "good": False}],
            "summary": [],
            "annotated_image": None
        }
