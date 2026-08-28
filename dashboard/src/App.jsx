import { useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const normalStyle = {
  width: 190,
  padding: 18,
  border: "2px solid #16a34a",
  borderRadius: 12,
  background: "#f0fdf4",
  textAlign: "center",
  fontWeight: "600",
};

const warningStyle = {
  width: 190,
  padding: 18,
  border: "2px solid #dc2626",
  borderRadius: 12,
  background: "#fef2f2",
  textAlign: "center",
  fontWeight: "600",
};

function App() {
  const [pipelineStatus, setPipelineStatus] = useState("HEALTHY");

  const isHealthy = pipelineStatus === "HEALTHY";

  const nodes = [
    {
      id: "kafka",
      position: { x: 50, y: 220 },
      data: {
        label: (
          <div>
            <div>📥 INGEST</div>
            <small>Apache Kafka</small>
            <br />
            <small>Streaming Input</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "flink",
      position: { x: 350, y: 220 },
      data: {
        label: (
          <div>
            <div>{isHealthy ? "⚙️" : "🚨"} PROCESS</div>
            <small>Apache Flink</small>
            <br />
            <small>
              {isHealthy ? "Processing" : "QUARANTINED"}
            </small>
          </div>
        ),
      },
      style: isHealthy ? normalStyle : warningStyle,
    },

    {
      id: "iceberg",
      position: { x: 650, y: 220 },
      data: {
        label: (
          <div>
            <div>🗄️ SERVE</div>
            <small>Apache Iceberg</small>
            <br />
            <small>
              {isHealthy ? "Lakehouse" : "Pipeline Paused"}
            </small>
          </div>
        ),
      },
      style: isHealthy ? normalStyle : warningStyle,
    },

    {
      id: "quarantine",
      position: { x: 350, y: 450 },
      data: {
        label: (
          <div>
            <div>🛑 QUARANTINE</div>
            <small>Bad Data / DLQ</small>
          </div>
        ),
      },
      style: warningStyle,
    },
  ];

  const edges = [
    {
      id: "kafka-flink",
      source: "kafka",
      target: "flink",
      animated: isHealthy,
    },

    {
      id: "flink-iceberg",
      source: "flink",
      target: "iceberg",
      animated: isHealthy,
    },

    {
      id: "flink-quarantine",
      source: "flink",
      target: "quarantine",
      animated: !isHealthy,
    },
  ];

  const togglePipeline = () => {
    setPipelineStatus(
      isHealthy ? "QUARANTINED" : "HEALTHY"
    );
  };

  return (
    <div className="dashboard">

      {/* HEADER */}
      <header className="dashboard-header">

        <div>
          <div className="brand">
            <span className="brand-mark">IS</span>

            <div>
              <h1>IceStream</h1>
              <p>Real-Time Lakehouse Observability</p>
            </div>
          </div>
        </div>

        <div
          className={`status-pill ${
            isHealthy ? "healthy" : "danger"
          }`}
        >
          <span className="status-dot"></span>
          {pipelineStatus}
        </div>

      </header>

      {/* TOP INFORMATION */}
      <section className="top-grid">

        <div className="info-card">
          <span className="card-label">PIPELINE</span>
          <strong>IceStream</strong>
          <span className="muted">
            Real-time data platform
          </span>
        </div>

        <div className="info-card">
          <span className="card-label">PROCESSING</span>
          <strong>{isHealthy ? "ACTIVE" : "PAUSED"}</strong>
          <span className="muted">
            Automated protection
          </span>
        </div>

        <div className="info-card">
          <span className="card-label">DATA QUALITY</span>
          <strong>{isHealthy ? "GOOD" : "14%"}</strong>
          <span className="muted">
            Error rate monitoring
          </span>
        </div>

        <button
          className={`simulation-button ${
            isHealthy ? "simulate" : "restore"
          }`}
          onClick={togglePipeline}
        >
          {isHealthy
            ? "⚠ Simulate Data Anomaly"
            : "✓ Restore Pipeline"}
        </button>

      </section>

      {/* ALERT */}
      {!isHealthy && (
        <section className="alert-banner">

          <div className="alert-icon">!</div>

          <div>
            <strong>Pipeline protection activated</strong>

            <p>
              Data quality error rate exceeded the configured
              2% threshold. Pipeline processing has been paused
              and bad records have been quarantined.
            </p>
          </div>

          <div className="alert-action">
            PAUSE
          </div>

        </section>
      )}

      {/* KPI SECTION */}
      <section className="section">

        <div className="section-heading">
          <div>
            <span className="eyebrow">OBSERVABILITY</span>
            <h2>Pipeline Health</h2>
            <p>Latest pipeline snapshot</p>
          </div>

          <span className="live-badge">
            ● LIVE
          </span>
        </div>

        <div className="kpi-grid">

          <div className="kpi-card">
            <span className="kpi-icon">Σ</span>
            <span className="kpi-label">PROCESSED RECORDS</span>
            <strong>100</strong>
            <small>Total records processed</small>
          </div>

          <div className="kpi-card">
            <span className="kpi-icon">✓</span>
            <span className="kpi-label">VALID RECORDS</span>
            <strong>86</strong>
            <small>Passed validation</small>
          </div>

          <div className="kpi-card danger-card">
            <span className="kpi-icon">!</span>
            <span className="kpi-label">INVALID RECORDS</span>
            <strong>14</strong>
            <small>Failed validation</small>
          </div>

          <div className="kpi-card danger-card">
            <span className="kpi-icon">%</span>
            <span className="kpi-label">ERROR RATE</span>
            <strong>14%</strong>
            <small>Threshold: 2%</small>
          </div>

        </div>

      </section>

      {/* MAIN GRID */}
      <section className="main-grid">

        {/* CIRCUIT BREAKER */}
        <div className="panel">

          <div className="panel-header">
            <div>
              <span className="eyebrow">PROTECTION</span>
              <h2>Pipeline Protection</h2>
            </div>

            <span className="panel-icon">⚡</span>
          </div>

          <div className="protection-status">
            <span
              className={`large-status ${
                isHealthy ? "green" : "red"
              }`}
            >
              {isHealthy ? "CLOSED" : "OPEN"}
            </span>

            <span className="muted">
              Circuit Breaker
            </span>
          </div>

          <div className="metric-row">
            <span>Error Rate</span>
            <strong>14%</strong>
          </div>

          <div className="metric-row">
            <span>Configured Threshold</span>
            <strong>2%</strong>
          </div>

          <div className="metric-row">
            <span>Pipeline Action</span>
            <strong>PAUSE</strong>
          </div>

          <div className="metric-row">
            <span>Remediation</span>
            <strong>QUARANTINE</strong>
          </div>

        </div>

        {/* BUSINESS ANALYTICS */}
        <div className="panel">

          <div className="panel-header">
            <div>
              <span className="eyebrow">GOLD LAYER</span>
              <h2>Business Analytics</h2>
            </div>

            <span className="panel-icon">₹</span>
          </div>

          <div className="analytics-grid">

            <div>
              <span>TRANSACTIONS</span>
              <strong>5</strong>
            </div>

            <div>
              <span>QUANTITY</span>
              <strong>10</strong>
            </div>

            <div>
              <span>TOTAL REVENUE</span>
              <strong>₹5,000</strong>
            </div>

            <div>
              <span>AVG ORDER VALUE</span>
              <strong>₹1,000</strong>
            </div>

          </div>

        </div>

      </section>

      {/* PRODUCT + INCIDENT */}
      <section className="main-grid">

        <div className="panel">

          <div className="panel-header">
            <div>
              <span className="eyebrow">ANALYTICS</span>
              <h2>Product Performance</h2>
            </div>

            <span className="panel-icon">★</span>
          </div>

          <div className="product-highlight">

            <div className="product-rank">
              #1
            </div>

            <div>
              <span>TOP PRODUCT</span>
              <strong>PRD-001</strong>
              <small>
                Revenue: ₹5,000
              </small>
            </div>

          </div>

          <div className="metric-row">
            <span>Unique Products</span>
            <strong>1</strong>
          </div>

          <div className="metric-row">
            <span>Avg. Quantity / Transaction</span>
            <strong>2.0</strong>
          </div>

        </div>

        <div className="panel">

          <div className="panel-header">
            <div>
              <span className="eyebrow">INCIDENT MANAGEMENT</span>
              <h2>Recent Incidents</h2>
            </div>

            <span className="panel-icon">⚠</span>
          </div>

          <div className="incident-list">

            <div className="incident">
              <span>08:59</span>
              <b>OPEN</b>
              <span>14%</span>
              <span>PAUSE</span>
              <strong>QUARANTINE</strong>
            </div>

            <div className="incident">
              <span>08:57</span>
              <b>OPEN</b>
              <span>3%</span>
              <span>PAUSE</span>
              <strong>QUARANTINE</strong>
            </div>

            <div className="incident">
              <span>08:55</span>
              <b>OPEN</b>
              <span>3%</span>
              <span>PAUSE</span>
              <strong>QUARANTINE</strong>
            </div>

          </div>

        </div>

      </section>

      {/* ARCHITECTURE */}
      <section className="architecture-section">

        <div className="section-heading">

          <div>
            <span className="eyebrow">SYSTEM ARCHITECTURE</span>
            <h2>IceStream Data Pipeline</h2>
            <p>
              End-to-end real-time lakehouse architecture
            </p>
          </div>

          <span className="architecture-badge">
            8 STAGES
          </span>

        </div>

        <div className="flow-container">

          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            nodesDraggable={false}
            nodesConnectable={false}
            zoomOnScroll={true}
          >
            <Controls />
            <MiniMap />
            <Background gap={20} size={1} />
          </ReactFlow>

        </div>

      </section>

      {/* FOOTER */}
      <footer>

        <div>
          <strong>IceStream</strong>
          <span>
            Real-Time Lakehouse Observability Platform
          </span>
        </div>

        <div className="footer-tags">
          <span>DATA QUALITY</span>
          <span>ANALYTICS</span>
          <span>AUTOMATED PROTECTION</span>
        </div>

      </footer>

    </div>
  );
}

export default App;