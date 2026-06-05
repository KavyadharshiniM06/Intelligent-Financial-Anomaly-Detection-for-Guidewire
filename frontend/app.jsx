const { useMemo, useState } = React;

const initialClaimForm = {
  customer_id: "1",
  policy_id: "1",
  claim_amount: "500",
  claim_date: new Date().toISOString().slice(0, 16),
};

function formatDate(value) {
  if (!value) return "Not available";
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}

function normalizeBaseUrl(url) {
  const trimmed = url.trim().replace(/\/+$/, "");
  if (!trimmed) {
    return "http://127.0.0.1:8000/api/v1";
  }
  if (trimmed.endsWith("/api/v1")) {
    return trimmed;
  }
  if (trimmed.endsWith("/api")) {
    return `${trimmed}/v1`;
  }
  return `${trimmed}/api/v1`;
}

async function apiRequest(baseUrl, path, options = {}) {
  const response = await fetch(`${normalizeBaseUrl(baseUrl)}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const detail = typeof payload === "object" && payload?.detail
      ? payload.detail
      : response.statusText;
    throw new Error(detail || "Request failed");
  }

  return payload;
}

function StatusPill({ tone, children }) {
  const className = `status-pill ${tone || ""}`.trim();
  return <div className={className}>{children}</div>;
}

function App() {
  const [baseUrl, setBaseUrl] = useState(() => {
    return localStorage.getItem("risk_engine_backend_url") || "http://127.0.0.1:8000";
  });

  React.useEffect(() => {
    localStorage.setItem("risk_engine_backend_url", baseUrl);
  }, [baseUrl]);

  const [healthState, setHealthState] = useState({
    loading: false,
    result: null,
    error: "",
  });
  const [claimForm, setClaimForm] = useState(initialClaimForm);
  const [submitState, setSubmitState] = useState({
    loading: false,
    result: null,
    error: "",
  });
  const [claimLookupId, setClaimLookupId] = useState("");
  const [claimLookupState, setClaimLookupState] = useState({
    loading: false,
    result: null,
    error: "",
  });
  const [auditLookupId, setAuditLookupId] = useState("");
  const [auditLookupState, setAuditLookupState] = useState({
    loading: false,
    result: null,
    error: "",
  });
  const [adminConfig, setAdminConfig] = useState({
    maxAmount: 50000,
    loading: false,
    error: "",
  });
  const [exportId, setExportId] = useState("");
  const [exportLoading, setExportLoading] = useState(false);
  const [customersState, setCustomersState] = useState({
    loading: false,
    data: [],
    error: "",
  });

  const resolvedApiBase = useMemo(() => normalizeBaseUrl(baseUrl), [baseUrl]);

  // Fetch initial config on load
  React.useEffect(() => {
    fetchConfig();
    fetchCustomers();
  }, [baseUrl]);

  async function fetchConfig() {
    try {
      const data = await apiRequest(baseUrl, "/admin/config/MAX_CREDIBLE_AMOUNT", { method: "GET" });
      setAdminConfig(prev => ({ ...prev, maxAmount: data.value }));
    } catch (err) {
      console.error("Failed to fetch system config:", err);
    }
  }

  async function fetchCustomers() {
    setCustomersState({ loading: true, data: [], error: "" });
    try {
      const data = await apiRequest(baseUrl, "/customers/", { method: "GET" });
      setCustomersState({ loading: false, data, error: "" });
    } catch (err) {
      setCustomersState({ loading: false, data: [], error: err.message });
    }
  }

  async function handleUpdateConfig() {
    setAdminConfig(prev => ({ ...prev, loading: true, error: "" }));
    try {
      const data = await apiRequest(baseUrl, "/admin/config/MAX_CREDIBLE_AMOUNT", {
        method: "PUT",
        body: JSON.stringify({ value: Number(adminConfig.maxAmount) }),
      });
      setAdminConfig({ maxAmount: data.value, loading: false, error: "" });
      alert("System Configuration Updated!");
    } catch (err) {
      setAdminConfig(prev => ({ ...prev, loading: false, error: err.message }));
    }
  }

  async function handleHealthCheck() {
    setHealthState({ loading: true, result: null, error: "" });
    try {
      const result = await apiRequest(baseUrl, "/health", { method: "GET" });
      setHealthState({ loading: false, result, error: "" });
    } catch (error) {
      setHealthState({ loading: false, result: null, error: error.message });
    }
  }

  async function handleClaimSubmit(event) {
    event.preventDefault();
    setSubmitState({ loading: true, result: null, error: "" });

    const payload = {
      customer_id: Number(claimForm.customer_id),
      policy_id: Number(claimForm.policy_id),
      claim_amount: Number(claimForm.claim_amount),
      claim_date: new Date(claimForm.claim_date).toISOString(),
    };

    try {
      const result = await apiRequest(baseUrl, "/claims/submit", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      setSubmitState({ loading: false, result, error: "" });
    } catch (error) {
      setSubmitState({ loading: false, result: null, error: error.message });
    }
  }

  async function handleClaimLookup(event) {
    event.preventDefault();
    setClaimLookupState({ loading: true, result: null, error: "" });
    try {
      const result = await apiRequest(baseUrl, `/claims/${claimLookupId}`, {
        method: "GET",
      });
      setClaimLookupState({ loading: false, result, error: "" });
    } catch (error) {
      setClaimLookupState({ loading: false, result: null, error: error.message });
    }
  }

  async function handleAuditLookup(event) {
    event.preventDefault();
    setAuditLookupState({ loading: true, result: null, error: "" });
    try {
      const result = await apiRequest(baseUrl, `/audit/${auditLookupId}`, {
        method: "GET",
      });
      setAuditLookupState({ loading: false, result, error: "" });
    } catch (error) {
      setAuditLookupState({ loading: false, result: null, error: error.message });
    }
  }

  async function handleExportAudit(event) {
    event.preventDefault();
    setExportLoading(true);
    try {
      const url = `${normalizeBaseUrl(baseUrl)}/audit/export/${exportId}`;
      const response = await fetch(url);
      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Export failed");
      }
      
      const blob = await response.blob();
      const downloadUrl = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = downloadUrl;
      a.download = `audit_history_cust_${exportId}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      setExportLoading(false);
    } catch (error) {
      setExportLoading(false);
      alert(`Export Error: ${error.message}`);
    }
  }

  return (
    <div className="app-shell">
      <section className="hero">
        <div className="eyebrow">React Operations Console</div>
        <div className="hero-grid">
          <div className="hero-copy">
            <h1>Risk decisions with a cleaner cockpit.</h1>
            <p>
              This frontend talks to your FastAPI service for claim submission,
              audit retrieval, and health checks. Start by keeping the backend
              running locally, then point this console at it using the base URL below.
            </p>
          </div>
          <div className="hero-stats">
            <div className="stat-card">
              <strong>/health</strong>
              <span>Connectivity and DB status checks before claim processing.</span>
            </div>
            <div className="stat-card">
              <strong>/claims/submit</strong>
              <span>Runs the risk pipeline and returns decision plus reasons.</span>
            </div>
            <div className="stat-card">
              <strong>/claims/{`{id}`}</strong>
              <span>Loads persisted claim details after submission.</span>
            </div>
            <div className="stat-card">
              <strong>/audit/{`{id}`}</strong>
              <span>Inspects the logged decision trail for a processed claim.</span>
            </div>
          </div>
        </div>
        <div className="toolbar">
          <div className="field">
            <label htmlFor="base-url">Backend Base URL</label>
            <input
              id="base-url"
              value={baseUrl}
              onChange={(event) => setBaseUrl(event.target.value)}
              placeholder="http://127.0.0.1:8000"
            />
          </div>
          <button className="primary" onClick={handleHealthCheck} disabled={healthState.loading}>
            {healthState.loading ? "Checking..." : "Run Health Check"}
          </button>
          <StatusPill tone={healthState.error ? "error" : healthState.result ? "ok" : "warn"}>
            {healthState.error
              ? "Health check failed"
              : healthState.result
                ? `${healthState.result.status} / ${healthState.result.db_status}`
                : "Awaiting check"}
          </StatusPill>
        </div>
      </section>

      <div className="grid">
        <section className="panel">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
            <h2>Submit Claim</h2>
            <StatusPill tone="ok">Smart Ingestion Active</StatusPill>
          </div>
          <p className="panel-subtitle">
            The engine now automatically pulls <strong>Vehicle Age</strong>, <strong>NCAP Rating</strong>, and 
            <strong>Customer Demographics</strong> from the database based on the IDs provided.
          </p>

          <form onSubmit={handleClaimSubmit}>
            <div className="form-grid">
              <div className="field">
                <label htmlFor="customer_id">Customer ID</label>
                <input
                  id="customer_id"
                  type="number"
                  min="1"
                  value={claimForm.customer_id}
                  onChange={(event) =>
                    setClaimForm((current) => ({ ...current, customer_id: event.target.value }))
                  }
                />
              </div>
              <div className="field">
                <label htmlFor="policy_id">Policy ID</label>
                <input
                  id="policy_id"
                  type="number"
                  min="1"
                  value={claimForm.policy_id}
                  onChange={(event) =>
                    setClaimForm((current) => ({ ...current, policy_id: event.target.value }))
                  }
                />
              </div>
              <div className="field">
                <label htmlFor="claim_amount">Claim Amount</label>
                <input
                  id="claim_amount"
                  type="number"
                  min="1"
                  step="0.01"
                  value={claimForm.claim_amount}
                  onChange={(event) =>
                    setClaimForm((current) => ({ ...current, claim_amount: event.target.value }))
                  }
                />
              </div>
              <div className="field">
                <label htmlFor="claim_date">Claim Date</label>
                <input
                  id="claim_date"
                  type="datetime-local"
                  value={claimForm.claim_date}
                  onChange={(event) =>
                    setClaimForm((current) => ({ ...current, claim_date: event.target.value }))
                  }
                />
              </div>
            </div>

            <div className="button-row">
              <button className="primary" type="submit" disabled={submitState.loading}>
                {submitState.loading ? "Processing..." : "Submit to Risk Engine"}
              </button>
              <button
                className="secondary"
                type="button"
                onClick={() => {
                  setClaimForm(initialClaimForm);
                  setSubmitState({ loading: false, result: null, error: "" });
                }}
              >
                Reset
              </button>
            </div>
          </form>

          {submitState.error && (
            <div className="result">
              <StatusPill tone="error">{submitState.error}</StatusPill>
            </div>
          )}

          {submitState.result && (
            <div className="result">
              <div className="result-grid">
                <div className="metric">
                  <span>Claim ID</span>
                  <strong>{submitState.result.claim_id}</strong>
                </div>
                <div className="metric">
                  <span>Risk Score</span>
                  <strong>{submitState.result.risk_score}</strong>
                </div>
                <div className="metric">
                  <span>Decision</span>
                  <strong>{submitState.result.decision}</strong>
                </div>
                <div className="metric">
                  <span>Confidence</span>
                  <strong>{submitState.result.confidence}</strong>
                </div>
              </div>
              <div>
                <strong>Reasons</strong>
                {submitState.result.reasons.length ? (
                  <ul className="reason-list">
                    {submitState.result.reasons.map((reason, index) => (
                      <li key={`${reason}-${index}`}>{reason}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="footer-note">No rule-based reasons were returned for this decision.</p>
                )}
              </div>
            </div>
          )}
        </section>

        <section className="panel stack">
          <div>
            <h2>Lookup Claim</h2>
            <p className="panel-subtitle">
              After a successful submission, use the generated claim ID from your API logs or
              database to inspect the stored claim record.
            </p>
            <form onSubmit={handleClaimLookup}>
              <div className="field">
                <label htmlFor="claim_lookup_id">Claim ID</label>
                <input
                  id="claim_lookup_id"
                  type="number"
                  min="1"
                  value={claimLookupId}
                  onChange={(event) => setClaimLookupId(event.target.value)}
                  placeholder="Enter claim ID"
                />
              </div>
              <div className="button-row">
                <button className="ghost" type="submit" disabled={claimLookupState.loading}>
                  {claimLookupState.loading ? "Loading..." : "Fetch Claim"}
                </button>
              </div>
            </form>

            {claimLookupState.error && (
              <div className="result">
                <StatusPill tone="error">{claimLookupState.error}</StatusPill>
              </div>
            )}

            {claimLookupState.result ? (
              <div className="result">
                <div className="result-grid">
                  <div className="metric">
                    <span>Status</span>
                    <strong>{claimLookupState.result.status}</strong>
                  </div>
                  <div className="metric">
                    <span>Amount</span>
                    <strong>{claimLookupState.result.claim_amount}</strong>
                  </div>
                  <div className="metric">
                    <span>Customer ID</span>
                    <strong>{claimLookupState.result.customer_id}</strong>
                  </div>
                  <div className="metric">
                    <span>Policy ID</span>
                    <strong>{claimLookupState.result.policy_id}</strong>
                  </div>
                </div>
                <div className="footer-note">
                  Claim date: {formatDate(claimLookupState.result.claim_date)}
                  <br />
                  Created at: {formatDate(claimLookupState.result.created_at)}
                </div>
              </div>
            ) : (
              <div className="empty-state">No claim lookup loaded yet.</div>
            )}
          </div>

          <div>
            <h2>Lookup Audit</h2>
            <p className="panel-subtitle">
              Audit logs capture the decision and reasons attached to a processed claim.
            </p>
            <form onSubmit={handleAuditLookup}>
              <div className="field">
                <label htmlFor="audit_lookup_id">Claim ID</label>
                <input
                  id="audit_lookup_id"
                  type="number"
                  min="1"
                  value={auditLookupId}
                  onChange={(event) => setAuditLookupId(event.target.value)}
                  placeholder="Enter claim ID"
                />
              </div>
              <div className="button-row">
                <button className="ghost" type="submit" disabled={auditLookupState.loading}>
                  {auditLookupState.loading ? "Loading..." : "Fetch Audit"}
                </button>
              </div>
            </form>

            {auditLookupState.error && (
              <div className="result">
                <StatusPill tone="error">{auditLookupState.error}</StatusPill>
              </div>
            )}

            {auditLookupState.result ? (
              <div className="result">
                <div className="result-grid">
                  <div className="metric">
                    <span>Decision</span>
                    <strong>{auditLookupState.result.decision}</strong>
                  </div>
                  <div className="metric">
                    <span>Risk Score</span>
                    <strong>{auditLookupState.result.risk_score}</strong>
                  </div>
                </div>
                <div>
                  <strong>Reasons</strong>
                  <ul className="reason-list">
                    {auditLookupState.result.reasons.map((reason, index) => (
                      <li key={`${reason}-${index}`}>{reason}</li>
                    ))}
                  </ul>
                </div>
                <div className="footer-note">
                  Logged at: {formatDate(auditLookupState.result.created_at)}
                </div>
              </div>
            ) : (
              <div className="empty-state">No audit log loaded yet.</div>
            )}
          </div>
        </section>
      </div>

      <div className="grid">
        <section className="panel administrative">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h2>Audit Evidence Export</h2>
              <p className="panel-subtitle">Generate a professional CSV history of all risk decisions for a customer.</p>
            </div>
            <StatusPill tone="ok">CSV Generator</StatusPill>
          </div>
          <form onSubmit={handleExportAudit}>
            <div className="field">
              <label htmlFor="export_cust_id">Customer ID</label>
              <input
                id="export_cust_id"
                type="number"
                min="1"
                value={exportId}
                onChange={(event) => setExportId(event.target.value)}
                placeholder="Enter customer ID (e.g. 13)"
              />
            </div>
            <div className="button-row" style={{ marginTop: '1rem' }}>
              <button className="primary" type="submit" disabled={exportLoading || !exportId} style={{ width: '100%' }}>
                {exportLoading ? "Generating CSV..." : "Download Audit Evidence (.csv)"}
              </button>
            </div>
          </form>
        </section>

        <section className="panel administrative">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <div>
              <h2>System Configuration</h2>
              <p className="panel-subtitle">Manage global risk thresholds and hard limits for the automated engine.</p>
            </div>
            <StatusPill tone={adminConfig.error ? "error" : "ok"}>Live Engine Settings</StatusPill>
          </div>

        <div className="form-grid">
          <div className="field">
            <label htmlFor="max-credible-amount">Max Credible Amount (USD)</label>
            <input
              id="max-credible-amount"
              type="number"
              value={adminConfig.maxAmount}
              onChange={(event) => setAdminConfig(prev => ({ ...prev, maxAmount: event.target.value }))}
              placeholder="e.g. 50000"
            />
            <p className="footer-note" style={{ marginTop: '0.5rem' }}>
              Claims exceeding this amount will trigger an <strong>Absolute Risk Alert</strong>. 
              Claims exceeding 2x this amount will be <strong>Automatically Rejected</strong>.
            </p>
          </div>
          <div className="field" style={{ display: 'flex', alignItems: 'flex-end', paddingBottom: '2.4rem' }}>
            <button 
              className="primary" 
              onClick={handleUpdateConfig} 
              disabled={adminConfig.loading}
              style={{ width: '100%' }}
            >
              {adminConfig.loading ? "Updating..." : "Update System Config"}
            </button>
          </div>
        </div>
      </section>

      <section className="panel registry-section">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
          <div>
            <h2>Customer Directory</h2>
            <p className="panel-subtitle">All registered customers with their policy details and computed risk profiles.</p>
          </div>
          <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
            <StatusPill tone={customersState.error ? "error" : customersState.data.length ? "ok" : "warn"}>
              {customersState.loading ? "Loading..." : customersState.error ? "Failed" : `${customersState.data.length} Customers`}
            </StatusPill>
            <button className="ghost" onClick={fetchCustomers} disabled={customersState.loading} style={{ fontSize: '0.85rem', padding: '8px 14px' }}>
              {customersState.loading ? "Refreshing..." : "Refresh"}
            </button>
          </div>
        </div>

        {customersState.error && (
          <div className="result">
            <StatusPill tone="error">{customersState.error}</StatusPill>
          </div>
        )}

        {customersState.data.length > 0 ? (
          <div className="registry-table-wrap">
            <table className="registry-table">
              <thead>
                <tr>
                  <th>Customer</th>
                  <th>Policy</th>
                  <th>Density Level</th>
                  <th>Profile Description</th>
                  <th>Risk Tier</th>
                </tr>
              </thead>
              <tbody>
                {customersState.data.map((cust) => (
                  <tr key={cust.customer_id}>
                    <td>
                      <div className="customer-name">{cust.name}</div>
                      <div className="customer-id">ID: {cust.customer_id} · Age {cust.age}</div>
                    </td>
                    <td>
                      {cust.policy_id ? (
                        <div>
                          <div style={{ fontWeight: 600 }}>{cust.policy_type}</div>
                          <div className="customer-id">Policy #{cust.policy_id} · NCAP {cust.ncap_rating} · {cust.vehicle_age}yr vehicle</div>
                        </div>
                      ) : (
                        <span className="customer-id">No policy</span>
                      )}
                    </td>
                    <td>
                      <span className="density-chip">{cust.density_label}</span>
                    </td>
                    <td>
                      <div className="profile-tags">
                        {cust.profile_description.split(" · ").map((tag, i) => (
                          <span className="profile-tag" key={i}>{tag}</span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <span className={`tier-badge ${cust.risk_tier}`}>
                        {cust.risk_tier === "safe" ? "✅ Safe" : cust.risk_tier === "moderate" ? "⚠️ Moderate" : "🔴 High Risk"}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : !customersState.loading && !customersState.error ? (
          <div className="empty-state">No customers found. Run <code>python -m app.db.seed_demo</code> to seed demo data.</div>
        ) : null}
      </section>

      <section className="panel">
        <h2>Working Notes</h2>
        <p className="panel-subtitle">
          This frontend is intentionally thin so it stays aligned with the backend you already have.
        </p>
        <ul className="hint-list">
          <li>The API base field accepts either `http://127.0.0.1:8000` or a full `/api/v1` URL.</li>
          <li>Seed demo records with `python -m app.db.seed_demo` to get a valid customer and policy pair.</li>
          <li>Run this frontend from `frontend/` using `python -m http.server 3000` for a quick local server.</li>
          <li>Keep the FastAPI backend running separately on port `8000` while using the UI.</li>
          <li><strong>Tip</strong>: Use the System Configuration below to test "Hard Rejection" for massive claims.</li>
        </ul>
      </section>
    </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
