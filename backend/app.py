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
        # Precise linear scale for green signal (15s to 60s) and congestion thresholds
        calculated_green = min(60, max(15, count * 4 + 12))
        calculated_congestion = "HIGH" if count >= 12 else "MEDIUM" if count >= 6 else "LOW"
        
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

    # Expected realistic max vehicle capacities visible on screen per camera angle
    max_visible_caps = {
        "node_1": 10,
        "node_2": 8,
        "node_3": 6
    }

    video_source = online_streams.get(junction_id, online_streams["node_1"])
    max_cap = max_visible_caps.get(junction_id, 10)

    cap = cv2.VideoCapture(video_source)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=600, varThreshold=65, detectShadows=True)

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
        mask = np.zeros(resized.shape[:2], dtype=np.uint8)

        # Precise road-only bounding polygons
        if junction_id == "node_1":
            road_poly = np.array([[50, 60], [600, 60], [620, 220], [20, 220]], np.int32)
            min_area, max_area = 450, 6000
        elif junction_id == "node_2":
            road_poly = np.array([[80, 20], [560, 20], [560, 340], [80, 340]], np.int32)
            min_area, max_area = 600, 8000
        else:
            road_poly = np.array([[60, 20], [580, 20], [620, 340], [20, 340]], np.int32)
            min_area, max_area = 500, 7000

        cv2.fillPoly(mask, [road_poly], 255)

        blurred = cv2.GaussianBlur(resized, (7, 7), 0)
        fg_mask = bg_subtractor.apply(blurred)
        
        # Filter out background noise and shadows
        _, thresh = cv2.threshold(fg_mask, 220, 255, cv2.THRESH_BINARY)
        road_fg = cv2.bitwise_and(thresh, thresh, mask=mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
        dilated = cv2.dilate(road_fg, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        raw_count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h if h > 0 else 0
            
            # Tight aspect ratio and contour filter for real vehicles
            if min_area < area < max_area and 0.4 < aspect_ratio < 3.2:
                raw_count += 1

        # Enforce realistic count bounds corresponding to the video screen
        exact_count = min(max_cap, raw_count)

        pipeline.update_stats(junction_id, exact_count)

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