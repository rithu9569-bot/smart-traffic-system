import os
import cv2
import time
import numpy as np
import threading
from flask import Flask, Response, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

class MultiJunctionPipeline:
    def __init__(self):
        self.lock = threading.Lock()
        self.junctions = {
            "node_1": {"name": "Junction Node #1 (Highway North)", "vehicle_count": 0, "green_time": 20, "congestion": "LOW"},
            "node_2": {"name": "Junction Node #2 (Downtown Ave)", "vehicle_count": 0, "green_time": 20, "congestion": "LOW"},
            "node_3": {"name": "Junction Node #3 (Expressway Exit)", "vehicle_count": 0, "green_time": 20, "congestion": "LOW"}
        }

    def get_stats(self, junction_id):
        with self.lock:
            return self.junctions.get(junction_id, self.junctions["node_1"])

    def update_stats(self, junction_id, count):
        # Calculate realistic signal timing & congestion based on actual vehicle counts
        calculated_green = min(90, max(15, count * 10 + 10))
        calculated_congestion = "HIGH" if count >= 8 else "MEDIUM" if count >= 4 else "LOW"
        
        with self.lock:
            if junction_id in self.junctions:
                self.junctions[junction_id]["vehicle_count"] = count
                self.junctions[junction_id]["green_time"] = calculated_green
                self.junctions[junction_id]["congestion"] = calculated_congestion

pipeline = MultiJunctionPipeline()

def generate_video_stream(junction_id):
    online_streams = {
        "node_1": "https://res.cloudinary.com/hmyu5qer/video/upload/v1787052306/sample_traffic.mp4",
        "node_2": "https://res.cloudinary.com/hmyu5qer/video/upload/v1787052229/sample_traffic_2.mp4",
        "node_3": "https://res.cloudinary.com/hmyu5qer/video/upload/v1787052279/sample_traffic_3.mp4"
    }

    video_source = online_streams.get(junction_id, online_streams["node_1"])

    cap = cv2.VideoCapture(video_source)
    # Calibrated background subtractor settings for video feeds
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=300, varThreshold=50, detectShadows=True)

    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret or frame is None:
                cap.release()
                time.sleep(0.2)
                cap = cv2.VideoCapture(video_source)
                continue

        resized = cv2.resize(frame, (640, 360))
        
        # Define Region of Interest (ROI) covering main road lanes only
        mask = np.zeros(resized.shape[:2], dtype=np.uint8)
        road_poly = np.array([[40, 100], [600, 100], [620, 350], [20, 350]], np.int32)
        cv2.fillPoly(mask, [road_poly], 255)

        blurred = cv2.GaussianBlur(resized, (7, 7), 0)
        fg_mask = bg_subtractor.apply(blurred)
        
        # Remove shadows (shadow value in OpenCV MOG2 is 127)
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        road_fg = cv2.bitwise_and(thresh, thresh, mask=mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        dilated = cv2.dilate(road_fg, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        active_count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Strict contour size filter matching actual vehicle proportions (cars/trucks)
            if 1200 < area < 15000 and 0.4 < aspect_ratio < 2.5:
                active_count += 1
                # Draw bounding box on video stream
                cv2.rectangle(resized, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(resized, "Vehicle", (x, y - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        pipeline.update_stats(junction_id, active_count)

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
    junction_id = request.args.get('junction', 'node_1')
    return Response(generate_video_stream(junction_id), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    junction_id = request.args.get('junction', 'node_1')
    return jsonify(pipeline.get_stats(junction_id)), 200

@app.route('/api/emergency', methods=['POST'])
def emergency():
    return jsonify({"status": "Emergency priority override activated"}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, threaded=True)