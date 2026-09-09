import sqlite3
from datetime import date, datetime, timedelta

DATABASE_NAME = "study_tracker.db"


# =========================================================
# CONNECTION
# =========================================================

def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER,
            duration_seconds INTEGER NOT NULL,
            started_at TEXT NOT NULL,
            ended_at TEXT NOT NULL,
            FOREIGN KEY(subject_id) REFERENCES subjects(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
    """)

    defaults = {
        "daily_goal": "14400",
        "water_goal": "8",
        "theme": "OCEAN",
        "appearance": "DARK",
        "eye_comfort": "OFF",
        "water_reminder": "OFF",
        "reminder_interval": "60"
    }

    for key, value in defaults.items():
        cursor.execute("""
            INSERT OR IGNORE INTO settings
            (key, value)
            VALUES (?, ?)
        """, (key, value))

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_tracking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tracking_date TEXT NOT NULL UNIQUE,
            glasses INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            completed_at TEXT
        )
    """)

    connection.commit()
    connection.close()


# Keep compatibility with your original main.py
def init_db():
    initialize_database()


# =========================================================
# SETTINGS
# =========================================================

def get_setting(key, default=None):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT value
        FROM settings
        WHERE key = ?
    """, (key,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return default

    return row["value"]


def set_setting(key, value):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO settings
        (key, value)
        VALUES (?, ?)
    """, (key, str(value)))

    connection.commit()
    connection.close()


# =========================================================
# SUBJECTS
# =========================================================

def add_subject(name):

    name = name.strip()

    if not name:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO subjects
            (name, created_at)
            VALUES (?, ?)
        """, (name, datetime.now().isoformat()))

        connection.commit()
        subject_id = cursor.lastrowid

    except sqlite3.IntegrityError:
        subject_id = None

    connection.close()

    return subject_id


def get_subjects():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subjects
        ORDER BY name
    """)

    rows = cursor.fetchall()
    connection.close()

    return rows


def get_subject_by_name(name):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM subjects
        WHERE name = ?
    """, (name,))

    row = cursor.fetchone()
    connection.close()

    return row


def rename_subject(subject_id, new_name):

    new_name = new_name.strip()

    if not new_name:
        return False

    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            UPDATE subjects
            SET name = ?
            WHERE id = ?
        """, (new_name, subject_id))

        connection.commit()

    except sqlite3.IntegrityError:
        connection.close()
        return False

    connection.close()
    return True


def delete_subject(subject_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM study_sessions
        WHERE subject_id = ?
    """, (subject_id,))

    cursor.execute("""
        DELETE FROM subjects
        WHERE id = ?
    """, (subject_id,))

    connection.commit()
    connection.close()


def get_subject_study_seconds(subject_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(duration_seconds), 0)
        FROM study_sessions
        WHERE subject_id = ?
    """, (subject_id,))

    result = cursor.fetchone()[0]

    connection.close()

    return int(result)


# =========================================================
# STUDY SESSIONS
# =========================================================

def save_session(
    subject_name,
    duration_seconds,
    started_at=None,
    ended_at=None
):

    if duration_seconds <= 0:
        return

    subject = get_subject_by_name(subject_name)

    if subject is None:
        subject_id = add_subject(subject_name)
    else:
        subject_id = subject["id"]

    if started_at is None:
        started_at = datetime.now().isoformat()

    if ended_at is None:
        ended_at = datetime.now().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO study_sessions
        (
            subject_id,
            duration_seconds,
            started_at,
            ended_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        subject_id,
        int(duration_seconds),
        started_at,
        ended_at
    ))

    connection.commit()
    connection.close()


def get_today_study_seconds():

    today = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(duration_seconds), 0)
        FROM study_sessions
        WHERE date(started_at) = ?
    """, (today,))

    result = cursor.fetchone()[0]
    connection.close()

    return int(result)


def get_week_study_seconds():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COALESCE(SUM(duration_seconds), 0)
        FROM study_sessions
        WHERE date(started_at) >= date(
            'now',
            'localtime',
            '-6 days'
        )
    """)

    result = cursor.fetchone()[0]
    connection.close()

    return int(result)


