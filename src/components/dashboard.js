import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();
  const [resultsByUrl, setResultsByUrl] = useState({});
  const [selectedUrl, setSelectedUrl] = useState("");

  useEffect(() => {
    const rawResults = JSON.parse(localStorage.getItem("csrfResults")) || [];
    const grouped = {};

    rawResults.forEach(result => {
      const [url, message] = result.split(" → ");
      if (!grouped[url]) grouped[url] = [];
      grouped[url].push(message);
    });

    setResultsByUrl(grouped);
    const firstUrl = Object.keys(grouped)[0];
    setSelectedUrl(firstUrl || "");
  }, []);

  const clearResults = () => {
    localStorage.removeItem("csrfResults");
    localStorage.removeItem("testResults");
    setResultsByUrl({});
    setSelectedUrl("");
  };

  return (
    <div className="dashboard-layout">
      {/* ✅ Sidebar URL List */}
      <div className="sidebar">
        <h3>🔗 URLs</h3>
        {Object.keys(resultsByUrl).map(url => (
          <button
            key={url}
            className={`url-button ${url === selectedUrl ? "active" : ""}`}
            onClick={() => setSelectedUrl(url)}
          >
            {url}
          </button>
        ))}
      </div>

      {/* ✅ Main Content */}
      <div className="dashboard-main">
        <div className="dashboard-header">
          <h1>🧪 CSRF Test Results</h1>
          <div>
            <button onClick={() => navigate("/main")}>⬅️ Back</button>
            <button onClick={clearResults}>🗑️ Clear</button>
          </div>
        </div>

        {selectedUrl && resultsByUrl[selectedUrl] ? (
          <div className="results-table">
            {resultsByUrl[selectedUrl].map((msg, idx) => {
              const isPassed = msg.toLowerCase().includes("successful");
              return (
                <div key={idx} className={`result-card ${isPassed ? "pass" : "fail"}`}>
                  <p><strong>📌 Test Result:</strong> {msg}</p>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="no-results">⚠️ No results available for this URL.</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
