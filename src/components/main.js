
import { useEffect, useRef } from "react";
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

  useEffect(() => {
    // เคลียร์ workspace เก่า
    if (workspace.current) {
      workspace.current.dispose();
      workspace.current = null;
    }

    // Inject Blockly
    workspace.current = Blockly.inject(blocklyDiv.current, {
      toolbox: `
        <xml>
          <block type="set_url"></block>
          <block type="add_url"></block>
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

  const generateCode = () => {
    if (!workspace.current || workspace.current.getAllBlocks(false).length === 0) {
      alert("⚠️ No blocks found! Please add blocks before generating code.");
      return;
    }

    const allBlocks = workspace.current.getAllBlocks(false);
    let hasSetUrl = false;
    let hasCheckBlock = false;

    allBlocks.forEach((block) => {
      if (block.type === "set_url") hasSetUrl = true;
      if (block.type.startsWith("check_")) hasCheckBlock = true;
    });

    if (!hasSetUrl) {
      alert("⚠️ You must set a URL before generating code.");
      return;
    }

    if (!hasCheckBlock) {
      alert("⚠️ Please add at least one security check before generating code.");
      return;
    }

    // ✅ เคลียร์ผลลัพธ์แต่ละประเภทก่อนรันใหม่
    localStorage.removeItem("xssResults");
    localStorage.removeItem("csrfResults");
    localStorage.removeItem("sqlResults");
    localStorage.removeItem("idorResults");
    localStorage.removeItem("bacResults");

    const code = javascriptGenerator.workspaceToCode(workspace.current);
    console.log("Generated Code:", code);

    try {
      eval(code); // 👈 จำไว้ว่าควรใช้ใน dev เท่านั้น

      setTimeout(() => {
        const xss = JSON.parse(localStorage.getItem("xssResults") || "[]");
        const csrf = JSON.parse(localStorage.getItem("csrfResults") || "[]");
        const sql = JSON.parse(localStorage.getItem("sqlResults") || "[]");
        const idor = JSON.parse(localStorage.getItem("idorResults") || "[]");
        const bac = JSON.parse(localStorage.getItem("bacResults") || "[]");

        const total =
          xss.length + csrf.length + sql.length + idor.length + bac.length;

        if (total === 0) {
          alert("⚠️ No test results found. Please ensure the test has run.");
          return;
        }

        alert("✅ Code Executed Successfully!");
        navigate("/dashboard");
      }, 30000); // ⏳ เผื่อเวลา API ทดสอบทั้งหมด
    } catch (error) {
      console.error("❌ Execution Error:", error);
      alert("Error executing generated code!");
    }
  };

  return (
    <div className="main-container">
      {/* ✅ Navigation Bar */}
      <div className="navbar">
        <div className="navbar-left">
          <h1>Website Security Testing 🚀</h1>
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
              localStorage.removeItem("token");
              navigate("/login");
            }}
          >
            Logout
          </button>
        </div>
      </div>

      {/* ✅ Blockly Workspace */}
      <div className="blockly-container">
        <div className="blockly-workspace" ref={blocklyDiv}></div>
      </div>
    </div>
  );
};

export default Main;
