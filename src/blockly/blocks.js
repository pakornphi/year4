import * as Blockly from "blockly";

// ✅ Block หลัก: ใส่ URL และสามารถเพิ่ม URL ได้หลายอัน
Blockly.Blocks["set_url"] = {
  init: function () {
    this.appendDummyInput()
      .appendField("Test Website URL:")
      .appendField(new Blockly.FieldTextInput(""), "URL"); // ✅ ให้ผู้ใช้กำหนดเอง
    // this.appendStatementInput("MORE_URLS") // ✅ เพิ่มการรองรับ URL หลายอัน
    //   .setCheck("String")
    //   .appendField("Add More URLs");
    this.appendStatementInput("SECURITY_TESTS")
      .setCheck(null)
      .appendField("Run Security Tests");
    this.setColour(230);
//         this.setTooltip(`
// <b>🌐 Test Website URL</b><br><br>
// ใช้สำหรับกำหนด URL ของเว็บไซต์ที่จะทดสอบ<br><br>

// <b>💡 คำแนะนำ:</b><br>
// คุณสามารถใช้ <code>localtunnel (lt)</code> เพื่อเปิดเว็บจากเครื่องของคุณ (localhost) ออกสู่อินเทอร์เน็ตได้<br><br>

// <b>📋 ขั้นตอนการใช้งาน:</b>
// <ol>
//   <li>เปิด Terminal หรือ Command Prompt</li>
//   <li>ติดตั้ง LocalTunnel (ครั้งเดียว):<br>
//     <code>npm install -g localtunnel</code>
//   </li>
//   <li>รันแอปของคุณ (เช่น React, Flask, Node.js) บนพอร์ตที่กำหนด เช่น <code>3000</code> หรือ <code>5000</code></li>
//   <li>เปิด tunnel ไปยังพอร์ตที่แอปรันอยู่ เช่น:<br>
//     <code>lt --port 3000</code><br>
//     หรือ <code>lt --port 5000</code>
//   </li>
//   <li>หากต้องการชื่อ URL ที่จำง่าย ให้เพิ่ม:<br>
//     <code>lt --port 3000 --subdomain myappdemo</code>
//   </li>
// </ol>

// <b>📌 วิธีดูว่าแอปรันอยู่ที่พอร์ตไหน:</b>
// <ul>
//   <li>หากคุณรัน React: ส่วนใหญ่จะเป็น <code>http://localhost:3000</code></li>
//   <li>ถ้าเป็น Flask: โดยทั่วไปจะรันที่ <code>http://127.0.0.1:5000</code></li>
//   <li>หรือดูจากข้อความใน Terminal เช่น<br>
//     <code>App listening on http://localhost:8000</code> = ใช้ <code>--port 8000</code>
//   </li>
// </ul>

// <b>🔗 ตัวอย่าง URL ที่ได้:</b><br>
// <code>https://myappdemo.loca.lt</code><br><br>

// ✅ ระบบรองรับเฉพาะ URL ที่ขึ้นต้นด้วย <code>https://xxx.loca.lt</code>
// `);
  },
};

// ✅ Block เพิ่ม URL เพิ่มเติม
// Blockly.Blocks["add_url"] = {
//   init: function () {
//     this.appendDummyInput()
//       .appendField("Add URL:")
//       .appendField(new Blockly.FieldTextInput(""), "URL");
//       this.setHidden(true);
//     this.setPreviousStatement(true, "String");
//     this.setNextStatement(true, "String");
//     this.setColour(160);
//     this.setTooltip("เพิ่มที่อยู่เว็บไซต์ (URL) ที่ต้องการทดสอบ");
    
//   },
// };

// ✅ Block ตรวจสอบ SQL Injection
Blockly.Blocks["check_sql_injection"] = {
  init: function () {
    this.appendDummyInput().appendField("Check SQL Injection");
    this.setColour(0);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
//     this.setTooltip(`
// <h3>🧩 ตรวจสอบช่องโหว่ SQL Injection</h3>
// <p>
//   <strong>📝 ความหมาย:</strong> การโจมตีที่แฮกเกอร์ฝังคำสั่ง SQL เข้าไปในฟอร์มหรือ URL<br />
//   เพื่อลวงให้เซิร์ฟเวอร์รันคำสั่งโดยไม่ตั้งใจ
// </p>
// <hr />
// <p>
//   <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
//   • Basic Injection<br />
//   • OR Condition<br />
//   • UNION, DROP, Comment-based และ Blind SQLi<br />
//   • ทดสอบ Error และ Response เพื่อวิเคราะห์การรั่วไหลของข้อมูล
// </p>

// `);
  },
};

