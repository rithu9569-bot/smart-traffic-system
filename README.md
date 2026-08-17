# 🚦 Smart Traffic AI & IoT Command Center

An end-to-end, real-time AI and IoT-powered traffic management platform. The system leverages **YOLOv8** computer vision to dynamically analyze traffic density at physical junctions, adaptively adjust signal timings, grant emergency vehicle priorities, and stream telemetry live to a React.js dashboard and an ESP32 hardware simulator.

---

## 🌟 Key Features

* **Real-Time Vehicle Detection:** Powered by Ultralytics YOLOv8 to track cars, buses, trucks, and motorcycles from aerial junction camera feeds.
* **Adaptive Green Signal Timing:** Dynamically calculates traffic density to optimize light duration (Low: 15s | Medium: 30s | High: 60s).
* **Emergency Priority Override:** Allows manual web overrides or automatic detection to trigger a **90-second priority green light**.
* **IoT Signal Controller Simulator:** Simulates physical ESP32 LED matrix state changes (🔴 RED, 🟡 YELLOW, 🟢 GREEN) synchronized via Firebase Realtime Database.
* **Live Command Center Dashboard:** Built with React.js, featuring direct MJPEG camera streams, dynamic telemetry cards, and real-time **Recharts** volume analytics.
* **Exportable Traffic Reports:** One-click CSV export functionality to archive traffic density trends and signal histories.

---

## 🏗️ System Architecture
┌──────────────────────────────┐
                   │   Live Junction Camera Feed  │
                   └──────────────┬───────────────┘
                                  │
                                  ▼
                    ┌───────────────────────────┐
                    │   YOLOv8 Detection Engine │
                    └─────────────┬─────────────┘
                                  │
          ┌───────────────────────┴───────────────────────┐
          ▼                                               ▼
┌───────────────────────────┐                   ┌───────────────────────────┐
│   Flask MJPEG Video Stream│                   │ Firebase Realtime Database│
└─────────────┬─────────────┘                   └─────────────┬─────────────┘
│                                               │
│               ┌───────────────────────────────┴───────────────────────────────┐
│               ▼                                                               ▼
│ ┌───────────────────────────┐                                   ┌───────────────────────────┐
└─► React.js Command Center   │                                   │ ESP32 Hardware Simulator  │
│ (UI / Analytics / CSV Export)│                                 │ (Virtual LED Signal Matrix│
└───────────────────────────┘                                   └───────────────────────────┘
---

## 🚀 Tech Stack

* **Frontend:** React.js, Recharts, Lucide Icons, Vite
* **Backend API & Vision:** Python, Flask, OpenCV, Ultralytics YOLOv8
* **IoT & Database:** Firebase Realtime Database, ESP32 Python Simulator

---

## 🛠️ Project Structure
smart_traffic_system/
├── backend/
│   ├── app.py                   # Flask server providing MJPEG stream & API endpoints
│   ├── traffic_ai.py            # YOLOv8 vehicle detection & Firebase sync engine
│   ├── sample_traffic.mp4       # Video feed source
│   ├── serviceAccountKey.json   # Firebase Admin SDK Credentials
│   └── yolov8n.pt               # YOLOv8 pre-trained model weights
├── frontend/
│   ├── src/
│   │   ├── App.jsx              # React Command Center Dashboard
│   │   └── main.jsx
│   └── package.json
└── iot_simulator/
└── esp32_sim.py             # Virtual ESP32 traffic light hardware controller
---

## ⚡ Getting Started

### **1. Prerequisites**
* Python 3.9+
* Node.js v18+
* Firebase Account & Realtime Database

### **2. Virtual Environment Setup**
```powershell
# Create & Activate Virtual Environment
python -m venv venv
.\venv\Scripts\activate.bat
cd backend
pip install flask flask-cors opencv-python ultralytics firebase-admin
cd ../frontend
npm install
npm install recharts lucide-react
cd frontend
npm run dev
cd backend
python app.py
cd backend
python traffic_ai.py
cd iot_simulator
python esp32_sim.py
📊 Telemetry & Analytics CSV Export
Click Export CSV Report on the header bar of the web dashboard to instantly generate a clean .csv file containing:

Precise Timestamps

Dynamic Vehicle Counts

Active Signal Durations

Junction Congestion Levels.          