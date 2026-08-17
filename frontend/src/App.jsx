import React, { useState, useEffect } from 'react';
import './App.css';

// Production Backend API URL on Render
const API_BASE_URL = "https://smart-traffic-system-u3el.onrender.com";

function App() {
  const [trafficData, setTrafficData] = useState({
    vehicle_count: 0,
    signal_status: 'GREEN',
    active_lane: 'Lane 1',
    emergency_active: false
  });
  const [loading, setLoading] = useState(false);
  const [overrideMessage, setOverrideMessage] = useState('');

  // Check backend health status on component mount
  useEffect(() => {
    fetch(`${API_BASE_URL}/api/health`)
      .then((res) => res.json())
      .then((data) => console.log('Backend connected:', data))
      .catch((err) => console.error('Error connecting to Render backend:', err));
  }, []);

  // Trigger Emergency Priority Override
  const handleEmergencyOverride = async (laneId) => {
    setLoading(true);
    setOverrideMessage('');
    try {
      const response = await fetch(`${API_BASE_URL}/api/emergency`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ lane_id: laneId }),
      });
      const result = await response.json();
      if (result.success) {
        setOverrideMessage(`Emergency priority override activated for ${laneId}!`);
      } else {
        setOverrideMessage('Failed to activate emergency override.');
      }
    } catch (error) {
      console.error('Error triggering emergency override:', error);
      setOverrideMessage('Network error triggering emergency mode.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app-container">
      <header className="dashboard-header">
        <h1>Smart AI & IoT Traffic Command Center</h1>
        <p className="status-badge">
          Backend API: <a href={API_BASE_URL} target="_blank" rel="noreferrer">{API_BASE_URL}</a>
        </p>
      </header>

      <main className="dashboard-grid">
        {/* Live Video Feed Section */}
        <section className="card video-card">
          <h2>Live Computer Vision Feed</h2>
          <div className="video-wrapper">
            <img 
              src={`${API_BASE_URL}/video_feed`} 
              alt="Live Traffic AI Camera Feed" 
              className="video-stream"
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "https://via.placeholder.com/640x360?text=Live+AI+Feed+Offline+(Run+traffic_ai.py+Locally)";
              }}
            />
          </div>
        </section>

        {/* Emergency Priority Control Section */}
        <section className="card control-card">
          <h2>Emergency Priority Controls</h2>
          <p>Click below to grant emergency green wave override for priority vehicles:</p>
          
          <div className="button-group">
            <button 
              className="btn btn-emergency" 
              onClick={() => handleEmergencyOverride('Lane 1')}
              disabled={loading}
            >
              Override Lane 1
            </button>
            <button 
              className="btn btn-emergency" 
              onClick={() => handleEmergencyOverride('Lane 2')}
              disabled={loading}
            >
              Override Lane 2
            </button>
          </div>

          {overrideMessage && (
            <div className="alert-box">
              {overrideMessage}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;