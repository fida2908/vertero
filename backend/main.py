from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import subprocess
from analyze import analyze_posture, analyze_image_posture

app = FastAPI()

# ✅ Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🎥 Convert .webm to .mp4 for OpenCV support
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
        os.makedirs("videos", exist_ok=True)
        filename = file.filename
        ext = filename.lower().split('.')[-1]

        # ✅ Supported file types
        valid_exts = ["mp4", "webm", "jpg", "jpeg", "png", "avi", "mov"]
        if ext not in valid_exts:
            raise ValueError(f"Unsupported file type: .{ext}")

        # 🔽 Save the uploaded file
        file_path = os.path.join("videos", filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        print(f"✅ File saved to: {file_path}")

        # 🔁 Convert if webm
        if ext == "webm":
            mp4_path = file_path.replace(".webm", ".mp4")
            convert_webm_to_mp4(file_path, mp4_path)
            file_path = mp4_path

        # 🔍 Analyze
        if ext in ["jpg", "jpeg", "png"]:
            result = analyze_image_posture(file_path)
        else:
            result = analyze_posture(file_path)

        print(f"✅ {filename}: {len(result['results'])} results, {len(result['summary'])} insights")

        return {
            "filename": filename,
            "status": "Analyzed successfully",
            "results": result["results"],
            "summary": result["summary"]
        }

    except Exception as e:
        print("❌ Error during upload or analysis:", e)
        return {
            "filename": file.filename if file else "unknown",
            "status": "Failed to analyze",
            "results": [{"frame": 0, "message": str(e), "good": False}],
            "summary": []
        }
