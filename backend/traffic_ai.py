import cv2
from ultralytics import YOLO
import firebase_admin
from firebase_admin import credentials, db
import time

# 1. Initialize Firebase Admin SDK
cred = credentials.Certificate('serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-traffic-system-5fcf1-default-rtdb.asia-southeast1.firebasedatabase.app/'
})

# Update line 12 in traffic_ai.py
ref = db.reference('junctions/junction_1')

# 2. Load YOLOv8 Model (yolov8s.pt or yolov8n.pt)
model = YOLO('yolov8n.pt')

# COCO Vehicle Classes: 2=car, 3=motorcycle, 5=bus, 7=truck
VEHICLE_CLASSES = [2, 3, 5, 7]

cap = cv2.VideoCapture('sample_traffic.mp4')

last_update_time = time.time()

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0) # Loop video
        continue

    # Read manual overrides from Firebase
    current_firebase_data = ref.get() or {}
    manual_emergency = current_firebase_data.get('emergency_override', False)

    # Run detection with lower confidence threshold (0.20) for distant cars
    results = model(frame, conf=0.20, verbose=False)[0]

    vehicle_count = 0

    for box in results.boxes:
        cls_id = int(box.cls[0])
        if cls_id in VEHICLE_CLASSES:
            vehicle_count += 1
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Dynamic Threshold Adjustments based on accurate count
    if manual_emergency:
        green_duration = 90
        status = "EMERGENCY OVERRIDE"
    else:
        if vehicle_count < 6:
            green_duration = 15
            status = "LOW"
        elif 6 <= vehicle_count <= 15:
            green_duration = 30
            status = "MEDIUM"
        else:
            green_duration = 60
            status = "HIGH"

    # Push to Firebase every 1 second
    if time.time() - last_update_time > 1.0:
        ref.update({
            'vehicle_count': vehicle_count,
            'green_duration': green_duration,
            'status': status,
            'emergency_override': manual_emergency
        })
        last_update_time = time.time()

    # Visual overlay
    overlay_text = f"Vehicles: {vehicle_count} | Green Time: {green_duration}s | Status: {status}"
    color = (0, 0, 255) if manual_emergency else (0, 255, 0)
    cv2.putText(frame, overlay_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    cv2.imshow("Smart Traffic AI Stream", cv2.resize(frame, (960, 540)))

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()