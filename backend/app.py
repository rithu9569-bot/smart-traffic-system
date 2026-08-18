import os
import cv2
import time
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class TrafficPipeline:
    def __init__(self):
        self.vehicle_count = 0
        self.green_time = 30
        self.congestion = "LOW"
        self.lock = threading.Lock()
        
    def get_stats(self):
        with self.lock:
            return {
                "vehicle_count": self.vehicle_count,
                "green_time": self.green_time,
                "congestion": self.congestion
            }

    def update_stats(self, count):
        # Calculate signal timing dynamically: 5 seconds per detected vehicle (capped between 15s and 90s)
        calculated_green = min(90, max(15, count * 5))
        calculated_congestion = "HIGH" if count >= 12 else "MEDIUM" if count >= 6 else "LOW"
        
        with self.lock:
            self.vehicle_count = count
            self.green_time = calculated_green
            self.congestion = calculated_congestion

pipeline = TrafficPipeline()

def generate_video_stream():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(base_dir, 'sample_traffic.mp4')
    if not os.path.exists(video_path):
        video_path = os.path.join(base_dir, '../frontend/public/sample_traffic.mp4')

    cap = cv2.VideoCapture(video_path if os.path.exists(video_path) else 0)
    
    # Tuned MOG2 parameters for smaller distant vehicles
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=500, varThreshold=16, detectShadows=False)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        resized = cv2.resize(frame, (640, 360))
        
        # Blur frame to reduce road surface noise
        blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        fg_mask = bg_subtractor.apply(blurred)
        
        # Morphological operations to merge fragmented vehicle contours
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(fg_mask, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        active_count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            # Area threshold tuned for highway camera perspective (80px to 4000px)
            if 80 < area < 4000:
                x, y, w, h = cv2.boundingRect(cnt)
                cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(resized, f"Car {active_count + 1}", (x, max(15, y - 5)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
                active_count += 1

        pipeline.update_stats(active_count)

        ret, buffer = cv2.imencode('.jpg', resized, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.04)

    cap.release()

@app.route('/video_feed')
def video_feed():
    return Response(generate_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    return jsonify(pipeline.get_stats()), 200

@app.route('/api/emergency', methods=['POST'])
def emergency():
    return jsonify({"status": "Emergency priority override activated"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)