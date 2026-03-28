import tkinter as tk
from tkinter import messagebox
import sqlite3


# ---------------- DATABASE LOGIN CHECK ---------------- #

def check_login(username, password):
    conn = sqlite3.connect("student_portal.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT role FROM users WHERE username = ? AND password = ?",
        (username, password)
    )

    result = cursor.fetchone()
    conn.close()

    return result


# ---------------- DASHBOARD ---------------- #
from student_module import open_add_student_window, view_students_window


def open_dashboard(role, root):
    dashboard = tk.Toplevel()
    dashboard.title("Dashboard")
    dashboard.geometry("400x300")
    dashboard.configure(bg="white")

    tk.Label(
        dashboard,
        text=f"Welcome {role.capitalize()}!",
        font=("Arial", 16, "bold"),
        bg="white"
    ).pack(pady=20)

    from student_module import open_add_student_window, view_students_window
    from marks_module import open_add_marks_window

    tk.Button(
    dashboard,
    text="Add Student",
    width=20,
    command=open_add_student_window
).pack(pady=10)

    tk.Button(
    dashboard,
    text="Add Marks",
    width=20,
    command=open_add_marks_window
).pack(pady=10)

    tk.Button(
        dashboard,
        text="View Students",
        width=20,
        command=view_students_window
    ).pack(pady=10)

    

    def logout():
        dashboard.destroy()
        root.deiconify()

    tk.Button(
        dashboard,
        text="Logout",
        width=20,
        command=logout
    ).pack(pady=10)
def open_student_dashboard(username, root):
    dashboard = tk.Toplevel()
    dashboard.title("Student Dashboard")
    dashboard.geometry("400x300")

    tk.Label(
        dashboard,
        text=f"Welcome Student {username}",
        font=("Arial", 14)
    ).pack(pady=20)

    from database import fetch_student_by_roll, get_attendance, calculate_attendance_percentage

    # Fetch student data
    student = fetch_student_by_roll(username)

    tk.Label(dashboard, text=f"Name: {student[1]}").pack()
    tk.Label(dashboard, text=f"Course: {student[3]}").pack()

    # Attendance
    percent = calculate_attendance_percentage(student[0])

    if percent is not None:
        tk.Label(dashboard, text=f"Attendance: {percent:.2f}%").pack()
    else:
        tk.Label(dashboard, text="Attendance: Not Available").pack()
    

    
    def logout():
        dashboard.destroy()
        root.deiconify()
    

    tk.Button(dashboard, text="Logout", command=logout).pack(pady=20)

# ---------------- LOGIN WINDOW ---------------- #

def start_login():
    root = tk.Tk()
    root.title("Student Portal Login")
    root.geometry("400x300")
    root.configure(bg="white")
    root.resizable(False, False)

    tk.Label(
        root,
        text="Student Portal Login",
        font=("Arial", 16, "bold"),
        bg="white"
    ).pack(pady=20)

    tk.Label(root, text="Username", bg="white").pack()
    username_entry = tk.Entry(root)
    username_entry.pack(pady=5)

    tk.Label(root, text="Password", bg="white").pack()
    password_entry = tk.Entry(root, show="*")
    password_entry.pack(pady=5)

    # ✅ FIXED FUNCTION
    def login_action():
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if username == "" or password == "":
            messagebox.showerror("Error", "Please fill all fields")
            return

        result = check_login(username, password)

        if not result:
            messagebox.showerror("Error", "Invalid Username or Password")
            return

        role = result[0]

        root.withdraw()

        if role == "admin":
            open_dashboard(role, root)

        elif role == "student":
            open_student_dashboard(username, root)

        else:
            messagebox.showerror("Error", "Invalid Role")

    # Button
    tk.Button(
        root,
        text="Login",
        width=15,
        command=login_action
    ).pack(pady=20)

    root.mainloop()


