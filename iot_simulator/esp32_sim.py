import time
import firebase_admin
from firebase_admin import credentials, db

# 1. Initialize Firebase Admin SDK
cred = credentials.Certificate('../backend/serviceAccountKey.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://smart-traffic-system-5fcf1-default-rtdb.asia-southeast1.firebasedatabase.app/'  # Replace with your URL
})

# Update line 11 in esp32_sim.py
ref = db.reference('junctions/junction_1')

print("=" * 60)
print("  ESP32 TRAFFIC LIGHT HARDWARE SIMULATOR — JUNCTION #1  ")
print("=" * 60)
print("Listening to Firebase Realtime Database updates...\n")

last_status = None
last_duration = None
last_emergency = None

def render_traffic_light(light_state, duration, vehicle_count, is_emergency):
    """Simulate hardware LED status display in terminal"""
    red_led    = "🔴 [RED ON]   " if light_state == "RED" else "⭕ [RED OFF]  "
    yellow_led = "🟡 [YELLOW ON]" if light_state == "YELLOW" else "⭕ [YELLOW OFF]"
    green_led  = "🟢 [GREEN ON] " if light_state == "GREEN" else "⭕ [GREEN OFF]"

    print("\033[H\033[J", end="") # Clear terminal screen
    print("=" * 60)
    print("      ESP32 HARDWARE SIGNAL CONTROLLER — LIVE MATRIX     ")
    print("=" * 60)
    print(f" Signal State  : {light_state}")
    print(f" Timer Counter : {duration}s remaining")
    print(f" Vehicle Count : {vehicle_count} detected")
    print(f" Priority Mode : {'EMERGENCY OVERRIDE' if is_emergency else 'AUTOMATED ADAPTIVE'}")
    print("-" * 60)
    print(f"  {red_led}")
    print(f"  {yellow_led}")
    print(f"  {green_led}")
    print("=" * 60)

def handle_stream_update(event):
    """Callback function triggered whenever Firebase data changes"""
    data = ref.get()
    if not data:
        return

    vehicle_count = data.get('vehicle_count', 0)
    green_duration = data.get('green_duration', 15)
    is_emergency = data.get('emergency_override', False)
    status = data.get('status', 'LOW')

    if is_emergency:
        render_traffic_light("GREEN", green_duration, vehicle_count, True)
    else:
        render_traffic_light("GREEN", green_duration, vehicle_count, False)

# Attach Firebase listener stream
ref.listen(handle_stream_update)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nESP32 Controller offline.")