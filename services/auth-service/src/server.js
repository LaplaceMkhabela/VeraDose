const express = require('express');
const path = require('path');
const Database = require('better-sqlite3');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const { v4: uuidv4 } = require('uuid');
require('dotenv').config();

const app = express();

// Middleware
app.use(express.json());
// Assuming your HTML files are in a folder named 'public'
app.use(express.static(path.join(__dirname, 'public')));

const db = new Database('database.db');
const JWT_SECRET = process.env.JWT_SECRET || 'super-secret-key';

// --- Database Schema ---
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT,
    is_verified BOOLEAN DEFAULT 0,
    role TEXT DEFAULT 'user',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );
`);

// --- Page Routes (Serving your HTML) ---

app.get('/register', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'register.html'));
});

app.get('/login', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'login.html'));
});

app.get('/verify', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'verify.html'));
});

// --- API Endpoints ---

// Register Logic
app.post('/api/v1/auth/register', async (req, res) => {
  const { email, password } = req.body;
  if (!email || !password) return res.status(400).json({ error: 'Missing fields' });

  try {
    const password_hash = await bcrypt.hash(password, 10);
    const id = uuidv4();
    db.prepare('INSERT INTO users (id, email, password_hash) VALUES (?, ?, ?)').run(id, email, password_hash);
    res.status(201).json({ message: 'User registered' });
  } catch (err) {
    res.status(409).json({ error: 'Email already exists' });
  }
});

// Login Logic
app.post('/api/v1/auth/login', async (req, res) => {
  const { email, password } = req.body;
  const user = db.prepare('SELECT * FROM users WHERE email = ?').get(email);

  if (user && await bcrypt.compare(password, user.password_hash)) {
    const token = jwt.sign({ id: user.id, role: user.role }, JWT_SECRET, { expiresIn: '1h' });
    return res.json({ token, redirect: '/dashboard' }); // You can tell the client where to go
  }
  res.status(401).json({ error: 'Invalid credentials' });
});

// Verify Logic
app.get('/api/v1/auth/verify', (req, res) => {
  const { email, otp } = req.query;
  // Simulation: OTP '1234' is always valid
  if (otp === '1234') {
    db.prepare('UPDATE users SET is_verified = 1 WHERE email = ?').run(email);
    return res.json({ message: 'Verified!' });
  }
  res.status(400).json({ error: 'Invalid OTP' });
});

// Start
app.listen(8080, () => console.log('Server running on http://localhost:8080'));