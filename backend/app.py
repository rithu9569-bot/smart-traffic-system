import os
import cv2
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, db

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enables cross-origin requests from your Vercel frontend

# Initialize Firebase Admin SDK (if serviceAccountKey.json exists)
cred_path = os.path.join(os.path.dirname(__file__), 'serviceAccountKey.json')
if os.path.exists(cred_path):
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://smart-traffic-system-default-rtdb.firebaseio.com/' # Replace with your Firebase DB URL if different
    })

# Root Endpoint (Fixes 404 on base Render URL)
@app.route('/')
def index():
    return jsonify({
        "status": "online",
        "system": "Smart AI & IoT Traffic Management System",
        "version": "1.0.0",
        "endpoints": {
            "video_feed": "/video_feed",
            "health": "/api/health",
            "emergency_override": "/api/emergency"
        }
    }), 200

# Health Check Endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"status": "healthy"}), 200

# Video Streaming Generator Function
def generate_frames():
    video_path = os.path.join(os.path.dirname(__file__), 'sample_traffic.mp4')
    
    # Fallback if local MP4 is not present on cloud server
    if not os.path.exists(video_path):
        camera = cv2.VideoCapture(0)  # Use webcam if available
    else:
        camera = cv2.VideoCapture(video_path)

    while True:
        success, frame = camera.read()
        if not success:
            camera.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video
            continue
        
        # Encode frame to JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        
        # Yield multipart image stream
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

# Live Video Stream Route
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Manual Emergency Override API Endpoint
@app.route('/api/emergency', methods=['POST'])
def trigger_emergency():
    data = request.get_json() or {}
    lane_id = data.get('lane_id', 'Lane_1')
    
    # Update Firebase Realtime Database if initialized
    try:
        ref = db.reference('traffic_signals/override')
        ref.set({
            'active': True,
            'lane': lane_id,
            'timestamp': os.popen('date').read().strip()
        })
        return jsonify({"success": True, "message": f"Emergency override activated for {lane_id}"}), 200
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    # Dynamic port binding for Render deployment
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)