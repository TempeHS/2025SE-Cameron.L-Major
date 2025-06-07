"""
This module provides database interaction functions for the GameStudy application.
"""

import sqlite3
from datetime import datetime

class DatabaseError(Exception):
    """Custom exception for database errors."""

def execute_query(query, params=None):
    """Execute a query and return the results."""
    try:
        conn = sqlite3.connect('.databaseFiles/database.db')
        cursor = conn.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        results = cursor.fetchall()
        conn.commit()
        return results
    except sqlite3.Error as e:
        raise DatabaseError(f"Database error: {e}") from e
    finally:
        if conn:
            cursor.close()
            conn.close()

def get_user(username):
    """Fetch a user by username, including XP, level, total study hours, progress to next level, and avatar."""
    conn = sqlite3.connect('.databaseFiles/database.db')
    conn.row_factory = sqlite3.Row  # Enable name-based access
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user:
        # Use column names for clarity
        total_study_time = user["total_study_time"] if "total_study_time" in user.keys() and user["total_study_time"] is not None else 0
        xp = user["xp"] if "xp" in user.keys() and user["xp"] is not None else 0
        level = user["level"] if "level" in user.keys() and user["level"] is not None else None
        avatar = user["avatar"] if "avatar" in user.keys() and user["avatar"] else "🙂"

        total_study_hours = round(total_study_time / 3600, 1)

        # Calculate level from XP if not stored
        if level is None:
            level = max(1, (xp // 100) + 1)
        else:
            level = max(1, int(level))

        xp_for_this_level = (level - 1) * 100
        xp_for_next_level = level * 100
        if xp_for_next_level > xp_for_this_level:
            progress = int(100 * (xp - xp_for_this_level) / (xp_for_next_level - xp_for_this_level))
        else:
            progress = 0
        progress = max(0, min(progress, 100))

        return {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "password": user["password"],
            "totp_secret": user["totp_secret"],
            "is_verified": user["is_verified"],
            "total_study_hours": total_study_hours,
            "xp": xp,
            "level": level,
            "progress_to_next_level": progress,
            "avatar": avatar
        }
    return None

def get_user_by_email(email):
    """Fetch a user by email."""
    conn = sqlite3.connect('.databaseFiles/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        return {"id": user[0], "username": user[1], "email": user[2], "password": user[3], "totp_secret": user[4], "is_verified": user[5]}
    return None

def add_user(username, email, password, totp_secret, avatar="🙂"):
    conn = sqlite3.connect('.databaseFiles/database.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password, totp_secret, is_verified, avatar) VALUES (?, ?, ?, ?, ?, ?)",
        (username, email, password, totp_secret, False, avatar)
    )
    conn.commit()
    conn.close()

def set_totp_secret(username, secret):
    """Set the TOTP secret for a user."""
    try:
        conn = sqlite3.connect('.databaseFiles/database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET totp_secret = ? WHERE username = ?", (secret, username))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Database error: {e}") from e

def store_reset_token(email, token, expiration):
    """Store a password reset token."""
    try:
        conn = sqlite3.connect('.databaseFiles/database.db')
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO password_resets (email, token, expiration) VALUES (?, ?, ?)",
            (email, token, expiration)
        )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Database error: {e}") from e

def get_reset_token(token):
    """Fetch a password reset token."""
    conn = sqlite3.connect('.databaseFiles/database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT email, expiration FROM password_resets WHERE token = ?", (token,))
    reset = cursor.fetchone()
    conn.close()
    if reset:
        return {"email": reset[0], "expiration": reset[1]}
    return None

def update_password(email, new_password):
    """Update a user's password."""
    try:
        conn = sqlite3.connect('.databaseFiles/database.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Database error: {e}") from e

def update_user_profile(current_username, new_email, new_username, new_password, new_avatar):
    """Update a user's profile, including avatar."""
    try:
        conn = sqlite3.connect('.databaseFiles/database.db')
        cursor = conn.cursor()
        if new_password:
            cursor.execute(
                "UPDATE users SET email = ?, username = ?, password = ?, avatar = ? WHERE username = ?",
                (new_email, new_username, new_password, new_avatar, current_username)
            )
        else:
            cursor.execute(
                "UPDATE users SET email = ?, username = ?, avatar = ? WHERE username = ?",
                (new_email, new_username, new_avatar, current_username)
            )
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise DatabaseError(f"Database error: {e}") from e

