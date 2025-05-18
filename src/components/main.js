
// import { useEffect, useRef } from "react";
// import { useNavigate } from "react-router-dom";
// import * as Blockly from "blockly";
// import { javascriptGenerator } from "blockly/javascript";
// import "../main.css";
// import { useState } from "react";

// // ✅ Import Blocks และ Generator
// import "../blockly/blocks";
// import "../blockly/generator";

// const Main = () => {
//   const navigate = useNavigate();
//   const blocklyDiv = useRef(null);
//   const workspace = useRef(null);
//   const [logoutMessage, setLogoutMessage] = useState("");
//   const [username, setUsername] = useState("");
  

//   useEffect(() => {
//     const storedUsername = localStorage.getItem("username");
//     if (storedUsername) {
//       setUsername(storedUsername);
//     }

//     // เคลียร์ workspace เก่า
//     if (workspace.current) {
//       workspace.current.dispose();
//       workspace.current = null;
//     }

//     // Inject Blockly
//     workspace.current = Blockly.inject(blocklyDiv.current, {
//       toolbox: `
//         <xml>
//           <block type="set_url"></block>
//           <block type="add_url"></block>
//           <block type="check_sql_injection"></block>
//           <block type="check_xss"></block>
//           <block type="check_csrf"></block>
//           <block type="check_idor"></block>
//           <block type="check_bac"></block>
//         </xml>
//       `,
//       rtl: false,
//       toolboxPosition: "start",
//     });

//     Blockly.svgResize(workspace.current);
//   }, [navigate]);

//   const generateCode = () => {
//     if (!workspace.current || workspace.current.getAllBlocks(false).length === 0) {
//       alert("⚠️ No blocks found! Please add blocks before generating code.");
//       return;
//     }

//     const allBlocks = workspace.current.getAllBlocks(false);
//     let hasSetUrl = false;
//     let hasCheckBlock = false;

//     allBlocks.forEach((block) => {
//       if (block.type === "set_url") hasSetUrl = true;
//       if (block.type.startsWith("check_")) hasCheckBlock = true;
//     });

//     if (!hasSetUrl) {
//       alert("⚠️ You must set a URL before generating code.");
//       return;
//     }

//     if (!hasCheckBlock) {
//       alert("⚠️ Please add at least one security check before generating code.");
//       return;
//     }

//     // ✅ เคลียร์ผลลัพธ์แต่ละประเภทก่อนรันใหม่
//     localStorage.removeItem("xssResults");
//     localStorage.removeItem("csrfResults");
//     localStorage.removeItem("sqlResults");
//     localStorage.removeItem("idorResults");
//     localStorage.removeItem("bacResults");

//     const code = javascriptGenerator.workspaceToCode(workspace.current);
//     console.log("Generated Code:", code);

//     try {
//       eval(code); // 👈 จำไว้ว่าควรใช้ใน dev เท่านั้น

//       setTimeout(() => {
//         const xss = JSON.parse(localStorage.getItem("xssResults") || "[]");
//         const csrf = JSON.parse(localStorage.getItem("csrfResults") || "[]");
//         const sql = JSON.parse(localStorage.getItem("sqlResults") || "[]");
//         const idor = JSON.parse(localStorage.getItem("idorResults") || "[]");
//         const bac = JSON.parse(localStorage.getItem("bacResults") || "[]");

//         const total =
//           xss.length + csrf.length + sql.length + idor.length + bac.length;

//         if (total === 0) {
//           alert("⚠️ No test results found. Please ensure the test has run.");
//           return;
//         }

//         alert("✅ Code Executed Successfully!");
//         navigate("/dashboard");
//       }, 40000); // ⏳ เผื่อเวลา API ทดสอบทั้งหมด
//     } catch (error) {
//       console.error("❌ Execution Error:", error);
//       alert("Error executing generated code!");
//     }
//   };

//   return (
//     <div className="main-container">
//       {/* ✅ Navigation Bar */}
//       <div className="navbar">
//         <div className="navbar-left">
//           <h1>Website Security Testing 🚀</h1>
//            <h1>Welcome, {username} 👋</h1>
//           <button className="dashboard-button" onClick={() => navigate("/dashboard")}>
//             Dashboard
//           </button>
    
//         </div>
//         <div className="navbar-buttons">
//           <button className="generate-button" onClick={generateCode}>
//             Simulate
//           </button>
//           <button
//             className="logout-button"
//             onClick={() => {
//               setLogoutMessage("✅ Logout successful!");
//               localStorage.removeItem("token");
//               localStorage.removeItem("username");
//               setTimeout(() => {
//                 setLogoutMessage("");
//                 navigate("/login");
//               }, 1500); // แสดงข้อความ 1.5 วินาที
//             }}
//           >
//             Logout
//           </button>
//         </div>
//       </div>

//       {/* ✅ Blockly Workspace */}
//       <div className="blockly-container">
//         <div className="blockly-workspace" ref={blocklyDiv}></div>
//       </div>
//     </div>
//   );
// };

// export default Main;

import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as Blockly from "blockly";
import { javascriptGenerator } from "blockly/javascript";
import "../main.css";

// ✅ Import Blocks และ Generator
import "../blockly/blocks";
import "../blockly/generator";

