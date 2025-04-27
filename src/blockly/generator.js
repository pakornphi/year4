import { javascriptGenerator } from "blockly/javascript";

// ✅ แปลง Block `set_url` เป็นตัวแปร URLs
javascriptGenerator.forBlock["set_url"] = function (block) {
  const mainUrl = `"${block.getFieldValue("URL")}"`;
  let extraUrls = javascriptGenerator.statementToCode(block, "MORE_URLS").trim();

  if (extraUrls) {
    extraUrls = extraUrls.split("\n").filter(url => url && url.includes(".loca.lt")).join(", ");
  }

  const securityTests = javascriptGenerator.statementToCode(block, "SECURITY_TESTS");

  return `
  const urls = [${mainUrl}${extraUrls ? `, ${extraUrls}` : ""}];
  // Filter URLs to only include those containing ".loca.lt"
  const filteredUrls = urls.filter(url => url.includes(".loca.lt"));

  filteredUrls.forEach(url => {
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
  const url = block.getFieldValue("URL");  // Get the URL field from the block
  
  return `
    fetch('http://localhost:5000/api/test-sql', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })  // Send the URL to the backend
    })
    .then(response => response.json())
    .then(data => {
      // Check if SQL injection vulnerability is detected
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
    fetch('http://localhost:5000/api/test-xss', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
      if (data.results) {
        console.log("XSS Test Result:", data);
      } else {
        console.log("No XSS vulnerabilities found.");
      }
    })
    .catch(error => {
      console.error('Error while testing for XSS:', error);
    });
  `;
};

// ✅ ทดสอบช่องโหว่ CSRF
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

      let results = JSON.parse(localStorage.getItem("testResults")) || [];
      const resultString = "🔍 " + url + " → " + JSON.stringify(data);
      if (!results.includes(resultString)) {
        results.push(resultString);
      }

      localStorage.setItem("testResults", JSON.stringify(results));

      // Display results on the page
      const resultContainer = document.getElementById("test-results");
      const resultItem = document.createElement("div");
      resultItem.className = "test-result-item";
      resultItem.innerHTML = "<strong>" + url + "</strong><br>" + JSON.stringify(data);
      resultContainer.appendChild(resultItem);
    })
    .catch(error => {
      console.error('Error during CSRF test:', error);
    });
  });
  `;
};

// ✅ ทดสอบช่องโหว่ IDOR
javascriptGenerator.forBlock["check_idor"] = function () {
  return `
    fetch('http://localhost:5000/api/test-idor', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
      console.log("IDOR Test Result:", data);
    })
    .catch(error => {
      console.error('Error while testing for IDOR:', error);
    });
  `;
};

// ✅ ทดสอบช่องโหว่ Broken Access Control
javascriptGenerator.forBlock["check_broken_access"] = function () {
  return `
    fetch('http://localhost:5000/api/test-broken-access-control', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ url: url })
    })
    .then(response => response.json())
    .then(data => {
      console.log("Broken Access Control Test Result:", data);
    })
    .catch(error => {
      console.error('Error while testing for Broken Access Control:', error);
    });
  `;
};
