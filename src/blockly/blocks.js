import * as Blockly from "blockly";

// ✅ Block หลัก: ใส่ URL และสามารถเพิ่ม URL ได้หลายอัน
Blockly.Blocks["set_url"] = {
  init: function () {
    this.appendDummyInput()
      .appendField("Test Website URL:")
      .appendField(new Blockly.FieldTextInput(""), "URL"); // ✅ ให้ผู้ใช้กำหนดเอง
    this.appendStatementInput("MORE_URLS") // ✅ เพิ่มการรองรับ URL หลายอัน
      .setCheck("String")
      .appendField("Add More URLs");
    this.appendStatementInput("SECURITY_TESTS")
      .setCheck(null)
      .appendField("Run Security Tests");
    this.setColour(230);
    this.setTooltip("ตั้งค่าที่อยู่เว็บไซต์ (URL) แล้วดำเนินการทดสอบด้านความปลอดภัยหลายๆ อัน");
  },
};

// ✅ Block เพิ่ม URL เพิ่มเติม
Blockly.Blocks["add_url"] = {
  init: function () {
    this.appendDummyInput()
      .appendField("Add URL:")
      .appendField(new Blockly.FieldTextInput(""), "URL");
    this.setPreviousStatement(true, "String");
    this.setNextStatement(true, "String");
    this.setColour(160);
    this.setTooltip("เพิ่มที่อยู่เว็บไซต์ (URL) ที่ต้องการทดสอบ");
  },
};

// ✅ Block ตรวจสอบ SQL Injection
Blockly.Blocks["check_sql_injection"] = {
  init: function () {
    this.appendDummyInput().appendField("Check SQL Injection");
    this.setColour(0);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("SQL Injection การโจมตีที่แฮกเกอร์สอดแทรกคำสั่ง SQL ลงไปในช่องใส่ข้อมูลของเว็บแอปพลิเคชัน (เช่น ฟอร์มล็อกอิน, พารามิเตอร์ใน URL หรือฟิลด์ค้นหา) เพื่อให้เซิร์ฟเวอร์ฐานข้อมูลประมวลผลคำสั่งผิดปกติที่ผู้พัฒนามิได้ตั้งใจเขียนไว้");
  },
};

// ✅ Block ตรวจสอบ XSS
Blockly.Blocks["check_xss"] = {
  init: function () {
    this.appendDummyInput().appendField("Check XSS");
    this.setColour(120);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Cross-Site Scripting (XSS) ช่องโหว่บนเว็บแอปพลิเคชัน ที่เกิดขึ้นเมื่อแฮกเกอร์สามารถ “ฝัง” โค้ดฝั่งไคลเอนต์ (โดยปกติคือ JavaScript) ลงไปในหน้าที่ผู้ใช้คนอื่นจะเข้าชมได้ ทำให้เบราว์เซอร์ของผู้ใช้คนอื่นรันโค้ดนั้นโดยไม่รู้ตัว");
  },
};

// ✅ Block ตรวจสอบ CSRF
Blockly.Blocks["check_csrf"] = {
  init: function () {
    this.appendDummyInput().appendField("Check CSRF");
    this.setColour(180);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Cross-Site Request Forgery (CSRF) การโจมตีที่หวังใช้สิทธิ์ของผู้ใช้ที่กำลังล็อกอินในเว็บแอปพลิเคชันหนึ่ง ให้ส่งคำขอ (request) ที่ผู้ใช้ไม่ได้ตั้งใจทำ เช่น โอนเงิน เปลี่ยนรหัสผ่าน หรือสั่งซื้อสินค้า โดยแฮกเกอร์จะหลอกให้เบราว์เซอร์ของเหยื่อส่งคำขอนั้นไปยังเซิร์ฟเวอร์โดยอัตโนมัติ");
  },
};

// ✅ Block ตรวจสอบ IDOR
Blockly.Blocks["check_idor"] = {
  init: function () {
    this.appendDummyInput().appendField("Check IDOR");
    this.setColour(260);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Insecure Direct Object References เป็นช่องโหว่ด้านการควบคุมสิทธิ์ (Authorization) ที่เกิดขึ้นเมื่อแอปพลิเคชันอนุญาตให้ผู้ใช้เข้าถึง “วัตถุ” (Object) เช่น ไฟล์ ข้อมูลเรคอร์ด หรือทรัพยากรต่างๆ โดยใช้ตัวระบุ (ID) ตรงๆ ใน URL หรือพารามิเตอร์ โดยไม่ตรวจสอบว่าผู้ใช้คนนั้นมีสิทธิ์เข้าถึงวัตถุนั้นจริงหรือไม่");
  },
};

// ✅ Block ตรวจสอบ Broken Access Control
Blockly.Blocks["check_broken_access"] = {
  init: function () {
    this.appendDummyInput().appendField("Check Broken Access Control");
    this.setColour(300);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Broken Access Control เกิดขึ้นเมื่อเว็บแอปพลิเคชันหรือ API ไม่ได้ตรวจสอบสิทธิ์ผู้ใช้อย่างถูกต้องก่อนอนุญาตให้เข้าถึงฟังก์ชันหรือข้อมูล ทำให้ผู้ไม่หวังดีเข้าถึงหรือกระทำการที่ควรสงวนไว้เฉพาะผู้ใช้ระดับสูงกว่าได้");
  },
};
Blockly.Tooltip.DELAY = 250;