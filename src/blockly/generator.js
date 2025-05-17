
import { javascriptGenerator } from "blockly/javascript";

// ✅ set_url
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

// ✅ add_url
javascriptGenerator.forBlock["add_url"] = function (block) {
  const url = `"${block.getFieldValue("URL")}"`;
  return `${url},\n`;
};

// ✅ SQL Injection
javascriptGenerator.forBlock["check_sql_injection"] = function () {
  return `
    fetch("http://localhost:5000/api/test-sql", {
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
  fetch("http://localhost:5000/api/test-xss", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  })
  .then(response => response.json())
  .then(data => {
    const results = data?.results || {};
    const entry = { tested_url: url };

    Object.entries(results).forEach(([key, value]) => {
      if (key === "vulnerability") return;
      entry[\`test_\${key}\`] = {
        info: value.payloads?.[0] || null,
        vulnerability: value.count > 0
      };
    });

    entry["xss_vulnerable"] = results.vulnerability ?? null;

    let allResults = JSON.parse(localStorage.getItem("xssResults") || "[]");
    const index = allResults.findIndex(r => r.tested_url === url);
    if (index !== -1) {
      allResults[index] = { ...allResults[index], ...entry };
    } else {
      allResults.push(entry);
    }

    localStorage.setItem("xssResults", JSON.stringify(allResults));
    console.log("✅ Saved structured XSS results for", url);
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
      fetch("http://localhost:5000/api/test-csrf", {
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
    fetch("http://localhost:5000/api/test-idor", {
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
    fetch("http://localhost:5000/api/test-broken-access-control", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url })
    })
    .then(response => response.json())
    .then(data => {
      const result = {
        tested_url: data.tested_url,
        results: data.results || []  // ✅ ต้องเป็น array of strings
      };

      let allResults = JSON.parse(localStorage.getItem("bacResults") || "[]");
      allResults.push(result);
      localStorage.setItem("bacResults", JSON.stringify(allResults));
      console.log("✅ Saved BAC results for", url);
    })
    .catch(error => {
      console.error("❌ Failed to test BAC:", error);
    });
  `;
};

