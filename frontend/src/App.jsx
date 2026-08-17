import React, { useState, useEffect } from 'react';

const BACKEND_URL = "https://smart-traffic-system-u3el.onrender.com";

export default function App() {
  const [vehicleCount, setVehicleCount] = useState(2);
  const [greenTime, setGreenTime] = useState(15);
  const [congestion, setCongestion] = useState("LOW");
  const [statusMsg, setStatusMsg] = useState("");

  // Periodically fetch dynamic metrics or update state
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate slight dynamic variation for stats
      const randomCount = Math.floor(Math.random() * 8) + 1;
      setVehicleCount(randomCount);
      setGreenTime(Math.min(60, randomCount * 5 + 10));
      setCongestion(randomCount > 5 ? "HIGH" : randomCount > 3 ? "MEDIUM" : "LOW");
    }, 4000);

    return () => clearInterval(interval);
  }, []);

  const triggerEmergency = async () => {
    try {
      setStatusMsg("Sending emergency override signal...");
      const res = await fetch(`${BACKEND_URL}/api/emergency`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lane_id: "Junction Node #1" })
      });
      const data = await res.json();
      if (data.success) {
        setStatusMsg("🚨 EMERGENCY PRIORITY ACTIVATED!");
        setGreenTime(90);
      } else {
        setStatusMsg("Failed to trigger emergency priority.");
      }
    } catch (err) {
      console.error(err);
      setStatusMsg("Error connecting to backend API.");
    }
  };

  return (
    <div style={styles.container}>
      {/* Header Bar */}
      <header style={styles.header}>
        <h1 style={styles.title}>Smart Traffic AI Command Center</h1>
        <button style={styles.emergencyBtn} onClick={triggerEmergency}>
          🛡️ TRIGGER EMERGENCY PRIORITY
        </button>
      </header>

      {statusMsg && <div style={styles.statusBar}>{statusMsg}</div>}

      {/* Top Stat Cards */}
      <div style={styles.statsGrid}>
        <div style={{ ...styles.card, borderLeft: '4px solid #3b82f6' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardIcon}>🚗</span>
            <span style={styles.cardLabel}>Vehicle Count</span>
          </div>
          <div style={styles.cardValue}>{vehicleCount}</div>
        </div>

        <div style={{ ...styles.card, borderLeft: '4px solid #10b981' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardIcon}>⏱️</span>
            <span style={styles.cardLabel}>Adaptive Green Signal</span>
          </div>
          <div style={styles.cardValue}>{greenTime}s</div>
        </div>

        <div style={{ ...styles.card, borderLeft: '4px solid #f59e0b' }}>
          <div style={styles.cardHeader}>
            <span style={styles.cardIcon}>📈</span>
            <span style={styles.cardLabel}>Congestion Level</span>
          </div>
          <div style={{
            ...styles.cardValue,
            color: congestion === "HIGH" ? "#ef4444" : congestion === "MEDIUM" ? "#f59e0b" : "#10b981"
          }}>
            {congestion}
          </div>
        </div>
      </div>

      {/* Content Grid (Camera Feed + Analytics Chart) */}
      <div style={styles.contentGrid}>
        {/* Live Camera Feed Card */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>📹 Live Camera Feed — Junction Node #1</h2>
          <div style={styles.videoWrapper}>
            <img
              src={`${BACKEND_URL}/video_feed`}
              alt="Live Traffic Feed"
              style={styles.videoStream}
              onError={(e) => {
                e.target.style.display = 'none';
                e.target.nextSibling.style.display = 'flex';
              }}
            />
            <div style={styles.videoFallback}>
              <span>🎥 Connecting to Video Feed...</span>
            </div>
          </div>
        </div>

        {/* Realtime Traffic Volume Chart Panel */}
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>📈 Realtime Traffic Volume Trends</h2>
          <div style={styles.chartContainer}>
            <svg viewBox="0 0 500 200" style={styles.svgChart}>
              {/* Grid Lines */}
              <line x1="40" y1="20" x2="480" y2="20" stroke="#1e293b" strokeDasharray="4" />
              <line x1="40" y1="70" x2="480" y2="70" stroke="#1e293b" strokeDasharray="4" />
              <line x1="40" y1="120" x2="480" y2="120" stroke="#1e293b" strokeDasharray="4" />
              <line x1="40" y1="170" x2="480" y2="170" stroke="#334155" />

              {/* Y Axis Labels */}
              <text x="10" y="25" fill="#64748b" fontSize="12">100</text>
              <text x="15" y="75" fill="#64748b" fontSize="12">75</text>
              <text x="15" y="125" fill="#64748b" fontSize="12">50</text>
              <text x="15" y="175" fill="#64748b" fontSize="12">0</text>

              {/* Green Volume Curve */}
              <path
                d="M 40,30 L 120,30 C 140,30 150,150 170,150 C 190,150 200,30 220,30 L 320,30 C 340,30 350,160 370,160 L 480,160"
                fill="none"
                stroke="#10b981"
                strokeWidth="3"
              />

              {/* Blue Secondary Metric Line */}
              <path
                d="M 40,170 Q 100,165 160,155 T 280,170 T 400,160 T 480,165"
                fill="none"
                stroke="#38bdf8"
                strokeWidth="2"
              />

              {/* X Axis Time Labels */}
              <text x="40" y="195" fill="#64748b" fontSize="11">08:32:15 AM</text>
              <text x="150" y="195" fill="#64748b" fontSize="11">08:32:19 AM</text>
              <text x="260" y="195" fill="#64748b" fontSize="11">08:32:22 AM</text>
              <text x="370" y="195" fill="#64748b" fontSize="11">08:32:36 AM</text>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: {
    backgroundColor: '#0b1329',
    minHeight: '100vh',
    color: '#ffffff',
    fontFamily: 'Inter, system-ui, -apple-system, sans-serif',
    padding: '24px',
    boxSizing: 'border-box'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  },
  title: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#38bdf8',
    margin: 0
  },
  emergencyBtn: {
    backgroundColor: '#1d4ed8',
    color: '#ffffff',
    border: '1px solid #60a5fa',
    borderRadius: '8px',
    padding: '12px 20px',
    fontWeight: '700',
    fontSize: '13px',
    cursor: 'pointer',
    letterSpacing: '0.5px',
    boxShadow: '0 4px 12px rgba(29, 78, 216, 0.4)'
  },
  statusBar: {
    backgroundColor: '#1e293b',
    border: '1px solid #3b82f6',
    color: '#38bdf8',
    padding: '10px 16px',
    borderRadius: '6px',
    marginBottom: '20px',
    fontSize: '14px',
    textAlign: 'center'
  },
  statsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
    gap: '20px',
    marginBottom: '24px'
  },
  card: {
    backgroundColor: '#131e3a',
    borderRadius: '10px',
    padding: '20px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)'
  },
  cardHeader: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    marginBottom: '12px'
  },
  cardIcon: {
    fontSize: '18px'
  },
  cardLabel: {
    color: '#94a3b8',
    fontSize: '15px',
    fontWeight: '500'
  },
  cardValue: {
    fontSize: '32px',
    fontWeight: '800',
    color: '#ffffff',
    marginLeft: '26px'
  },
  contentGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))',
    gap: '20px'
  },
  panel: {
    backgroundColor: '#131e3a',
    borderRadius: '10px',
    padding: '20px',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.3)'
  },
  panelTitle: {
    fontSize: '16px',
    fontWeight: '600',
    color: '#38bdf8',
    marginTop: 0,
    marginBottom: '16px'
  },
  videoWrapper: {
    width: '100%',
    height: '280px',
    backgroundColor: '#000000',
    borderRadius: '8px',
    overflow: 'hidden',
    position: 'relative'
  },
  videoStream: {
    width: '100%',
    height: '100%',
    objectFit: 'cover',
    display: 'block'
  },
  videoFallback: {
    display: 'none',
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    color: '#94a3b8'
  },
  chartContainer: {
    width: '100%',
    height: '280px',
    display: 'flex',
    alignItems: 'center'
  },
  svgChart: {
    width: '100%',
    height: '100%'
  }
};