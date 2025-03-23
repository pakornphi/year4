import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import "./dashboard.css"; // ✅ Import CSS

const Dashboard = () => {
  const navigate = useNavigate();
  const [results, setResults] = useState([]);

  useEffect(() => {
    // ✅ ดึงผลลัพธ์จาก LocalStorage ทุกครั้งที่โหลดหน้า
    const storedResults = JSON.parse(localStorage.getItem("csrfResults")) || [];
    
    console.log("📢 Loaded CSRF Test Results:", storedResults);

    setResults(storedResults);
  }, []);

  // ✅ ฟังก์ชันล้างผลลัพธ์
  const clearResults = () => {
    localStorage.removeItem("csrfResults"); // ✅ ลบผลลัพธ์ CSRF
    localStorage.removeItem("testResults"); // ✅ ลบข้อมูลที่ใช้ Generate Code
    setResults([]); // ✅ อัปเดต UI ให้ว่าง
  
    // ✅ ตรวจสอบว่า token ยังอยู่
    const token = localStorage.getItem("token");
    if (!token) {
      localStorage.setItem("token", "your_token_value"); // 🛑 ใส่ค่าเดิมถ้าหาย
    }
  };
  
  return (
    <div className="dashboard-container">
      <h1 className="dashboard-title">🔍 CSRF Test Results</h1>
      <button className="back-button" onClick={() => {navigate("/main");}}>⬅️ Back to Main</button>
      <button className="clear-button" onClick={clearResults}>🗑️ Clear Results</button>

      {results.length > 0 ? (
        <div className="results-table">
          {results.map((result, index) => {
            const isPassed = result.includes("successful");
            return (
              <div key={index} className={`result-card ${isPassed ? "pass" : "fail"}`}>
                <p><strong>🛡️ URL:</strong> {result.split(" → ")[0]}</p>
                <p><strong>📌 Test Result:</strong> {result.split(" → ")[1]}</p>
              </div>
            );
          })}
        </div>
      ) : (
        <p className="no-results">⚠️ No results available. Please generate code first.</p>
      )}
    </div>
  );
};

export default Dashboard;
