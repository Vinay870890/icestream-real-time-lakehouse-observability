import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const API = "http://127.0.0.1:8000";

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

const breakerClosedStyle = {
  width: 190,
  padding: 18,
  border: "2px solid #2563eb",
  borderRadius: 12,
  background: "#eff6ff",
  textAlign: "center",
  fontWeight: "600",
};

async function fetchJSON(endpoint) {
  const response = await fetch(`${API}${endpoint}`);

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

function App() {
  const [status, setStatus] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [kpis, setKpis] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [apiError, setApiError] = useState("");

  const loadDashboard = async (manual = false) => {
    if (manual) {
      setRefreshing(true);
    }

    try {
      const [
        statusData,
        metricsData,
        kpiData,
        incidentData,
      ] = await Promise.all([
        fetchJSON("/api/status"),
        fetchJSON("/api/metrics"),
        fetchJSON("/api/kpis"),
        fetchJSON("/api/incidents"),
      ]);

      setStatus(statusData);
      setMetrics(metricsData);
      setKpis(kpiData);
      setIncidents(incidentData.incidents || []);
      setApiError("");
    } catch (error) {
      console.error(error);

      setApiError(
        "Unable to connect to IceStream API. Make sure FastAPI is running on port 8000."
      );
    } finally {
      setLoading(false);

      if (manual) {
        setRefreshing(false);
      }
    }
  };

  useEffect(() => {
    loadDashboard();

    const interval = setInterval(() => {
      loadDashboard();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const isHealthy =
    status?.status === "CLOSED" ||
    status?.status === "HEALTHY";

  const pipelineStatus = isHealthy
    ? "HEALTHY"
    : "QUARANTINED";

  const errorRate = Number(
    metrics?.error_rate ??
      status?.error_rate ??
      0
  );

  const threshold = Number(
    status?.threshold ?? 0.02
  );

  const errorRatePercent =
    errorRate <= 1
      ? errorRate * 100
      : errorRate;

  const thresholdPercent =
    threshold <= 1
      ? threshold * 100
      : threshold;

  const nodes = useMemo(
    () => [
      {
        id: "kafka",
        position: { x: 40, y: 180 },
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
        position: { x: 300, y: 180 },
        data: {
          label: (
            <div>
              <div>
                {isHealthy ? "⚙️" : "🚨"} PROCESS
              </div>
              <small>Apache Flink</small>
              <br />
              <small>
                {isHealthy
                  ? "Processing"
                  : "Data Quality Failure"}
              </small>
            </div>
          ),
        },
        style: isHealthy
          ? normalStyle
          : warningStyle,
      },
      {
        id: "breaker",
        position: { x: 560, y: 180 },
        data: {
          label: (
            <div>
              <div>
                {isHealthy ? "🛡️" : "🚨"} CIRCUIT BREAKER
              </div>
              <small>
                {isHealthy ? "CLOSED" : "OPEN"}
              </small>
              <br />
              <small>
                {isHealthy
                  ? "Pipeline Allowed"
                  : "Pipeline Paused"}
              </small>
            </div>
          ),
        },
        style: isHealthy
          ? breakerClosedStyle
          : warningStyle,
      },
      {
        id: "iceberg",
        position: { x: 820, y: 80 },
        data: {
          label: (
            <div>
              <div>🗄️ SERVE</div>
              <small>Apache Iceberg</small>
              <br />
              <small>
                {isHealthy
                  ? "Lakehouse Active"
                  : "PAUSED"}
              </small>
            </div>
          ),
        },
        style: isHealthy
          ? normalStyle
          : warningStyle,
      },
      {
        id: "quarantine",
        position: { x: 820, y: 300 },
        data: {
          label: (
            <div>
              <div>🛑 QUARANTINE</div>
              <small>Bad Data / DLQ</small>
              <br />
              <small>
                {isHealthy
                  ? "Standby"
                  : "Bad Records Isolated"}
              </small>
            </div>
          ),
        },
        style: warningStyle,
      },
    ],
    [isHealthy]
  );

  const edges = useMemo(
    () => [
      {
        id: "kafka-flink",
        source: "kafka",
        target: "flink",
        animated: true,
        label: "STREAM",
      },
      {
        id: "flink-breaker",
        source: "flink",
        target: "breaker",
        animated: true,
        label: isHealthy
          ? "VALIDATE"
          : "DQ FAILURE",
      },
      {
        id: "breaker-iceberg",
        source: "breaker",
        target: "iceberg",
        animated: isHealthy,
        label: isHealthy ? "ALLOW" : "BLOCK",
      },
      {
        id: "breaker-quarantine",
        source: "breaker",
        target: "quarantine",
        animated: !isHealthy,
        label: !isHealthy
          ? "QUARANTINE"
          : "STANDBY",
      },
    ],
    [isHealthy]
  );

  if (loading) {
    return (
      <div className="loading-screen">
        <h1>IceStream</h1>
        <p>Connecting to observability backend...</p>
      </div>
    );
  }

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>IceStream</h1>
          <p>Real-Time Lakehouse Observability</p>
        </div>

        <div className="header-actions">
          <button
            type="button"
            onClick={() => loadDashboard(true)}
            disabled={refreshing}
            style={{
              border: "1px solid rgba(255,255,255,0.35)",
              background: "rgba(255,255,255,0.12)",
              color: "#fff",
              padding: "9px 14px",
              borderRadius: "9px",
              cursor: refreshing ? "wait" : "pointer",
              fontWeight: "600",
              marginRight: "10px",
            }}
          >
            {refreshing ? "↻ Refreshing..." : "↻ Refresh Now"}
          </button>

          <div
            className={`status-badge ${
              isHealthy ? "healthy" : "danger"
            }`}
          >
            ● {pipelineStatus}
          </div>
        </div>
      </header>

      {apiError && (
        <div className="api-error">
          ⚠️ {apiError}
        </div>
      )}

      <section className="hero">
        <div>
          <span className="eyebrow">LIVE MONITORING</span>
          <h2>Pipeline Observability</h2>
          <p>
            Real-time health monitoring and automated
            data-quality protection.
          </p>
        </div>

        <div className="refresh">
          ● Live · Refreshing every 5 seconds
        </div>
      </section>

      <section className="kpi-grid">
        <div className="card">
          <span>Pipeline Status</span>
          <strong className={isHealthy ? "green" : "red"}>
            {pipelineStatus}
          </strong>
          <small>{status?.action || "UNKNOWN"}</small>
        </div>

        <div className="card">
          <span>Error Rate</span>
          <strong className="red">
            {errorRatePercent.toFixed(2)}%
          </strong>
          <small>
            Threshold: {thresholdPercent.toFixed(2)}%
          </small>
        </div>

        <div className="card">
          <span>Processed</span>
          <strong>{metrics?.total_records ?? 0}</strong>
          <small>
            Valid: {metrics?.valid_records ?? 0}
          </small>
        </div>

        <div className="card">
          <span>Invalid Records</span>
          <strong className="red">
            {metrics?.invalid_records ?? 0}
          </strong>
          <small>Quarantine protected</small>
        </div>
      </section>

      <section className="analytics-grid">
        <div className="panel">
          <h3>Business Analytics</h3>

          <div className="metric-list">
            <div>
              <span>Transactions</span>
              <strong>
                {kpis?.total_transactions ?? 0}
              </strong>
            </div>

            <div>
              <span>Quantity</span>
              <strong>
                {kpis?.total_quantity ?? 0}
              </strong>
            </div>

            <div>
              <span>Revenue</span>
              <strong>
                ₹
                {Number(
                  kpis?.total_revenue ?? 0
                ).toLocaleString()}
              </strong>
            </div>

            <div>
              <span>Average Order Value</span>
              <strong>
                ₹
                {Number(
                  kpis?.average_order_value ?? 0
                ).toLocaleString()}
              </strong>
            </div>
          </div>
        </div>

        <div className="panel">
          <h3>Pipeline Protection</h3>

          <div className="protection">
            <div
              className={
                isHealthy
                  ? "protection-ok"
                  : "protection-danger"
              }
            >
              {isHealthy ? "● CLOSED" : "● OPEN"}
            </div>

            <p>
              Error Rate:{" "}
              <strong>
                {errorRatePercent.toFixed(2)}%
              </strong>
            </p>

            <p>
              Threshold:{" "}
              <strong>
                {thresholdPercent.toFixed(2)}%
              </strong>
            </p>

            <p>
              Action:{" "}
              <strong>
                {status?.action || "UNKNOWN"}
              </strong>
            </p>

            <p>
              Reason:{" "}
              {status?.reason || "No reason available"}
            </p>
          </div>
        </div>

        <div className="panel">
          <h3>Product Analytics</h3>

          <div className="metric-list">
            <div>
              <span>Top Product</span>
              <strong>
                {kpis?.top_product || "N/A"}
              </strong>
            </div>

            <div>
              <span>Product Revenue</span>
              <strong>
                ₹
                {Number(
                  kpis?.top_product_revenue ?? 0
                ).toLocaleString()}
              </strong>
            </div>

            <div>
              <span>Unique Products</span>
              <strong>
                {kpis?.unique_products ?? 0}
              </strong>
            </div>

            <div>
              <span>Avg Quantity / Transaction</span>
              <strong>
                {kpis?.average_quantity_per_transaction ?? 0}
              </strong>
            </div>
          </div>
        </div>
      </section>

      <section className="panel architecture">
        <div className="section-heading">
          <div>
            <span className="eyebrow">DATA FLOW</span>
            <h3>Live Pipeline Architecture</h3>
          </div>

          <span className="live-indicator">● LIVE</span>
        </div>

        <div className="flow-container">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            fitViewOptions={{ padding: 0.2 }}
          >
            <Controls />
            <MiniMap />
            <Background />
          </ReactFlow>
        </div>
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <span className="eyebrow">
              INCIDENT MANAGEMENT
            </span>
            <h3>Recent Incidents</h3>
          </div>

          <span>{incidents.length} recorded</span>
        </div>

        {incidents.length === 0 ? (
          <div className="empty">
            No incidents recorded.
          </div>
        ) : (
          <div className="incident-table">
            {incidents.slice(0, 8).map(
              (incident, index) => {
                const incidentHealthy =
                  incident.status === "CLOSED" ||
                  incident.pipeline_status === "RUNNING";

                const incidentRate = Number(
                  incident.error_rate ?? 0
                );

                const incidentRatePercent =
                  incidentRate <= 1
                    ? incidentRate * 100
                    : incidentRate;

                return (
                  <div
                    className="incident-row"
                    key={index}
                  >
                    <span>
                      {incident.timestamp
                        ? new Date(
                            incident.timestamp
                          ).toLocaleTimeString()
                        : "—"}
                    </span>

                    <strong
                      className={
                        incidentHealthy
                          ? "green"
                          : "red"
                      }
                    >
                      {incident.status || "OPEN"}
                    </strong>

                    <span>
                      Error Rate:{" "}
                      {incidentRatePercent.toFixed(2)}%
                    </span>

                    <span>
                      {incident.action ||
                        incident.pipeline_action ||
                        "PAUSE"}
                    </span>

                    <span
                      className={
                        incidentHealthy
                          ? "green"
                          : "red"
                      }
                    >
                      {incidentHealthy
                        ? "—"
                        : "QUARANTINE"}
                    </span>
                  </div>
                );
              }
            )}
          </div>
        )}
      </section>

      <footer>
        <span>
          IceStream · Real-Time Lakehouse Observability
        </span>

        <span>
          FastAPI · React · React Flow
        </span>
      </footer>
    </div>
  );
}

export default App;