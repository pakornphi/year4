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
  const [selectedUrl, setSelectedUrl] = useState("");
  const [results, setResults] = useState({});
  const COLORS = ["#f87171", "#4ade80"];

  const categoryKeys = [
    "xssResults",
    "csrfResults",
    "sqlResults",
    "idorResults",
    "bacResults",
  ];

  useEffect(() => {
    const data = {};
    categoryKeys.forEach((key) => {
      const parsed = JSON.parse(localStorage.getItem(key) || "[]");
      parsed.forEach((entry) => {
        const url = entry.tested_url || entry.url;
        if (!data[url]) data[url] = {};
        data[url][key] = entry;
      });
    });

    setResults(data);

    const firstUrl = Object.keys(data)[0];
    if (firstUrl) setSelectedUrl(firstUrl);
  }, []);

  const generateChartData = (entry) => {
    let trueCount = 0;
    let falseCount = 0;

    Object.entries(entry).forEach(([k, v]) => {
      if (typeof v === "object" && v !== null && "vulnerability" in v) {
        if (v.vulnerability === true) trueCount++;
        else if (v.vulnerability === false) falseCount++;
      } else if (typeof v === "boolean") {
        v ? trueCount++ : falseCount++;
      } else if (typeof v === "string") {
        const lower = v.toLowerCase();
        if (lower.includes("vulnerability:true")) trueCount++;
        else if (lower.includes("vulnerability:false")) falseCount++;
      } else if (Array.isArray(v)) {
        // หากเป็น array ของ string เช่น ['... → vulnerability:True']
        v.forEach((line) => {
          const lower = line.toLowerCase();
          if (lower.includes("vulnerability:true")) trueCount++;
          else if (lower.includes("vulnerability:false")) falseCount++;
        });
      }
    });

    return [
      { name: "Vulnerable", value: trueCount, color: COLORS[0] },
      { name: "Safe", value: falseCount, color: COLORS[1] },
    ];
  };

  const clearResults = () => {
    categoryKeys.forEach((key) => localStorage.removeItem(key));
    setResults({});
    setSelectedUrl("");
  };

  const exportPDF = () => {
    const input = document.querySelector(".dashboard-main");

    html2canvas(input).then((canvas) => {
      const imgData = canvas.toDataURL("image/png");
      const pdf = new jsPDF({ orientation: "portrait", unit: "mm", format: "a4" });
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
        {Object.keys(results).map((url) => (
          <button
            key={url}
            className={`url-button ${url === selectedUrl ? "active" : ""}`}
            onClick={() => setSelectedUrl(url)}
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

        {selectedUrl && results[selectedUrl] ? (
          categoryKeys.map((key) => {
            const entry = results[selectedUrl][key];
            if (!entry) return null;

            const chartData = generateChartData(entry);
            const lines = [];
                  Object.entries(entry).forEach(([field, value]) => {
                    if (field === "url" || field === "tested_url") return;
                    if (field.startsWith("test_")) return; // ✅ ข้าม internal field เช่น test_*

                    if (field === "xss_vulnerable" || field.endsWith("_vulnerable")) {
                      lines.push(`${field} → vulnerability:${value}`);
                      return;
                    }

                    if (typeof value === "object" && value !== null && "vulnerability" in value) {
                      lines.push(`${field} → vulnerability:${value.vulnerability}`);
                      if (value.info && value.info !== "/" && value.info !== null) {
                        lines.push(`info=${JSON.stringify(value.info)}`);
                      }
                    } else if (typeof value === "boolean") {
                      lines.push(`${field} → vulnerability:${value}`);
                    } else if (Array.isArray(value)) {
                      value.forEach((v) => lines.push(v));
                    } else if (typeof value === "string" && field.includes("vulnerable")) {
                      lines.push(`${field} → vulnerability:${value}`);
                    }
                  });
            return (
              <div key={key} className="vuln-section">
                <h3 className="vuln-heading">{key.replace("Results", "").toUpperCase()}</h3>

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

                <pre className="vuln-pre">{lines.join("\n")}</pre>
              </div>
            );
          })
        ) : (
          <p className="no-results">⚠️ No results available for this URL.</p>
        )}
      </div>
    </div>
  );
};

export default Dashboard;
