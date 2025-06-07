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

--ALTER TABLE users ADD COLUMN avatar TEXT DEFAULT '🙂';


-- Challenge templates table (list of possible challenges)
--CREATE TABLE IF NOT EXISTS challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    xp_reward INTEGER NOT NULL
--);

-- User's daily challenges (links users to challenges for a specific day)
--CREATE TABLE IF NOT EXISTS user_daily_challenges (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    challenge_id INTEGER NOT NULL,
    date TEXT NOT NULL,  -- e.g., '2025-06-03'
    progress INTEGER DEFAULT 0,
    completed INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (challenge_id) REFERENCES challenges(id)
--);

--INSERT INTO challenges (description, xp_reward) VALUES
--('Study for 30 minutes', 50),
--('Complete 2 study sessions', 40),
--('Log in today', 20);

--INSERT INTO challenges (description, xp_reward) VALUES
--('Study for 60 minutes', 50),
--('Complete 3 study sessions', 40),
--('Study for 15 minutes without pausing', 25),
--('Log a study session with a note', 20);


--CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    subject_name TEXT NOT NULL,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
--);

--ALTER TABLE study_sessions ADD COLUMN subject TEXT;

--CREATE TABLE IF NOT EXISTS password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    token TEXT NOT NULL,
    expires_at DATETIME NOT NULL
--);

--DROP TABLE IF EXISTS password_resets;

--CREATE TABLE password_resets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL,
    token TEXT NOT NULL,
    expiration DATETIME NOT NULL
--);