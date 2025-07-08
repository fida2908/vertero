from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import subprocess

from analyze import analyze_posture, analyze_image_posture  # 🆕 Import new function

app = FastAPI()

# ✅ Allow frontend requests (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Optional: Convert .webm to .mp4 for OpenCV compatibility
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

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    try:
        os.makedirs("videos", exist_ok=True)
        file_path = f"videos/{file.filename}"

        # 🔽 Save uploaded file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        print(f"✅ File saved to: {file_path}")

        # ✅ Validate file extension
        ext = file_path.lower()
        if not ext.endswith((".mp4", ".webm", ".jpg", ".jpeg", ".png", ".avi", ".mov")):
            raise ValueError("Unsupported file type")

        # 🔁 Convert .webm to .mp4 for OpenCV
        if ext.endswith(".webm"):
            mp4_path = file_path.replace(".webm", ".mp4")
            convert_webm_to_mp4(file_path, mp4_path)
            file_path = mp4_path

        # 🧠 Run the correct analysis function
        if ext.endswith((".jpg", ".jpeg", ".png")):
            results = analyze_image_posture(file_path)  # 🆕 Analyze image
        else:
            results = analyze_posture(file_path)  # ✅ Analyze video

        print(f"✅ Analysis results: {results}")

        return {
            "filename": file.filename,
            "status": "Analyzed successfully",
            "results": results
        }

    except Exception as e:
        print("❌ Error in /upload/:", e)
        return {
            "filename": file.filename if file else "unknown",
            "status": "Failed to analyze",
            "results": [
                {"frame": 0, "message": str(e) or "Upload failed", "good": False}
            ]
        }