def get_recent_sessions(limit=50):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            study_sessions.id,
            subjects.name AS subject_name,
            study_sessions.duration_seconds,
            study_sessions.started_at,
            study_sessions.ended_at
        FROM study_sessions
        LEFT JOIN subjects
        ON study_sessions.subject_id = subjects.id
        ORDER BY study_sessions.started_at DESC
        LIMIT ?
    """, (limit,))

    rows = cursor.fetchall()
    connection.close()

    return rows


def delete_session(session_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM study_sessions
        WHERE id = ?
    """, (session_id,))

    connection.commit()
    connection.close()


def clear_history():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM study_sessions
    """)

    connection.commit()
    connection.close()


def get_daily_study():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            date(started_at) AS study_date,
            SUM(duration_seconds) AS seconds
        FROM study_sessions
        GROUP BY date(started_at)
        ORDER BY study_date DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return rows


# =========================================================
# STREAK
# =========================================================

def get_streak():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT DISTINCT date(started_at) AS study_date
        FROM study_sessions
    """)

    rows = cursor.fetchall()
    connection.close()

    days = {row["study_date"] for row in rows}

    if not days:
        return 0

    current = date.today()
    streak = 0

    while current.isoformat() in days:
        streak += 1
        current -= timedelta(days=1)

    return streak


# =========================================================
# WATER
# =========================================================

def get_water_goal():
    return int(get_setting("water_goal", "8"))


def set_water_goal(goal):

    goal = max(1, int(goal))
    set_setting("water_goal", goal)


def get_today_water():

    today = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT glasses
        FROM water_tracking
        WHERE tracking_date = ?
    """, (today,))

    row = cursor.fetchone()
    connection.close()

    if row is None:
        return 0

    return int(row["glasses"])


def set_today_water(glasses):

    glasses = max(0, int(glasses))
    today = date.today().isoformat()

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO water_tracking
        (tracking_date, glasses)
        VALUES (?, ?)
        ON CONFLICT(tracking_date)
        DO UPDATE SET glasses = excluded.glasses
    """, (today, glasses))

    connection.commit()
    connection.close()


def add_water_glass():

    current = get_today_water()
    goal = get_water_goal()

    if current < goal:
        set_today_water(current + 1)


def remove_water_glass():

    current = get_today_water()

    if current > 0:
        set_today_water(current - 1)


# =========================================================
# TASKS
# =========================================================

def add_task(title):

    title = title.strip()

    if not title:
        return None

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (title, completed, created_at)
        VALUES (?, 0, ?)
    """, (title, datetime.now().isoformat()))

    connection.commit()

    task_id = cursor.lastrowid

    connection.close()

    return task_id


def get_tasks():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tasks
        ORDER BY completed ASC, created_at DESC
    """)

    rows = cursor.fetchall()
    connection.close()

    return rows


def get_pending_tasks(limit=None):

    connection = get_connection()
    cursor = connection.cursor()

    if limit is None:
        cursor.execute("""
            SELECT *
            FROM tasks
            WHERE completed = 0
            ORDER BY created_at DESC
        """)
    else:
        cursor.execute("""
            SELECT *
            FROM tasks
            WHERE completed = 0
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))

    rows = cursor.fetchall()
    connection.close()

    return rows


def toggle_task(task_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT completed
        FROM tasks
        WHERE id = ?
    """, (task_id,))

    row = cursor.fetchone()

    if row is not None:

        new_value = 0 if row["completed"] else 1

        completed_at = (
            datetime.now().isoformat()
            if new_value
            else None
        )

        cursor.execute("""
            UPDATE tasks
            SET completed = ?,
                completed_at = ?
            WHERE id = ?
        """, (
            new_value,
            completed_at,
            task_id
        ))

    connection.commit()
    connection.close()


def delete_task(task_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM tasks
        WHERE id = ?
    """, (task_id,))

    connection.commit()
    connection.close()


def get_task_count():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            COALESCE(
                SUM(
                    CASE
                        WHEN completed = 1 THEN 1
                        ELSE 0
                    END
                ),
                0
            ) AS completed
        FROM tasks
    """)

    row = cursor.fetchone()
    connection.close()

    return (
        int(row["total"]),
        int(row["completed"])
    )