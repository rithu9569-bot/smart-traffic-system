from flask import Flask, Response, jsonify, request
from flask_cors import CORS
import cv2

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend requests

def generate_frames():
    # Load video file from backend directory
    cap = cv2.VideoCapture('sample_traffic.mp4')
    
    while True:
        success, frame = cap.read()
        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Loop video continuously
            continue
        
        # Resize frame for web stream efficiency
        frame = cv2.resize(frame, (720, 405))
        
        # Encode frame as JPEG
        ret, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        # Yield frame in multipart HTTP response format
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/emergency', methods=['POST'])
def emergency_override():
    """API endpoint to receive emergency toggle events"""
    data = request.get_json() or {}
    emergency_state = data.get('emergency', False)
    print(f"[API Log] Emergency priority state set to: {emergency_state}")
    return jsonify({"status": "success", "emergency": emergency_state})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)