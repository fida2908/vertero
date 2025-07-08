import mediapipe as mp
import cv2
import numpy as np

def calculate_angle(a, b, c):
    """Calculate angle between three points"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)

    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180:
        angle = 360 - angle
    return angle

def analyze_posture(video_path):
    mp_pose = mp.solutions.pose
    pose = mp_pose.Pose(static_image_mode=False)
    cap = cv2.VideoCapture(video_path)

    issues = []
    frame_number = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_number > 30:  # Limit to first 30 frames
            break

        frame_number += 1
        image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = pose.process(image_rgb)

        if not result.pose_landmarks:
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

        # 🔺 Back angle
        back_angle = calculate_angle(shoulder, hip, knee)
        if back_angle < 150:
            issues.append({
                "frame": frame_number,
                "message": f"Back angle too low: {int(back_angle)}°",
                "good": False
            })

        # 🦵 Knee beyond toe
        if knee[0] > ankle[0] + 0.02:
            issues.append({
                "frame": frame_number,
                "message": "Knee goes beyond toe",
                "good": False
            })

        # 🔻 Neck bent (ear–shoulder–hip)
        neck_angle = calculate_angle(ear, shoulder, hip)
        if neck_angle < 150:
            issues.append({
                "frame": frame_number,
                "message": f"Neck bent too much: {int(neck_angle)}°",
                "good": False
            })

        # 🪑 Back not straight
        if back_angle < 165:
            issues.append({
                "frame": frame_number,
                "message": f"Back not straight: {int(back_angle)}°",
                "good": False
            })

    cap.release()
    return issues if issues else [{"frame": 0, "message": "Posture looks good!", "good": True}]
