import { useEffect, useMemo, useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  Position,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";
import "./App.css";

const REFRESH_INTERVAL = 3000;
const THRESHOLD = 2;

const DATA_FILES = {
  metrics: "/data/pipeline_metrics.jsonl",
  summary: "/data/daily_summary.json",
  products: "/data/product_performance.jsonl",
  status: "/pipeline_status.json",
  incidents: "/incident_log.jsonl",
};

const normalStyle = {
  width: 185,
  padding: 16,
  border: "1px solid rgba(34, 197, 94, 0.45)",
  borderRadius: 14,
  background: "#0d1f18",
  color: "#e5e7eb",
  textAlign: "center",
  fontWeight: 600,
  boxShadow: "0 0 0 1px rgba(34,197,94,0.05)",
};

const warningStyle = {
  width: 185,
  padding: 16,
  border: "1px solid rgba(239, 68, 68, 0.65)",
  borderRadius: 14,
  background: "#251113",
  color: "#fef2f2",
  textAlign: "center",
  fontWeight: 600,
  boxShadow: "0 0 25px rgba(239,68,68,0.08)",
};

async function fetchText(url) {
  const response = await fetch(`${url}?t=${Date.now()}`);

  if (!response.ok) {
    throw new Error(`Unable to load ${url}`);
  }

  return response.text();
}

async function fetchJson(url) {
  const response = await fetch(`${url}?t=${Date.now()}`);

  if (!response.ok) {
    throw new Error(`Unable to load ${url}`);
  }

  return response.json();
}

function parseJsonLines(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      try {
        return JSON.parse(line);
      } catch {
        return null;
      }
    })
    .filter(Boolean);
}

function formatNumber(value) {
  return new Intl.NumberFormat("en-IN").format(Number(value || 0));
}

function formatCurrency(value) {
  return `₹${new Intl.NumberFormat("en-IN", {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(Number(value || 0))}`;
}

function formatPercent(value) {
  return `${Number(value || 0).toFixed(1)}%`;
}

function formatTime(timestamp) {
  if (!timestamp) return "--";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return "--";
  }

  return date.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatDateTime(timestamp) {
  if (!timestamp) return "--";

  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return "--";
  }

  return date.toLocaleString([], {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
  });
}

