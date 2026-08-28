import "./App.css";

function App() {
  const pipelineStatus = {
    status: "OPEN",
    action: "PAUSE",
    remediation: "QUARANTINE",
    errorRate: 14,
    threshold: 2,
    processed: 100,
    valid: 86,
    invalid: 14,
  };

  const kpis = {
    transactions: 5,
    quantity: 10,
    revenue: 5000,
    averageOrderValue: 1000,
    uniqueProducts: 1,
    topProduct: "PRD-001",
  };

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>IceStream</h1>
          <p>Real-Time Lakehouse Observability</p>
        </div>

        <div className={`status-badge ${pipelineStatus.status.toLowerCase()}`}>
          ● {pipelineStatus.status}
        </div>
      </header>

      <main>
        <section className="hero">
          <div>
            <h2>Pipeline Overview</h2>
            <p>Real-time data quality and pipeline health</p>
          </div>

          <div className="pipeline-action">
            <span>Pipeline Action</span>
            <strong>{pipelineStatus.action}</strong>
          </div>
        </section>

        <section className="cards">
          <div className="card">
            <span>Processed Records</span>
            <strong>{pipelineStatus.processed}</strong>
          </div>

          <div className="card">
            <span>Valid Records</span>
            <strong>{pipelineStatus.valid}</strong>
          </div>

          <div className="card danger">
            <span>Invalid Records</span>
            <strong>{pipelineStatus.invalid}</strong>
          </div>

          <div className="card danger">
            <span>Error Rate</span>
            <strong>{pipelineStatus.errorRate}%</strong>
            <small>Threshold: {pipelineStatus.threshold}%</small>
          </div>
        </section>

        <section className="section">
          <h2>Business KPIs</h2>

          <div className="cards">
            <div className="card">
              <span>Total Transactions</span>
              <strong>{kpis.transactions}</strong>
            </div>

            <div className="card">
              <span>Total Quantity</span>
              <strong>{kpis.quantity}</strong>
            </div>

            <div className="card">
              <span>Total Revenue</span>
              <strong>₹{kpis.revenue}</strong>
            </div>

            <div className="card">
              <span>Average Order Value</span>
              <strong>₹{kpis.averageOrderValue}</strong>
            </div>
          </div>
        </section>

        <section className="bottom-grid">
          <div className="panel">
            <h2>Pipeline Protection</h2>

            <div className="protection-row">
              <span>Circuit Breaker</span>
              <strong className="danger-text">
                {pipelineStatus.status}
              </strong>
            </div>

            <div className="protection-row">
              <span>Pipeline Action</span>
              <strong>{pipelineStatus.action}</strong>
            </div>

            <div className="protection-row">
              <span>Remediation</span>
              <strong>{pipelineStatus.remediation}</strong>
            </div>

            <div className="protection-row">
              <span>Threshold</span>
              <strong>{pipelineStatus.threshold}%</strong>
            </div>
          </div>

          <div className="panel">
            <h2>Product Analytics</h2>

            <div className="product">
              <span>Top Product</span>
              <strong>{kpis.topProduct}</strong>
            </div>

            <div className="product">
              <span>Unique Products</span>
              <strong>{kpis.uniqueProducts}</strong>
            </div>
          </div>
        </section>
      </main>

      <footer>
        IceStream • Real-Time Data Engineering & Observability
      </footer>
    </div>
  );
}

export default App;