import os
import sqlite3
from flask import (
    Flask, g, render_template, request,
    redirect, url_for, session, jsonify
)
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config["SECRET_KEY"] = "change-this-secret-key"
app.config["DATABASE"] = os.path.join(app.root_path, "database.db")


# LOGIN REQUIRED DECORATOR
def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user():
            return redirect(url_for("signin"))
        return f(*args, **kwargs)
    return wrapper


# DATABASE CONNECTION
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(app.config["DATABASE"])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS moments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            time_value TEXT NOT NULL,
            mood TEXT,
            text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );

        CREATE TABLE IF NOT EXISTS swaps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            giver_moment_id INTEGER,
            receiver_moment_id INTEGER,
            swap_time TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(giver_moment_id) REFERENCES moments(id),
            FOREIGN KEY(receiver_moment_id) REFERENCES moments(id)
        );
    """)
    db.commit()


with app.app_context():
    init_db()


# AUTH HELPERS
def login_user(user_id):
    session["user_id"] = user_id

def logout_user():
    session.pop("user_id", None)

def current_user():
    return session.get("user_id")


# PAGE ROUTES
@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/exchange", methods=["GET", "POST"])
@login_required
def exchange():
    user_id = current_user()
    db = get_db()

    if request.method == "POST":
        time_value = request.form.get("time_value") or "00:00"
        mood = request.form.get("mood")
        text = (request.form.get("text") or "").strip()

        if not text:
            return redirect(url_for("exchange"))

        # Save your moment
        cur = db.execute(
            "INSERT INTO moments (user_id, time_value, mood, text) VALUES (?, ?, ?, ?)",
            (user_id, time_value, mood, text)
        )
        user_moment_id = cur.lastrowid
        db.commit()

        # Random moment from others
        cur = db.execute(
            """
            SELECT id, time_value, mood, text
            FROM moments
            WHERE id != ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (user_moment_id,),
        )
        received = cur.fetchone()

        # If no other moment, return your own
        if not received:
            cur = db.execute(
                "SELECT id, time_value, mood, text FROM moments WHERE id = ?",
                (user_moment_id,)
            )
            received = cur.fetchone()

        # Save swap
        db.execute(
            "INSERT INTO swaps (user_id, giver_moment_id, receiver_moment_id) VALUES (?, ?, ?)",
            (user_id, user_moment_id, received["id"])
        )
        db.commit()

        return render_template("result.html", received_moment=received)

    return render_template("exchange.html")


@app.route("/gallery")
@login_required
def gallery():
    return render_template("gallery.html")


@app.route("/stats")
@login_required
def stats():
    return render_template("stats.html")


@app.route("/signout")
@login_required
def signout():
    logout_user()
    return redirect(url_for("landing"))


# AUTH ROUTES
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if not username or not email or not password:
            return render_template("signup.html", error="All fields required")

        db = get_db()

        exists = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()
        if exists:
            return render_template("signup.html", error="Email already registered")

        db.execute(
            "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
            (username, email, generate_password_hash(password))
        )
        db.commit()

        user_id = db.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()["id"]

        login_user(user_id)
        return redirect(url_for("exchange"))

    return render_template("signup.html")


@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        db = get_db()
        user = db.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if not user or not check_password_hash(user["password_hash"], password):
            return render_template("signin.html", error="Invalid email or password")

        login_user(user["id"])
        return redirect(url_for("exchange"))

    return render_template("signin.html")


# API ROUTES
@app.route("/api/moments")
@login_required
def api_moments():
    user_id = current_user()
    db = get_db()

    offset = int(request.args.get("offset", 0))
    limit = int(request.args.get("limit", 9))

    cur = db.execute(
        """
        SELECT m.id, m.time_value, m.mood, m.text
        FROM swaps s
        JOIN moments m ON s.receiver_moment_id = m.id
        WHERE s.user_id = ?
        ORDER BY s.swap_time DESC
        LIMIT ? OFFSET ?
        """,
        (user_id, limit, offset)
    )
    rows = cur.fetchall()

    return jsonify([
        dict(r) for r in rows
    ])


@app.route("/api/stats")
@login_required
def api_stats():
    user_id = current_user()
    db = get_db()

    # Moments you shared
    user_moments = db.execute(
        "SELECT COUNT(*) FROM moments WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    # Moments you received
    user_received = db.execute(
        "SELECT COUNT(*) FROM swaps WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    # Total moments
    total_moments = db.execute(
        "SELECT COUNT(*) FROM moments"
    ).fetchone()[0]

    # Days streak
    streak = db.execute(
        "SELECT COUNT(DISTINCT date(created_at)) FROM moments WHERE user_id = ?",
        (user_id,)
    ).fetchone()[0]

    return jsonify({
        "user_moments": user_moments,
        "user_received": user_received,
        "total_moments": total_moments,
        "streak": streak
    })


# MAIN
if __name__ == "__main__":
    app.run(debug=True)
