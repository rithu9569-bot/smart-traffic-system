import os
import cv2
import time
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({"status": "online", "system": "Smart Traffic AI Command Center"}), 200

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

def generate_frames():
    # Use reliable public MP4 traffic stream or local file
    video_source = "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
    local_path = os.path.join(os.path.dirname(__file__), 'sample_traffic.mp4')
    
    if os.path.exists(local_path):
        video_source = local_path

    cap = cv2.VideoCapture(video_source)

    while True:
        success, frame = cap.read()
        if not success or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        frame = cv2.resize(frame, (640, 360))
        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
        time.sleep(0.03)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/emergency', methods=['POST'])
def trigger_emergency():
    return jsonify({"success": True, "message": "Emergency priority activated"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)