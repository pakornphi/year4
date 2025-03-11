import { javascriptGenerator } from "blockly/javascript";

// ✅ Generator: `set_url` รองรับหลาย URL
javascriptGenerator.forBlock["set_url"] = function (block) {
  const urls = [`"${block.getFieldValue("URL")}"`];
  let extraUrls = javascriptGenerator.statementToCode(block, "MORE_URLS").trim();
  if (extraUrls) {
    urls.push(extraUrls);
  }
  const securityTests = javascriptGenerator.statementToCode(block, "SECURITY_TESTS");
  return `const urls = [${urls.join(", ")}];\nurls.forEach(url => {\n${securityTests}});\n`;
};

// ✅ Generator: `add_url`
javascriptGenerator.forBlock["add_url"] = function (block) {
  const url = block.getFieldValue("URL");
  return `"${url}",\n`;
};

// ✅ Generator: ทดสอบช่องโหว่ทั้งหมด
const securityChecks = [
  "check_sql_injection",
  "check_xss",
  "check_csrf",
  "check_idor",
  "check_broken_access"
];

securityChecks.forEach((type) => {
  javascriptGenerator.forBlock[type] = function () {
    return `  ${type}(url);\n`;
  };
});
