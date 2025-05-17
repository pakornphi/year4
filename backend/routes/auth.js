const express = require("express");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");
const pool = require("../db");
require("dotenv").config();

const router = express.Router();

// 🔹 API: Register
router.post("/register", async (req, res) => {
  try {
    const { username, email, password, confirmPassword } = req.body;

    if (!username.trim() || !email.trim() || !password.trim() || !confirmPassword.trim()) {
      setError("All fields are required");
      return;
    }

    if (password !== confirmPassword) {
      return res.status(400).json({ message: "Passwords do not match" });
    }

    // 🔹 ตรวจสอบว่า username ถูกใช้ไปแล้วหรือยัง
    const userExists = await pool.query("SELECT * FROM register WHERE username = $1", [username]);
    if (userExists.rows.length > 0) {
      return res.status(400).json({ message: "Username is already taken" });
    }

    // 🔹 ตรวจสอบว่า email ถูกใช้ไปแล้วหรือยัง
    const emailExists = await pool.query("SELECT * FROM register WHERE email = $1", [email]);
    if (emailExists.rows.length > 0) {
      return res.status(400).json({ message: "Email is already registered" });
    }

    // 🔹 เข้ารหัสรหัสผ่าน
    const salt = await bcrypt.genSalt(10);
    const hashedPassword = await bcrypt.hash(password, salt);

    // 🔹 เพิ่มข้อมูลลง Table `register`
    const newUser = await pool.query(
      "INSERT INTO register (username, email, password) VALUES ($1, $2, $3) RETURNING id, username, email",
      [username, email, hashedPassword]
    );

    // 🔹 สร้าง JWT Token
    const token = jwt.sign(
      { userId: newUser.rows[0].id, username: newUser.rows[0].username, email: newUser.rows[0].email },
      process.env.JWT_SECRET,
      { expiresIn: "10m" }
    );

    res.status(201).json({
      token,
      username: newUser.rows[0].username,
      email: newUser.rows[0].email,
    });

  } catch (error) {
    console.error("❌ ERROR:", error);
    res.status(500).json({ message: "Internal Server Error", error: error.message });
  }
});

// 🔹 API: Login (ใช้ `username` แทน `email`)
router.post("/login", async (req, res) => {
  try {
    const { username, password } = req.body;

    // 🔹 ค้นหาผู้ใช้จาก Table `register` โดยใช้ `username`
    const userResult = await pool.query("SELECT * FROM register WHERE username = $1", [username]);
    if (userResult.rows.length === 0) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    const user = userResult.rows[0];

    // 🔹 ตรวจสอบรหัสผ่าน
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    // 🔹 สร้าง JWT Token
    const token = jwt.sign(
      { userId: user.id, username: user.username, email: user.email },
      process.env.JWT_SECRET,
      { expiresIn: "10m" }
    );

    res.json({ token, username: user.username, email: user.email });

  } catch (error) {
    console.error("❌ ERROR:", error);
    res.status(500).json({ message: "Internal Server Error", error: error.message });
  }
});

// 🔹 Middleware: ตรวจสอบ JWT Token
const authenticateToken = (req, res, next) => {
  const token = req.header("Authorization");
  if (!token) return res.status(401).json({ message: "Access denied" });

  try {
    const verified = jwt.verify(token.replace("Bearer ", ""), process.env.JWT_SECRET);
    req.user = verified;
    next();
  } catch (error) {
    res.status(403).json({ message: "Invalid token" });
  }
};

// 🔹 API: Get Profile (ใช้ JWT Token)
router.get("/profile", authenticateToken, async (req, res) => {
  try {
    const { userId } = req.user;
    const userResult = await pool.query("SELECT id, username, email FROM register WHERE id = $1", [userId]);

    if (userResult.rows.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }

    res.json(userResult.rows[0]);

  } catch (error) {
    console.error("❌ ERROR:", error);
    res.status(500).json({ message: "Internal Server Error", error: error.message });
  }
});

module.exports = router;
