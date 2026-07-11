import sqlite3

DB_NAME = "student_portal.db"


# ─────────────────────────────────────────────
#  CONNECTION
# ─────────────────────────────────────────────

def connect_db():
    return sqlite3.connect(DB_NAME)


# ─────────────────────────────────────────────
#  CREATE TABLES
# ─────────────────────────────────────────────

def create_tables():
    conn = connect_db()
    try:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    UNIQUE NOT NULL,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            roll_no TEXT UNIQUE NOT NULL,
            course  TEXT NOT NULL,
            photo   BLOB
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject    TEXT    NOT NULL,
            marks      INTEGER NOT NULL,
            UNIQUE(student_id, subject),
            FOREIGN KEY(student_id) REFERENCES students(id)
        )""")

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id               INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id       INTEGER NOT NULL,
            total_classes    INTEGER NOT NULL,
            attended_classes INTEGER NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(id)
        )""")

        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  MIGRATION  (adds photo column to old DBs)
# ─────────────────────────────────────────────

def _migrate():
    """Safely add the photo column if it doesn't exist yet."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(students)")
        columns = [row[1] for row in cursor.fetchall()]
        if "photo" not in columns:
            cursor.execute("ALTER TABLE students ADD COLUMN photo BLOB")
            conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  DEFAULT ADMIN
# ─────────────────────────────────────────────

def insert_default_admin():
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", ("admin",))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                ("admin", "admin123", "admin")
            )
            conn.commit()
    finally:
        conn.close()


def setup_database():
    create_tables()
    _migrate()
    insert_default_admin()


# ─────────────────────────────────────────────
#  STUDENT FUNCTIONS
# ─────────────────────────────────────────────

def insert_student(name, roll_no, course):
    name    = name.strip()
    roll_no = roll_no.strip()
    course  = course.strip()

    if not name or not roll_no or not course:
        raise ValueError("All fields are required")

    conn = connect_db()
    try:
        cursor = conn.cursor()

        # check duplicate roll number
        cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
        if cursor.fetchone():
            raise ValueError("Roll number already exists")

        cursor.execute(
            "INSERT INTO students (name, roll_no, course) VALUES (?, ?, ?)",
            (name, roll_no, course)
        )

        # create login credentials only if not already present
        cursor.execute("SELECT id FROM users WHERE username = ?", (roll_no,))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (roll_no, roll_no, "student")
            )

        conn.commit()

    except ValueError:
        conn.rollback()
        raise
    except sqlite3.IntegrityError as e:
        conn.rollback()
        raise ValueError(f"Database error: {e}")
    finally:
        conn.close()


def fetch_students():
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, roll_no, course FROM students ORDER BY roll_no")
        return cursor.fetchall()
    finally:
        conn.close()


def fetch_student_by_roll(roll_no):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, name, roll_no, course FROM students WHERE roll_no = ?",
            (roll_no.strip(),)
        )
        return cursor.fetchone()
    finally:
        conn.close()


def get_student_id_by_roll(roll_no):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM students WHERE roll_no = ?",
            (roll_no.strip(),)
        )
        result = cursor.fetchone()
        return result[0] if result else None
    finally:
        conn.close()


def update_student(roll_no, new_name, new_course):
    new_name   = new_name.strip()
    new_course = new_course.strip()

    if not new_name or not new_course:
        raise ValueError("Name and course cannot be empty")

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET name = ?, course = ? WHERE roll_no = ?",
            (new_name, new_course, roll_no.strip())
        )
        if cursor.rowcount == 0:
            raise ValueError("Student not found")
        conn.commit()
    finally:
        conn.close()


def delete_student(roll_no):
    conn = connect_db()
    try:
        cursor   = conn.cursor()
        student_id = get_student_id_by_roll(roll_no)
        if student_id is None:
            raise ValueError("Student not found")

        cursor.execute("DELETE FROM marks      WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM attendance  WHERE student_id = ?", (student_id,))
        cursor.execute("DELETE FROM students    WHERE roll_no    = ?", (roll_no.strip(),))
        cursor.execute("DELETE FROM users       WHERE username   = ?", (roll_no.strip(),))
        conn.commit()
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  PHOTO FUNCTIONS
# ─────────────────────────────────────────────

def save_student_photo(roll_no, photo_path):
    """Read image file from disk and store as binary blob in DB."""
    with open(photo_path, "rb") as f:
        photo_data = f.read()

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE students SET photo = ? WHERE roll_no = ?",
            (photo_data, roll_no.strip())
        )
        if cursor.rowcount == 0:
            raise ValueError("Student not found")
        conn.commit()
    finally:
        conn.close()


def get_student_photo(roll_no):
    """Return raw photo bytes, or None if no photo is stored."""
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT photo FROM students WHERE roll_no = ?",
            (roll_no.strip(),)
        )
        row = cursor.fetchone()
        return row[0] if row and row[0] else None
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  MARKS FUNCTIONS
# ─────────────────────────────────────────────

def insert_marks(student_id, subject, marks):
    subject = subject.strip()
    if not subject:
        raise ValueError("Subject is required")
    if not isinstance(marks, int):
        raise ValueError("Marks must be an integer")
    if marks < 0 or marks > 100:
        raise ValueError("Marks must be between 0 and 100")

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO marks (student_id, subject, marks)
            VALUES (?, ?, ?)
            ON CONFLICT(student_id, subject)
            DO UPDATE SET marks = excluded.marks
        """, (student_id, subject, marks))
        conn.commit()
    finally:
        conn.close()


