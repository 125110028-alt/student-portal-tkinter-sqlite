import sqlite3

conn = sqlite3.connect("student_portal.db")
c = conn.cursor()

c.execute("ALTER TABLE marks RENAME TO marks_old")

c.execute("""
    CREATE TABLE marks (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject    TEXT    NOT NULL,
        marks      INTEGER NOT NULL,
        UNIQUE(student_id, subject),
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
""")

c.execute("""
    INSERT INTO marks (id, student_id, subject, marks)
    SELECT id, student_id, subject, marks FROM marks_old
""")

c.execute("DROP TABLE marks_old")
conn.commit()
conn.close()
print("Migration done.")