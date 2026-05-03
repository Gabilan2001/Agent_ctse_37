import { useState, useRef, useEffect } from "react";

const API_BASE = "http://localhost:8000";

const AGENTS = [
  {
    id: "code_understanding",
    label: "CodeUnderstandingAgent",
    icon: "⬡",
    color: "#4FC3F7",
    desc: "Reads & understands structure",
  },
  {
    id: "bug_analyst",
    label: "BugAnalystAgent",
    icon: "⬡",
    color: "#EF5350",
    desc: "Finds bugs & vulnerabilities",
  },
  {
    id: "fix_generation",
    label: "FixGenerationAgent",
    icon: "⬡",
    color: "#FFCA28",
    desc: "Generates corrected code",
  },
  {
    id: "test_validation",
    label: "TestValidationAgent",
    icon: "⬡",
    color: "#66BB6A",
    desc: "Runs tests & validates fixes",
  },
];

const SEVERITY_COLOR = {
  CRITICAL: "#EF5350",
  HIGH: "#FF7043",
  MEDIUM: "#FFCA28",
  LOW: "#66BB6A",
};

function SeverityBadge({ severity }) {
  return (
    <span
      style={{
        background: SEVERITY_COLOR[severity] + "22",
        color: SEVERITY_COLOR[severity],
        border: `1px solid ${SEVERITY_COLOR[severity]}44`,
        borderRadius: 4,
        padding: "1px 8px",
        fontSize: 11,
        fontFamily: "monospace",
        fontWeight: 700,
        letterSpacing: 1,
      }}
    >
      {severity}
    </span>
  );
}

function AgentNode({ agent, status }) {
  const isActive = status === "active";
  const isDone = status === "done";
  const isPending = status === "pending";

  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        gap: 8,
        position: "relative",
      }}
    >
      <div
        style={{
          width: 56,
          height: 56,
          borderRadius: "50%",
          border: `2px solid ${isDone ? agent.color : isActive ? agent.color : "#2a2a3a"}`,
          background: isDone
            ? agent.color + "22"
            : isActive
            ? agent.color + "11"
            : "#12121a",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          fontSize: 22,
          color: isDone ? agent.color : isActive ? agent.color : "#333350",
          boxShadow: isActive
            ? `0 0 18px ${agent.color}66`
            : isDone
            ? `0 0 8px ${agent.color}33`
            : "none",
          transition: "all 0.4s ease",
          position: "relative",
        }}
      >
        {isDone ? "✓" : isActive ? (
          <span style={{ animation: "spin 1s linear infinite", display: "inline-block" }}>◌</span>
        ) : agent.icon}
        {isActive && (
          <div
            style={{
              position: "absolute",
              inset: -4,
              borderRadius: "50%",
              border: `1px solid ${agent.color}44`,
              animation: "pulse-ring 1.5s ease-out infinite",
            }}
          />
        )}
      </div>
      <div style={{ textAlign: "center" }}>
        <div
          style={{
            fontSize: 10,
            fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
            color: isDone ? agent.color : isActive ? agent.color : "#444460",
            fontWeight: 700,
            letterSpacing: 0.5,
            transition: "color 0.3s",
          }}
        >
          {agent.label}
        </div>
        <div style={{ fontSize: 9, color: "#444460", marginTop: 2 }}>
          {agent.desc}
        </div>
      </div>
    </div>
  );
}

