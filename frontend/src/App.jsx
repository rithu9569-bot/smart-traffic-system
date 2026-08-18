import React, { useState, useEffect } from 'react';

const BACKEND_URL = "https://smart-traffic-system-1-pqtm.onrender.com";

export default function App() {
  const [selectedJunction, setSelectedJunction] = useState("node_1");
  const [vehicleCount, setVehicleCount] = useState(0);
  const [greenTime, setGreenTime] = useState(15);
  const [congestion, setCongestion] = useState("LOW");
  const [statusMsg, setStatusMsg] = useState("");
  const [isEmergency, setIsEmergency] = useState(false);

  const [trendHistory, setTrendHistory] = useState([]);

  useEffect(() => {
    const fetchStats = async () => {
      if (isEmergency) return;

      try {
        const res = await fetch(`${BACKEND_URL}/api/stats?junction=${selectedJunction}`);
        if (res.ok) {
          const data = await res.json();
          setVehicleCount(data.vehicle_count);
          setGreenTime(data.green_time);
          setCongestion(data.congestion);

          const timeStr = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
          setTrendHistory(prev => {
            const updated = [...prev, { time: timeStr, count: data.vehicle_count, green: data.green_time }];
            return updated.length > 10 ? updated.slice(1) : updated;
          });
        }
      } catch (err) {
        console.error("API error:", err);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 500);
    return () => clearInterval(interval);
  }, [selectedJunction, isEmergency]);

  const triggerEmergency = async () => {
    setIsEmergency(true);
    setStatusMsg(`🚨 EMERGENCY OVERRIDE ACTIVATED — GREEN WAVE GRANTED FOR ${selectedJunction.toUpperCase()}`);
    setGreenTime(90);
    setCongestion("LOW");

    try {
      await fetch(`${BACKEND_URL}/api/emergency`, { method: 'POST' });
    } catch (err) {
      console.error(err);
    }

    setTimeout(() => {
      setIsEmergency(false);
      setStatusMsg("");
    }, 10000);
  };

  const exportCSV = () => {
    const timestamp = new Date().toISOString();
    const csvContent = `data:text/csv;charset=utf-8,Timestamp,Junction,Vehicle_Count,Green_Signal_Sec,Congestion_Level\n${timestamp},${selectedJunction},${vehicleCount},${greenTime},${congestion}\n`;
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `traffic_report_${selectedJunction}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const printPDFReport = () => {
    window.print();
  };

  const generatePath = (key, maxVal) => {
    if (trendHistory.length < 2) return "";
    const startX = 40;
    const endX = 460;
    const step = (endX - startX) / (trendHistory.length - 1);

    return trendHistory.map((pt, i) => {
      const x = startX + i * step;
      const y = 170 - (pt[key] / maxVal) * 140;
      return `${i === 0 ? 'M' : 'L'} ${x},${Math.max(20, Math.min(170, y))}`;
    }).join(' ');
  };

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Smart Traffic AI Command Center</h1>
          <div style={styles.selectWrapper}>
            <label style={styles.selectLabel}>Select Junction: </label>
            <select
              value={selectedJunction}
              onChange={(e) => {
                setSelectedJunction(e.target.value);
                setTrendHistory([]);
              }}
              style={styles.select}
            >
              <option value="node_1">Junction Node #1 (Highway North)</option>
              <option value="node_2">Junction Node #2 (Downtown Ave)</option>
              <option value="node_3">Junction Node #3 (Express Way Exit)</option>
            </select>
          </div>
        </div>

        <div style={styles.headerBtns}>
          <button style={styles.csvBtn} onClick={exportCSV}>
            📥 EXPORT CSV REPORT
          </button>
          <button style={styles.pdfBtn} onClick={printPDFReport}>
            📄 PRINT PDF REPORT
          </button>
          <button 
            style={{
              ...styles.emergencyBtn,
              backgroundColor: isEmergency ? '#dc2626' : '#1d4ed8',
              borderColor: isEmergency ? '#fca5a5' : '#60a5fa'
            }} 
            onClick={triggerEmergency}
          >
            🛡️ EMERGENCY PRIORITY
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
          <h2 style={styles.panelTitle}>📹 Live Camera Feed — {selectedJunction.toUpperCase()}</h2>
          <div style={styles.videoWrapper}>
            <img
              src={`${BACKEND_URL}/video_feed?junction=${selectedJunction}`}
              alt="Live AI Traffic Feed"
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

              <text x="5" y="25" fill="#64748b" fontSize="10">100 (Sec)</text>
              <text x="5" y="75" fill="#64748b" fontSize="10">50</text>
              <text x="5" y="125" fill="#64748b" fontSize="10">25 (Cars)</text>
              <text x="15" y="175" fill="#64748b" fontSize="10">0</text>

              <path
                d={generatePath('green', 100)}
                fill="none"
                stroke="#10b981"
                strokeWidth="3"
              />
              <path
                d={generatePath('count', 25)}
                fill="none"
                stroke="#38bdf8"
                strokeWidth="3"
              />

              {trendHistory.map((pt, i) => {
                const step = (420) / (trendHistory.length - 1 || 1);
                return (
                  <text key={i} x={40 + i * step - 15} y="193" fill="#64748b" fontSize="9">
                    {pt.time}
                  </text>
                );
              })}
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  container: { backgroundColor: '#0b1329', minHeight: '100vh', color: '#ffffff', fontFamily: 'Inter, system-ui, sans-serif', padding: '24px', boxSizing: 'border-box' },
  header: { display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px', flexWrap: 'wrap', gap: '12px' },
  title: { fontSize: '24px', fontWeight: '700', color: '#38bdf8', margin: 0 },
  selectWrapper: { marginTop: '8px', display: 'flex', alignItems: 'center', gap: '8px' },
  selectLabel: { fontSize: '14px', color: '#94a3b8' },
  select: { backgroundColor: '#131e3a', color: '#38bdf8', border: '1px solid #1e293b', borderRadius: '6px', padding: '6px 12px', fontWeight: '600', cursor: 'pointer' },
  headerBtns: { display: 'flex', gap: '10px', flexWrap: 'wrap' },
  csvBtn: { backgroundColor: '#059669', color: '#ffffff', border: '1px solid #34d399', borderRadius: '8px', padding: '10px 16px', fontWeight: '700', fontSize: '12px', cursor: 'pointer' },
  pdfBtn: { backgroundColor: '#4f46e5', color: '#ffffff', border: '1px solid #818cf8', borderRadius: '8px', padding: '10px 16px', fontWeight: '700', fontSize: '12px', cursor: 'pointer' },
  emergencyBtn: { color: '#ffffff', border: '1px solid', borderRadius: '8px', padding: '10px 18px', fontWeight: '700', fontSize: '12px', cursor: 'pointer', transition: 'all 0.3s ease' },
  statusBar: { border: '1px solid #3b82f6', padding: '12px 16px', borderRadius: '6px', marginBottom: '20px', fontSize: '14px', fontWeight: '600', textAlign: 'center' },
  statsGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px', marginBottom: '24px' },
  card: { backgroundColor: '#131e3a', borderRadius: '10px', padding: '20px' },
  cardHeader: { display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' },
  cardIcon: { fontSize: '18px' },
  cardLabel: { color: '#94a3b8', fontSize: '15px', fontWeight: '500' },
  cardValue: { fontSize: '32px', fontWeight: '800', color: '#ffffff', marginLeft: '26px' },
  contentGrid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(420px, 1fr))', gap: '20px' },
  panel: { backgroundColor: '#131e3a', borderRadius: '10px', padding: '20px' },
  panelTitle: { fontSize: '16px', fontWeight: '600', color: '#38bdf8', marginTop: 0, marginBottom: '16px' },
  videoWrapper: { width: '100%', height: '280px', backgroundColor: '#000000', borderRadius: '8px', overflow: 'hidden', display: 'flex', justifyContent: 'center', alignItems: 'center' },
  videoStream: { width: '100%', height: '100%', objectFit: 'contain' },
  chartContainer: { width: '100%', height: '280px', display: 'flex', alignItems: 'center' },
  svgChart: { width: '100%', height: '100%' }
};