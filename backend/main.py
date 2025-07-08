from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os

from analyze import analyze_posture  # 👈 Import your analyzer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_video(file: UploadFile = File(...)):
    os.makedirs("videos", exist_ok=True)
    file_path = f"videos/{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    print(f"✅ Saved to: {file_path}")

    # ✅ Analyze posture
    results = analyze_posture(file_path)

    return {
        "filename": file.filename,
        "status": "Analyzed successfully",
        "results": results
    }