const Main = () => {
  const navigate = useNavigate();
  const blocklyDiv = useRef(null);
  const workspace = useRef(null);
  const [logoutMessage, setLogoutMessage] = useState("");
  const [username, setUsername] = useState("");

  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) setUsername(storedUsername);

    // ✅ ล้าง run-count ของวันเก่า
    const cleanOldRunData = () => {
      const user = storedUsername || "anonymous";
      const today = new Date().toISOString().split("T")[0];
      Object.keys(localStorage).forEach((key) => {
        if (key.startsWith(`runTimestamps_${user}_`)) {
          const keyDate = key.split("_").pop();
          if (keyDate !== today) {
            localStorage.removeItem(key);
          }
        }
      });
    };

    cleanOldRunData();

    // ✅ เคลียร์ workspace เก่า
    if (workspace.current) {
      workspace.current.dispose();
      workspace.current = null;
    }

    // ✅ สร้าง Blockly workspace ใหม่
    workspace.current = Blockly.inject(blocklyDiv.current, {
      toolbox: `
        <xml>
          <block type="set_url"></block>
          <block type="check_sql_injection"></block>
          <block type="check_xss"></block>
          <block type="check_csrf"></block>
          <block type="check_idor"></block>
          <block type="check_bac"></block>
        </xml>
      `,
      rtl: false,
      toolboxPosition: "start",
    });

    Blockly.svgResize(workspace.current);
  }, [navigate]);

  // ✅ Utility
  const getTodayKey = () => {
    const today = new Date().toISOString().split("T")[0];
    const user = localStorage.getItem("username") || "anonymous";
    return `runTimestamps_${user}_${today}`;
  };

    const getRemainingTimeMessage = () => {
    const timestamps = JSON.parse(localStorage.getItem(getTodayKey()) || "[]");
    if (timestamps.length < 1000) return null;

    // ⏰ ตั้งเวลา reset ที่เที่ยงคืนวันถัดไป
    const now = new Date();
    const tomorrowMidnight = new Date();
    tomorrowMidnight.setHours(24, 0, 0, 0); // 24:00 = เที่ยงคืนถัดไป

    const diffMs = tomorrowMidnight - now;
    if (diffMs <= 0) return null;

    const minutes = Math.ceil(diffMs / 1000 / 60);
    return `⏳ You've reached the 3-run limit today. Try again in ${minutes} minute(s).`;
  };

  const canRunTest = () => {
    const timestamps = JSON.parse(localStorage.getItem(getTodayKey()) || "[]");
    return timestamps.length < 1000;
  };

  const recordRun = () => {
    const key = getTodayKey();
    const timestamps = JSON.parse(localStorage.getItem(key) || "[]");
    timestamps.push(new Date().toISOString());
    localStorage.setItem(key, JSON.stringify(timestamps));
  };

  const generateCode = () => {
    const remainingMessage = getRemainingTimeMessage();
    if (!canRunTest()) {
      alert(remainingMessage || "⚠️ You've reached the maximum number of test runs for today.");
      return;
    }

    if (!workspace.current || workspace.current.getAllBlocks(false).length === 0) {
      alert("⚠️ No blocks found! Please add blocks before generating code.");
      return;
    }

    const allBlocks = workspace.current.getAllBlocks(false);
    let hasSetUrl = false;
    const resultKeysToCheck = [];

    allBlocks.forEach((block) => {
      if (block.type === "set_url") hasSetUrl = true;
      if (block.type === "check_sql_injection") resultKeysToCheck.push("sqlResults");
      if (block.type === "check_xss") resultKeysToCheck.push("xssResults");
      if (block.type === "check_csrf") resultKeysToCheck.push("csrfResults");
      if (block.type === "check_idor") resultKeysToCheck.push("idorResults");
      if (block.type === "check_bac") resultKeysToCheck.push("bacResults");
    });

    if (!hasSetUrl) {
      alert("⚠️ You must set a URL before generating code.");
      return;
    }

    if (resultKeysToCheck.length === 0) {
      alert("⚠️ Please add at least one security check before generating code.");
      return;
    }

    // ✅ ล้างผลลัพธ์เก่าทุกประเภท
    ["sqlResults", "xssResults", "csrfResults", "idorResults", "bacResults"].forEach((key) =>
      localStorage.removeItem(key)
    );

    const code = javascriptGenerator.workspaceToCode(workspace.current);
    console.log("Generated Code:", code);

    try {
      recordRun();
      eval(code);
      waitForResults(resultKeysToCheck);
    } catch (error) {
      console.error("❌ Execution Error:", error);
      alert("Error executing generated code!");
    }
  };

  const waitForResults = (keys) => {
    const startTime = Date.now();

    const interval = setInterval(() => {
      const allReady = keys.every((key) => {
        const val = localStorage.getItem(key);
        return val && JSON.parse(val).length > 0;
      });

      if (allReady) {
        clearInterval(interval);
        alert("✅ Code executed successfully!");
        navigate("/dashboard");
      }

      if (Date.now() - startTime > 60000) {
        clearInterval(interval);
        alert("⚠️ Timeout: Some test results did not complete in time.");
      }
    }, 1000);
  };

  return (
    <div className="main-container">
      <div className="navbar">
        <div className="navbar-left">
          <h1>Website Security Testing 🚀</h1>
          <h1>Welcome, {username} 👋</h1>
          <button className="dashboard-button" onClick={() => navigate("/dashboard")}>
            Dashboard
          </button>
        </div>
        <div className="navbar-buttons">
          <button className="generate-button" onClick={generateCode}>
            Simulate
          </button>
          <button
            className="logout-button"
            onClick={() => {
              setLogoutMessage("✅ Logout successful!");
              localStorage.removeItem("token");
              localStorage.removeItem("username");
              setTimeout(() => {
                setLogoutMessage("");
                navigate("/login");
              }, 1500);
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="blockly-container">
        <div className="blockly-workspace" ref={blocklyDiv}></div>
      </div>
    </div>
  );
};

export default Main;
