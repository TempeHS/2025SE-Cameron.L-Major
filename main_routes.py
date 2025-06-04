from flask import render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta, date
import userManagement as dbHandler
import bcrypt
from utils import validate_password, basic_sanitize_input
from flask_wtf.csrf import validate_csrf, generate_csrf
import sqlite3
import os
import random

def register_main_routes(app):
    def get_db():
        db_path = '.databaseFiles/database.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_user_subjects(username):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT subject_name FROM subjects WHERE username=?", (username,))
        subjects = [row["subject_name"] for row in cur.fetchall()]
        conn.close()
        return subjects

    @app.route("/add_subject", methods=["POST"])
    def add_subject():
        if 'username' not in session:
            return redirect(url_for('login'))
        try:
            validate_csrf(request.form['csrf_token'])
        except Exception:
            flash("CSRF token is missing or invalid.")
            return redirect(url_for('study_timer'))
        subject_name = request.form["subject_name"].strip()
        if subject_name:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("INSERT INTO subjects (username, subject_name) VALUES (?, ?)", (session['username'], subject_name))
            conn.commit()
            conn.close()
        return redirect(url_for('study_timer'))

    def assign_daily_challenges(user_id, conn):
        today = date.today().isoformat()
        cur = conn.cursor()
        # Check if already assigned
        cur.execute(
            "SELECT 1 FROM user_daily_challenges WHERE user_id=? AND date=?",
            (user_id, today)
        )
        if cur.fetchone():
            return  # Already assigned today

        # Get all challenge IDs
        cur.execute("SELECT id FROM challenges")
        challenge_ids = [row['id'] for row in cur.fetchall()]
        if not challenge_ids:
            return
        chosen = random.sample(challenge_ids, min(3, len(challenge_ids)))
        for cid in chosen:
            cur.execute(
                "INSERT INTO user_daily_challenges (user_id, challenge_id, date) VALUES (?, ?, ?)",
                (user_id, cid, today)
            )
        conn.commit()

    def get_user_id(username, conn):
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username = ?", (username,))
        row = cur.fetchone()
        return row['id'] if row else None

    @app.route("/", methods=["GET"])
    @app.route("/index.html", methods=["GET"])
    def home():
        if 'username' in session:
            return redirect(url_for('home_logged_in'))
        else:
            return render_template("index.html")

    @app.route("/dashboard")
    def dashboard():
        if 'username' in session and 'email' in session:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT total_study_time, xp, id FROM users WHERE username = ?", (session['username'],))
            user = cur.fetchone()

            total_seconds = user["total_study_time"] if user and user["total_study_time"] is not None else 0
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            xp = user["xp"] if user and user["xp"] is not None else 0
            user_id = user["id"] if user else None

            # Assign daily challenges if needed
            if user_id:
                assign_daily_challenges(user_id, conn)

            # Fetch today's challenges
            today = date.today().isoformat()
            cur.execute("""
                SELECT c.description, c.xp_reward, u.progress, u.completed, u.challenge_id, u.id as user_challenge_id
                FROM user_daily_challenges u
                JOIN challenges c ON u.challenge_id = c.id
                WHERE u.user_id=? AND u.date=?
            """, (user_id, today))
            challenges = cur.fetchall()

            # Fetch achievements
            cur.execute("SELECT achievement_name, unlocked_at FROM achievements WHERE username=?", (session['username'],))
            achievements = cur.fetchall()

            # Fetch streak
            streak = get_study_streak(session['username'], cur)

            conn.close()
            return render_template(
                "dashboard.html",
                username=session['username'],
                email=session['email'],
                study_hours=hours,
                study_minutes=minutes,
                xp=xp,
                achievements=achievements,
                streak=streak,
                challenges=challenges
            )
        else:
            flash("You need to log in first.")
            return redirect(url_for('login'))

    @app.route("/complete_challenge", methods=["POST"])
    def complete_challenge():
        if 'username' not in session:
            return jsonify({"error": "Not logged in"}), 401

        data = request.get_json()
        user_challenge_id = data.get("user_challenge_id")
        if not user_challenge_id:
            return jsonify({"error": "Missing challenge ID"}), 400

        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT u.user_id, u.challenge_id, u.completed, c.xp_reward
            FROM user_daily_challenges u
            JOIN challenges c ON u.challenge_id = c.id
            WHERE u.id = ?
        """, (user_challenge_id,))
        row = cur.fetchone()
        if not row or row["completed"]:
            conn.close()
            return jsonify({"error": "Invalid or already completed"}), 400

        cur.execute("UPDATE user_daily_challenges SET completed=1 WHERE id=?", (user_challenge_id,))
        cur.execute("UPDATE users SET xp = xp + ? WHERE id=?", (row["xp_reward"], row["user_id"]))
        conn.commit()
        conn.close()
        return jsonify({"success": True, "xp_awarded": row["xp_reward"]})

    @app.route("/log_study_time", methods=["POST"])
    def log_study_time():
        if 'username' not in session:
            return jsonify({"error": "Not logged in"}), 401

        data = request.get_json()
        seconds = data.get("seconds", 0)
        subject = data.get("subject", "General")
        try:
            seconds = int(seconds)
        except Exception:
            return jsonify({"error": "Invalid data"}), 400

        xp_earned = seconds // 60  # 1 XP per minute

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            """
            UPDATE users
            SET total_study_time = COALESCE(total_study_time, 0) + ?,
                xp = COALESCE(xp, 0) + ?
            WHERE username = ?
            """,
            (seconds, xp_earned, session['username'])
        )
        conn.commit()

        cur.execute("SELECT xp, id FROM users WHERE username = ?", (session['username'],))
        row = cur.fetchone()
        new_xp = row['xp'] if row else 0
        user_id = row['id'] if row else None

        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute(
            "INSERT INTO study_sessions (username, date, seconds, subject) VALUES (?, ?, ?, ?)",
            (session['username'], today, seconds, subject)
        )

        # --- Challenge: Study for 30 minutes ---
        cur.execute(
            "SELECT SUM(seconds) FROM study_sessions WHERE username=? AND date=?",
            (session['username'], today)
        )
        total_today = cur.fetchone()[0] or 0
        cur.execute("""
            SELECT u.id, u.completed, c.xp_reward
            FROM user_daily_challenges u
            JOIN challenges c ON u.challenge_id = c.id
            WHERE u.user_id = ? AND u.date=? AND c.description='Study for 30 minutes'
        """, (user_id, today))
        row30 = cur.fetchone()
        if row30 and not row30["completed"] and total_today >= 1800:
            cur.execute("UPDATE user_daily_challenges SET completed=1 WHERE id=?", (row30["id"],))
            cur.execute("UPDATE users SET xp = xp + ? WHERE id=?", (row30["xp_reward"], user_id))

        # --- Challenge: Complete 2 study sessions ---
        cur.execute(
            "SELECT COUNT(*) FROM study_sessions WHERE username=? AND date=?",
            (session['username'], today)
        )
        sessions_today = cur.fetchone()[0]
        cur.execute("""
            SELECT u.id, u.completed, c.xp_reward
            FROM user_daily_challenges u
            JOIN challenges c ON u.challenge_id = c.id
            WHERE u.user_id = ? AND u.date=? AND c.description='Complete 2 study sessions'
        """, (user_id, today))
        row2 = cur.fetchone()
        if row2 and not row2["completed"] and sessions_today >= 2:
            cur.execute("UPDATE user_daily_challenges SET completed=1 WHERE id=?", (row2["id"],))
            cur.execute("UPDATE users SET xp = xp + ? WHERE id=?", (row2["xp_reward"], user_id))

        # --- Challenge: Study for 60 minutes ---
        cur.execute("""
            SELECT u.id, u.completed, c.xp_reward
            FROM user_daily_challenges u
            JOIN challenges c ON u.challenge_id = c.id
            WHERE u.user_id = ? AND u.date=? AND c.description='Study for 60 minutes'
        """, (user_id, today))
        row60 = cur.fetchone()
        if row60 and not row60["completed"] and total_today >= 3600:
            cur.execute("UPDATE user_daily_challenges SET completed=1 WHERE id=?", (row60["id"],))
            cur.execute("UPDATE users SET xp = xp + ? WHERE id=?", (row60["xp_reward"], user_id))

        # --- Challenge: Complete 3 study sessions ---
        cur.execute("""
            SELECT u.id, u.completed, c.xp_reward
            FROM user_daily_challenges u
            JOIN challenges c ON u.challenge_id = c.id
            WHERE u.user_id = ? AND u.date=? AND c.description='Complete 3 study sessions'
        """, (user_id, today))
        row3 = cur.fetchone()
        if row3 and not row3["completed"] and sessions_today >= 3:
            cur.execute("UPDATE user_daily_challenges SET completed=1 WHERE id=?", (row3["id"],))
            cur.execute("UPDATE users SET xp = xp + ? WHERE id=?", (row3["xp_reward"], user_id))

        # --- Challenge: Study for 15 minutes without pausing ---
        cur.execute(
            "SELECT id FROM study_sessions WHERE username=? AND date=? AND seconds>=900",
            (session['username'], today)
        )
        row15 = cur.fetchone()
        cur.execute("""
            SELECT u.id, u.completed, c.xp_reward
            FROM user_daily_challenges u
            JOIN challenges c ON u.challenge_id = c.id
            WHERE u.user_id = ? AND u.date=? AND c.description='Study for 15 minutes without pausing'
        """, (user_id, today))
        row15c = cur.fetchone()
        if row15 and row15c and not row15c["completed"]:
            cur.execute("UPDATE user_daily_challenges SET completed=1 WHERE id=?", (row15c["id"],))
            cur.execute("UPDATE users SET xp = xp + ? WHERE id=?", (row15c["xp_reward"], user_id))

        new_xp_achievements = check_and_unlock_achievements(session['username'], new_xp, cur)
        new_streak_achievements, streak = check_streak_achievements(session['username'], cur)
        cur.execute("SELECT achievement_name, unlocked_at FROM achievements WHERE username=?", (session['username'],))
        achievements = [{"name": r["achievement_name"], "unlocked_at": r["unlocked_at"]} for r in cur.fetchall()]

        conn.commit()
        conn.close()

        new_achievements = new_xp_achievements + new_streak_achievements

        print(f"Added {seconds}s and {xp_earned} XP to {session['username']} (new XP: {new_xp}, streak: {streak})")
        return jsonify({
            "success": True,
            "added_seconds": seconds,
            "added_xp": xp_earned,
            "new_xp": new_xp,
            "streak": streak,
            "new_achievements": new_achievements,
            "achievements": achievements
        })

    @app.route("/analytics")
    def analytics():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))
        
        user = dbHandler.get_user(session['username'])
        # Progress tracking per subject
        conn = get_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT subject, SUM(seconds) as total_seconds
            FROM study_sessions
            WHERE username = ?
            GROUP BY subject
        """, (session['username'],))
        subject_stats = cur.fetchall()
        conn.close()

        stats = dbHandler.get_user_stats(user['username'])
        recent_logs = dbHandler.get_recent_logs(user['username'])
        top_projects = dbHandler.get_top_projects(user['username'])
        
        return render_template("analytics.html", user=user, stats=stats, recent_logs=recent_logs, top_projects=top_projects, subject_stats=subject_stats)

    @app.route("/home_logged_in", methods=["GET"])
    def home_logged_in():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT username, COALESCE(total_study_time, 0) as total_study_time FROM users ORDER BY total_study_time DESC LIMIT 10")
        leaderboard = [
            {"username": row["username"], "study_hours": round(row["total_study_time"] / 3600, 1)}
            for row in cur.fetchall()
        ]
        conn.close()

        return render_template(
            "home_logged_in.html",
            username=session['username'],
            email=session.get('email'),
            leaderboard=leaderboard
        )

    @app.route("/profile", methods=["GET"])
    def profile():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))
        
        user = dbHandler.get_user(session['username'])
        return render_template("profile.html", user=user)

    @app.route("/update_profile", methods=["POST"])
    def update_profile():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        try:
            validate_csrf(request.form['csrf_token'])
        except ValueError:
            flash("CSRF token is missing or invalid.")
            return redirect(url_for('profile'))
        
        email = basic_sanitize_input(request.form["email"])
        new_username = basic_sanitize_input(request.form["username"])
        new_password = request.form["password"]
        current_username = session['username']
        avatar = request.form.get("avatar", "🙂") 
        
        username_error = None
        password_error = None
        
        hashed_password = None
        try:
            if new_username != current_username and dbHandler.get_user(new_username):
                username_error = "Username is already taken."
            
            if new_password:
                validation_result = validate_password(new_password)
                if validation_result != "Password is valid.":
                    password_error = validation_result
                else:
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            if username_error or password_error:
                user = dbHandler.get_user(current_username)
                return render_template("profile.html", user=user, username_error=username_error, password_error=password_error)
            
            dbHandler.update_user_profile(current_username, email, new_username, hashed_password, avatar)
            if new_username != current_username:
                flash("Username updated successfully.")
                session['username'] = new_username
            if new_password:
                flash("Password updated successfully.")
            flash("Profile updated successfully.")
            session['username'] = new_username
        except ValueError as e:
            flash(f"Value error occurred: {e}")
        except KeyError as e:
            flash(f"Key error occurred: {e}")
        except dbHandler.DatabaseError as e:
            flash(f"An error occurred: {e}")
        
        return redirect(url_for('profile'))

    def check_and_unlock_achievements(username, xp, cur):
        milestones = [
            (1, "First Steps"),
            (50, "Warming Up"),
            (100, "Getting Serious"),
            (250, "Quarter Master"),
            (500, "Study Pro"),
            (750, "XP Grinder"),
            (1000, "Master"),
            (2000, "Legend"),
            (5000, "Study Machine"),
            (10000, "Ultimate Scholar"),
        ]
        unlocked = []
        for threshold, name in milestones:
            cur.execute("SELECT 1 FROM achievements WHERE username=? AND achievement_name=?", (username, name))
            if xp >= threshold and not cur.fetchone():
                cur.execute("INSERT INTO achievements (username, achievement_name) VALUES (?, ?)", (username, name))
                unlocked.append(name)
        return unlocked

    def get_study_streak(username,cur):
        streak = 0
        today = datetime.now().date()
        for i in range(0, 100):
            day = today - timedelta(days=i)
            cur.execute(
                "SELECT 1 FROM study_sessions WHERE username=? AND date=?",
                (username, day.strftime('%Y-%m-%d'))
            )
            if cur.fetchone():
                streak += 1
            else:
                break
        return streak

    def check_streak_achievements(username, cur):
        streak = get_study_streak(username, cur)
        unlocked = []
        milestones = [
            (3, "3-Day Streaker"),
            (7, "One Week Wonder"),
            (14, "Two Week Warrior"),
            (30, "Month Master"),
        ]
        for threshold, name in milestones:
            cur.execute("SELECT 1 FROM achievements WHERE username=? AND achievement_name=?", (username, name))
            if streak >= threshold and not cur.fetchone():
                cur.execute("INSERT INTO achievements (username, achievement_name) VALUES (?, ?)", (username, name))
                unlocked.append(name)
        return unlocked, streak

    @app.route("/study_timer")
    def study_timer():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))
        user_subjects = get_user_subjects(session['username'])
        csrf_token = generate_csrf()
        return render_template("study_timer.html", user_subjects=user_subjects,csrf_token=csrf_token) 

    @app.route("/achievements")
    def achievements():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        all_achievements = [
            {"name": "First Steps", "icon": "🎉", "threshold": 1},
            {"name": "Warming Up", "icon": "🔥", "threshold": 50},
            {"name": "Getting Serious", "icon": "💪", "threshold": 100},
            {"name": "Quarter Master", "icon": "🏅", "threshold": 250},
            {"name": "Study Pro", "icon": "📚", "threshold": 500},
            {"name": "XP Grinder", "icon": "⚡", "threshold": 750},
            {"name": "Master", "icon": "🥇", "threshold": 1000},
            {"name": "Legend", "icon": "🌟", "threshold": 2000},
            {"name": "Study Machine", "icon": "🤖", "threshold": 5000},
            {"name": "Ultimate Scholar", "icon": "🏆", "threshold": 10000},
        ]

        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT achievement_name, unlocked_at FROM achievements WHERE username=?", (session['username'],))
        unlocked = cur.fetchall()
        cur.execute("SELECT xp FROM users WHERE username=?", (session['username'],))
        user = cur.fetchone()
        user_xp = user['xp'] if user else 0
        conn.close()

        user_achievements = {row['achievement_name']: {"unlocked_at": row['unlocked_at']} for row in unlocked}

        for milestone in all_achievements:
            if milestone['name'] in user_achievements:
                milestone['progress'] = 100
            else:
                milestone['progress'] = min(100, int((user_xp / milestone['threshold']) * 100))

        return render_template(
            "achievements.html",
            all_achievements=all_achievements,
            user_achievements=user_achievements,
            user_xp=user_xp
        )

    @app.route("/leaderboard")
    def leaderboard():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        period = request.args.get('period', 'all')
        conn = get_db()
        cur = conn.cursor()

        if period == 'today':
            date_filter = datetime.now().strftime('%Y-%m-%d')
            cur.execute("""
                SELECT username, SUM(seconds) as study_seconds
                FROM study_sessions
                WHERE date = ?
                GROUP BY username
                ORDER BY study_seconds DESC
                LIMIT 20
            """, (date_filter,))
        elif period == 'week':
            start_of_week = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
            cur.execute("""
                SELECT username, SUM(seconds) as study_seconds
                FROM study_sessions
                WHERE date >= ?
                GROUP BY username
                ORDER BY study_seconds DESC
                LIMIT 20
            """, (start_of_week,))
        else:
            cur.execute("""
                SELECT username, COALESCE(total_study_time, 0) as study_seconds
                FROM users
                ORDER BY study_seconds DESC
                LIMIT 20
            """)

        users = cur.fetchall()

        def get_streak(username):
            streak = 0
            today = datetime.now().date()
            for i in range(0, 100):
                day = today - timedelta(days=i)
                cur.execute(
                    "SELECT 1 FROM study_sessions WHERE username=? AND date=?",
                    (username, day.strftime('%Y-%m-%d'))
                )
                if cur.fetchone():
                    streak += 1
                else:
                    break
            return streak

        leaderboard = [
            {
                "username": row["username"],
                "avatar": dbHandler.get_user(row["username"])["avatar"] if dbHandler.get_user(row["username"]) else "🙂",
                "study_hours": round((row["study_seconds"] or 0) / 3600, 1),
                "streak": get_streak(row["username"])
            }
            for row in users
        ]
        conn.close()

        return render_template(
            "leaderboard.html",
            leaderboard=leaderboard,
            period=period,
            session=session
        )