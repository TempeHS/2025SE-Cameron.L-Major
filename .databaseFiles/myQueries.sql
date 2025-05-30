-- database: database.db

--CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    totp_secret TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
--);

--CREATE TABLE achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    date_earned DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
--);


--ALTER TABLE users ADD COLUMN is_verified INTEGER DEFAULT 0;

--CREATE TABLE logins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    login_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
--);

--ALTER TABLE users ADD COLUMN total_study_time INTEGER;

--UPDATE users SET total_study_time = 0 WHERE total_study_time IS NULL;

--ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0;

--CREATE TABLE IF NOT EXISTS achievements (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    achievement_name TEXT NOT NULL,
    unlocked_at DATETIME DEFAULT CURRENT_TIMESTAMP
--);

--CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    date TEXT NOT NULL,  -- e.g., '2025-05-30'
    seconds INTEGER NOT NULL
--);