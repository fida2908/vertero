import cv2
import numpy as np
import mediapipe as mp
import os
from collections import defaultdict

# MediaPipe setup
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# 📐 Calculate the angle between three points
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return angle if angle <= 180 else 360 - angle

# 📊 Summarize bad posture messages
def summarize_results(results):
    summary = defaultdict(list)
    for r in results:
        if not r['good']:
            summary[r['message']].append(r.get('second', 0))
    insights = []
    for msg, seconds in summary.items():
        formatted = ", ".join(f"{s:.1f}s" for s in seconds[:3])
        insights.append(f"{msg} detected at {formatted}" + ("..." if len(seconds) > 3 else ""))
    return insights

# 📍 Check if knee goes beyond toe
def is_knee_beyond_toe(knee, ankle):
    return abs(knee[0] - ankle[0]) > 0.05

# 🎥 Analyze posture from video
def analyze_posture(video_path):
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return {
            "results": [{"frame": 0, "message": "❌ Could not open video", "good": False}],
            "summary": [],
            "annotated_image": None
        }

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_number = 0
    results_list = []
    annotated_frame_saved = False
    annotated_path = None

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
            continue

        lm = result.pose_landmarks.landmark
        def get_point(idx): return [lm[idx].x, lm[idx].y]

        # Key landmarks
        shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
        hip = get_point(mp_pose.PoseLandmark.LEFT_HIP.value)
        knee_left = get_point(mp_pose.PoseLandmark.LEFT_KNEE.value)
        ankle_left = get_point(mp_pose.PoseLandmark.LEFT_ANKLE.value)
        knee_right = get_point(mp_pose.PoseLandmark.RIGHT_KNEE.value)
        ankle_right = get_point(mp_pose.PoseLandmark.RIGHT_ANKLE.value)
        ear = get_point(mp_pose.PoseLandmark.LEFT_EAR.value)

        # 📏 Angle checks
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

        if issues:
            for msg in issues:
                results_list.append({
                    "frame": frame_number,
                    "second": second,
                    "message": msg,
                    "good": False
                })
        else:
            results_list.append({
                "frame": frame_number,
                "second": second,
                "message": "✅ Good posture",
                "good": True
            })

        # Save only first annotated frame
        if not annotated_frame_saved:
            mp_drawing.draw_landmarks(
                frame,
                result.pose_landmarks,
                mp_pose.POSE_CONNECTIONS,
                landmark_drawing_spec=mp_drawing_styles.get_default_pose_landmarks_style()
            )
            os.makedirs("annotated", exist_ok=True)
            annotated_path = f"annotated/frame_{frame_number}.jpg"
            cv2.imwrite(annotated_path, frame)
            annotated_frame_saved = True

    cap.release()
    summary = summarize_results(results_list)
    if not summary:
        summary = ["✅ Your posture looks good!"]

    return {
        "results": results_list,
        "summary": summary,
        "annotated_image": annotated_path
    }

# 🖼️ Analyze posture from image
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

    # Draw and save annotated image
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
    if not summary:
        summary = ["✅ Your posture looks good!"]

    return {
        "results": results,
        "summary": summary,
        "annotated_image": annotated_path
    }