function App() {
  const [metricsHistory, setMetricsHistory] = useState([]);
  const [summary, setSummary] = useState(null);
  const [products, setProducts] = useState([]);
  const [pipelineStatus, setPipelineStatus] = useState(null);
  const [incidents, setIncidents] = useState([]);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [connectionError, setConnectionError] = useState("");
  const [refreshing, setRefreshing] = useState(false);

  const loadDashboardData = async () => {
    setRefreshing(true);

    try {
      const [
        metricsText,
        summaryData,
        productsText,
        statusData,
        incidentsText,
      ] = await Promise.all([
        fetchText(DATA_FILES.metrics),
        fetchJson(DATA_FILES.summary),
        fetchText(DATA_FILES.products),
        fetchJson(DATA_FILES.status),
        fetchText(DATA_FILES.incidents),
      ]);

      const metrics = parseJsonLines(metricsText);
      const productData = parseJsonLines(productsText);
      const incidentData = parseJsonLines(incidentsText);

      setMetricsHistory(metrics);
      setSummary(summaryData);
      setProducts(productData);
      setPipelineStatus(statusData);
      setIncidents(incidentData);
      setLastUpdated(new Date());
      setConnectionError("");
    } catch (error) {
      console.error("Dashboard refresh failed:", error);
      setConnectionError(
        "Unable to refresh pipeline data. Showing the last available snapshot."
      );
    } finally {
      setRefreshing(false);
    }
  };

  useEffect(() => {
    loadDashboardData();

    const interval = setInterval(
      loadDashboardData,
      REFRESH_INTERVAL
    );

    return () => clearInterval(interval);
  }, []);

  const latestMetrics = useMemo(() => {
    if (!metricsHistory.length) {
      return {
        total_records: 0,
        valid_records: 0,
        invalid_records: 0,
        error_rate: 0,
        error_breakdown: {},
      };
    }

    return metricsHistory[metricsHistory.length - 1];
  }, [metricsHistory]);

  const processed = Number(
    latestMetrics.total_records || 0
  );

  const valid = Number(
    latestMetrics.valid_records || 0
  );

  const invalid = Number(
    latestMetrics.invalid_records || 0
  );

  const errorRate =
    processed > 0
      ? (invalid / processed) * 100
      : Number(latestMetrics.error_rate || 0);

  const isHealthy =
    errorRate <= THRESHOLD &&
    pipelineStatus?.status !== "OPEN";

  const circuitOpen =
    !isHealthy ||
    pipelineStatus?.status === "OPEN";

  const topProducts = useMemo(() => {
    return [...products]
      .sort(
        (a, b) =>
          Number(b.total_revenue || 0) -
          Number(a.total_revenue || 0)
      )
      .slice(0, 5);
  }, [products]);

  const latestIncidents = useMemo(() => {
    return [...incidents]
      .reverse()
      .slice(0, 5);
  }, [incidents]);

  const healthLabel = isHealthy
    ? "HEALTHY"
    : "OPEN";

  const processingLabel = isHealthy
    ? "ACTIVE"
    : "PAUSED";

  const pipelineAction = isHealthy
    ? "NONE"
    : "PAUSE";

  const remediation = isHealthy
    ? "NONE"
    : "QUARANTINE";

  const nodes = [
    {
      id: "generator",
      position: { x: 0, y: 180 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>⚡ GENERATE</div>
            <small>Transaction Generator</small>
            <br />
            <small>Streaming Data</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "kafka",
      position: { x: 235, y: 180 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>📥 INGEST</div>
            <small>Apache Kafka</small>
            <br />
            <small>Event Stream</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "quality",
      position: { x: 470, y: 180 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>
              {circuitOpen ? "🚨 QUALITY" : "✓ QUALITY"}
            </div>
            <small>Validation</small>
            <br />
            <small>
              {circuitOpen
                ? "Errors Detected"
                : "Data Validated"}
            </small>
          </div>
        ),
      },
      style: circuitOpen
        ? warningStyle
        : normalStyle,
    },

    {
      id: "bronze",
      position: { x: 705, y: 180 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>🥉 BRONZE</div>
            <small>Raw Storage</small>
            <br />
            <small>JSONL</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "silver",
      position: { x: 940, y: 180 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>🥈 SILVER</div>
            <small>Cleaned Data</small>
            <br />
            <small>Validated Records</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "gold",
      position: { x: 1175, y: 180 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>🥇 GOLD</div>
            <small>Business Analytics</small>
            <br />
            <small>Aggregated Data</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "observability",
      position: { x: 1410, y: 180 },
      sourcePosition: Position.Right,
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>📊 OBSERVE</div>
            <small>Metrics Engine</small>
            <br />
            <small>Health Monitoring</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "dashboard",
      position: { x: 1645, y: 180 },
      targetPosition: Position.Left,
      data: {
        label: (
          <div>
            <div>🖥 DASHBOARD</div>
            <small>IceStream UI</small>
            <br />
            <small>Live Monitoring</small>
          </div>
        ),
      },
      style: normalStyle,
    },

    {
      id: "quarantine",
      position: { x: 470, y: 430 },
      targetPosition: Position.Top,
      data: {
        label: (
          <div>
            <div>🛑 QUARANTINE</div>
            <small>Bad Data / DLQ</small>
            <br />
            <small>Automated Remediation</small>
          </div>
        ),
      },
      style: warningStyle,
    },
  ];

  const edges = [
    {
      id: "generator-kafka",
      source: "generator",
      target: "kafka",
      animated: true,
    },

    {
      id: "kafka-quality",
      source: "kafka",
      target: "quality",
      animated: true,
    },

    {
      id: "quality-bronze",
      source: "quality",
      target: "bronze",
      animated: isHealthy,
    },

    {
      id: "bronze-silver",
      source: "bronze",
      target: "silver",
      animated: isHealthy,
    },

    {
      id: "silver-gold",
      source: "silver",
      target: "gold",
      animated: isHealthy,
    },

    {
      id: "gold-observability",
      source: "gold",
      target: "observability",
      animated: true,
    },

    {
      id: "observability-dashboard",
      source: "observability",
      target: "dashboard",
      animated: true,
    },

    {
      id: "quality-quarantine",
      source: "quality",
      target: "quarantine",
      animated: circuitOpen,
    },
  ];

  return (
    <div className="dashboard">

      {/* HEADER */}
      <header className="dashboard-header">

        <div className="brand">

          <div className="brand-mark">
            IS
          </div>

          <div>
            <h1>IceStream</h1>
            <p>
              Real-Time Lakehouse Observability
            </p>
          </div>

        </div>

        <div className="header-right">

          <div className="live-indicator">
            <span className="live-dot"></span>
            LIVE
          </div>

          <div
            className={`status-pill ${
              isHealthy
                ? "healthy"
                : "danger"
            }`}
          >
            <span className="status-dot"></span>
            {healthLabel}
          </div>

        </div>

      </header>

      {/* CONNECTION STATUS */}
      <div className="connection-bar">

        <div>

          <span
            className={
              connectionError
                ? "connection-dot offline"
                : "connection-dot"
            }
          />

          {connectionError
            ? connectionError
            : "Pipeline data connected"}

        </div>

        <div>
          Last refresh:{" "}
          <strong>
            {lastUpdated
              ? lastUpdated.toLocaleTimeString()
              : "--"}
          </strong>

          <span className="refresh-state">
            {refreshing ? " • refreshing..." : ""}
          </span>
        </div>

      </div>

      {/* TOP SUMMARY */}
      <section className="top-grid">

        <div className="info-card">

          <span className="card-label">
            PIPELINE
          </span>

          <strong>
            IceStream
          </strong>

          <span className="muted">
            Real-time data platform
          </span>

        </div>

        <div className="info-card">

          <span className="card-label">
            PROCESSING
          </span>

          <strong>
            {processingLabel}
          </strong>

          <span className="muted">
            Automated protection
          </span>

        </div>

        <div className="info-card">

          <span className="card-label">
            DATA QUALITY
          </span>

          <strong>
            {formatPercent(errorRate)}
          </strong>

          <span className="muted">
            Threshold: {THRESHOLD}%
          </span>

        </div>

        <div className="info-card">

          <span className="card-label">
            SNAPSHOTS
          </span>

          <strong>
            {formatNumber(metricsHistory.length)}
          </strong>

          <span className="muted">
            Recorded metric snapshots
          </span>

        </div>

      </section>

      {/* ALERT */}
      {circuitOpen && (
        <section className="alert-banner">

          <div className="alert-icon">
            !
          </div>

          <div className="alert-content">

            <strong>
              Pipeline protection activated
            </strong>

            <p>
              Data quality error rate exceeded the
              configured {THRESHOLD}% threshold.
              Pipeline processing has been paused
              and bad records have been quarantined.
            </p>

          </div>

          <div className="alert-action">
            PAUSE
          </div>

        </section>
      )}

      {/* PIPELINE HEALTH */}
      <section className="section">

        <div className="section-heading">

          <div>

            <span className="eyebrow">
              OBSERVABILITY
            </span>

            <h2>
              Pipeline Health
            </h2>

            <p>
              Latest pipeline snapshot
            </p>

          </div>

          <div className="section-meta">
            <span className="live-badge">
              ● LIVE
            </span>

            <span className="timestamp">
              {formatDateTime(
                latestMetrics.timestamp
              )}
            </span>
          </div>

        </div>

        <div className="kpi-grid">

          <div className="kpi-card">

            <span className="kpi-icon">
              Σ
            </span>

            <span className="kpi-label">
              PROCESSED RECORDS
            </span>

            <strong>
              {formatNumber(processed)}
            </strong>

            <small>
              Total records processed
            </small>

          </div>

          <div className="kpi-card success-card">

            <span className="kpi-icon">
              ✓
            </span>

            <span className="kpi-label">
              VALID RECORDS
            </span>

            <strong>
              {formatNumber(valid)}
            </strong>

            <small>
              Passed validation
            </small>

          </div>

          <div className="kpi-card danger-card">

            <span className="kpi-icon">
              !
            </span>

            <span className="kpi-label">
              INVALID RECORDS
            </span>

            <strong>
              {formatNumber(invalid)}
            </strong>

            <small>
              Failed validation
            </small>

          </div>

          <div className="kpi-card danger-card">

            <span className="kpi-icon">
              %
            </span>

            <span className="kpi-label">
              ERROR RATE
            </span>

            <strong>
              {formatPercent(errorRate)}
            </strong>

            <small>
              Threshold: {THRESHOLD}%
            </small>

          </div>

        </div>

      </section>

      {/* TREND + PROTECTION */}
      <section className="main-grid">

        {/* TREND */}
        <div className="panel trend-panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                QUALITY TREND
              </span>

              <h2>
                Error Rate History
              </h2>

              <p>
                Recent pipeline quality snapshots
              </p>
            </div>

            <span className="panel-icon">
              ↗
            </span>

          </div>

          <div className="trend-chart">

            {metricsHistory.length === 0 ? (
              <div className="empty-state">
                No metric history available.
              </div>
            ) : (
              metricsHistory
                .slice(-12)
                .map((metric, index) => {

                  const rate =
                    Number(
                      metric.error_rate || 0
                    );

                  const height =
                    Math.min(
                      Math.max(rate, 2),
                      100
                    );

                  return (
                    <div
                      className="trend-column"
                      key={`${metric.timestamp}-${index}`}
                    >

                      <div className="trend-value">
                        {rate.toFixed(1)}%
                      </div>

                      <div className="trend-bar-wrapper">

                        <div
                          className={`trend-bar ${
                            rate > THRESHOLD
                              ? "bad"
                              : "good"
                          }`}
                          style={{
                            height: `${height}%`,
                          }}
                        />

                      </div>

                      <small>
                        {formatTime(
                          metric.timestamp
                        )}
                      </small>

                    </div>
                  );
                })
            )}

          </div>

          <div className="threshold-line">
            <span>
              Threshold
            </span>

            <strong>
              {THRESHOLD}%
            </strong>
          </div>

        </div>

        {/* PROTECTION */}
        <div className="panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                PROTECTION
              </span>

              <h2>
                Pipeline Protection
              </h2>

              <p>
                Automated circuit breaker
              </p>
            </div>

            <span className="panel-icon">
              ⚡
            </span>

          </div>

          <div className="protection-status">

            <span
              className={`large-status ${
                circuitOpen
                  ? "red"
                  : "green"
              }`}
            >
              {circuitOpen
                ? "OPEN"
                : "CLOSED"}
            </span>

            <span className="muted">
              Circuit Breaker
            </span>

          </div>

          <div className="metric-row">
            <span>
              Error Rate
            </span>

            <strong>
              {formatPercent(errorRate)}
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Configured Threshold
            </span>

            <strong>
              {THRESHOLD}%
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Pipeline Action
            </span>

            <strong>
              {pipelineAction}
            </strong>
          </div>

          <div className="metric-row">
            <span>
              Remediation
            </span>

            <strong>
              {remediation}
            </strong>
          </div>

        </div>

      </section>

      {/* GOLD LAYER */}
      <section className="main-grid">

        <div className="panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                GOLD LAYER
              </span>

              <h2>
                Business Analytics
              </h2>

              <p>
                Curated lakehouse business metrics
              </p>
            </div>

            <span className="panel-icon">
              ₹
            </span>

          </div>

          <div className="analytics-grid">

            <div>
              <span>
                TRANSACTIONS
              </span>

              <strong>
                {formatNumber(
                  summary?.total_transactions
                )}
              </strong>
            </div>

            <div>
              <span>
                QUANTITY
              </span>

              <strong>
                {formatNumber(
                  summary?.total_quantity
                )}
              </strong>
            </div>

            <div>
              <span>
                TOTAL REVENUE
              </span>

              <strong>
                {formatCurrency(
                  summary?.total_revenue
                )}
              </strong>
            </div>

            <div>
              <span>
                AVG ORDER VALUE
              </span>

              <strong>
                {formatCurrency(
                  summary?.average_order_value
                )}
              </strong>
            </div>

          </div>

        </div>

        {/* DATA QUALITY BREAKDOWN */}
        <div className="panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                DATA QUALITY
              </span>

              <h2>
                Error Breakdown
              </h2>

              <p>
                Latest validation failures
              </p>
            </div>

            <span className="panel-icon">
              !
            </span>

          </div>

          <div className="error-list">

            {Object.entries(
              latestMetrics.error_breakdown || {}
            ).length === 0 ? (
              <div className="quality-good">
                <span>✓</span>
                <div>
                  <strong>
                    No validation errors
                  </strong>

                  <small>
                    Latest snapshot passed quality checks.
                  </small>
                </div>
              </div>
            ) : (
              Object.entries(
                latestMetrics.error_breakdown || {}
              )
                .sort((a, b) => b[1] - a[1])
                .map(([name, count]) => (
                  <div
                    className="error-item"
                    key={name}
                  >

                    <div className="error-name">
                      <span className="error-dot"></span>
                      {name}
                    </div>

                    <strong>
                      {count}
                    </strong>

                  </div>
                ))
            )}

          </div>

        </div>

      </section>

      {/* PRODUCT + INCIDENTS */}
      <section className="main-grid">

        {/* PRODUCTS */}
        <div className="panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                ANALYTICS
              </span>

              <h2>
                Product Performance
              </h2>

              <p>
                Top products by revenue
              </p>
            </div>

            <span className="panel-icon">
              ★
            </span>

          </div>

          <div className="product-table">

            <div className="product-table-header">
              <span>RANK</span>
              <span>PRODUCT</span>
              <span>REVENUE</span>
              <span>QTY</span>
            </div>

            {topProducts.length === 0 ? (
              <div className="empty-state">
                No product data available.
              </div>
            ) : (
              topProducts.map(
                (product, index) => (
                  <div
                    className="product-row"
                    key={product.product_id}
                  >

                    <span className="rank">
                      #{index + 1}
                    </span>

                    <strong>
                      {product.product_id}
                    </strong>

                    <span>
                      {formatCurrency(
                        product.total_revenue
                      )}
                    </span>

                    <span>
                      {formatNumber(
                        product.total_quantity
                      )}
                    </span>

                  </div>
                )
              )
            )}

          </div>

          <div className="product-footer">

            <span>
              Unique Products
            </span>

            <strong>
              {formatNumber(
                summary?.unique_products
              )}
            </strong>

            <span>
              Avg. Quantity / Transaction
            </span>

            <strong>
              {summary?.total_transactions
                ? (
                    Number(
                      summary.total_quantity
                    ) /
                    Number(
                      summary.total_transactions
                    )
                  ).toFixed(1)
                : "0.0"}
            </strong>

          </div>

        </div>

        {/* INCIDENTS */}
        <div className="panel">

          <div className="panel-header">

            <div>
              <span className="eyebrow">
                INCIDENT MANAGEMENT
              </span>

              <h2>
                Recent Incidents
              </h2>

              <p>
                Pipeline protection events
              </p>
            </div>

            <span className="panel-icon">
              ⚠
            </span>

          </div>

          <div className="incident-list">

            {latestIncidents.length === 0 ? (
              <div className="quality-good">
                <span>✓</span>

                <div>
                  <strong>
                    No recent incidents
                  </strong>

                  <small>
                    Pipeline operating normally.
                  </small>
                </div>
              </div>
            ) : (
              latestIncidents.map(
                (incident, index) => {

                  const rate =
                    incident.error_rate ??
                    incident.errorRate ??
                    0;

                  const time =
                    incident.timestamp ||
                    incident.time ||
                    incident.created_at;

                  return (
                    <div
                      className="incident"
                      key={`${time}-${index}`}
                    >

                      <span className="incident-time">
                        {formatTime(time)}
                      </span>

                      <b className="incident-open">
                        {incident.status ||
                          "OPEN"}
                      </b>

                      <span>
                        {formatPercent(rate)}
                      </span>

                      <span>
                        {incident.pipeline_action ||
                          incident.action ||
                          "PAUSE"}
                      </span>

                      <strong>
                        {incident.remediation ||
                          "QUARANTINE"}
                      </strong>

                    </div>
                  );
                }
              )
            )}

          </div>

        </div>

      </section>

      {/* ARCHITECTURE */}
      <section className="architecture-section">

        <div className="section-heading">

          <div>

            <span className="eyebrow">
              SYSTEM ARCHITECTURE
            </span>

            <h2>
              IceStream Data Pipeline
            </h2>

            <p>
              End-to-end real-time lakehouse architecture
            </p>

          </div>

          <div className="architecture-badge">
            9 STAGES
          </div>

        </div>

        <div className="flow-container">

          <ReactFlow
            nodes={nodes}
            edges={edges}
            fitView
            fitViewOptions={{
              padding: 0.12,
            }}
            nodesDraggable={false}
            nodesConnectable={false}
            zoomOnScroll
            panOnScroll
            minZoom={0.25}
            maxZoom={1.5}
          >

            <Controls />

            <MiniMap />

            <Background
              gap={24}
              size={1}
            />

          </ReactFlow>

        </div>

      </section>

      {/* FOOTER */}
      <footer>

        <div className="footer-brand">

          <strong>
            IceStream
          </strong>

          <span>
            Real-Time Lakehouse Observability Platform
          </span>

        </div>

        <div className="footer-tags">

          <span>
            DATA QUALITY
          </span>

          <span>
            LAKEHOUSE
          </span>

          <span>
            ANALYTICS
          </span>

          <span>
            AUTOMATED PROTECTION
          </span>

        </div>

      </footer>

    </div>
  );
}

export default App;