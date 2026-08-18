import os
import cv2
import time
import threading
from flask import Flask, Response, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Enable CORS for all incoming requests (Netlify and local dev)
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
        calculated_green = min(90, max(15, count * 5))
        calculated_congestion = "HIGH" if count > 14 else "MEDIUM" if count > 8 else "LOW"
        
        with self.lock:
            self.vehicle_count = count
            self.green_time = calculated_green
            self.congestion = calculated_congestion

pipeline = TrafficPipeline()

def generate_video_stream():
    # Resolve video path relative to backend folder or frontend fallback
    base_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(base_dir, 'sample_traffic.mp4')
    if not os.path.exists(video_path):
        video_path = os.path.join(base_dir, '../frontend/public/sample_traffic.mp4')

    cap = cv2.VideoCapture(video_path if os.path.exists(video_path) else 0)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=40)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            # Restart video loop on completion
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Resize for smooth real-time stream performance
        resized = cv2.resize(frame, (640, 360))
        fg_mask = bg_subtractor.apply(resized)
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        active_count = 0
        for cnt in contours:
            if cv2.contourArea(cnt) > 350:  # Vehicle detection area threshold
                x, y, w, h = cv2.boundingRect(cnt)
                # Draw bounding box and label directly onto video frame
                cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(resized, "Vehicle", (x, max(15, y - 5)), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
                active_count += 1

        # Push updated metrics to thread pipeline
        pipeline.update_stats(active_count)

        # Encode frame to JPEG format for MJPEG stream
        ret, buffer = cv2.imencode('.jpg', resized)
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()

        # Yield HTTP multipart stream chunk
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.04)  # Maintain ~25 FPS stream speed

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