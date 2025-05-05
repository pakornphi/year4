import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Label
} from "recharts";
import "./dashboard.css";

const Dashboard = () => {
  const navigate = useNavigate();
  const [resultsByUrl, setResultsByUrl] = useState({});
  const [selectedUrl, setSelectedUrl] = useState("");
  const [chartData, setChartData] = useState([]);

  useEffect(() => {
    const rawResults = JSON.parse(localStorage.getItem("testResults")) || [];
    const grouped = {};

    rawResults.forEach((result) => {
      const url = result.tested_url || result.url;
      const messages = [];

      Object.entries(result).forEach(([key, value]) => {
        if (key.startsWith("test_")) {
          const status = value?.vulnerability === true ? "True" :
                         value?.vulnerability === false ? "False" : "None";
          messages.push(`${key}: ${status}`);
        }
        if (key === "results" && typeof value === "object") {
          // เพิ่มกรณี XSS
          Object.entries(value).forEach(([xssKey, xssVal]) => {
            messages.push(`${xssKey}: ${xssVal.count} vulnerable payload(s)`);
          });
        }
      });

      // Add overall summary if available
      if ("csrf_vulnerable" in result) {
        messages.push(`csrf_vulnerable: ${result.csrf_vulnerable}`);
      }
      if ("xss_vulnerable" in result) {
        messages.push(`xss_vulnerable: ${result.xss_vulnerable}`);
      }

      if (!grouped[url]) {
        grouped[url] = [];
      }
      grouped[url] = messages;
    });

    setResultsByUrl(grouped);
    const firstUrl = Object.keys(grouped)[0];
    setSelectedUrl(firstUrl || "");

    if (grouped[firstUrl]) {
      updateChartData(grouped[firstUrl]);
    }
  }, []);

  const updateChartData = (messages) => {
    let trueCount = 0;
    let falseCount = 0;

    messages.forEach((item) => {
      if (item.includes(": True")) trueCount++;
      else if (item.includes(": False")) falseCount++;
    });

    setChartData([
      { name: "Vulnerable", value: trueCount, color: "#f87171" },
      { name: "Safe", value: falseCount, color: "#4ade80" }
    ]);
  };

  const clearResults = () => {
    localStorage.removeItem("testResults");
    setResultsByUrl({});
    setSelectedUrl("");
    setChartData([]);
  };

  return (
    <div className="dashboard-layout">
      <div className="sidebar">
        <h3>🔗 URLs</h3>
        {Object.keys(resultsByUrl).map((url) => (
          <button
            key={url}
            className={`url-button ${url === selectedUrl ? "active" : ""}`}
            onClick={() => {
              setSelectedUrl(url);
              updateChartData(resultsByUrl[url]);
            }}
          >
            {url}
          </button>
        ))}
      </div>

      <div className="dashboard-main">
        <div className="dashboard-header">
          <h1>🧪 Web Vulnerability Test Results</h1>
          <div>
            <button onClick={() => navigate("/main")}>⬅️ Back</button>
            <button onClick={clearResults}>🗑️ Clear</button>
          </div>
        </div>

        {selectedUrl && resultsByUrl[selectedUrl]?.length > 0 ? (
          <>
            {/* Pie Chart on Top */}
            <div style={{ width: "100%", height: 350, marginBottom: 50 }}>
              <h3>📊 Vulnerability Summary</h3>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={3}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="result-card full">
              <pre>{resultsByUrl[selectedUrl].join("\n")}</pre>
            </div>
          </>
        ) : (
          <p className="no-results">⚠️ No results available for this URL.</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
