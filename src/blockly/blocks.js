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
    this.setTooltip("Set multiple URLs and run security tests.");
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
    this.setTooltip("Add another URL to test.");
  },
};

// ✅ Block ตรวจสอบ SQL Injection
Blockly.Blocks["check_sql_injection"] = {
  init: function () {
    this.appendDummyInput().appendField("Check SQL Injection");
    this.setColour(0);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Check for SQL Injection vulnerabilities.");
  },
};

// ✅ Block ตรวจสอบ XSS
Blockly.Blocks["check_xss"] = {
  init: function () {
    this.appendDummyInput().appendField("Check XSS");
    this.setColour(120);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Check for Cross-Site Scripting (XSS) vulnerabilities.");
  },
};

// ✅ Block ตรวจสอบ CSRF
Blockly.Blocks["check_csrf"] = {
  init: function () {
    this.appendDummyInput().appendField("Check CSRF");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(180);
    this.setTooltip("Check for Cross-Site Request Forgery (CSRF) vulnerabilities.");
  },
};

// ✅ Block ตรวจสอบ IDOR
Blockly.Blocks["check_idor"] = {
  init: function () {
    this.appendDummyInput().appendField("Check IDOR");
    this.setColour(260);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Check for Insecure Direct Object References (IDOR) vulnerabilities.");
  },
};

// ✅ Block ตรวจสอบ Broken Access Control
Blockly.Blocks["check_broken_access"] = {
  init: function () {
    this.appendDummyInput().appendField("Check Broken Access Control");
    this.setColour(300);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setTooltip("Check for Broken Access Control vulnerabilities.");
  },
};
