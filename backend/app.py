import os
import cv2
import time
import threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class VideoStreamer:
    def __init__(self):
        self.frame = None
        self.lock = threading.Lock()
        self.running = True
        self.thread = threading.Thread(target=self._update_frames, daemon=True)
        self.thread.start()

    def _update_frames(self):
        # Determine video source
        local_path = os.path.join(os.path.dirname(__file__), 'sample_traffic.mp4')
        video_source = local_path if os.path.exists(local_path) else "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"

        cap = cv2.VideoCapture(video_source)

        while self.running:
            success, frame = cap.read()
            if not success or frame is None:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue

            frame = cv2.resize(frame, (640, 360))
            ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 75])
            
            if ret:
                with self.lock:
                    self.frame = buffer.tobytes()

            time.sleep(0.04)  # ~25 FPS loop

        cap.release()

    def get_frame(self):
        with self.lock:
            return self.frame

streamer = VideoStreamer()

@app.route('/')
def index():
    return jsonify({"status": "online", "system": "Smart Traffic AI Command Center"}), 200

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

def generate_stream():
    while True:
        frame_bytes = streamer.get_frame()
        if frame_bytes is not None:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/emergency', methods=['POST'])
def trigger_emergency():
    return jsonify({"success": True, "message": "Emergency priority activated"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)