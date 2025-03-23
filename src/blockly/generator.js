import { javascriptGenerator } from "blockly/javascript";


// ✅ แปลง Block `set_url` เป็นตัวแปร URLs
javascriptGenerator.forBlock["set_url"] = function (block) {
  const mainUrl = `"${block.getFieldValue("URL")}"`;
  let extraUrls = javascriptGenerator.statementToCode(block, "MORE_URLS").trim();

  if (extraUrls) {
    extraUrls = extraUrls.split("\n").filter(url => url).join(", ");
  }

  const securityTests = javascriptGenerator.statementToCode(block, "SECURITY_TESTS");

  return `
  const urls = [${mainUrl}${extraUrls ? `, ${extraUrls}` : ""}];
  urls.forEach(url => {
    ${securityTests}
  });
  `;
};

// ✅ แปลง Block `add_url` เป็นตัวแปร URL
javascriptGenerator.forBlock["add_url"] = function (block) {
  const url = `"${block.getFieldValue("URL")}"`;
  return `${url},\n`;
};

// ✅ ทดสอบช่องโหว่ SQL Injection
javascriptGenerator.forBlock["check_sql_injection"] = function () {
  return `  check_sql_injection(url);\n`;
};

// ✅ ทดสอบช่องโหว่ XSS
javascriptGenerator.forBlock["check_xss"] = function () {
  return `  check_xss(url);\n`;
};

// ✅ ทดสอบช่องโหว่ CSRF (เรียก Flask API)
javascriptGenerator.forBlock["check_csrf"] = function () {
  return `
  urls.forEach(url => {
    fetch("http://localhost:5000/api/test-csrf", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    })
    .then(response => response.json())
    .then(data => {
      console.log("✅ CSRF Test Result for", url, ":", data.results);

      
      let results = JSON.parse(localStorage.getItem("testResults")) || [];
      
     
      const resultString = "🔍 " + url + " → " + data.results.join(" | ");
      if (!results.includes(resultString)) {
        results.push(resultString);
      }

      localStorage.setItem("testResults", JSON.stringify(results));
    })
    .catch(error => console.error("❌ Error:", error));
  });
  `;
};
// ✅ ทดสอบช่องโหว่ IDOR
javascriptGenerator.forBlock["check_idor"] = function () {
  return `  check_idor(url);\n`;
};

// ✅ ทดสอบช่องโหว่ Broken Access Control
javascriptGenerator.forBlock["check_broken_access"] = function () {
  return `  check_broken_access(url);\n`;
};
