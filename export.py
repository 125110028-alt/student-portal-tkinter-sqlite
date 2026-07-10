import tkinter as tk
from tkinter import messagebox
import csv
import sqlite3
import os

DB_NAME = "student_portal.db"
EXPORT_FILE = "student_results.csv"


# Saves student data to a CSV file
def export_to_csv(data, filename=EXPORT_FILE):
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(
            ["Name", "Roll No", "Course", "Subject", "Marks", "Total", "Percentage", "Grade"]
        )
        writer.writerows(data)

    return filename


# Returns grade letter based on percentage
def get_grade(percentage):
    if percentage >= 90:
        return "A+"
    if percentage >= 75:
        return "A"
    if percentage >= 60:
        return "B"
    if percentage >= 45:
        return "C"
    return "F"


# Export dummy data if database is not available
def export_dummy_data():
    dummy = [
        ["Raunak", "101", "BCA", "Maths, Science, English", "85, 90, 78", 253, 84.33, "A"],
        ["Divyanshu", "102", "BCA", "Maths, Science, English", "70, 88, 92", 250, 83.33, "A"],
        ["Tanvi", "103", "BCA", "Maths, Science, English", "95, 82, 88", 265, 88.33, "A"],
        ["Sahil", "104", "BCA", "Maths, Science, English", "60, 75, 70", 205, 68.33, "B"],
        ["Nupur", "105", "BCA", "Maths, Science, English", "88, 91, 85", 264, 88.00, "A"],
        ["Kshitiz", "106", "BCA", "Maths, Science, English", "77, 80, 83", 240, 80.00, "A"],
    ]
    return export_to_csv(dummy)


# Fetches real student data from SQLite DB and exports to CSV
def export_real_data():
    if not os.path.exists(DB_NAME):
        return export_dummy_data()

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT s.name, s.roll_no, s.course, m.subject, m.marks
            FROM students s
            LEFT JOIN marks m ON s.id = m.student_id
            ORDER BY s.roll_no, m.subject
        """)
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            return export_dummy_data()

        student_data = {}

        for name, roll_no, course, subject, marks in rows:
            key = (name, roll_no, course)

            if key not in student_data:
                student_data[key] = []

            if subject is not None and marks is not None:
                student_data[key].append((subject, marks))

        processed = []

        for (name, roll_no, course), marks_list in student_data.items():
            if marks_list:
                subjects = ", ".join(subject for subject, _ in marks_list)
                marks_text = ", ".join(str(mark) for _, mark in marks_list)
                total = sum(mark for _, mark in marks_list)
                percentage = round(total / len(marks_list), 2)
                grade = get_grade(percentage)
            else:
                subjects = "No subjects"
                marks_text = "No marks"
                total = 0
                percentage = 0
                grade = "F"

            processed.append(
                [name, roll_no, course, subjects, marks_text, total, percentage, grade]
            )

        return export_to_csv(processed)

    except Exception as e:
        print(f"Database error: {e}")
        return None


# Checks if all required modules and the database file are working
def run_integration_check():
    print("\n--- Integration Check ---")

    try:
        import csv
        print("[OK] csv")
    except Exception:
        print("[FAIL] csv")

    try:
        import sqlite3
        print("[OK] sqlite3")
    except Exception:
        print("[FAIL] sqlite3")

    try:
        import tkinter
        print("[OK] tkinter")
    except Exception:
        print("[FAIL] tkinter")

    if os.path.exists(DB_NAME):
        print(f"[OK] {DB_NAME} found")
    else:
        print(f"[WARN] {DB_NAME} not found")

    print("--- Done ---\n")


# Main UI window
def launch_export_ui():
    root = tk.Tk()
    root.title("Student Portal - Export Panel")
    root.configure(bg="#1e1e2e")
    root.geometry("900x600")
    root.resizable(True, True)

    BG = "#1e1e2e"
    CARD = "#2a2a3e"
    GREEN = "#4ade80"
    BLUE = "#60a5fa"
    RED = "#f87171"
    YELLOW = "#facc15"
    TEXT = "#e2e8f0"
    MUTED = "#94a3b8"

    tk.Label(
        root,
        text="Student Portal",
        bg=BG,
        fg=TEXT,
        font=("Courier New", 28, "bold")
    ).pack(pady=(50, 4))

    tk.Label(
        root,
        text="Export & Integration Panel",
        bg=BG,
        fg=MUTED,
        font=("Courier New", 13)
    ).pack(pady=(0, 30))

    status_var = tk.StringVar(value="Ready.")
    tk.Label(
        root,
        textvariable=status_var,
        bg=CARD,
        fg=GREEN,
        font=("Courier New", 13),
        width=60,
        pady=12
    ).pack(pady=(0, 30), padx=40)

    def make_button(parent, text, color, command):
        return tk.Button(
            parent,
            text=text,
            bg=color,
            fg="#0f172a",
            font=("Courier New", 14, "bold"),
            padx=30,
            pady=16,
            relief="flat",
            cursor="hand2",
            activebackground=color,
            command=command
        )

    def btn_export_dummy():
        file_path = export_dummy_data()
        status_var.set(f"Exported dummy data -> {file_path}")
        messagebox.showinfo("Done", f"CSV saved as:\n{file_path}")

    def btn_export_real():
        file_path = export_real_data()
        if file_path:
            status_var.set(f"Exported data -> {file_path}")
            messagebox.showinfo("Done", f"CSV saved as:\n{file_path}")
        else:
            status_var.set("Export failed. Check database.")
            messagebox.showerror("Error", "Export failed. Check database.")

    def btn_check():
        run_integration_check()
        status_var.set("Integration check done. See terminal.")
        messagebox.showinfo("Done", "Integration check completed.\nSee terminal for details.")

    def btn_clear():
        if os.path.exists(EXPORT_FILE):
            os.remove(EXPORT_FILE)
            status_var.set("Old CSV deleted.")
            messagebox.showinfo("Cleared", f"{EXPORT_FILE} deleted.")
        else:
            status_var.set("No CSV file found.")
            messagebox.showinfo("Info", "No CSV file to delete.")

    frame = tk.Frame(root, bg=BG)
    frame.pack(padx=30, pady=20)

    make_button(frame, "Export Dummy Data", GREEN, btn_export_dummy).grid(
        row=0, column=0, padx=20, pady=20
    )
    make_button(frame, "Export Real DB Data", BLUE, btn_export_real).grid(
        row=0, column=1, padx=20, pady=20
    )
    make_button(frame, "Run Integration Check", YELLOW, btn_check).grid(
        row=1, column=0, padx=20, pady=20
    )
    make_button(frame, "Clear Old CSV", RED, btn_clear).grid(
        row=1, column=1, padx=20, pady=20
    )

    tk.Label(
        root,
        text="Run the full project with: python main.py",
        bg=BG,
        fg=MUTED,
        font=("Courier New", 11)
    ).pack(pady=(30, 10))

    root.mainloop()


if __name__ == "__main__":
    run_integration_check()
    launch_export_ui()
