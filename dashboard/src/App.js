import React, { useState, useEffect } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from "recharts";
import "./App.css";

function App() {
  const [latest, setLatest] = useState(null);
  const [history, setHistory] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  const API_BASE = "http://localhost:8000";

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [latestRes, historyRes, statsRes] = await Promise.all([
          fetch(`${API_BASE}/latest`),
          fetch(`${API_BASE}/history/60`),
          fetch(`${API_BASE}/stats`),
        ]);

        const latestData = await latestRes.json();
        const historyData = await historyRes.json();
        const statsData = await statsRes.json();

        setLatest(latestData);
        setHistory(historyData);
        setStats(statsData);
        setLoading(false);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 5000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="container">
        <div className="loading-spinner">
          <div className="spinner"></div>
          <p>Loading real-time data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      <header className="header">
        <div className="header-content">
          <div>
            <h1>Crypto Pipeline</h1>
            <p className="subtitle">
              Real-time BTC monitoring • Kafka → Spark → FastAPI → React
            </p>
          </div>
          <div className="status-badge">
            <span className="status-dot"></span>
            <span>Live</span>
          </div>
        </div>
      </header>

      {latest && (
        <div className="metrics-grid">
          <div className="metric-card primary">
            <div className="metric-header">
              <h3>Current Price</h3>
              <span className="metric-icon">💰</span>
            </div>
            <p className="price">${latest.price?.toFixed(2)}</p>
            <p
              className={`price-change ${latest.price_change > 0 ? "positive" : "negative"}`}
            >
              {latest.price_change > 0 ? "↑" : "↓"}{" "}
              {Math.abs(latest.price_change).toFixed(2)} USD
            </p>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <h3>Moving Average</h3>
              <span className="metric-icon">📈</span>
            </div>
            <p className="metric-value">${latest.moving_average?.toFixed(2)}</p>
            <p className="metric-desc">100-tick rolling average</p>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <h3>Volatility</h3>
              <span className="metric-icon">⚡</span>
            </div>
            <p className="metric-value">{latest.volatility?.toFixed(4)}</p>
            <p className="metric-desc">Standard deviation</p>
          </div>

          <div className="metric-card">
            <div className="metric-header">
              <h3>Last Update</h3>
              <span className="metric-icon">🕐</span>
            </div>
            <p className="metric-value">
              {new Date(latest.timestamp).toLocaleTimeString()}
            </p>
            <p className="metric-desc">Auto-refreshes every 5s</p>
          </div>
        </div>
      )}

      <div className="chart-container">
        <div className="chart-header">
          <h2>Price Chart</h2>
          <p className="chart-desc">
            Last 60 minutes • Real-time streaming data
          </p>
        </div>
        <ResponsiveContainer width="100%" height={450}>
          <AreaChart
            data={history}
            margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
          >
            <defs>
              <linearGradient id="colorPrice" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#ff7300" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#ff7300" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="colorMA" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8} />
                <stop offset="95%" stopColor="#82ca9d" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(ts) =>
                new Date(ts).toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })
              }
              stroke="#999"
            />
            <YAxis domain={["dataMin - 100", "dataMax + 100"]} stroke="#999" />
            <Tooltip
              formatter={(value) => `$${value.toFixed(2)}`}
              labelFormatter={(label) => new Date(label).toLocaleTimeString()}
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #ccc",
                borderRadius: "8px",
              }}
            />
            <Legend wrapperStyle={{ paddingTop: "20px" }} />
            <Area
              type="monotone"
              dataKey="price"
              stroke="#ff7300"
              fillOpacity={1}
              fill="url(#colorPrice)"
              name="BTC Price"
            />
            <Area
              type="monotone"
              dataKey="moving_average"
              stroke="#82ca9d"
              fillOpacity={1}
              fill="url(#colorMA)"
              name="MA (100 ticks)"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {stats && (
        <div className="stats-section">
          <h2>Market Statistics</h2>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <label>Total Records Processed</label>
              <p className="stat-value">
                {stats.total_records?.toLocaleString()}
              </p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📉</div>
              <label>Price Low</label>
              <p className="stat-value">${stats.price_min?.toFixed(2)}</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📈</div>
              <label>Price High</label>
              <p className="stat-value">${stats.price_max?.toFixed(2)}</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">⚖️</div>
              <label>Average Price</label>
              <p className="stat-value">${stats.price_mean?.toFixed(2)}</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📐</div>
              <label>Std Deviation</label>
              <p className="stat-value">${stats.price_std?.toFixed(2)}</p>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🌪️</div>
              <label>Avg Volatility</label>
              <p className="stat-value">{stats.avg_volatility?.toFixed(4)}</p>
            </div>
          </div>
        </div>
      )}

      <footer className="footer">
        <div className="footer-content">
          <p>
            🚀 <strong>Data Pipeline Architecture</strong>
          </p>
          <p>
            Binance WebSocket → Kafka Topic → Spark (Bronze/Gold) → S3 Lakehouse
            → FastAPI → React Dashboard
          </p>
          <p className="tech-stack">
            Built with: Python • Kafka • Apache Spark • AWS S3 • FastAPI • React
            • Docker
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