function CodeBlock({ code, language = "python" }) {
  const [copied, setCopied] = useState(false);
  return (
    <div style={{ position: "relative" }}>
      <button
        onClick={() => {
          navigator.clipboard.writeText(code);
          setCopied(true);
          setTimeout(() => setCopied(false), 2000);
        }}
        style={{
          position: "absolute",
          top: 8,
          right: 8,
          background: copied ? "#66BB6A22" : "#1e1e2e",
          border: `1px solid ${copied ? "#66BB6A" : "#2a2a3a"}`,
          color: copied ? "#66BB6A" : "#555570",
          borderRadius: 4,
          padding: "3px 10px",
          fontSize: 10,
          cursor: "pointer",
          fontFamily: "monospace",
          transition: "all 0.2s",
          zIndex: 2,
        }}
      >
        {copied ? "✓ copied" : "copy"}
      </button>
      <pre
        style={{
          background: "#0a0a12",
          border: "1px solid #1e1e2e",
          borderRadius: 8,
          padding: "16px 16px 16px 16px",
          overflowX: "auto",
          fontSize: 12,
          lineHeight: 1.7,
          color: "#c9d1d9",
          fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
          margin: 0,
          maxHeight: 380,
          overflowY: "auto",
        }}
      >
        <code>{code}</code>
      </pre>
    </div>
  );
}

function TabButton({ label, active, count, color, onClick }) {
  return (
    <button
      onClick={onClick}
      style={{
        background: active ? "#1a1a2e" : "transparent",
        border: "none",
        borderBottom: active ? `2px solid ${color || "#4FC3F7"}` : "2px solid transparent",
        color: active ? "#e0e0f0" : "#444460",
        padding: "10px 18px",
        fontSize: 12,
        fontFamily: "'JetBrains Mono', monospace",
        cursor: "pointer",
        transition: "all 0.2s",
        display: "flex",
        alignItems: "center",
        gap: 6,
        whiteSpace: "nowrap",
      }}
    >
      {label}
      {count !== undefined && (
        <span
          style={{
            background: active ? (color || "#4FC3F7") + "33" : "#1e1e2e",
            color: active ? color || "#4FC3F7" : "#444460",
            borderRadius: 10,
            padding: "1px 7px",
            fontSize: 10,
            fontWeight: 700,
          }}
        >
          {count}
        </span>
      )}
    </button>
  );
}

