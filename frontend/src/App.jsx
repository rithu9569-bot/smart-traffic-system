import React, { useEffect, useState } from 'react';
import { initializeApp } from 'firebase/app';
import { getDatabase, ref, onValue, update } from 'firebase/database';
import { ShieldAlert, Car, Clock, Activity, Video, TrendingUp, Download } from 'lucide-react';
import { ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';

// Replace with your actual Firebase Realtime Database URL
const firebaseConfig = {
  databaseURL: "https://smart-traffic-system-5fcf1-default-rtdb.asia-southeast1.firebasedatabase.app/",
};

const app = initializeApp(firebaseConfig);
const database = getDatabase(app);

export default function Dashboard() {
  const [trafficData, setTrafficData] = useState({
    vehicle_count: 0,
    green_duration: 0,
    status: 'LOADING',
    emergency_override: false
  });

  const [history, setHistory] = useState([]);

  useEffect(() => {
    // Listening to Junction 1 data
    const trafficRef = ref(database, 'junctions/junction_1');
    const unsubscribe = onValue(trafficRef, (snapshot) => {
      const data = snapshot.val();
      if (data) {
        setTrafficData(data);

        // Append live data point to chart history (keep last 20 data points)
        const timestamp = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
        setHistory((prevHistory) => [
          ...prevHistory.slice(-19),
          { time: timestamp, count: data.vehicle_count, duration: data.green_duration, status: data.status }
        ]);
      }
    });

    return () => unsubscribe();
  }, []);

  const toggleEmergency = async () => {
    const newEmergencyState = !trafficData.emergency_override;
    const trafficRef = ref(database, 'junctions/junction_1');

    try {
      await update(trafficRef, {
        emergency_override: newEmergencyState,
        green_duration: newEmergencyState ? 90 : trafficData.green_duration,
        status: newEmergencyState ? "EMERGENCY OVERRIDE" : trafficData.status
      });
    } catch (err) {
      console.error("Firebase update failed:", err);
    }

    try {
      await fetch('http://localhost:5000/api/emergency', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ emergency: newEmergencyState })
      });
    } catch (err) {
      console.log("Flask API notify fallback handled.");
    }
  };

  // Exportable Traffic Reports CSV Handler
  const exportCSVReport = () => {
    if (history.length === 0) {
      alert("No traffic telemetry data recorded yet to export!");
      return;
    }

    const headers = ["Timestamp", "Vehicle Count", "Green Signal Duration (s)", "Congestion Status"];
    const rows = history.map(item => [
      item.time,
      item.count,
      item.duration,
      `"${item.status}"`
    ]);

    const csvContent = "data:text/csv;charset=utf-8," 
      + [headers.join(","), ...rows.map(e => e.join(","))].join("\n");

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `Traffic_Report_Junction1_${new Date().toISOString().slice(0, 10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={{ backgroundColor: '#0f172a', color: '#f8fafc', minHeight: '100vh', padding: '24px', fontFamily: 'sans-serif' }}>
      {/* Header */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', borderBottom: '1px solid #334155', paddingBottom: '16px', flexWrap: 'wrap', gap: '16px' }}>
        <h1 style={{ fontSize: '24px', fontWeight: 'bold', color: '#38bdf8', margin: 0 }}>
          Smart Traffic AI Command Center — Junction #1
        </h1>
        <div style={{ display: 'flex', gap: '12px' }}>
          <button 
            onClick={exportCSVReport}
            style={{
              backgroundColor: '#334155', color: '#f8fafc', border: '1px solid #475569',
              padding: '12px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold',
              display: 'flex', alignItems: 'center', gap: '8px', transition: 'all 0.2s ease'
            }}>
            <Download size={18} /> Export CSV Report
          </button>
          <button 
            onClick={toggleEmergency}
            style={{
              backgroundColor: trafficData.emergency_override ? '#ef4444' : '#3b82f6',
              color: 'white', border: 'none', padding: '12px 24px', borderRadius: '8px',
              cursor: 'pointer', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px',
              transition: 'all 0.2s ease'
            }}>
            <ShieldAlert size={18} /> {trafficData.emergency_override ? "EMERGENCY OVERRIDE ACTIVE" : "TRIGGER EMERGENCY PRIORITY"}
          </button>
        </div>
      </header>

      {/* Dynamic Metrics Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '20px', marginBottom: '32px' }}>
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', borderLeft: '4px solid #38bdf8' }}>
          <div style={{ color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '8px' }}><Car /> Vehicle Count</div>
          <h2 style={{ fontSize: '32px', marginTop: '8px', marginBottom: 0 }}>{trafficData.vehicle_count}</h2>
        </div>

        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', borderLeft: '4px solid #22c55e' }}>
          <div style={{ color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '8px' }}><Clock /> Adaptive Green Signal</div>
          <h2 style={{ fontSize: '32px', marginTop: '8px', marginBottom: 0, color: trafficData.emergency_override ? '#ef4444' : '#f8fafc' }}>
            {trafficData.green_duration}s
          </h2>
        </div>

        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', borderLeft: '4px solid #eab308' }}>
          <div style={{ color: '#94a3b8', display: 'flex', alignItems: 'center', gap: '8px' }}><Activity /> Congestion Level</div>
          <h2 style={{ fontSize: '24px', marginTop: '8px', marginBottom: 0, color: trafficData.emergency_override ? '#ef4444' : '#f8fafc' }}>
            {trafficData.status}
          </h2>
        </div>
      </div>

      {/* Main Grid: Live Camera + Analytics Chart */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '24px' }}>
        
        {/* Camera Feed Stream */}
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <Video color="#38bdf8" />
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f8fafc', margin: 0 }}>
              Live Camera Feed — Junction Node #1
            </h3>
          </div>
          <div style={{ width: '100%', height: '320px', backgroundColor: '#000', borderRadius: '8px', overflow: 'hidden', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
            <img 
              src="http://localhost:5000/video_feed" 
              alt="Live Junction Stream" 
              style={{ width: '100%', height: '100%', objectFit: 'contain' }}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.parentNode.innerHTML = '<div style="padding: 40px; color: #ef4444; font-weight: bold;">Stream Offline: Ensure python app.py is running on port 5000</div>';
              }}
            />
          </div>
        </div>

        {/* Realtime Traffic Analytics Chart */}
        <div style={{ background: '#1e293b', padding: '20px', borderRadius: '12px', border: '1px solid #334155' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
            <TrendingUp color="#38bdf8" />
            <h3 style={{ fontSize: '18px', fontWeight: '600', color: '#f8fafc', margin: 0 }}>
              Realtime Traffic Volume Trends
            </h3>
          </div>
          <div style={{ width: '100%', height: '320px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="time" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }} />
                <Line type="monotone" dataKey="count" stroke="#38bdf8" strokeWidth={3} name="Vehicle Count" dot={false} />
                <Line type="monotone" dataKey="duration" stroke="#22c55e" strokeWidth={2} name="Green Time (s)" dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </div>
  );
}