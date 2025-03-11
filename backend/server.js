const express = require("express");
const cors = require("cors");
require("dotenv").config();

const app = express();

// Middleware
app.use(cors());
app.use(express.json());

// เชื่อม API Authentication
app.use("/api/auth", require("./routes/auth"));

// ตรวจสอบว่าเซิร์ฟเวอร์ทำงานปกติ
app.get("/", (req, res) => {
  res.send("🚀 Backend is running...");
});

// กำหนดพอร์ต
const PORT = process.env.PORT || 8000;
app.listen(PORT, () => console.log(`✅ Server running on port ${PORT}`));
