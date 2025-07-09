from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import shutil
import os
import subprocess
from analyze import analyze_posture, analyze_image_posture





app = FastAPI()

# ✅ CORS: Allow React frontend (adjust origin if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 📁 Create required folders
os.makedirs("videos", exist_ok=True)
os.makedirs("annotated", exist_ok=True)

# 🖼️ Serve annotated media
app.mount("/annotated", StaticFiles(directory="annotated"), name="annotated")

# 🔄 Convert webm to mp4 using FFmpeg
def convert_webm_to_mp4(input_path, output_path):
    try:
        command = [
            "ffmpeg", "-i", input_path,
            "-c:v", "libx264", "-crf", "23", "-preset", "veryfast",
            output_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print(f"🎥 Converted: {input_path} ➝ {output_path}")
    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg conversion failed:", e)

# 📤 Upload and Analyze Endpoint
@app.post("/upload/")
async def upload_and_analyze(file: UploadFile = File(...)):
    try:
        filename = file.filename
        ext = filename.lower().split('.')[-1]
        allowed_exts = ["mp4", "webm", "jpg", "jpeg", "png", "avi", "mov"]
        if ext not in allowed_exts:
            raise ValueError(f"Unsupported file type: .{ext}")

        # 📥 Save file to disk
        input_path = os.path.join("videos", filename)
        with open(input_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved: {input_path}")

        # 🔄 Convert if .webm
        if ext == "webm":
            converted_path = input_path.replace(".webm", ".mp4")
            convert_webm_to_mp4(input_path, converted_path)
            input_path = converted_path

        # 🔍 Analyze posture
        if ext in ["jpg", "jpeg", "png"]:
            result = analyze_image_posture(input_path)
        else:
            result = analyze_posture(input_path)

        print(f"📊 Analysis complete: {len(result['results'])} results")

        return {
            "filename": filename,
            "status": "Analyzed successfully",
            "results": result.get("results", []),
            "summary": result.get("summary", []),
            "annotated_image": result.get("annotated_image"),
            "annotated_video": result.get("annotated_video")
        }

    except Exception as e:
        print("❌ Analysis failed:", str(e))
        return {
            "filename": file.filename if file else "unknown",
            "status": "Failed to analyze",
            "results": [{"frame": 0, "message": str(e), "good": False}],
            "summary": [],
            "annotated_image": None,
            "annotated_video": None
        }
