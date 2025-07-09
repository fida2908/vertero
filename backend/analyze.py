import os
import cv2
import mediapipe as mp
import subprocess
import numpy as np

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


def calculate_angle(a, b, c):
    a, b, c = map(np.array, [a, b, c])
    ba = a - b
    bc = c - b
    cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
    return np.degrees(angle)


def is_knee_beyond_toe(knee, ankle):
    return knee[0] > ankle[0]


def summarize_results(results):
    issues = [r['message'] for r in results if not r['good']]
    if not issues:
        return ["✅ Great posture in all frames!"]
    summary = list(set(issues))  # Unique issues
    return summary


def reencode_for_browser(input_path, output_path):
    try:
        command = [
            "ffmpeg", "-y", "-i", input_path,
            "-vcodec", "libx264", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            output_path
        ]
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"🎞️ Re-encoded {input_path} to {output_path}")
    except Exception as e:
        print("❌ FFmpeg re-encoding failed:", e)


def analyze_posture(video_path):
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {
            "results": [{"frame": 0, "message": "❌ Could not open video", "good": False}],
            "summary": [],
            "annotated_video": None
        }

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    os.makedirs("annotated", exist_ok=True)
    base_name = os.path.basename(video_path).rsplit('.', 1)[0]
    raw_annotated_path = f"annotated/{base_name}_annotated.mp4"
    out = cv2.VideoWriter(raw_annotated_path, fourcc, fps, (width, height))

    results_list = []
    frame_number = 0

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_number += 1
        second = round(frame_number / fps, 2)
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        if not result.pose_landmarks:
            results_list.append({
                "frame": frame_number,
                "second": second,
                "message": "⚠️ No person detected",
                "good": False
            })
            out.write(frame)
            continue

        lm = result.pose_landmarks.landmark
        def get_point(idx): return [lm[idx].x, lm[idx].y]

        shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
        hip = get_point(mp_pose.PoseLandmark.LEFT_HIP.value)
        knee_left = get_point(mp_pose.PoseLandmark.LEFT_KNEE.value)
        ankle_left = get_point(mp_pose.PoseLandmark.LEFT_ANKLE.value)
        knee_right = get_point(mp_pose.PoseLandmark.RIGHT_KNEE.value)
        ankle_right = get_point(mp_pose.PoseLandmark.RIGHT_ANKLE.value)
        ear = get_point(mp_pose.PoseLandmark.LEFT_EAR.value)

        back_angle = calculate_angle(shoulder, hip, knee_left)
        neck_angle = calculate_angle(ear, shoulder, hip)

        issues = []
        if back_angle < 150:
            issues.append(f"Back angle too low: {int(back_angle)}°")
        if is_knee_beyond_toe(knee_left, ankle_left) or is_knee_beyond_toe(knee_right, ankle_right):
            issues.append("Knee goes beyond toe")
        if neck_angle < 150:
            issues.append(f"Neck bent too much: {int(neck_angle)}°")
        if back_angle < 165:
            issues.append(f"Back not straight: {int(back_angle)}°")

        if not issues:
            results_list.append({
                "frame": frame_number,
                "second": second,
                "message": "✅ Good posture",
                "good": True
            })
        else:
            for msg in issues:
                results_list.append({
                    "frame": frame_number,
                    "second": second,
                    "message": msg,
                    "good": False
                })

        # Annotate frame
        color = (0, 0, 255) if issues else (0, 255, 0)
        for conn in mp_pose.POSE_CONNECTIONS:
            x1 = int(lm[conn[0]].x * width)
            y1 = int(lm[conn[0]].y * height)
            x2 = int(lm[conn[1]].x * width)
            y2 = int(lm[conn[1]].y * height)
            cv2.line(frame, (x1, y1), (x2, y2), color, 2)

        for p in lm:
            x, y = int(p.x * width), int(p.y * height)
            cv2.circle(frame, (x, y), 4, (255, 255, 255), -1)

        if issues:
            cv2.putText(frame, "⚠️ Bad posture", (30, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        out.write(frame)

    cap.release()
    out.release()

    # Re-encode to browser-compatible format
    browser_compatible_path = raw_annotated_path.replace("_annotated.mp4", "_final.mp4")
    reencode_for_browser(raw_annotated_path, browser_compatible_path)

    summary = summarize_results(results_list)

    return {
        "results": results_list,
        "summary": summary,
        "annotated_video": browser_compatible_path.replace("\\", "/")
    }


def analyze_image_posture(image_path):
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)
    image = cv2.imread(image_path)

    if image is None:
        return {
            "results": [{"frame": 0, "message": "❌ Failed to load image", "good": False}],
            "summary": [],
            "annotated_image": None
        }

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = pose.process(image_rgb)

    if not result.pose_landmarks:
        return {
            "results": [{"frame": 0, "message": "⚠️ No person detected", "good": False}],
            "summary": [],
            "annotated_image": None
        }

    lm = result.pose_landmarks.landmark
    def get_point(idx): return [lm[idx].x, lm[idx].y]

    shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
    hip = get_point(mp_pose.PoseLandmark.LEFT_HIP.value)
    knee_left = get_point(mp_pose.PoseLandmark.LEFT_KNEE.value)
    ankle_left = get_point(mp_pose.PoseLandmark.LEFT_ANKLE.value)
    knee_right = get_point(mp_pose.PoseLandmark.RIGHT_KNEE.value)
    ankle_right = get_point(mp_pose.PoseLandmark.RIGHT_ANKLE.value)
    ear = get_point(mp_pose.PoseLandmark.LEFT_EAR.value)

    back_angle = calculate_angle(shoulder, hip, knee_left)
    neck_angle = calculate_angle(ear, shoulder, hip)

    results = []
    if back_angle < 150:
        results.append({"frame": 0, "message": f"Back angle too low: {int(back_angle)}°", "good": False})
    if is_knee_beyond_toe(knee_left, ankle_left) or is_knee_beyond_toe(knee_right, ankle_right):
        results.append({"frame": 0, "message": "Knee goes beyond toe", "good": False})
    if neck_angle < 150:
        results.append({"frame": 0, "message": f"Neck bent too much: {int(neck_angle)}°", "good": False})
    if back_angle < 165:
        results.append({"frame": 0, "message": f"Back not straight: {int(back_angle)}°", "good": False})

    if not results:
        results.append({"frame": 0, "message": "✅ Good posture!", "good": True})

    mp_drawing.draw_landmarks(
        image,
        result.pose_landmarks,
        mp_pose.POSE_CONNECTIONS,
        landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
    )

    os.makedirs("annotated", exist_ok=True)
    annotated_filename = os.path.basename(image_path).split('.')[0] + "_annotated.jpg"
    annotated_path = os.path.join("annotated", annotated_filename)
    cv2.imwrite(annotated_path, image)

    summary = summarize_results(results)

    return {
        "results": results,
        "summary": summary,
        "annotated_image": annotated_path.replace("\\", "/")
    }
