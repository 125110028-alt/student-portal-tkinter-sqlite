# Kshitiz - Student Portal | Role: Export + UI Styling + Integration Lead

import tkinter as tk
from tkinter import messagebox
import csv
import sqlite3
import os


# Saves student data to a CSV file
# 'data' is a list like: [["Name", maths, science, english, total, percent, grade], ...]
def export_to_csv(data):
    filename = "student_results.csv"
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Maths", "Science", "English", "Total", "Percentage", "Grade"])  # header
        for row in data:
            writer.writerow(row)
    print(f"CSV saved as '{filename}'")
    return filename


# Fetches real student data from SQLite DB and exports to CSV
# Falls back to dummy data if database doesn't exist yet
def export_real_data():
    if not os.path.exists("student_portal.db"):
        print("Database not found. Using dummy data.")
        dummy = [
            ["Raunak",    85, 90, 78, 253, 84.3, "A"],
            ["Divyanshu", 70, 88, 92, 250, 83.3, "A"],
            ["Tanvi",     95, 82, 88, 265, 88.3, "A+"],
            ["Sahil",     60, 75, 70, 205, 68.3, "B"],
            ["Nupur",     88, 91, 85, 264, 88.0, "A+"],
            ["Kshitiz",   77, 80, 83, 240, 80.0, "A"],
        ]
        return export_to_csv(dummy)

    try:
        conn = sqlite3.connect("student_portal.db")
        cursor = conn.cursor()
        # Join students and marks tables to get full data
        cursor.execute("""
            SELECT students.name, marks.maths, marks.science, marks.english
            FROM students
            JOIN marks ON students.id = marks.student_id
        """)
        rows = cursor.fetchall()
        conn.close()

        # Calculate total, percentage and grade for each student
        processed = []
        for row in rows:
            name, maths, science, english = row
            total = maths + science + english
            percentage = round(total / 3, 2)
            grade = get_grade(percentage)
            processed.append([name, maths, science, english, total, percentage, grade])

        return export_to_csv(processed)

    except Exception as e:
        print(f"Database error: {e}")
        return None


# Returns grade letter based on percentage
def get_grade(percentage):
    if percentage >= 90: return "A+"
    elif percentage >= 75: return "A"
    elif percentage >= 60: return "B"
    elif percentage >= 45: return "C"
    else: return "F"


# Checks if all required modules and the database file are working
def run_integration_check():
    print("\n--- Integration Check ---")
    try:
        import csv;     print("[OK] csv")
    except: print("[FAIL] csv")
    try:
        import sqlite3; print("[OK] sqlite3")
    except: print("[FAIL] sqlite3")
    try:
        import tkinter; print("[OK] tkinter")
    except: print("[FAIL] tkinter")
    if os.path.exists("student_portal.db"):
        print("[OK] student_portal.db found")
    else:
        print("[WARN] student_portal.db not found - Tanvi needs to create it")
    print("--- Done ---\n")


# Main UI window - styled dark theme with 4 action buttons
def launch_export_ui():
    root = tk.Tk()
    root.title("Student Portal - Kshitiz")
    root.configure(bg="#1e1e2e")
    root.attributes("-zoomed", True)  # full screen on Linux/Mac

    # Colors
    BG     = "#1e1e2e"
    CARD   = "#2a2a3e"
    GREEN  = "#4ade80"
    BLUE   = "#60a5fa"
    RED    = "#f87171"
    YELLOW = "#facc15"
    TEXT   = "#e2e8f0"
    MUTED  = "#94a3b8"

    tk.Label(root, text="📊 Student Portal", bg=BG, fg=TEXT,
             font=("Courier New", 28, "bold")).pack(pady=(60, 4))
    tk.Label(root, text="Export & Integration Panel — Kshitiz", bg=BG, fg=MUTED,
             font=("Courier New", 13)).pack(pady=(0, 30))

    # Status bar - shows what happened after each button click
    status_var = tk.StringVar(value="Ready.")
    tk.Label(root, textvariable=status_var, bg=CARD, fg=GREEN,
             font=("Courier New", 13), width=60, pady=12).pack(pady=(0, 30), padx=40)

    # Reusable function to create a styled button
    def make_button(parent, text, color, command):
        return tk.Button(parent, text=text, bg=color, fg="#0f172a",
                         font=("Courier New", 14, "bold"), padx=30, pady=16,
                         relief="flat", cursor="hand2",
                         activebackground=color, command=command)

    def btn_export_dummy():
        dummy = [
            ["Raunak",    85, 90, 78, 253, 84.3, "A"],
            ["Divyanshu", 70, 88, 92, 250, 83.3, "A"],
            ["Tanvi",     95, 82, 88, 265, 88.3, "A+"],
            ["Sahil",     60, 75, 70, 205, 68.3, "B"],
            ["Nupur",     88, 91, 85, 264, 88.0, "A+"],
            ["Kshitiz",   77, 80, 83, 240, 80.0, "A"],
        ]
        f = export_to_csv(dummy)
        status_var.set(f"Exported dummy data → {f}")
        messagebox.showinfo("Done!", f"CSV saved as:\n{f}")

    def btn_export_real():
        f = export_real_data()
        if f:
            status_var.set(f"Exported real data → {f}")
            messagebox.showinfo("Done!", f"CSV saved as:\n{f}")
        else:
            status_var.set("Export failed. Check DB.")
            messagebox.showerror("Error", "Export failed. Check database.")

    def btn_check():
        run_integration_check()
        status_var.set("Integration check done. See terminal.")
        messagebox.showinfo("Done", "Check complete!\nSee terminal for details.")

    def btn_clear():
        if os.path.exists("student_results.csv"):
            os.remove("student_results.csv")
            status_var.set("Old CSV deleted.")
            messagebox.showinfo("Cleared", "student_results.csv deleted.")
        else:
            status_var.set("No CSV file found.")
            messagebox.showinfo("Info", "No CSV file to delete.")

    # 2x2 grid of buttons
    frame = tk.Frame(root, bg=BG)
    frame.pack(padx=30)
    make_button(frame, "📁  Export (Dummy Data)",   GREEN,  btn_export_dummy).grid(row=0, column=0, padx=20, pady=20)
    make_button(frame, "🗄️  Export (Real DB Data)", BLUE,   btn_export_real ).grid(row=0, column=1, padx=20, pady=20)
    make_button(frame, "🔍  Run Integration Check", YELLOW, btn_check       ).grid(row=1, column=0, padx=20, pady=20)
    make_button(frame, "🗑️  Clear Old CSV",         RED,    btn_clear       ).grid(row=1, column=1, padx=20, pady=20)

    tk.Label(root, text="Run the full project with: python main.py",
             bg=BG, fg=MUTED, font=("Courier New", 11)).pack(pady=(40, 10))

    root.mainloop()


# Entry point - runs integration check first, then opens the UI
if __name__ == "__main__":
    run_integration_check()
    launch_export_ui()