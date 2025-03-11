import * as Blockly from "blockly";

// ✅ Block หลัก: สามารถใส่หลาย URL ได้
Blockly.Blocks["set_url"] = {
  init: function () {
    this.appendDummyInput()
      .appendField("Test Website URL:")
      .appendField(new Blockly.FieldTextInput("http://example.com"), "URL");
    this.appendStatementInput("MORE_URLS")
      .setCheck("String")
      .appendField("Add More URLs");
    this.appendStatementInput("SECURITY_TESTS")
      .setCheck(null)
      .appendField("Run Security Tests");
    this.setColour(230);
    this.setTooltip("Set one or more URLs and run security tests.");
  },
};

// ✅ Block เพิ่ม URL ใหม่
Blockly.Blocks["add_url"] = {
  init: function () {
    this.appendDummyInput()
      .appendField("Add URL:")
      .appendField(new Blockly.FieldTextInput("http://example2.com"), "URL");
    this.setPreviousStatement(true, "String");
    this.setNextStatement(true, "String");
    this.setColour(160);
    this.setTooltip("Add another URL to test.");
  },
};

// ✅ Block ทดสอบช่องโหว่
const securityChecks = [
  { type: "check_sql_injection", name: "SQL Injection", color: 0 },
  { type: "check_xss", name: "XSS", color: 120 },
  { type: "check_csrf", name: "CSRF", color: 180 },
  { type: "check_idor", name: "IDOR", color: 260 },
  { type: "check_broken_access", name: "Broken Access Control", color: 300 }
];

securityChecks.forEach(({ type, name, color }) => {
  Blockly.Blocks[type] = {
    init: function () {
      this.appendDummyInput().appendField(`Check ${name}`);
      this.setColour(color);
      this.setPreviousStatement(true, null);
      this.setNextStatement(true, null);
      this.setTooltip(`Check for ${name} vulnerabilities.`);
    },
  };
});
