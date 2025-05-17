import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import "./dashboard.css";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";

const Dashboard = () => {
  const navigate = useNavigate();
  const [resultsByUrl, setResultsByUrl] = useState({});
  const [selectedUrl, setSelectedUrl] = useState("");
  const [chartData, setChartData] = useState([]);

  const mergeResults = (...arrays) => {
    const merged = {};
    arrays.flat().forEach((entry) => {
      const url = entry.tested_url || entry.url;
      const messages = [];

      // ✅ รองรับแบบ result.results เป็น array ของ string
      if (Array.isArray(entry.results)) {
        messages.push(...entry.results);
      }

      if (Array.isArray(entry.messages)) {
        messages.push(...entry.messages);
      }

      if ("xss_vulnerable" in entry)
        messages.push(`(XSS) xss_vulnerable: ${entry.xss_vulnerable}`);
      if ("csrf_vulnerable" in entry)
        messages.push(`(CSRF) csrf_vulnerable: ${entry.csrf_vulnerable}`);
      if ("idor_vulnerable" in entry)
        messages.push(`(IDOR) idor_vulnerable: ${entry.idor_vulnerable}`);
      if ("bac_vulnerable" in entry)
        messages.push(`(BAC) bac_vulnerable: ${entry.bac_vulnerable}`);
      if ("vulnerable" in entry)
        messages.push(`(SQL) vulnerable: ${entry.vulnerable}`);

      Object.entries(entry).forEach(([key, value]) => {
        if (key.startsWith("test_") && typeof value === "object") {
          const status =
            value.vulnerability === true
              ? "True"
              : value.vulnerability === false
              ? "False"
              : "None";
          messages.push(`(CSRF) ${key}: ${status}`);
        }
      });

      if (!merged[url]) merged[url] = [];
      merged[url].push(...messages);
    });
    return merged;
  };

  useEffect(() => {
    const xss = JSON.parse(localStorage.getItem("xssResults") || "[]");
    const csrf = JSON.parse(localStorage.getItem("csrfResults") || "[]");
    const sql = JSON.parse(localStorage.getItem("sqlResults") || "[]");
    const idor = JSON.parse(localStorage.getItem("idorResults") || "[]");
    const bac = JSON.parse(localStorage.getItem("bacResults") || "[]");

    const grouped = mergeResults(xss, csrf, sql, idor, bac);
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

    messages.forEach((msg) => {
      if (msg.includes("vulnerability:True")) trueCount++;
      else if (msg.includes("vulnerability:False")) falseCount++;
    });

    setChartData([
      { name: "Vulnerable", value: trueCount, color: "#f87171" },
      { name: "Safe", value: falseCount, color: "#4ade80" },
    ]);
  };

  const clearResults = () => {
    [
      "xssResults",
      "csrfResults",
      "sqlResults",
      "idorResults",
      "bacResults",
    ].forEach((key) => localStorage.removeItem(key));

    setResultsByUrl({});
    setSelectedUrl("");
    setChartData([]);
  };

  const exportPDF = () => {
    const input = document.querySelector(".dashboard-main");

    html2canvas(input).then((canvas) => {
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF({
        orientation: "portrait",
        unit: "mm",
        format: "a4",
      });

      const imgProps = pdf.getImageProperties(imgData);
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = (imgProps.height * pdfWidth) / imgProps.width;

      pdf.addImage(imgData, "PNG", 0, 0, pdfWidth, pdfHeight);
      pdf.save("vulnerability-report.pdf");
    });
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
            <button onClick={exportPDF}>📄 Export PDF</button>
          </div>
        </div>

        {selectedUrl && resultsByUrl[selectedUrl]?.length > 0 ? (
          <div className="result-card full">
            <h3 className="vuln-heading">{selectedUrl}</h3>

            <div style={{ width: "100%", height: 280, marginBottom: 20 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie
                    data={chartData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={90}
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                  >
                    {chartData.map((entry, index) => (
                      <Cell key={index} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <pre className="vuln-pre">
              {resultsByUrl[selectedUrl].join("\n")}
            </pre>
          </div>
        ) : (
          <p className="no-results">⚠️ No results available for this URL.</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
