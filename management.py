import tkinter as tk
from tkinter import messagebox
import sqlite3

# =============================================
#   STUDENT PORTAL - navigation.py
#   Member 2 : Divyanshu (Navigation System)
# =============================================

root = tk.Tk()
root.title("Student Portal")
root.geometry("700x500")
root.config(bg="#1e1e2e")
root.resizable(False, False)

# =============================================
#   DATABASE SETUP (basic, helps Tanvi too)
# =============================================
def init_db():
    conn = sqlite3.connect("student_portal.db")
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    """)

    # Students table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll_no TEXT,
            branch TEXT
        )
    """)

    # Marks table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            marks INTEGER
        )
    """)

    # Insert default admin if not exists
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password, role) VALUES ('admin', 'admin123', 'admin')")

    conn.commit()
    conn.close()

# =============================================
#   SHOW FRAME FUNCTION (your main job)
# =============================================
def show_frame(frame):
    # Hide all frames
    login_frame.pack_forget()
    admin_frame.pack_forget()
    student_frame.pack_forget()

    # Show the chosen frame
    frame.pack(fill="both", expand=True)

# =============================================
#   LOGIN LOGIC (connected with show_frame)
# =============================================
def handle_login():
    username = username_entry.get().strip()
    password = password_entry.get().strip()

    if username == "" or password == "":
        messagebox.showwarning("Empty Fields", "Please enter username and password!")
        return

    conn = sqlite3.connect("student_portal.db")
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        role = result[0]
        if role == "admin":
            admin_name_label.config(text=f"Welcome, {username}  (Admin)")
            show_frame(admin_frame)
        else:
            student_name_label.config(text=f"Welcome, {username}  (Student)")
            show_frame(student_frame)
        # Clear fields after login
        username_entry.delete(0, tk.END)
        password_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Login Failed", "Invalid username or password!")

def handle_logout():
    show_frame(login_frame)

# =============================================
#   COLORS & FONTS
# =============================================
BG       = "#1e1e2e"
CARD     = "#2a2a3e"
ACCENT   = "#7c3aed"
BTN_CLR  = "#7c3aed"
BTN_HOV  = "#5b21b6"
TEXT     = "#ffffff"
SUBTEXT  = "#a0a0b0"
SUCCESS  = "#22c55e"
DANGER   = "#ef4444"

FONT_TITLE  = ("Courier New", 22, "bold")
FONT_LABEL  = ("Courier New", 11)
FONT_BTN    = ("Courier New", 11, "bold")
FONT_SMALL  = ("Courier New", 9)

# Hover effect helper
def on_enter(btn, color=BTN_HOV):
    btn.config(bg=color)

def on_leave(btn, color=BTN_CLR):
    btn.config(bg=color)

def styled_button(parent, text, command, bg=BTN_CLR, fg=TEXT, width=22):
    btn = tk.Button(parent, text=text, command=command,
                    bg=bg, fg=fg, font=FONT_BTN,
                    relief="flat", cursor="hand2",
                    width=width, pady=8)
    btn.bind("<Enter>", lambda e: on_enter(btn, BTN_HOV if bg == BTN_CLR else bg))
    btn.bind("<Leave>", lambda e: on_leave(btn, bg))
    return btn

# =============================================
#   FRAME 1 — LOGIN FRAME
# =============================================
login_frame = tk.Frame(root, bg=BG)

# Title
tk.Label(login_frame, text="🎓 STUDENT PORTAL",
         font=FONT_TITLE, bg=BG, fg=ACCENT).pack(pady=(50, 5))
tk.Label(login_frame, text="Sign in to continue",
         font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack(pady=(0, 30))

# Card frame
card = tk.Frame(login_frame, bg=CARD, padx=40, pady=30)
card.pack()

# Username
tk.Label(card, text="Username", font=FONT_LABEL, bg=CARD, fg=TEXT).grid(row=0, column=0, sticky="w", pady=5)
username_entry = tk.Entry(card, font=FONT_LABEL, bg="#3a3a4e", fg=TEXT,
                          insertbackground=TEXT, relief="flat", width=28)
username_entry.grid(row=1, column=0, ipady=8, pady=(0, 15))

# Password
tk.Label(card, text="Password", font=FONT_LABEL, bg=CARD, fg=TEXT).grid(row=2, column=0, sticky="w", pady=5)
password_entry = tk.Entry(card, font=FONT_LABEL, bg="#3a3a4e", fg=TEXT,
                           insertbackground=TEXT, relief="flat", width=28, show="*")
password_entry.grid(row=3, column=0, ipady=8, pady=(0, 20))

# Login Button
login_btn = styled_button(card, "🔐  LOGIN", handle_login, width=28)
login_btn.grid(row=4, column=0, pady=5)

# Hint
tk.Label(login_frame, text="Default admin → username: admin  |  password: admin123",
         font=FONT_SMALL, bg=BG, fg=SUBTEXT).pack(pady=(15, 0))

# Enter key also triggers login
root.bind("<Return>", lambda event: handle_login())

# =============================================
#   FRAME 2 — ADMIN DASHBOARD FRAME
# =============================================
admin_frame = tk.Frame(root, bg=BG)

# Top bar
top_bar = tk.Frame(admin_frame, bg=CARD, height=55)
top_bar.pack(fill="x")
top_bar.pack_propagate(False)

admin_name_label = tk.Label(top_bar, text="Welcome, Admin",
                             font=FONT_LABEL, bg=CARD, fg=TEXT)
admin_name_label.pack(side="left", padx=20, pady=15)

logout_btn1 = styled_button(top_bar, "Logout", handle_logout, bg=DANGER, width=10)
logout_btn1.pack(side="right", padx=20, pady=10)

# Sidebar + Content layout
body = tk.Frame(admin_frame, bg=BG)
body.pack(fill="both", expand=True)

sidebar = tk.Frame(body, bg=CARD, width=180)
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

content_area = tk.Frame(body, bg=BG)
content_area.pack(side="left", fill="both", expand=True)

# Sidebar buttons
tk.Label(sidebar, text="MENU", font=FONT_SMALL, bg=CARD, fg=SUBTEXT).pack(pady=(20, 10))

def sidebar_btn(text):
    b = tk.Button(sidebar, text=text, font=FONT_SMALL,
                  bg=CARD, fg=TEXT, relief="flat",
                  cursor="hand2", width=18, pady=10,
                  command=lambda: messagebox.showinfo("Info", f"{text} - will be added by your team!"))
    b.pack(pady=3, padx=10)
    b.bind("<Enter>", lambda e: b.config(bg=ACCENT))
    b.bind("<Leave>", lambda e: b.config(bg=CARD))
    return b

sidebar_btn("👤  Add Student")
sidebar_btn("🔍  Search Student")
sidebar_btn("📋  Marksheet")
sidebar_btn("📊  Result Analyzer")
sidebar_btn("🏆  Top Rankers")
sidebar_btn("📤  Export Result")
sidebar_btn("📈  Pass %")

# Content area welcome message
tk.Label(content_area, text="ADMIN DASHBOARD",
         font=FONT_TITLE, bg=BG, fg=ACCENT).pack(pady=(60, 10))
tk.Label(content_area, text="Use the sidebar to manage the student portal.",
         font=FONT_LABEL, bg=BG, fg=SUBTEXT).pack()

# Stats row (dummy)
stats_row = tk.Frame(content_area, bg=BG)
stats_row.pack(pady=30)

def stat_card(parent, title, value, color):
    f = tk.Frame(parent, bg=CARD, width=130, height=90)
    f.pack(side="left", padx=10)
    f.pack_propagate(False)
    tk.Label(f, text=value, font=("Courier New", 22, "bold"), bg=CARD, fg=color).pack(pady=(15, 2))
    tk.Label(f, text=title, font=FONT_SMALL, bg=CARD, fg=SUBTEXT).pack()

stat_card(stats_row, "Students",  "0",    SUCCESS)
stat_card(stats_row, "Subjects",  "0",    ACCENT)
stat_card(stats_row, "Pass Rate", "0%",   "#f59e0b")

# =============================================
#   FRAME 3 — STUDENT DASHBOARD FRAME
# =============================================
student_frame = tk.Frame(root, bg=BG)

# Top bar
top_bar2 = tk.Frame(student_frame, bg=CARD, height=55)
top_bar2.pack(fill="x")
top_bar2.pack_propagate(False)

student_name_label = tk.Label(top_bar2, text="Welcome, Student",
                               font=FONT_LABEL, bg=CARD, fg=TEXT)
student_name_label.pack(side="left", padx=20, pady=15)

logout_btn2 = styled_button(top_bar2, "Logout", handle_logout, bg=DANGER, width=10)
logout_btn2.pack(side="right", padx=20, pady=10)

# Student content
tk.Label(student_frame, text="STUDENT DASHBOARD",
         font=FONT_TITLE, bg=BG, fg=SUCCESS).pack(pady=(60, 10))
tk.Label(student_frame, text="View your results and performance here.",
         font=FONT_LABEL, bg=BG, fg=SUBTEXT).pack(pady=5)

# Student quick buttons
btn_row = tk.Frame(student_frame, bg=BG)
btn_row.pack(pady=30)

def stu_btn(text):
    b = tk.Button(btn_row, text=text, font=FONT_BTN,
                  bg=CARD, fg=TEXT, relief="flat",
                  cursor="hand2", width=18, pady=12,
                  command=lambda: messagebox.showinfo("Info", f"{text} - coming soon!"))
    b.pack(side="left", padx=10)
    b.bind("<Enter>", lambda e: b.config(bg=SUCCESS))
    b.bind("<Leave>", lambda e: b.config(bg=CARD))

stu_btn("📋  My Marksheet")
stu_btn("📊  My Result")
stu_btn("🏆  Class Rankers")

# =============================================
#   START THE APP
# =============================================
init_db()          # setup database
show_frame(login_frame)   # start at login
root.mainloop()