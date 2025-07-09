import cv2
import numpy as np
import mediapipe as mp

# 📐 Calculate the angle between three points
def calculate_angle(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    return angle if angle <= 180 else 360 - angle


# 🎥 Analyze posture from video file
def analyze_posture(video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose()
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        return [{"frame": 0, "message": "❌ Could not open video", "good": False}]

    frame_number = 0
    results_list = []

    while True:
        success, frame = cap.read()
        if not success:
            break

        frame_number += 1
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        if not result.pose_landmarks:
            results_list.append({
                "frame": frame_number,
                "message": "⚠️ No person detected",
                "good": False
            })
            continue

        lm = result.pose_landmarks.landmark

        def get_point(idx):
            pt = lm[idx]
            return [pt.x, pt.y]

        shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
        hip = get_point(mp_pose.PoseLandmark.LEFT_HIP.value)
        knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE.value)
        ankle = get_point(mp_pose.PoseLandmark.LEFT_ANKLE.value)
        ear = get_point(mp_pose.PoseLandmark.LEFT_EAR.value)

        # 📏 Angle calculations
        back_angle = calculate_angle(shoulder, hip, knee)
        neck_angle = calculate_angle(ear, shoulder, hip)

        issues = []

        if back_angle < 150:
            issues.append(f"Back angle too low: {int(back_angle)}°")

        if knee[0] > ankle[0] + 0.02:
            issues.append("Knee goes beyond toe")

        if neck_angle < 150:
            issues.append(f"Neck bent too much: {int(neck_angle)}°")

        if back_angle < 165:
            issues.append(f"Back not straight: {int(back_angle)}°")

        if issues:
            for msg in issues:
                results_list.append({
                    "frame": frame_number,
                    "message": msg,
                    "good": False
                })
        else:
            results_list.append({
                "frame": frame_number,
                "message": "✅ Good posture",
                "good": True
            })

    cap.release()
    return results_list


# 🖼️ Analyze posture from image file
def analyze_image_posture(image_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)

    image = cv2.imread(image_path)
    if image is None:
        return [{"frame": 0, "message": "❌ Failed to load image", "good": False}]

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    result = pose.process(image_rgb)

    if not result.pose_landmarks:
        return [{"frame": 0, "message": "⚠️ No person detected", "good": False}]

    lm = result.pose_landmarks.landmark

    def get_point(idx):
        pt = lm[idx]
        return [pt.x, pt.y]

    shoulder = get_point(mp_pose.PoseLandmark.LEFT_SHOULDER.value)
    hip = get_point(mp_pose.PoseLandmark.LEFT_HIP.value)
    knee = get_point(mp_pose.PoseLandmark.LEFT_KNEE.value)
    ankle = get_point(mp_pose.PoseLandmark.LEFT_ANKLE.value)
    ear = get_point(mp_pose.PoseLandmark.LEFT_EAR.value)

    back_angle = calculate_angle(shoulder, hip, knee)
    neck_angle = calculate_angle(ear, shoulder, hip)

    issues = []

    if back_angle < 150:
        issues.append({"frame": 0, "message": f"Back angle too low: {int(back_angle)}°", "good": False})

    if knee[0] > ankle[0] + 0.02:
        issues.append({"frame": 0, "message": "Knee goes beyond toe", "good": False})

    if neck_angle < 150:
        issues.append({"frame": 0, "message": f"Neck bent too much: {int(neck_angle)}°", "good": False})

    if back_angle < 165:
        issues.append({"frame": 0, "message": f"Back not straight: {int(back_angle)}°", "good": False})

    return issues if issues else [{"frame": 0, "message": "✅ Good posture!", "good": True}]