def save_student_marks(student_id, subject_marks):
    if not subject_marks:
        raise ValueError("No marks provided")

    conn = connect_db()
    try:
        cursor = conn.cursor()
        for subject, marks in subject_marks.items():
            if not isinstance(marks, int):
                raise ValueError(f"Marks for {subject} must be an integer")
            if marks < 0 or marks > 100:
                raise ValueError(f"Marks for {subject} must be between 0 and 100")
            cursor.execute("""
                INSERT INTO marks (student_id, subject, marks)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id, subject)
                DO UPDATE SET marks = excluded.marks
            """, (student_id, subject.strip(), marks))
        conn.commit()
    finally:
        conn.close()


def get_marks_by_student(student_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT subject, marks FROM marks WHERE student_id = ? ORDER BY subject",
            (student_id,)
        )
        return cursor.fetchall()
    finally:
        conn.close()


def delete_marks_by_student(student_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM marks WHERE student_id = ?", (student_id,))
        conn.commit()
    finally:
        conn.close()


def get_top_rankers(limit=3):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.name, s.roll_no, s.course, SUM(m.marks) AS total
            FROM students s
            JOIN marks m ON s.id = m.student_id
            GROUP BY s.id, s.name, s.roll_no, s.course
            ORDER BY total DESC, s.name ASC
            LIMIT ?
        """, (limit,))
        return cursor.fetchall()
    finally:
        conn.close()


def get_pass_fail_stats(pass_marks=40):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.id, s.name,
                   COUNT(m.id) AS subject_count,
                   SUM(CASE WHEN m.marks >= ? THEN 1 ELSE 0 END) AS passed_subjects
            FROM students s
            JOIN marks m ON s.id = m.student_id
            GROUP BY s.id, s.name
        """, (pass_marks,))

        passed = 0
        failed = 0
        for _, _, subject_count, passed_subjects in cursor.fetchall():
            if subject_count > 0 and subject_count == passed_subjects:
                passed += 1
            else:
                failed += 1
        return passed, failed
    finally:
        conn.close()


# ─────────────────────────────────────────────
#  ATTENDANCE FUNCTIONS
# ─────────────────────────────────────────────

def add_attendance(student_id, total_classes, attended_classes):
    if total_classes < 0 or attended_classes < 0:
        raise ValueError("Attendance values cannot be negative")
    if attended_classes > total_classes:
        raise ValueError("Attended classes cannot exceed total classes")

    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attendance (student_id, total_classes, attended_classes)
            VALUES (?, ?, ?)
        """, (student_id, total_classes, attended_classes))
        conn.commit()
    finally:
        conn.close()


def get_attendance(student_id):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT total_classes, attended_classes
            FROM attendance
            WHERE student_id = ?
            ORDER BY id DESC LIMIT 1
        """, (student_id,))
        return cursor.fetchone()
    finally:
        conn.close()


def calculate_attendance_percentage(student_id):
    record = get_attendance(student_id)
    if not record:
        return None
    total, attended = record
    if total == 0:
        return 0.0
    return round((attended / total) * 100, 2)


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    setup_database()
    print("Database setup complete.")