import tkinter as tk
from tkinter import messagebox
import sqlite3

DB_NAME = "student_portal.db"

# Stores attendance percentage by roll number and subject during runtime
global_attendance = {}


# ── Database Setup ────────────────────────────────────────────────────

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS students (
                roll_number TEXT PRIMARY KEY,
                name TEXT NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS marks (
                roll_number TEXT NOT NULL,
                subject TEXT NOT NULL,
                internal REAL NOT NULL,
                external REAL NOT NULL,
                PRIMARY KEY (roll_number, subject)
            )
        """)
        conn.commit()
    finally:
        conn.close()


# ── Core Logic ────────────────────────────────────────────────────────

def calculate_percentage(total, maximum):
    return round((total / maximum) * 100, 2) if maximum else 0.0


def calculate_attendance_pct(total_classes, attended):
    return round((attended / total_classes) * 100, 2) if total_classes else 0.0


def attendance_marks(att_pct):
    if att_pct >= 90:
        return 10
    if att_pct >= 85:
        return 9
    if att_pct >= 80:
        return 8
    if att_pct >= 75:
        return 7
    return 0


def get_all_fail_reasons(subject_marks, attendance_data):
    failures = []

    for subject, (internal, external) in subject_marks.items():
        att_pct = attendance_data.get(subject)

        if att_pct is not None and att_pct < 75:
            failures.append(f"{subject} - Attendance")

        if internal <= 20:
            failures.append(f"{subject} - Internal")

        if external <= 20:
            failures.append(f"{subject} - External")

    return failures


def calculate_cgpa(pct):
    if pct > 85:
        return 10
    if pct > 75:
        return 9
    if pct > 65:
        return 8
    if pct > 50:
        return 6
    if pct > 40:
        return 4
    return 0


# ── Database Helpers ──────────────────────────────────────────────────

def save_student(roll, name):
    conn = sqlite3.connect(DB_NAME)
    try:
        c = conn.cursor()
        c.execute(
            "INSERT OR REPLACE INTO students (roll_number, name) VALUES (?, ?)",
            (roll, name)
        )
        conn.commit()
    finally:
        conn.close()


def get_student_name(roll):
    conn = sqlite3.connect(DB_NAME)
    try:
        c = conn.cursor()
        c.execute("SELECT name FROM students WHERE roll_number = ?", (roll,))
        row = c.fetchone()
        return row[0] if row else "N/A"
    finally:
        conn.close()


def save_marks(roll, subject_marks):
    conn = sqlite3.connect(DB_NAME)
    try:
        c = conn.cursor()
        for subject, (internal, external) in subject_marks.items():
            c.execute(
                """
                INSERT OR REPLACE INTO marks (roll_number, subject, internal, external)
                VALUES (?, ?, ?, ?)
                """,
                (roll, subject, internal, external)
            )
        conn.commit()
    finally:
        conn.close()


def fetch_marks(roll):
    conn = sqlite3.connect(DB_NAME)
    try:
        c = conn.cursor()
        c.execute(
            "SELECT subject, internal, external FROM marks WHERE roll_number = ?",
            (roll,)
        )
        rows = c.fetchall()
        return {row[0]: (row[1], row[2]) for row in rows}
    finally:
        conn.close()


# ── Enter Marks Screen ────────────────────────────────────────────────

def open_enter_marks_screen(parent):
    win = tk.Toplevel(parent)
    win.title("Enter Marks")
    win.geometry("900x700")
    win.configure(bg="#add8e6")

    tk.Label(
        win,
        text="Enter Marks",
        font=("Arial", 16, "bold"),
        bg="#2c3e50",
        fg="white"
    ).pack(fill="x", ipady=10)

    top_frame = tk.Frame(win, bg="#add8e6")
    top_frame.pack(pady=10)

    tk.Label(top_frame, text="Roll Number:", bg="#add8e6").grid(row=0, column=0, padx=5, pady=5)
    roll_entry = tk.Entry(top_frame)
    roll_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(top_frame, text="Student Name:", bg="#add8e6").grid(row=0, column=2, padx=5, pady=5)
    name_entry = tk.Entry(top_frame)
    name_entry.grid(row=0, column=3, padx=5, pady=5)

    subjects = [
        "Business/Economics",
        "Data Structures and Algorithms",
        "Digital System Design",
        "Maths",
        "Python"
    ]

    main_frame = tk.Frame(win, bg="#add8e6")
    main_frame.pack(padx=10, pady=10)

    entries = {}
    attendance_entries = {}

    def create_subject_block(frame, subject, start_row):
        tk.Label(frame, text=subject, font=("Arial", 11, "bold"), bg="#add8e6").grid(
            row=start_row, column=0, pady=5
        )
        row = start_row + 1

        parts = [
            ("Mid Sem 1 (15)", 15),
            ("Mid Sem 2 (15)", 15),
            ("Teacher Assessment (10)", 10),
            ("End Sem (50)", 50)
        ]

        part_entries = []

        for part_label, _ in parts:
            tk.Label(frame, text=part_label, bg="#add8e6").grid(row=row, column=0, sticky="w")
            entry = tk.Entry(frame, width=10)
            entry.grid(row=row, column=1, padx=5, pady=2)
            part_entries.append(entry)
            row += 1

        tk.Label(frame, text="Total Classes", bg="#add8e6").grid(row=row, column=0, sticky="w")
        total_cls = tk.Entry(frame, width=10)
        total_cls.grid(row=row, column=1, padx=5, pady=2)
        row += 1

        tk.Label(frame, text="Attended", bg="#add8e6").grid(row=row, column=0, sticky="w")
        attended = tk.Entry(frame, width=10)
        attended.grid(row=row, column=1, padx=5, pady=2)

        entries[subject] = part_entries
        attendance_entries[subject] = (total_cls, attended)

        return row + 1

    col1 = tk.Frame(main_frame, bg="#add8e6")
    col2 = tk.Frame(main_frame, bg="#add8e6")
    col3 = tk.Frame(main_frame, bg="#add8e6")

    col1.grid(row=0, column=0, padx=10, sticky="n")
    col2.grid(row=0, column=1, padx=10, sticky="n")
    col3.grid(row=0, column=2, padx=10, sticky="n")

    row = 0
    for subject in subjects[:2]:
        row = create_subject_block(col1, subject, row)

    row = 0
    for subject in subjects[2:3]:
        row = create_subject_block(col2, subject, row)

    row = 0
    for subject in subjects[3:]:
        row = create_subject_block(col3, subject, row)

    def submit():
        roll = roll_entry.get().strip()
        name = name_entry.get().strip()

        if not roll or not name:
            messagebox.showerror("Error", "Enter roll number and name.")
            return

        subject_totals = {}
        attendance_data = {}

        for subject in subjects:
            try:
                mid1 = float(entries[subject][0].get().strip())
                mid2 = float(entries[subject][1].get().strip())
                teacher_assessment = float(entries[subject][2].get().strip())
                end_sem = float(entries[subject][3].get().strip())

                total_classes = int(attendance_entries[subject][0].get().strip())
                attended = int(attendance_entries[subject][1].get().strip())

                if not (0 <= mid1 <= 15 and 0 <= mid2 <= 15 and 0 <= teacher_assessment <= 10 and 0 <= end_sem <= 50):
                    messagebox.showerror("Error", f"Marks out of range in {subject}.")
                    return

                if total_classes < 0 or attended < 0 or attended > total_classes:
                    messagebox.showerror("Error", f"Invalid attendance in {subject}.")
                    return

                att_pct = calculate_attendance_pct(total_classes, attended)
                att_bonus = attendance_marks(att_pct)

                internal = mid1 + mid2 + teacher_assessment + att_bonus
                external = end_sem

                subject_totals[subject] = (internal, external)
                attendance_data[subject] = att_pct

            except ValueError:
                messagebox.showerror("Error", f"Invalid input in {subject}.")
                return

        global global_attendance
        global_attendance[roll] = attendance_data

        save_student(roll, name)
        save_marks(roll, subject_totals)

        messagebox.showinfo("Success", f"Data saved for roll number {roll}.")
        win.destroy()

    tk.Button(win, text="Save", bg="green", fg="white", command=submit).pack(pady=10)


# ── View Result Screen ────────────────────────────────────────────────

def open_result_screen(parent):
    win = tk.Toplevel(parent)
    win.title("Result")
    win.geometry("500x520")
    win.configure(bg="#ffcccb")

    tk.Label(win, text="Roll No", bg="#ffcccb").pack(pady=(10, 0))
    roll_entry = tk.Entry(win)
    roll_entry.pack(pady=5)

    out = tk.Text(win, width=58, height=24)
    out.pack(padx=10, pady=10)

    def show():
        roll = roll_entry.get().strip()
        if not roll:
            messagebox.showerror("Error", "Enter a roll number.")
            return

        subject_marks = fetch_marks(roll)

        if not subject_marks:
            messagebox.showerror("Error", "No data found.")
            return

        name = get_student_name(roll)
        attendance_data = global_attendance.get(roll, {})

        total = sum(internal + external for internal, external in subject_marks.values())
        maximum = len(subject_marks) * 100
        pct = calculate_percentage(total, maximum)

        failures = get_all_fail_reasons(subject_marks, attendance_data)

        text = f"Roll: {roll}\nName: {name}\n\n"

        for subject, (internal, external) in subject_marks.items():
            text += f"{subject}:\n"
            text += f"Internal: {internal}/50\n"
            text += f"External: {external}/50\n"
            if subject in attendance_data:
                text += f"Attendance: {attendance_data[subject]}%\n"
            text += "\n"

        text += f"Total: {total}/{maximum}\n"
        text += f"Percentage: {pct}%\n"

        if not failures:
            cgpa = calculate_cgpa(pct)
            text += f"Final Result: PASS\nCGPA = {cgpa}"
        else:
            fail_text = ", ".join(failures)
            text += f"Final Result: Re({fail_text})"

        out.delete("1.0", tk.END)
        out.insert(tk.END, text)

    tk.Button(win, text="Show", command=show).pack(pady=(0, 10))


# ── Main ──────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    root.title("Data Storing and Result Generation")
    root.geometry("300x200")
    root.configure(bg="#90ee90")

    setup_database()

    tk.Button(root, text="Enter Marks", command=lambda: open_enter_marks_screen(root)).pack(pady=10)
    tk.Button(root, text="View Result", command=lambda: open_result_screen(root)).pack(pady=10)

    root.mainloop()


if __name__ == "__main__":
    main()
