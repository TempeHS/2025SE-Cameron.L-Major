from flask import render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta 
import userManagement as dbHandler
import bcrypt
from utils import validate_password, basic_sanitize_input
from flask_wtf.csrf import validate_csrf
import sqlite3
import os

def register_main_routes(app):
    @app.route("/", methods=["GET"])
    @app.route("/index.html", methods=["GET"])
    def home():
        """Render the home page."""
        if 'username' in session:
            return redirect(url_for('home_logged_in'))
        else:
            return render_template("index.html")


    def get_db():
        db_path = '.databaseFiles/database.db'
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn


    @app.route("/dashboard")
    def dashboard():
        if 'username' in session and 'email' in session:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT total_study_time, xp FROM users WHERE username = ?", (session['username'],))
            user = cur.fetchone()

            total_seconds = user["total_study_time"] if user and user["total_study_time"] is not None else 0
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            xp = user["xp"] if user and user["xp"] is not None else 0

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
                streak=streak
            )
        else:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        
    @app.route("/analytics")
    def analytics():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))
        
        user = dbHandler.get_user(session['username'])
        stats = dbHandler.get_user_stats(user['username'])
        recent_logs = dbHandler.get_recent_logs(user['username'])
        top_projects = dbHandler.get_top_projects(user['username'])
        
        return render_template("analytics.html", user=user, stats=stats, recent_logs=recent_logs, top_projects=top_projects)

    @app.route("/create_log", methods=["GET", "POST"])
    def create_log():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))
        
        if request.method == "GET":
            current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return render_template("create_log.html", current_datetime=current_datetime, username=session['username'])
        if request.method == "POST":
            try:
                validate_csrf(request.form['csrf_token'])
            except ValueError:
                flash("CSRF token is missing or invalid.")
                return redirect(url_for('create_log'))

            date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            developer_name = session['username']
            project = basic_sanitize_input(request.form["project"])
            content = basic_sanitize_input(request.form["content"])
            code_snippet = basic_sanitize_input(request.form["code_snippet"])
            repository = basic_sanitize_input(request.form.get("repository_link"))
            
            dbHandler.add_log(date, developer_name, project, content, code_snippet, repository)
            flash("Log created successfully!")
            return redirect(url_for("dashboard"))


    @app.route("/home_logged_in", methods=["GET"])
    def home_logged_in():
        """Render the home page for logged-in users with leaderboard."""
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        conn = get_db()
        cur = conn.cursor()
        # Get top 10 users by total study time (in seconds)
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

    @app.route("/search_logs", methods=["GET"])
    def search_logs():
        """Search logs by developer, date, and project."""
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))
        
        developer = basic_sanitize_input(request.args.get('developer'))
        date = basic_sanitize_input(request.args.get('date'))
        project = basic_sanitize_input(request.args.get('project'))
        sort_by = basic_sanitize_input(request.args.get('sort_by', 'date'))
        sort_order = basic_sanitize_input(request.args.get('sort_order', 'asc'))
        
        page = request.args.get('page', 1, type=int)
        per_page = 5
        logs = dbHandler.search_logs(developer, date, project, sort_by, sort_order)
        total_logs = len(logs)  # Assuming search_logs returns all matching logs
        print(f"Logs passed to template: {logs}")  # Debug print
        return render_template("home_logged_in.html", username=session['username'], email=session['email'], logs=logs, page=page, per_page=per_page, total_logs=total_logs)

    @app.route("/edit_log/<int:log_id>", methods=["GET", "POST"])
    def edit_log(log_id):
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        log = dbHandler.get_log_by_id(log_id)
        if not log or not dbHandler.is_log_editable(log_id, session['username']):
            flash("You do not have permission to edit this log.")
            return redirect(url_for('dashboard'))

        if request.method == "GET":
            return render_template("edit_log.html", log=log)
        if request.method == "POST":
            try:
                validate_csrf(request.form['csrf_token'])
            except ValueError:
                flash("CSRF token is missing or invalid.")
                return render_template("edit_log.html", log=log, error="CSRF token is missing or invalid.")

            project = basic_sanitize_input(request.form["project"])
            content = basic_sanitize_input(request.form["content"])
            code_snippet = basic_sanitize_input(request.form["code_snippet"])
            
            dbHandler.update_log(log_id, project, content, code_snippet)
            flash("Log updated successfully!")
            return redirect(url_for("dashboard"))

    @app.route("/delete_log/<int:log_id>", methods=["POST"])
    def delete_log(log_id):
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        try:
            validate_csrf(request.form['csrf_token'])
        except ValueError:
            flash("CSRF token is missing or invalid.")
            return redirect(url_for('dashboard'))

        if not dbHandler.is_log_deletable(log_id, session['username']):
            flash("You do not have permission to delete this log.")
            return redirect(url_for('dashboard'))

        dbHandler.delete_log(log_id)
        flash("Log deleted successfully!")
        return redirect(url_for("dashboard"))
    
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
        new_password = request.form["password"]  # Password validation is done separately
        current_username = session['username']
        
        username_error = None
        password_error = None
        
        hashed_password = None
        try:
            if new_username != current_username and dbHandler.get_user(new_username):
                username_error = "Username is already taken."
            
            # Validate the new password if provided
            if new_password:
                validation_result = validate_password(new_password)
                if validation_result != "Password is valid.":
                    password_error = validation_result
                else:
                    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            if username_error or password_error:
                user = dbHandler.get_user(current_username)
                return render_template("profile.html", user=user, username_error=username_error, password_error=password_error)
            
            dbHandler.update_user_profile(current_username, email, new_username, hashed_password)
            if new_username != current_username:
                flash("Username updated successfully.")
                session['username'] = new_username  # Update session username if changed
            if new_password:
                flash("Password updated successfully.")
            flash("Profile updated successfully.")
            session['username'] = new_username  # Update session username if changed
        except ValueError as e:
            flash(f"Value error occurred: {e}")
        except KeyError as e:
            flash(f"Key error occurred: {e}")
        except dbHandler.DatabaseError as e:
            flash(f"An error occurred: {e}")
        
        return redirect(url_for('profile'))


    @app.route("/log_study_time", methods=["POST"])
    def log_study_time():
        if 'username' not in session:
            return jsonify({"error": "Not logged in"}), 401

        data = request.get_json()
        seconds = data.get("seconds", 0)
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

        # Fetch new XP value
        cur.execute("SELECT xp FROM users WHERE username = ?", (session['username'],))
        row = cur.fetchone()
        new_xp = row['xp'] if row else 0

        # Log today's session
        today = datetime.now().strftime('%Y-%m-%d')
        cur.execute(
            "INSERT INTO study_sessions (username, date, seconds) VALUES (?, ?, ?)",
            (session['username'], today, seconds)
        )

        # Unlock XP-based achievements (pass cur!)
        new_xp_achievements = check_and_unlock_achievements(session['username'], new_xp, cur)

        # Unlock streak achievements and get current streak
        new_streak_achievements, streak = check_streak_achievements(session['username'], cur)

        # Optionally, fetch all achievements for display
        cur.execute("SELECT achievement_name, unlocked_at FROM achievements WHERE username=?", (session['username'],))
        achievements = [{"name": r["achievement_name"], "unlocked_at": r["unlocked_at"]} for r in cur.fetchall()]

        conn.commit()
        conn.close()

        # Combine all newly unlocked achievements for notification
        new_achievements = new_xp_achievements + new_streak_achievements

        print(f"Added {seconds}s and {xp_earned} XP to {session['username']} (new XP: {new_xp}, streak: {streak})")
        return jsonify({
            "success": True,
            "added_seconds": seconds,
            "added_xp": xp_earned,
            "new_xp": new_xp,
            "streak": streak,
            "new_achievements": new_achievements,
            "achievements": achievements  # for dashboard display
        })

    def check_and_unlock_achievements(username, xp, cur):
        print(f"DEBUG: Checking achievements for {username} with XP {xp}")
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
                print(f"DEBUG: Unlocking {name} for {username} at {xp} XP")
                cur.execute("INSERT INTO achievements (username, achievement_name) VALUES (?, ?)", (username, name))
                unlocked.append(name)
        return unlocked


    def get_study_streak(username,cur):
        streak = 0
        today = datetime.now().date()
        for i in range(0, 100):  # check up to 100 days back
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
        return render_template("study_timer.html")

    @app.route("/achievements")
    def achievements():
        if 'username' not in session:
            flash("You need to log in first.")
            return redirect(url_for('login'))

        # Define all possible achievements (add icons as you like)
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

        # Fetch unlocked achievements
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT achievement_name, unlocked_at FROM achievements WHERE username=?", (session['username'],))
        unlocked = cur.fetchall()
        cur.execute("SELECT xp FROM users WHERE username=?", (session['username'],))
        user = cur.fetchone()
        user_xp = user['xp'] if user else 0
        conn.close()

        # Build dict for unlocked achievements
        user_achievements = {row['achievement_name']: {"unlocked_at": row['unlocked_at']} for row in unlocked}

        # Add progress to each milestone
        for milestone in all_achievements:
            if milestone['name'] in user_achievements:
                milestone['progress'] = 100
            else:
                milestone['progress'] = min(100, int((user_xp / milestone['threshold']) * 100))

        return render_template(
            "achievements.html",
            all_achievements=all_achievements,
            user_achievements=user_achievements
        )

    @app.route("/leaderboard")
    def leaderboard():
        """Show the top 20 users by total study time and streak, with period filter."""
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
        else:  # all time
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