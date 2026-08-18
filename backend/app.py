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
            "node_1": {"name": "Junction Node #1 (Highway North)", "vehicle_count": 0, "green_time": 30, "congestion": "LOW"},
            "node_2": {"name": "Junction Node #2 (Downtown Ave)", "vehicle_count": 0, "green_time": 30, "congestion": "LOW"},
            "node_3": {"name": "Junction Node #3 (Expressway Exit)", "vehicle_count": 0, "green_time": 30, "congestion": "LOW"}
        }

    def get_stats(self, junction_id):
        with self.lock:
            return self.junctions.get(junction_id, self.junctions["node_1"])

    def update_stats(self, junction_id, count):
        calculated_green = min(90, max(15, count * 5))
        calculated_congestion = "HIGH" if count >= 10 else "MEDIUM" if count >= 5 else "LOW"
        
        with self.lock:
            if junction_id in self.junctions:
                self.junctions[junction_id]["vehicle_count"] = count
                self.junctions[junction_id]["green_time"] = calculated_green
                self.junctions[junction_id]["congestion"] = calculated_congestion

pipeline = MultiJunctionPipeline()

def generate_video_stream(junction_id):
    # Unique traffic density and speeds per junction
    speeds = {"node_1": 4, "node_2": 7, "node_3": 5}
    car_counts = {"node_1": 7, "node_2": 14, "node_3": 9}
    
    num_cars = car_counts.get(junction_id, 7)
    speed = speeds.get(junction_id, 4)
    
    np.random.seed(hash(junction_id) % 10000)
    cars = []
    for _ in range(num_cars):
        cars.append({
            'x': int(np.random.randint(40, 600)),
            'y': int(np.random.randint(-50, 350)),
            'color': (int(np.random.randint(50, 250)), int(np.random.randint(50, 250)), int(np.random.randint(50, 250)))
        })

    while True:
        # Asphalt road background
        frame = np.full((360, 640, 3), (35, 40, 50), dtype=np.uint8)
        
        # Lane Dividers
        cv2.line(frame, (213, 0), (213, 360), (255, 255, 255), 2, cv2.LINE_AA)
        cv2.line(frame, (426, 0), (426, 360), (255, 255, 255), 2, cv2.LINE_AA)
        
        for y_pos in range(0, 360, 40):
            cv2.line(frame, (106, y_pos), (106, y_pos + 20), (180, 180, 180), 1)
            cv2.line(frame, (320, y_pos), (320, y_pos + 20), (180, 180, 180), 1)
            cv2.line(frame, (533, y_pos), (533, y_pos + 20), (180, 180, 180), 1)

        active_cars = 0
        for car in cars:
            car['y'] += speed
            if car['y'] > 380:
                car['y'] = -50
                car['x'] = int(np.random.randint(40, 600))

            x, y = car['x'], car['y']
            if -50 <= y <= 400:
                active_cars += 1
                # Vehicle body
                cv2.rectangle(frame, (x, y), (x + 28, y + 50), car['color'], -1)
                # Windshield
                cv2.rectangle(frame, (x + 4, y + 10), (x + 24, y + 20), (210, 230, 250), -1)
                # Headlights
                cv2.circle(frame, (x + 6, y + 2), 2, (0, 255, 255), -1)
                cv2.circle(frame, (x + 22, y + 2), 2, (0, 255, 255), -1)

        pipeline.update_stats(junction_id, active_cars)

        ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 85])
        if not ret:
            continue
            
        frame_bytes = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

        time.sleep(0.04)

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