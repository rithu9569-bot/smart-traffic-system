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
        calculated_green = min(90, max(15, count * 6 + 15))
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

    video_source = online_streams.get(junction_id, online_streams["node_1"])

    cap = cv2.VideoCapture(video_source)
    bg_subtractor = cv2.createBackgroundSubtractorMOG2(history=400, varThreshold=30, detectShadows=True)

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

        # Custom Road Polygons per camera perspective to cover all active lanes
        if junction_id == "node_1":
            # Highway perspective: covering upper highway lanes, excluding trees
            road_poly = np.array([[0, 0], [640, 0], [640, 240], [0, 240]], np.int32)
            min_area, max_area = 180, 8000
        elif junction_id == "node_2":
            # Direct top-down view
            road_poly = np.array([[0, 0], [640, 0], [640, 360], [0, 360]], np.int32)
            min_area, max_area = 250, 10000
        else:
            # Multi-lane expressway view
            road_poly = np.array([[10, 0], [630, 0], [630, 360], [10, 360]], np.int32)
            min_area, max_area = 200, 9000

        cv2.fillPoly(mask, [road_poly], 255)

        blurred = cv2.GaussianBlur(resized, (5, 5), 0)
        fg_mask = bg_subtractor.apply(blurred)
        
        # Remove background shadows
        _, thresh = cv2.threshold(fg_mask, 200, 255, cv2.THRESH_BINARY)
        road_fg = cv2.bitwise_and(thresh, thresh, mask=mask)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(road_fg, kernel, iterations=2)
        
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        active_count = 0
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if min_area < area < max_area:
                active_count += 1
                # Green rectangle/text overlay code removed for a clean video feed

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