// ✅ Block ตรวจสอบ XSS
Blockly.Blocks["check_xss"] = {
  init: function () {
    this.appendDummyInput().appendField("Check XSS");
    this.setColour(120);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
//     this.setTooltip(`
// <h3>🧪 ตรวจสอบช่องโหว่ XSS</h3>
// <p>
//   <strong>📝 ความหมาย:</strong> ช่องโหว่ Cross-Site Scripting เกิดจากการที่เว็บไซต์ไม่กรองอินพุตของผู้ใช้อย่างเหมาะสม<br />
//   ทำให้แฮกเกอร์สามารถฝังโค้ด JavaScript ลงไปในหน้าเว็บ ซึ่งจะรันในเบราว์เซอร์ของผู้ใช้รายอื่น
// </p>
// <hr />
// <p>
//   <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
//   • การแสดงผลอินพุตกลับออกไปยังหน้า HTML โดยไม่มีการ escape<br />
//   • ทดสอบผ่าน query, form, header, comment และช่อง bio/profile ต่าง ๆ
// </p>

// `);
  },
};

// ✅ Block ตรวจสอบ CSRF
Blockly.Blocks["check_csrf"] = {
  init: function () {
    this.appendDummyInput().appendField("Check CSRF");
    this.setColour(180);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
//     this.setTooltip(`
// <h3>🔐 ตรวจสอบช่องโหว่ CSRF</h3>
// <p>
//   <strong>📝 ความหมาย:</strong> การโจมตีที่หลอกให้ผู้ใช้ที่ล็อกอินอยู่แล้วส่งคำขอโดยไม่ตั้งใจ<br />
//   เช่น โอนเงิน เปลี่ยนรหัสผ่าน ผ่านลิงก์ที่ฝังมา
// </p>
// <hr />
// <p>
//   <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
//   • ตรวจสอบการมี CSRF Token หรือไม่<br />
//   • ทดสอบ Token ซ้ำได้หรือไม่<br />
//   • ทดสอบ Token แบบ static และ rotation<br />
//   • ทดสอบ cookie แบบ double-submit<br />
//   • ตรวจสอบการหมดอายุ และ Session Fixation
// </p>

// `);
  },
};

// ✅ Block ตรวจสอบ IDOR
Blockly.Blocks["check_idor"] = {
  init: function () {
    this.appendDummyInput().appendField("Check IDOR");
    this.setColour(260);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
//     this.setTooltip(`
//   <h4>🔍 ตรวจสอบช่องโหว่ IDOR</h4>
//   <p><strong>Insecure Direct Object References</strong> คือช่องโหว่ที่ผู้ใช้สามารถเข้าถึงทรัพยากรโดยไม่ผ่านการตรวจสอบสิทธิ์ที่เหมาะสม</p>
//   <hr />
//   <p>🧪 <strong>สิ่งที่ระบบทดสอบ:</strong></p>
//   <ul>
//     <li>การเปลี่ยนค่า <code>ID</code> เช่น <code>user_id</code>, <code>file_id</code></li>
//     <li>การเข้าถึงข้อมูลของผู้อื่นผ่าน URL</li>
//     <li>ตรวจสอบการ <strong>ขาด Authorization</strong> ที่เหมาะสม</li>
//   </ul>
//   <p>❗ <strong>หากระบบไม่มีการตรวจสอบ</strong> อาจเกิดการเข้าถึง/แก้ไขข้อมูลของผู้อื่นได้</p>
// `
// );
  },
};

// ✅ Block ตรวจสอบ Broken Access Control
Blockly.Blocks["check_bac"] = {
  init: function () {
    this.appendDummyInput().appendField("Check Broken Access Control");
    this.setColour(300);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
//     this.setTooltip(`
// <h3>🚫 ตรวจสอบช่องโหว่ Broken Access Control</h3>
// <p>
//   <strong>📝 ความหมาย:</strong> ระบบควบคุมสิทธิ์ที่ล้มเหลว เช่น หน้า admin เปิดให้ user ทั่วไปเข้าถึงได้<br />
//   หรือการ bypass การจำกัดสิทธิ์ เช่น ลบข้อมูลคนอื่น
// </p>
// <hr />
// <p>
//   <strong>🔍 สิ่งที่ทดสอบ:</strong><br />
//   • ทดสอบ URL ที่ควรจำกัดเฉพาะผู้ดูแล<br />
//   • ทดสอบ API ที่ควรจำกัดการเข้าถึง<br />
//   • ตรวจสอบว่า user ธรรมดาสามารถทำ action ของ admin ได้หรือไม่
// </p>

// `);
  },
};
Blockly.Tooltip.DELAY = 250;