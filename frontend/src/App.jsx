import { useState } from "react";
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
} from "@xyflow/react";

import "@xyflow/react/dist/style.css";

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

  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        background: "#f8fafc",
      }}
    >
      {/* Header */}
      <div
        style={{
          position: "absolute",
          zIndex: 10,
          top: 20,
          left: 20,
          right: 20,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          background: "white",
          padding: "15px 25px",
          borderRadius: 12,
          boxShadow: "0 2px 12px rgba(0,0,0,0.12)",
        }}
      >
        <div>
          <h1 style={{ margin: 0 }}>IceStream</h1>
          <p style={{ margin: "5px 0 0" }}>
            Real-Time Lakehouse Observability
          </p>
        </div>

        <div
          style={{
            padding: "10px 18px",
            borderRadius: 20,
            background: isHealthy ? "#dcfce7" : "#fee2e2",
            color: isHealthy ? "#166534" : "#991b1b",
            fontWeight: "bold",
          }}
        >
          ● {pipelineStatus}
        </div>
      </div>

      {/* Controls */}
      <div
        style={{
          position: "absolute",
          zIndex: 10,
          top: 120,
          right: 20,
          background: "white",
          padding: 15,
          borderRadius: 10,
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
        }}
      >
        <button
          onClick={() =>
            setPipelineStatus(
              isHealthy ? "QUARANTINED" : "HEALTHY"
            )
          }
          style={{
            padding: "10px 15px",
            cursor: "pointer",
            borderRadius: 8,
            border: "1px solid #ccc",
          }}
        >
          {isHealthy
            ? "Simulate Data Anomaly"
            : "Restore Pipeline"}
        </button>
      </div>

      {/* React Flow */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
      >
        <Controls />
        <MiniMap />
        <Background />
      </ReactFlow>

      {/* Footer / Legend */}
      <div
        style={{
          position: "absolute",
          zIndex: 10,
          bottom: 20,
          left: 20,
          background: "white",
          padding: "12px 18px",
          borderRadius: 10,
          boxShadow: "0 2px 10px rgba(0,0,0,0.1)",
          fontSize: 14,
        }}
      >
        🟢 Healthy &nbsp;&nbsp; 🔴 Quarantined &nbsp;&nbsp;
        🛑 Bad Data
      </div>
    </div>
  );
}

export default App;