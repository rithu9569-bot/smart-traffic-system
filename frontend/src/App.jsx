import React, { useState, useEffect } from 'react';

const BACKEND_URL = "https://smart-traffic-system-u3el.onrender.com";

export default function App() {
  const [vehicleCount, setVehicleCount] = useState(2);
  const [greenTime, setGreenTime] = useState(15);
  const [congestion, setCongestion] = useState("LOW");
  const [statusMsg, setStatusMsg] = useState("");
  const [isEmergency, setIsEmergency] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      if (!isEmergency) {
        const randomCount = Math.floor(Math.random() * 8) + 1;
        setVehicleCount(randomCount);
        setGreenTime(Math.min(60, randomCount * 5 + 10));
        setCongestion(randomCount > 5 ? "HIGH" : randomCount > 3 ? "MEDIUM" : "LOW");
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [isEmergency]);

  const triggerEmergency = async () => {
    setIsEmergency(true);
    setStatusMsg("🚨 EMERGENCY OVERRIDE ACTIVATED — GREEN WAVE GRANTED FOR JUNCTION NODE #1");
    setGreenTime(90);
    setCongestion("LOW");

    try {
      await fetch(`${BACKEND_URL}/api/emergency`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lane_id: "Junction Node #1" })
      });
    } catch (err) {
      console.error("Backend request error:", err);
    }

    setTimeout(() => {
      setIsEmergency(false);
      setStatusMsg("");
    }, 10000);
  };

  const exportCSV = () => {
    const timestamp = new Date().toISOString();
    const csvContent = `data:text/csv;charset=utf-8,Timestamp,Junction,Vehicle_Count,Green_Signal_Sec,Congestion_Level\n${timestamp},Junction Node #1,${vehicleCount},${greenTime},${congestion}\n`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `traffic_report_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <h1 style={styles.title}>Smart Traffic AI Command Center</h1>
        <div style={styles.headerBtns}>
          <button style={styles.csvBtn} onClick={exportCSV}>
            📥 EXPORT CSV REPORT
          </button>
          <button 
            style={{
              ...styles.emergencyBtn,
              backgroundColor: isEmergency ? '#dc2626' : '#1d4ed8',
              borderColor: isEmergency ? '#fca5a5' : '#60a5fa'
            }} 
            onClick={triggerEmergency}
          >
            🛡️ TRIGGER EMERGENCY PRIORITY
          </button>
        </div>
      </header>

      {statusMsg && (
        <div style={{
          ...styles.statusBar,
          backgroundColor: isEmergency ? '#7f1d1d' : '#1e293b',
          color: isEmergency ? '#fecaca' : '#38bdf8'
        }}>
          {statusMsg}
        </div>
      )}

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

      <div style={styles.contentGrid}>
        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>📹 Live Camera Feed — Junction Node #1</h2>
          <div style={styles.videoWrapper}>
            <video
              src={`${import.meta.env.BASE_URL}sample_traffic.mp4`}
              autoPlay
              loop
              muted
              playsInline
              controls
              style={styles.videoStream}
            />
          </div>
        </div>

        <div style={styles.panel}>
          <h2 style={styles.panelTitle}>📈 Realtime Traffic Volume Trends</h2>
          <div style={styles.chartContainer}>
            <svg viewBox="0 0 500 200" style={styles.svgChart}>
              <line x1="40" y1="20" x2="480" y2="20" stroke="#1e293b" strokeDasharray="4" />
              <line x1="40" y1="70" x2="480" y2="70" stroke="#1e293b" strokeDasharray="4" />
              <line x1="40" y1="120" x2="480" y2="120" stroke="#1e293b" strokeDasharray="4" />
              <line x1="40" y1="170" x2="480" y2="170" stroke="#334155" />

              <text x="10" y="25" fill="#64748b" fontSize="12">100</text>
              <text x="15" y="75" fill="#64748b" fontSize="12">75</text>
              <text x="15" y="125" fill="#64748b" fontSize="12">50</text>
              <text x="15" y="175" fill="#64748b" fontSize="12">0</text>

              <path
                d="M 40,30 L 120,30 C 140,30 150,150 170,150 C 190,150 200,30 220,30 L 320,30 C 340,30 350,160 370,160 L 480,160"
                fill="none"
                stroke="#10b981"
                strokeWidth="3"
              />
              <path
                d="M 40,170 Q 100,165 160,155 T 280,170 T 400,160 T 480,165"
                fill="none"
                stroke="#38bdf8"
                strokeWidth="2"
              />

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
    marginBottom: '24px',
    flexWrap: 'wrap',
    gap: '12px'
  },
  title: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#38bdf8',
    margin: 0
  },
  headerBtns: {
    display: 'flex',
    gap: '12px'
  },
  csvBtn: {
    backgroundColor: '#059669',
    color: '#ffffff',
    border: '1px solid #34d399',
    borderRadius: '8px',
    padding: '12px 18px',
    fontWeight: '700',
    fontSize: '13px',
    cursor: 'pointer',
    boxShadow: '0 4px 12px rgba(5, 150, 105, 0.3)'
  },
  emergencyBtn: {
    color: '#ffffff',
    border: '1px solid',
    borderRadius: '8px',
    padding: '12px 20px',
    fontWeight: '700',
    fontSize: '13px',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    boxShadow: '0 4px 12px rgba(29, 78, 216, 0.4)'
  },
  statusBar: {
    border: '1px solid #3b82f6',
    padding: '12px 16px',
    borderRadius: '6px',
    marginBottom: '20px',
    fontSize: '14px',
    fontWeight: '600',
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
    overflow: 'hidden'
  },
  videoStream: {
    width: '100%',
    height: '100%',
    objectFit: 'cover'
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