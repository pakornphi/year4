const express = require('express');
const router = express.Router();
const bcrypt = require('bcrypt');
const pool = require('../db'); // เชื่อมกับ database

router.post('/', async (req, res) => {
  const { username, password } = req.body;

  if (!username || !password) {
    return res.status(400).json({ error: 'Username and password are required.' });
  }

  try {
    const userQuery = 'SELECT * FROM users WHERE username = $1';
    const { rows } = await pool.query(userQuery, [username]);

    if (rows.length === 0) {
      return res.status(401).json({ error: 'Username not found.' });
    }

    const user = rows[0];
    const isMatch = await bcrypt.compare(password, user.password);

    if (!isMatch) {
      return res.status(401).json({ error: 'Invalid password.' });
    }

    res.json({ message: 'Login successful' });
    
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Server error' });
  }
});

module.exports = router;
