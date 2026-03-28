import sqlite3

DB_NAME = "student_portal.db"


def connect_db():
    return sqlite3.connect(DB_NAME)


def create_tables():
    conn = connect_db()
    cursor = conn.cursor()

    # USERS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # STUDENTS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        roll_no TEXT UNIQUE NOT NULL,
        course TEXT NOT NULL
    )
    """)

    # MARKS TABLE
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject TEXT NOT NULL,
        marks INTEGER NOT NULL,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )
    """)

    # ATTENDANCE TABLE (IMPORTANT FIX)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        total_classes INTEGER,
        attended_classes INTEGER,
        FOREIGN KEY(student_id) REFERENCES students(id)
    )
    """)

    conn.commit()
    conn.close()
    print("Tables created successfully.")


def insert_default_admin():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username = ?", ("admin",))
    if not cursor.fetchone():
        cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, ("admin", "admin123", "admin"))
        print("Default admin created.")
    else:
        print("Admin already exists.")

    conn.commit()
    conn.close()


def insert_student(name, roll_no, course):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Insert into students table
        cursor.execute("""
        INSERT INTO students (name, roll_no, course)
        VALUES (?, ?, ?)
        """, (name, roll_no, course))

        # Insert into users table for login
        cursor.execute("""
        INSERT INTO users (username, password, role)
        VALUES (?, ?, ?)
        """, (roll_no, roll_no, "student"))

        conn.commit()
        print("Student + login created successfully")

    except sqlite3.IntegrityError:
        print("Error: Roll number already exists")

    conn.close()

def get_student_id_by_roll(roll_no):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM students WHERE roll_no = ?", (roll_no,))
    result = cursor.fetchone()

    conn.close()

    return result[0] if result else None

def fetch_student_by_roll(roll_no):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM students WHERE roll_no = ?",
        (roll_no,)
    )

    student = cursor.fetchone()
    conn.close()

    return student

def update_student(roll_no, new_name, new_course):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE students
    SET name = ?, course = ?
    WHERE roll_no = ?
    """, (new_name, new_course, roll_no))

    conn.commit()
    conn.close()

def add_attendance(student_id, total_classes, attended_classes):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO attendance (student_id, total_classes, attended_classes)
    VALUES (?, ?, ?)
    """, (student_id, total_classes, attended_classes))

    conn.commit()
    conn.close()

    print("Attendance added successfully.")

def delete_student(roll_no):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE roll_no = ?", (roll_no,))

    conn.commit()
    conn.close()


def get_attendance(student_id):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT total_classes, attended_classes
    FROM attendance
    WHERE student_id = ?
    """, (student_id,))

    record = cursor.fetchone()
    conn.close()

    return record


def calculate_attendance_percentage(student_id):
    record = get_attendance(student_id)

    if not record:
        return None

    total, attended = record

    if total == 0:
        return 0

    return (attended / total) * 100
def fetch_students():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students")
    data = cursor.fetchall()

    conn.close()
    return data

def insert_marks(student_id, subject, marks):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO marks (student_id, subject, marks)
    VALUES (?, ?, ?)
    """, (student_id, subject, marks))

    conn.commit()
    conn.close()

# ---------- RUN DATABASE FILE ---------- #
if __name__ == "__main__":
    create_tables()
    insert_default_admin()

    # Test attendance
    add_attendance(1, 50, 40)
    percent = calculate_attendance_percentage(1)
    print("Attendance %:", percent)