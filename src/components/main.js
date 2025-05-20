import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as Blockly from "blockly";
import { javascriptGenerator } from "blockly/javascript";
import "../main.css";

// ✅ Import Blocks และ Generator
import "../blockly/blocks";
import "../blockly/generator";
const blockDescriptions = {
  set_url: `
<b>🌐 Test Website URL</b><br><br>
ใช้สำหรับกำหนด URL ของเว็บไซต์ที่จะทดสอบ<br><br>

<b>💡 คำแนะนำ:</b><br>
คุณสามารถใช้ <code>localtunnel (lt)</code> เพื่อเปิดเว็บจากเครื่องของคุณ (localhost) ออกสู่อินเทอร์เน็ตได้<br><br>

<b>📋 ขั้นตอนการใช้งาน:</b>
<ol>
  <li>เปิด Terminal หรือ Command Prompt</li>
  <li>ติดตั้ง LocalTunnel (ครั้งเดียว):<br>
    <code>npm install -g localtunnel</code>
  </li>
  <li>รันแอปของคุณ (เช่น React, Flask, Node.js) บนพอร์ตที่กำหนด เช่น <code>3000</code> หรือ <code>5000</code></li>
  <li>เปิด tunnel ไปยังพอร์ตที่แอปรันอยู่ เช่น:<br>
    <code>lt --port 3000</code><br>
    หรือ <code>lt --port 5000</code>
  </li>
  <li>หากต้องการชื่อ URL ที่จำง่าย ให้เพิ่ม:<br>
    <code>lt --port 3000 --subdomain myappdemo</code>
  </li>
</ol>

<b>📌 วิธีดูว่าแอปรันอยู่ที่พอร์ตไหน:</b>
<ul>
  <li>หากคุณรัน React: ส่วนใหญ่จะเป็น <code>http://localhost:3000</code></li>
  <li>ถ้าเป็น Flask: โดยทั่วไปจะรันที่ <code>http://127.0.0.1:5000</code></li>
  <li>หรือดูจากข้อความใน Terminal เช่น<br>
    <code>App listening on http://localhost:8000</code> = ใช้ <code>--port 8000</code>
  </li>
</ul>

<b>🔗 ตัวอย่าง URL ที่ได้:</b><br>
<code>https://myappdemo.loca.lt</code><br><br>

✅ ระบบรองรับเฉพาะ URL ที่ขึ้นต้นด้วย <code>https://xxx.loca.lt</code>
`,
  check_sql_injection: `
<h3>🧩 ตรวจสอบช่องโหว่ SQL Injection</h3>
<p>
  <strong>📝 ความหมาย:</strong> การโจมตีที่แฮกเกอร์ฝังคำสั่ง SQL เข้าไปในฟอร์มหรือ URL<br />
  เพื่อลวงให้เซิร์ฟเวอร์รันคำสั่งโดยไม่ตั้งใจ
</p>
<hr />
<p>
  <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
  • Basic Injection<br />
  • OR Condition<br />
  • UNION, DROP, Comment-based และ Blind SQLi<br />
  • ทดสอบ Error และ Response เพื่อวิเคราะห์การรั่วไหลของข้อมูล
</p>

`,
  check_xss: `
<h3>🧪 ตรวจสอบช่องโหว่ XSS</h3>
<p>
  <strong>📝 ความหมาย:</strong> ช่องโหว่ Cross-Site Scripting เกิดจากการที่เว็บไซต์ไม่กรองอินพุตของผู้ใช้อย่างเหมาะสม<br />
  ทำให้แฮกเกอร์สามารถฝังโค้ด JavaScript ลงไปในหน้าเว็บ ซึ่งจะรันในเบราว์เซอร์ของผู้ใช้รายอื่น
</p>
<hr />
<p>
  <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
  • การแสดงผลอินพุตกลับออกไปยังหน้า HTML โดยไม่มีการ escape<br />
  • ทดสอบผ่าน query, form, header, comment และช่อง bio/profile ต่าง ๆ
</p>

`,
  check_csrf: `
<h3>🔐 ตรวจสอบช่องโหว่ CSRF</h3>
<p>
  <strong>📝 ความหมาย:</strong> การโจมตีที่หลอกให้ผู้ใช้ที่ล็อกอินอยู่แล้วส่งคำขอโดยไม่ตั้งใจ<br />
  เช่น โอนเงิน เปลี่ยนรหัสผ่าน ผ่านลิงก์ที่ฝังมา
</p>
<hr />
<p>
  <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
  • ตรวจสอบการมี CSRF Token หรือไม่<br />
  • ทดสอบ Token ซ้ำได้หรือไม่<br />
  • ทดสอบ Token แบบ static และ rotation<br />
  • ทดสอบ cookie แบบ double-submit<br />
  • ตรวจสอบการหมดอายุ และ Session Fixation
</p>

`,
  check_idor: `
  <h4>🔍 ตรวจสอบช่องโหว่ IDOR</h4>
  <p><strong>Insecure Direct Object References</strong> คือช่องโหว่ที่ผู้ใช้สามารถเข้าถึงทรัพยากรโดยไม่ผ่านการตรวจสอบสิทธิ์ที่เหมาะสม</p>
  <hr />
  <p>🧪 <strong>สิ่งที่ระบบทดสอบ:</strong></p>
  <ul>
    <li>การเปลี่ยนค่า <code>ID</code> เช่น <code>user_id</code>, <code>file_id</code></li>
    <li>การเข้าถึงข้อมูลของผู้อื่นผ่าน URL</li>
    <li>ตรวจสอบการ <strong>ขาด Authorization</strong> ที่เหมาะสม</li>
  </ul>
  <p>❗ <strong>หากระบบไม่มีการตรวจสอบ</strong> อาจเกิดการเข้าถึง/แก้ไขข้อมูลของผู้อื่นได้</p>
`,
  check_bac: `
<h3>🚫 ตรวจสอบช่องโหว่ Broken Access Control</h3>
<p>
  <strong>📝 ความหมาย:</strong> ระบบควบคุมสิทธิ์ที่ล้มเหลว เช่น หน้า admin เปิดให้ user ทั่วไปเข้าถึงได้<br />
  หรือการ bypass การจำกัดสิทธิ์ เช่น ลบข้อมูลคนอื่น
</p>
<hr />
<p>
  <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
  • ทดสอบ URL ที่ควรจำกัดเฉพาะผู้ดูแล<br />
  • ทดสอบ API ที่ควรจำกัดการเข้าถึง<br />
  • ตรวจสอบว่า user ธรรมดาสามารถทำ action ของ admin ได้หรือไม่
</p>

`,
};
const Main = () => {
  const navigate = useNavigate();
  const blocklyDiv = useRef(null);
  const workspace = useRef(null);
  const [logoutMessage, setLogoutMessage] = useState("");
  const [username, setUsername] = useState("");
  const [blockDescription, setBlockDescription] = useState("");
  const [sidebarVisible, setSidebarVisible] = useState(false);

  useEffect(() => {
    const storedUsername = localStorage.getItem("username");
    if (storedUsername) setUsername(storedUsername);

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

    if (workspace.current) {
      workspace.current.dispose();
      workspace.current = null;
    }

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

    // ✅ ฟังค์ชันเมื่อเลือกบล็อก
        workspace.current.addChangeListener((event) => {
  if (event.type === Blockly.Events.SELECTED) {
    const block = workspace.current.getBlockById(event.newElementId);
    const sidebar = document.querySelector(".blockly-sidebar");

    if (block && sidebar) {
      const html = blockDescriptions[block.type] || "ℹ️ ไม่มีคำอธิบายสำหรับบล็อกนี้";
      setBlockDescription(html);
      sidebar.classList.add("visible");
    } else if (sidebar) {
      setBlockDescription("");
      sidebar.classList.remove("visible");
    }
  }
});


    Blockly.svgResize(workspace.current);
  }, [navigate]);

  const getTodayKey = () => {
    const today = new Date().toISOString().split("T")[0];
    const user = localStorage.getItem("username") || "anonymous";
    return `runTimestamps_${user}_${today}`;
  };

  const getRemainingTimeMessage = () => {
    const timestamps = JSON.parse(localStorage.getItem(getTodayKey()) || "[]");
    if (timestamps.length < 1000) return null;

    const now = new Date();
    const tomorrowMidnight = new Date();
    tomorrowMidnight.setHours(24, 0, 0, 0);
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
    const setUrlBlock = allBlocks.find(b => b.type === "set_url");
    const urlValue = setUrlBlock?.getFieldValue("URL") || "";
    if (!/^https:\/\/.*\.loca\.lt/.test(urlValue))  {
      alert("❌ Only loca.lt URLs are allowed. Please enter a valid https://xxx.loca.lt URL.");
      return;
    }

    if (resultKeysToCheck.length === 0) {
      alert("⚠️ Please add at least one security check before generating code.");
      return;
    }

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

  {/* ✅ Sidebar แบบพับได้ */}
  <div className={`blockly-sidebar ${sidebarVisible ? "visible" : ""}`}>
    <h3>🧾 Block Description</h3>
    <div dangerouslySetInnerHTML={{ __html: blockDescription }} />
  </div>
</div>

</div>
  );
};

export default Main;
