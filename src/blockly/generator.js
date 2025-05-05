import { javascriptGenerator } from "blockly/javascript";


// ✅ แปลง Block `set_url` เป็นตัวแปร URLs
javascriptGenerator.forBlock["set_url"] = function (block) {
  const mainUrl = `"${block.getFieldValue("URL")}"`;
  let extraUrls = javascriptGenerator.statementToCode(block, "MORE_URLS").trim();

  if (extraUrls) {
    extraUrls = extraUrls
      .split("\n")
      .filter(line => line.trim() !== "")
      .join(", ");
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
javascriptGenerator.forBlock["check_sql_injection"] = function (block) {
  const url = block.getFieldValue("URL"); // Assuming the URL is a field in the block
  
  return `
    fetch('http://localhost:5000/api/test-sql', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: "${url}" })
    })
    .then(response => response.json())
    .then(data => {
      if (data.vulnerable) {
        console.log('SQL Injection Vulnerability detected with payload:', data.payload);
      } else {
        console.log('No SQL Injection vulnerabilities found.');
      }
    })
    .catch(error => {
      console.error('Error while testing for SQL injection:', error);
    });
  `;
};


// ✅ ทดสอบช่องโหว่ XSS
javascriptGenerator.forBlock["check_xss"] = function () {
  return `
  fetch("http://localhost:5000/api/test-xss", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  })
  .then(response => response.json())
  .then(data => {
    const isVulnerable = data?.results?.vulnerability === true;
    console.log("✅ XSS Test Result for", url, ":", isVulnerable);

    let results = JSON.parse(localStorage.getItem("testResults")) || [];
    const existingIndex = results.findIndex(r => r.url === url);
    const newEntry = {
      url: url,
      xss_vulnerable: isVulnerable
    };

    if (existingIndex !== -1) {
      results[existingIndex] = { ...results[existingIndex], ...newEntry };
    } else {
      results.push(newEntry);
    }

    localStorage.setItem("testResults", JSON.stringify(results));
  })
  .catch(error => {
    console.error("❌ Failed to test XSS:", error);
  });
  `;
};

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
      console.log("✅ CSRF Test Result for", url, ":", data);

      // 🧠 สร้างผลลัพธ์แบบเต็มให้ Dashboard อ่านได้
      const result = { tested_url: url };
      Object.entries(data).forEach(([key, value]) => {
        if (key.startsWith("test_")) {
          result[key] = value;
        }
      });

      let results = JSON.parse(localStorage.getItem("testResults")) || [];

      // ถ้า URL นี้ยังไม่ถูกเพิ่ม ให้เพิ่มใหม่
      if (!results.some(entry => entry.tested_url === url)) {
        results.push(result);
        localStorage.setItem("testResults", JSON.stringify(results));
      }
    })
    .catch(error => {
      console.error("❌ Failed to test CSRF:", error);
    });
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