export default function App() {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const [running, setRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState("summary");
  const [agentStatuses, setAgentStatuses] = useState(
    Object.fromEntries(AGENTS.map((a) => [a.id, "pending"]))
  );
  const fileInputRef = useRef();
  const dropRef = useRef();

  // Simulate agent progress
  useEffect(() => {
    if (!running) return;
    const order = AGENTS.map((a) => a.id);
    let i = 0;
    setAgentStatuses(Object.fromEntries(order.map((id) => [id, "pending"])));

    const interval = setInterval(() => {
      if (i >= order.length) {
        clearInterval(interval);
        return;
      }
      setAgentStatuses((prev) => ({
        ...prev,
        ...(i > 0 ? { [order[i - 1]]: "done" } : {}),
        [order[i]]: "active",
      }));
      i++;
    }, 2200);

    return () => clearInterval(interval);
  }, [running]);

  const handleFile = (f) => {
    if (f && f.name.endsWith(".py")) {
      setFile(f);
      setError(null);
      setResults(null);
    } else {
      setError("Please upload a .py Python file.");
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    handleFile(f);
  };

  const handleAnalyze = async () => {
    if (!file) return;
    setRunning(true);
    setResults(null);
    setError(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/analyze`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();
      setResults(data);
      setAgentStatuses(Object.fromEntries(AGENTS.map((a) => [a.id, "done"])));
      setActiveTab("summary");
    } catch (err) {
      setError(
        "Could not connect to backend. Make sure uvicorn is running on port 8000."
      );
      setAgentStatuses(Object.fromEntries(AGENTS.map((a) => [a.id, "pending"])));
    } finally {
      setRunning(false);
    }
  };

  const bugCount = results?.bug_report?.length || 0;
  const secCount = results?.security_issues?.length || 0;
  const passed = results?.test_results?.passed || 0;
  const failed = results?.test_results?.failed || 0;

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "#0d0d1a",
        color: "#c9d1d9",
        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
        padding: 0,
      }}
    >
      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Syne:wght@700;800&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: #0a0a12; }
        ::-webkit-scrollbar-thumb { background: #2a2a3a; border-radius: 3px; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
        @keyframes pulse-ring {
          0% { transform: scale(1); opacity: 0.6; }
          100% { transform: scale(1.8); opacity: 0; }
        }
        @keyframes fadeIn {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }
      `}</style>

      {/* Header */}
      <div
        style={{
          borderBottom: "1px solid #1e1e2e",
          padding: "16px 32px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          background: "#0a0a12",
          position: "sticky",
          top: 0,
          zIndex: 100,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div
            style={{
              width: 32,
              height: 32,
              background: "linear-gradient(135deg, #4FC3F7, #7C4DFF)",
              borderRadius: 8,
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: 16,
            }}
          >
            ⬡
          </div>
          <div>
            <div
              style={{
                fontFamily: "'Syne', sans-serif",
                fontWeight: 800,
                fontSize: 16,
                color: "#e0e0f0",
                letterSpacing: -0.5,
              }}
            >
              MAS Code Review
            </div>
            <div style={{ fontSize: 9, color: "#444460", letterSpacing: 1 }}>
              MULTI-AGENT PIPELINE · LLAMA3:8B · LOCAL
            </div>
          </div>
        </div>
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            fontSize: 10,
            color: "#444460",
          }}
        >
          <div
            style={{
              width: 6,
              height: 6,
              borderRadius: "50%",
              background: "#66BB6A",
              boxShadow: "0 0 6px #66BB6A",
            }}
          />
          OLLAMA RUNNING
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: "0 auto", padding: "32px 24px" }}>

        {/* Agent Pipeline Visualization */}
        <div
          style={{
            background: "#0f0f1e",
            border: "1px solid #1e1e2e",
            borderRadius: 12,
            padding: "24px 32px",
            marginBottom: 24,
            animation: "fadeIn 0.4s ease",
          }}
        >
          <div
            style={{
              fontSize: 10,
              color: "#444460",
              letterSpacing: 2,
              marginBottom: 20,
            }}
          >
            AGENT PIPELINE
          </div>
          <div
            style={{
              display: "flex",
              alignItems: "flex-start",
              justifyContent: "center",
              gap: 0,
              overflowX: "auto",
              paddingBottom: 4,
            }}
          >
            {AGENTS.map((agent, i) => (
              <div
                key={agent.id}
                style={{ display: "flex", alignItems: "center" }}
              >
                <AgentNode agent={agent} status={agentStatuses[agent.id]} />
                {i < AGENTS.length - 1 && (
                  <div
                    style={{
                      width: 40,
                      height: 1,
                      background:
                        agentStatuses[AGENTS[i + 1].id] !== "pending"
                          ? `linear-gradient(90deg, ${agent.color}88, ${AGENTS[i+1].color}88)`
                          : "#1e1e2e",
                      margin: "0 4px",
                      marginBottom: 28,
                      transition: "background 0.5s",
                      flexShrink: 0,
                    }}
                  />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Upload Area */}
        <div
          ref={dropRef}
          onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={handleDrop}
          onClick={() => !file && fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${dragging ? "#4FC3F7" : file ? "#7C4DFF" : "#1e1e2e"}`,
            borderRadius: 12,
            padding: "28px 32px",
            marginBottom: 24,
            cursor: file ? "default" : "pointer",
            background: dragging
              ? "#4FC3F708"
              : file
              ? "#7C4DFF08"
              : "#0f0f1e",
            transition: "all 0.2s",
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 16,
            flexWrap: "wrap",
            animation: "fadeIn 0.4s ease 0.1s both",
          }}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".py"
            style={{ display: "none" }}
            onChange={(e) => handleFile(e.target.files[0])}
          />
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div
              style={{
                width: 48,
                height: 48,
                borderRadius: 10,
                background: file ? "#7C4DFF22" : "#1e1e2e",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 22,
                flexShrink: 0,
              }}
            >
              {file ? "🐍" : "⬆"}
            </div>
            <div>
              {file ? (
                <>
                  <div style={{ fontSize: 13, color: "#e0e0f0", fontWeight: 600 }}>
                    {file.name}
                  </div>
                  <div style={{ fontSize: 10, color: "#7C4DFF", marginTop: 3 }}>
                    {(file.size / 1024).toFixed(1)} KB · Python file ready
                  </div>
                </>
              ) : (
                <>
                  <div style={{ fontSize: 13, color: "#e0e0f0" }}>
                    Drop your Python file here
                  </div>
                  <div style={{ fontSize: 10, color: "#444460", marginTop: 3 }}>
                    or click to browse · .py files only
                  </div>
                </>
              )}
            </div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            {file && (
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setFile(null);
                  setResults(null);
                  setError(null);
                  setAgentStatuses(Object.fromEntries(AGENTS.map(a => [a.id, "pending"])));
                }}
                style={{
                  background: "transparent",
                  border: "1px solid #2a2a3a",
                  color: "#555570",
                  borderRadius: 6,
                  padding: "8px 14px",
                  fontSize: 11,
                  cursor: "pointer",
                }}
              >
                clear
              </button>
            )}
            <button
              onClick={(e) => {
                e.stopPropagation();
                if (!file) { fileInputRef.current?.click(); return; }
                handleAnalyze();
              }}
              disabled={running}
              style={{
                background: running
                  ? "#1e1e2e"
                  : file
                  ? "linear-gradient(135deg, #4FC3F7, #7C4DFF)"
                  : "#1e1e2e",
                border: "none",
                color: running ? "#444460" : file ? "#fff" : "#444460",
                borderRadius: 8,
                padding: "10px 24px",
                fontSize: 12,
                fontFamily: "inherit",
                fontWeight: 700,
                cursor: running ? "not-allowed" : "pointer",
                letterSpacing: 0.5,
                transition: "all 0.2s",
                boxShadow: file && !running ? "0 0 20px #4FC3F733" : "none",
              }}
            >
              {running ? "⟳ analyzing..." : file ? "▶ run pipeline" : "select file"}
            </button>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div
            style={{
              background: "#EF535022",
              border: "1px solid #EF535044",
              borderRadius: 8,
              padding: "12px 16px",
              marginBottom: 24,
              fontSize: 12,
              color: "#EF5350",
              animation: "fadeIn 0.3s ease",
            }}
          >
            ⚠ {error}
          </div>
        )}

        {/* Results */}
        {results && (
          <div style={{ animation: "fadeIn 0.5s ease" }}>
            {/* Stats Row */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))",
                gap: 12,
                marginBottom: 24,
              }}
            >
              {[
                {
                  label: "Functions Found",
                  value: results.functions?.length || 0,
                  color: "#4FC3F7",
                  icon: "ƒ",
                },
                {
                  label: "Complexity Score",
                  value: results.complexity_score || 0,
                  color: "#AB47BC",
                  icon: "~",
                },
                {
                  label: "Bugs Found",
                  value: bugCount + secCount,
                  color: "#EF5350",
                  icon: "✗",
                },
                {
                  label: "Tests Passed",
                  value: `${passed}/${passed + failed}`,
                  color: "#66BB6A",
                  icon: "✓",
                },
              ].map((stat) => (
                <div
                  key={stat.label}
                  style={{
                    background: "#0f0f1e",
                    border: `1px solid ${stat.color}22`,
                    borderRadius: 10,
                    padding: "16px",
                  }}
                >
                  <div
                    style={{
                      fontSize: 22,
                      fontWeight: 700,
                      color: stat.color,
                      fontFamily: "'Syne', sans-serif",
                    }}
                  >
                    {stat.value}
                  </div>
                  <div style={{ fontSize: 10, color: "#444460", marginTop: 4 }}>
                    {stat.label}
                  </div>
                </div>
              ))}
            </div>

            {/* Tabs */}
            <div
              style={{
                background: "#0f0f1e",
                border: "1px solid #1e1e2e",
                borderRadius: 12,
                overflow: "hidden",
              }}
            >
              <div
                style={{
                  display: "flex",
                  borderBottom: "1px solid #1e1e2e",
                  overflowX: "auto",
                  background: "#0a0a12",
                }}
              >
                <TabButton label="📋 Summary" active={activeTab === "summary"} color="#4FC3F7" onClick={() => setActiveTab("summary")} />
                <TabButton label="🐛 Bugs" active={activeTab === "bugs"} count={bugCount} color="#EF5350" onClick={() => setActiveTab("bugs")} />
                <TabButton label="🔐 Security" active={activeTab === "security"} count={secCount} color="#FF7043" onClick={() => setActiveTab("security")} />
                <TabButton label="✨ Fixed Code" active={activeTab === "fixed"} color="#FFCA28" onClick={() => setActiveTab("fixed")} />
                <TabButton label="🧪 Tests" active={activeTab === "tests"} color="#66BB6A" onClick={() => setActiveTab("tests")} />
                <TabButton label="📜 Logs" active={activeTab === "logs"} count={results.logs?.length} color="#AB47BC" onClick={() => setActiveTab("logs")} />
              </div>

              <div style={{ padding: 24 }}>

                {/* Summary Tab */}
                {activeTab === "summary" && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                    <div>
                      <div style={{ fontSize: 10, color: "#444460", letterSpacing: 2, marginBottom: 10 }}>
                        CODE UNDERSTANDING
                      </div>
                      <p style={{ fontSize: 13, color: "#c9d1d9", lineHeight: 1.8, background: "#0a0a12", padding: 16, borderRadius: 8, border: "1px solid #1e1e2e" }}>
                        {results.code_summary}
                      </p>
                    </div>
                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
                      <div>
                        <div style={{ fontSize: 10, color: "#444460", letterSpacing: 2, marginBottom: 10 }}>
                          FUNCTIONS DETECTED
                        </div>
                        <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                          {results.functions?.length > 0 ? results.functions.map((fn) => (
                            <span key={fn} style={{ background: "#4FC3F722", color: "#4FC3F7", border: "1px solid #4FC3F733", borderRadius: 4, padding: "3px 10px", fontSize: 11 }}>
                              {fn}()
                            </span>
                          )) : <span style={{ color: "#444460", fontSize: 12 }}>None detected</span>}
                        </div>
                      </div>
                      <div>
                        <div style={{ fontSize: 10, color: "#444460", letterSpacing: 2, marginBottom: 10 }}>
                          FIX SUMMARY
                        </div>
                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                          {results.fix_summary?.length > 0 ? results.fix_summary.map((fix, i) => (
                            <div key={i} style={{ fontSize: 11, color: "#FFCA28", display: "flex", gap: 8 }}>
                              <span style={{ color: "#444460" }}>{String(i + 1).padStart(2, "0")}.</span> {fix}
                            </div>
                          )) : <span style={{ color: "#444460", fontSize: 12 }}>No fixes applied</span>}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Bugs Tab */}
                {activeTab === "bugs" && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {results.bug_report?.length === 0 ? (
                      <div style={{ textAlign: "center", color: "#66BB6A", padding: 32, fontSize: 13 }}>
                        ✓ No bugs found
                      </div>
                    ) : results.bug_report?.map((bug, i) => (
                      <div key={i} style={{ background: "#0a0a12", border: "1px solid #1e1e2e", borderLeft: `3px solid ${SEVERITY_COLOR[bug.severity] || "#555570"}`, borderRadius: 8, padding: "14px 16px", display: "flex", gap: 12, alignItems: "flex-start" }}>
                        <div style={{ fontSize: 10, color: "#444460", minWidth: 28, paddingTop: 2 }}>L{bug.line}</div>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 6 }}>
                            <SeverityBadge severity={bug.severity} />
                            <span style={{ fontSize: 10, color: "#555570", background: "#1e1e2e", padding: "1px 8px", borderRadius: 4 }}>{bug.type}</span>
                          </div>
                          <div style={{ fontSize: 12, color: "#c9d1d9" }}>{bug.description}</div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}

                {/* Security Tab */}
                {activeTab === "security" && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {results.security_issues?.length === 0 ? (
                      <div style={{ textAlign: "center", color: "#66BB6A", padding: 32, fontSize: 13 }}>
                        ✓ No security issues found
                      </div>
                    ) : results.security_issues?.map((issue, i) => (
                      <div key={i} style={{ background: "#0a0a12", border: "1px solid #FF704322", borderLeft: "3px solid #FF7043", borderRadius: 8, padding: "14px 16px" }}>
                        <div style={{ display: "flex", gap: 8, marginBottom: 8, alignItems: "center" }}>
                          <span style={{ fontSize: 10, color: "#444460" }}>Line {issue.line}</span>
                          <SeverityBadge severity={issue.severity} />
                        </div>
                        <div style={{ fontSize: 12, color: "#c9d1d9", marginBottom: 6 }}>{issue.issue}</div>
                        {issue.recommendation && (
                          <div style={{ fontSize: 11, color: "#555570" }}>→ {issue.recommendation}</div>
                        )}
                      </div>
                    ))}
                  </div>
                )}

                {/* Fixed Code Tab */}
                {activeTab === "fixed" && (
                  <div>
                    {results.fixed_code ? (
                      <CodeBlock code={results.fixed_code} />
                    ) : (
                      <div style={{ textAlign: "center", color: "#444460", padding: 32 }}>No fixed code generated</div>
                    )}
                  </div>
                )}

                {/* Tests Tab */}
                {activeTab === "tests" && (
                  <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
                    <div style={{ display: "flex", gap: 12 }}>
                      <div style={{ background: "#66BB6A22", border: "1px solid #66BB6A44", borderRadius: 8, padding: "12px 24px", textAlign: "center" }}>
                        <div style={{ fontSize: 24, fontWeight: 700, color: "#66BB6A", fontFamily: "Syne, sans-serif" }}>{passed}</div>
                        <div style={{ fontSize: 10, color: "#444460" }}>PASSED</div>
                      </div>
                      <div style={{ background: "#EF535022", border: "1px solid #EF535044", borderRadius: 8, padding: "12px 24px", textAlign: "center" }}>
                        <div style={{ fontSize: 24, fontWeight: 700, color: "#EF5350", fontFamily: "Syne, sans-serif" }}>{failed}</div>
                        <div style={{ fontSize: 10, color: "#444460" }}>FAILED</div>
                      </div>
                    </div>
                    {results.test_results?.errors?.length > 0 && (
                      <div>
                        <div style={{ fontSize: 10, color: "#444460", letterSpacing: 2, marginBottom: 8 }}>ERRORS</div>
                        {results.test_results.errors.map((err, i) => (
                          <div key={i} style={{ background: "#EF535011", border: "1px solid #EF535022", borderRadius: 6, padding: "8px 12px", fontSize: 11, color: "#EF5350", marginBottom: 4 }}>{err}</div>
                        ))}
                      </div>
                    )}
                    <div>
                      <div style={{ fontSize: 10, color: "#444460", letterSpacing: 2, marginBottom: 10 }}>GENERATED TEST CODE</div>
                      {results.test_code && <CodeBlock code={results.test_code} />}
                    </div>
                  </div>
                )}

                {/* Logs Tab */}
                {activeTab === "logs" && (
                  <div style={{ background: "#0a0a12", border: "1px solid #1e1e2e", borderRadius: 8, padding: 16, maxHeight: 400, overflowY: "auto" }}>
                    {results.logs?.length === 0 ? (
                      <div style={{ color: "#444460", fontSize: 12 }}>No logs available</div>
                    ) : results.logs?.map((log, i) => (
                      <div key={i} style={{ fontSize: 11, color: "#555570", lineHeight: 1.8, borderBottom: "1px solid #1a1a2a", padding: "4px 0" }}>
                        <span style={{ color: "#AB47BC" }}>[{String(i).padStart(3, "0")}]</span>{" "}
                        <span style={{ color: "#c9d1d9" }}>{log}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Footer */}
        <div style={{ marginTop: 32, textAlign: "center", fontSize: 9, color: "#2a2a3a", letterSpacing: 2 }}>
          SE4010 · CTSE · SLIIT · MAS CODE REVIEW PIPELINE
        </div>
      </div>
    </div>
  );
}
