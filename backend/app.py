import os
import cv2
import time
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "system": "Smart AI Traffic System",
        "endpoints": {
            "video_feed": "/video_feed",
            "health": "/api/health",
            "emergency": "/api/emergency"
        }
    }), 200

@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

def generate_frames():
    # Detect video file in backend directory
    video_filename = 'sample_traffic.mp4'
    video_path = os.path.join(os.path.dirname(__file__), video_filename)
    
    # If file name varies, attempt to pick any .mp4 file in backend/
    if not os.path.exists(video_path):
        for file in os.listdir(os.path.dirname(__file__)):
            if file.endswith('.mp4'):
                video_path = os.path.join(os.path.dirname(__file__), file)
                break

    cap = cv2.VideoCapture(video_path)

    while True:
        success, frame = cap.read()
        
        # Loop video automatically when it reaches the end
        if not success or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue

        # Resize for smooth bandwidth streaming
        frame = cv2.resize(frame, (640, 360))

        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # Frame timing delay (~25 FPS)
        time.sleep(0.04)

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/emergency', methods=['POST'])
def trigger_emergency():
    data = request.get_json() or {}
    lane_id = data.get('lane_id', 'Junction Node #1')
    return jsonify({
        "success": True, 
        "message": f"🚨 Emergency priority granted to {lane_id}!"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)