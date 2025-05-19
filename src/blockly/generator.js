
import { javascriptGenerator } from "blockly/javascript";

// ✅ set_url
javascriptGenerator.forBlock["set_url"] = function (block) {
  const mainUrl = `"${block.getFieldValue("URL")}"`;

  const securityTests = javascriptGenerator.statementToCode(block, "SECURITY_TESTS");

  return `
    const urls = [${mainUrl}];

    urls.forEach(url => {
      ${securityTests}
    });
  `;
};

// ✅ add_url
// javascriptGenerator.forBlock["add_url"] = function (block) {
//   const url = `"${block.getFieldValue("URL")}"`;
//   return `${url},\n`;
// };

// ✅ SQL Injection
javascriptGenerator.forBlock["check_sql_injection"] = function () {
  return `
    fetch("https://vast-sound-sunbird.ngrok-free.app/api/test-sql", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    })
    .then(response => response.json())
    .then(data => {
      const result = {
        tested_url: data.tested_url,
        results: data.results || []
      };

      let allResults = JSON.parse(localStorage.getItem("sqlResults") || "[]");
      allResults.push(result);
      localStorage.setItem("sqlResults", JSON.stringify(allResults));
      console.log("✅ Saved SQL Injection results for", url);
    })
    .catch(error => {
      console.error("❌ Failed to test SQL injection:", error);
    });
  `;
};


// ✅ XSS
javascriptGenerator.forBlock["check_xss"] = function () {
  return `
    fetch("https://vast-sound-sunbird.ngrok-free.app/api/test-xss", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    })
    .then(response => response.json())
    .then(data => {
      const entry = {
        tested_url: data.tested_url,
        xss_vulnerable: false,
        messages: data.results || []
      };

      // ดึงค่า test_xxx ออกมาเก็บใน entry ให้ Dashboard อ่านได้
      (data.results || []).forEach((line) => {
        const match = line.match(/^\\s*(.+?)\\s+→ vulnerability:(True|False|None)/);
        if (match) {
          const label = match[1].trim().toLowerCase().replace(/\\s+/g, "_"); // เช่น: "form_input_xss"
          const key = "test_" + label;
          const vuln = match[2] === "True" ? true : match[2] === "False" ? false : null;

          entry[key] = {
            vulnerability: vuln,
            info: null
          };

          if (vuln === true) {
            entry.xss_vulnerable = true;
          }
        }
      });

      let allResults = JSON.parse(localStorage.getItem("xssResults") || "[]");
      const index = allResults.findIndex(r => r.tested_url === entry.tested_url);
      if (index !== -1) {
        allResults[index] = { ...allResults[index], ...entry };
      } else {
        allResults.push(entry);
      }

      localStorage.setItem("xssResults", JSON.stringify(allResults));
      console.log("✅ Saved XSS results for", url);
    })
    .catch(error => {
      console.error("❌ Failed to test XSS:", error);
    });
  `;
};




// ✅ CSRF
javascriptGenerator.forBlock["check_csrf"] = function () {
  return `
    urls.forEach(url => {
      fetch("https://vast-sound-sunbird.ngrok-free.app/api/test-csrf", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      })
      .then(response => response.json())
      .then(data => {
        const result = {
          tested_url: data.tested_url,
          results: data.results || []
        };

        let results = JSON.parse(localStorage.getItem("csrfResults") || "[]");
        results.push(result);
        localStorage.setItem("csrfResults", JSON.stringify(results));
        console.log("✅ Saved formatted CSRF result for", url);
      })
      .catch(error => {
        console.error("❌ Failed to test CSRF:", error);
      });
    });
  `;
};

// ✅ IDOR
javascriptGenerator.forBlock["check_idor"] = function () {
  return `
    fetch("https://vast-sound-sunbird.ngrok-free.app/api/test-idor", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    })
    .then(response => response.json())
    .then(data => {
      const messages = data.messages || [];
      const isVulnerable = data.idor_vulnerable;

      const newEntry = {
        url: url,
        tested_url: data.tested_url || url,
        idor_vulnerable: isVulnerable,
        messages
      };

      let allResults = JSON.parse(localStorage.getItem("idorResults") || "[]");
      const index = allResults.findIndex(r => r.tested_url === newEntry.tested_url);
      if (index !== -1) {
        allResults[index] = { ...allResults[index], ...newEntry };
      } else {
        allResults.push(newEntry);
      }

      localStorage.setItem("idorResults", JSON.stringify(allResults));
      console.log("✅ Saved IDOR results for", url);
    })
    .catch(error => {
      console.error("❌ Failed to test IDOR:", error);
    });
  `;
};

// ✅ BAC
javascriptGenerator.forBlock["check_bac"] = function () {
  return `
    fetch("https://vast-sound-sunbird.ngrok-free.app/api/test-broken-access-control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    })
    .then(response => response.json())
    .then(data => {
      const entry = {
        url: data.tested_url,
        tested_url: data.tested_url,
        bac_vulnerable: data.report.some(line => line.includes("vulnerability:True")),
        messages: data.report || []
      };

      let allResults = JSON.parse(localStorage.getItem("bacResults") || "[]");
      const index = allResults.findIndex(r => r.tested_url === data.tested_url);
      if (index !== -1) {
        allResults[index] = { ...allResults[index], ...entry };
      } else {
        allResults.push(entry);
      }

      localStorage.setItem("bacResults", JSON.stringify(allResults));
      console.log("✅ Saved BAC results for", data.tested_url);
    })
    .catch(error => {
      console.error("❌ Failed to test BAC:", error);
    });
  `;
};


