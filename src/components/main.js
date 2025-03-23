import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import * as Blockly from "blockly";
import { javascriptGenerator } from "blockly/javascript";
import "../main.css"; // ✅ Import CSS

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

    if (workspace.current) {
      workspace.current.dispose();
      workspace.current = null;
    }

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

    Blockly.svgResize(workspace.current);
  }, [navigate]);

  // ✅ ฟังก์ชัน Generate Code
  const generateCode = () => {
    if (!workspace.current || workspace.current.getAllBlocks(false).length === 0) {
      alert("⚠️ No blocks found! Please add blocks before generating code.");
      return;
    }
  
    const allBlocks = workspace.current.getAllBlocks(false);
    let hasSetUrl = false;
    let hasCheckBlock = false;
  
    allBlocks.forEach(block => {
      if (block.type === "set_url") {
        hasSetUrl = true;
      }
      if (block.type.startsWith("check_")) {
        hasCheckBlock = true;
      }
    });
  
    if (!hasSetUrl) {
      alert("⚠️ You must set a URL before generating code.");
      return;
    }
  
    if (!hasCheckBlock) {
      alert("⚠️ Please add at least one security check before generating code.");
      return;
    }
  
    localStorage.removeItem("testResults"); // ✅ ล้างค่าก่อน Generate ใหม่
    const code = javascriptGenerator.workspaceToCode(workspace.current);
    
    console.log("Generated Code:", code); // ✅ Debug ตรวจสอบโค้ดที่ถูกสร้าง
    
    try {
      eval(code);
  
      setTimeout(() => {
        const testResults = JSON.parse(localStorage.getItem("testResults")) || [];
        console.log("📌 Debug: testResults = ", testResults); // ✅ Debug ดูค่าที่บันทึกได้
  
        if (testResults.length === 0) {
          alert("No test results found. Please ensure the test has run.");
          return;
        }
  
        localStorage.setItem("csrfResults", JSON.stringify(testResults));
        alert("Code Executed Successfully!");
        navigate("/dashboard");
  
      }, 1000); // ✅ ใช้ `setTimeout` รอให้ `testResults` อัปเดตก่อน
  
    } catch (error) {
      console.error("Execution Error:", error);
      alert("Error executing code!");
    }
  };
  return (
    <div className="main-container">
      {/* ✅ Navigation Bar */}
      <div className="navbar">
        <h1>Website Security Testing 🚀</h1>
        <div className="navbar-buttons">
          <button className="generate-button" onClick={generateCode}>Generate Code</button>
          <button className="logout-button" onClick={() => {
            localStorage.removeItem("token");
            navigate("/login");
          }}>Logout</button>
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
