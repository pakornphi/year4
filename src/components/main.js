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
    const token = localStorage.getItem("token");
    if (!token) {
      alert("⚠️ You must be logged in to access this page.");
      navigate("/login");
    }

    // 🔹 ลบ Workspace เดิมก่อนสร้างใหม่ (ป้องกัน 2 อัน)
    if (workspace.current) {
      workspace.current.dispose();
      workspace.current = null;
    }

    // 🔹 Inject Blockly (สร้าง Workspace ใหม่)
    workspace.current = Blockly.inject(blocklyDiv.current, {
      toolbox: `
        <xml>
          <block type="set_url"></block>
          <block type="add_url"></block>
          <block type="check_sql_injection"></block>
          <block type="check_xss"></block>
          <block type="check_csrf"></block>
          <block type="check_idor"></block>
          <block type="check_broken_access"></block>
        </xml>
      `,
      rtl: false,
      toolboxPosition: "start",
    });

  }, [navigate]);

  // ✅ แปลง Block เป็นโค้ด JavaScript
  const generateCode = () => {
    const code = javascriptGenerator.workspaceToCode(workspace.current);
    alert("Generated Code:\n" + code);
  };

  return (
    <div className="main-container">
      <h1>Website Security Testing 🚀</h1>
      <div className="blockly-container">
        <div className="blockly-workspace" ref={blocklyDiv}></div>
      </div>
      <button onClick={generateCode} className="generate-btn">Generate Code</button>
      <button onClick={() => { localStorage.removeItem("token"); navigate("/login"); }} className="logout-btn">Logout</button>
    </div>
  );
};

export default Main;
