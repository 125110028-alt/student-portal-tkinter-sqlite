import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import sqlite3
import io
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use("TkAgg")

from PIL import Image, ImageTk

from database import (
    insert_student,
    fetch_student_by_roll,
    get_student_id_by_roll,
    get_marks_by_student,
    save_student_marks,
    get_top_rankers,
    get_pass_fail_stats,
    save_student_photo,
    get_student_photo,
)
from export import export_real_data


# ═══════════════════════════════════════════════════
#  GLOBAL STATE
# ═══════════════════════════════════════════════════

root             = None
login_root       = None
current_username = ""
current_role     = ""


# ═══════════════════════════════════════════════════
#  DATABASE INIT
# ═══════════════════════════════════════════════════

def init_db():
    conn = sqlite3.connect("student_portal.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL,
            role     TEXT    NOT NULL
        )""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            roll_no TEXT NOT NULL UNIQUE,
            course  TEXT NOT NULL,
            photo   BLOB
        )""")
    c.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject    TEXT    NOT NULL,
            marks      INTEGER NOT NULL,
            UNIQUE(student_id, subject),
            FOREIGN KEY (student_id) REFERENCES students(id)
        )""")

    # migrate old DBs that don't have the photo column
    c.execute("PRAGMA table_info(students)")
    cols = [row[1] for row in c.fetchall()]
    if "photo" not in cols:
        c.execute("ALTER TABLE students ADD COLUMN photo BLOB")

    c.execute("SELECT id FROM users WHERE username = ?", ("admin",))
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?,?,?)",
            ("admin", "admin123", "admin"),
        )
    conn.commit()
    conn.close()


# ═══════════════════════════════════════════════════
#  DESIGN TOKENS
# ═══════════════════════════════════════════════════

BG      = "#0D1117"
PANEL   = "#161B22"
CARD    = "#21262D"
BORDER  = "#30363D"
ACCENT  = "#58A6FF"
ACCENT2 = "#3FB950"
WARN    = "#D29922"
DANGER  = "#F85149"
TEXT    = "#E6EDF3"
SUBTEXT = "#8B949E"
HOVER   = "#1F6FEB"

FT       = ("Consolas", 11)
FT_TITLE = ("Consolas", 20, "bold")
FT_HEAD  = ("Consolas", 13, "bold")
FT_SMALL = ("Consolas", 9)
FT_MONO  = ("Consolas", 10)


# ═══════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════

def _center(win, w, h):
    win.update_idletasks()
    sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
    safe_h = min(h, sh - 80)
    win.geometry(f"{w}x{safe_h}+{(sw-w)//2}+{(sh-safe_h)//2}")


def _sep(parent, color=BORDER):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", pady=6)


def _card(parent, **kw):
    return tk.Frame(parent, bg=CARD,
                    highlightbackground=BORDER,
                    highlightthickness=1, **kw)


def btn(parent, text, cmd, color=ACCENT, fg=BG, w=18, pad=8):
    b = tk.Button(parent, text=text, command=cmd,
                  bg=color, fg=fg, font=FT, relief="flat",
                  cursor="hand2", width=w, pady=pad, bd=0,
                  activebackground=HOVER, activeforeground=TEXT)
    b.bind("<Enter>", lambda e: b.config(bg=_darken(color)))
    b.bind("<Leave>", lambda e: b.config(bg=color))
    return b


def _darken(hex_color):
    try:
        r  = max(0, int(hex_color[1:3], 16) - 30)
        g  = max(0, int(hex_color[3:5], 16) - 30)
        b_ = max(0, int(hex_color[5:7], 16) - 30)
        return f"#{r:02x}{g:02x}{b_:02x}"
    except Exception:
        return hex_color


def _label(parent, text="", font=FT, fg=TEXT, bg=None, **kw):
    return tk.Label(parent, text=text, font=font, fg=fg,
                    bg=bg or parent.cget("bg"), **kw)


def _entry(parent, show=None, w=28):
    return tk.Entry(parent, show=show, width=w, font=FT,
                    bg=BG, fg=TEXT, insertbackground=ACCENT,
                    relief="flat", bd=6,
                    highlightthickness=1,
                    highlightbackground=BORDER,
                    highlightcolor=ACCENT)


def _modal(title, w, h):
    win = tk.Toplevel(root)
    win.title(title)
    win.configure(bg=BG)
    win.resizable(False, False)
    win.grab_set()
    _center(win, w, h)
    return win


# ═══════════════════════════════════════════════════
#  PHOTO HELPER
# ═══════════════════════════════════════════════════

def _photo_widget(parent, roll_no, size=(100, 120), bg=CARD):
    """
    Return a Label showing the student photo.
    Falls back to a placeholder if no photo is stored.
    """
    lbl = tk.Label(parent, bg=bg)
    try:
        raw = get_student_photo(roll_no)
        if raw:
            img   = Image.open(io.BytesIO(raw)).resize(size, Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            lbl.config(image=photo)
            lbl._photo = photo          # keep reference — prevents GC
        else:
            raise ValueError("no photo")
    except Exception:
        lbl.config(text="📷\nNo Photo", fg=SUBTEXT, font=FT_SMALL,
                   width=10, height=5,
                   highlightbackground=BORDER, highlightthickness=1)
    return lbl


# ═══════════════════════════════════════════════════
#  TOAST NOTIFICATIONS
# ═══════════════════════════════════════════════════

def toast(message, kind="info"):
    colors = {"info": ACCENT, "success": ACCENT2, "error": DANGER, "warn": WARN}
    color  = colors.get(kind, ACCENT)
    t = tk.Toplevel(root)
    t.overrideredirect(True)
    t.attributes("-topmost", True)
    t.configure(bg=CARD)
    tk.Frame(t, bg=color, width=4).pack(side="left", fill="y")
    tk.Label(t, text=message, font=FT_SMALL, bg=CARD, fg=TEXT,
             padx=14, pady=10).pack(side="left")
    root.update_idletasks()
    rx = root.winfo_x() + root.winfo_width()  - 340
    ry = root.winfo_y() + root.winfo_height() - 70
    t.geometry(f"320x42+{rx}+{ry}")
    t.after(3000, t.destroy)


# ═══════════════════════════════════════════════════
#  LIVE STATS
# ═══════════════════════════════════════════════════

def _get_live_stats():
    try:
        conn = sqlite3.connect("student_portal.db")
        c    = conn.cursor()
        c.execute("SELECT COUNT(*) FROM students")
        stu = c.fetchone()[0]
        c.execute("SELECT COUNT(DISTINCT subject) FROM marks")
        sub = c.fetchone()[0]
        passed, failed = get_pass_fail_stats()
        total = passed + failed
        rate  = f"{round(passed/total*100)}%" if total else "—"
        conn.close()
        return stu, sub, rate
    except Exception:
        return "—", "—", "—"


# ═══════════════════════════════════════════════════
#  MODAL — ADD STUDENT  (with photo upload)
# ═══════════════════════════════════════════════════

def open_add_student(refresh_cb=None):
    win = _modal("Add New Student", 460, 420)

    # ── buttons pinned to bottom FIRST ──
    btn_f = tk.Frame(win, bg=BG)
    btn_f.pack(side="bottom", pady=12)

    # ── header ──
    _label(win, "ADD STUDENT", font=FT_HEAD, fg=ACCENT, bg=BG).pack(pady=(14, 4))
    _sep(win)

    # ── body: photo left | form right ──
    body = tk.Frame(win, bg=BG)
    body.pack(padx=20, pady=6, fill="x")

    # --- Photo column ---
    photo_col = tk.Frame(body, bg=BG)
    photo_col.pack(side="left", padx=(0, 18), anchor="n", pady=4)

    photo_path_var = tk.StringVar(value="")
    photo_box = tk.Label(photo_col, text="📷\nNo Photo",
                         fg=SUBTEXT, bg=CARD, font=FT_SMALL,
                         width=11, height=6,
                         highlightbackground=BORDER,
                         highlightthickness=1)
    photo_box.pack()

    def pick_photo():
        path = filedialog.askopenfilename(
            parent=win,
            title="Select Student Photo",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if not path:
            return
        try:
            img   = Image.open(path).resize((88, 100), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            photo_box.config(image=photo, text="", width=88, height=100)
            photo_box._photo = photo
            photo_path_var.set(path)
            status.config(text="")
        except Exception as e:
            status.config(text=f"✕ Image error: {e}")

    tk.Button(photo_col, text="📁 Upload Photo",
              bg=CARD, fg=SUBTEXT, font=FT_SMALL,
              relief="flat", cursor="hand2", bd=0,
              command=pick_photo).pack(pady=(6, 0))

    # --- Form column ---
    form = tk.Frame(body, bg=BG)
    form.pack(side="left", fill="x", expand=True)

    fields = {}
    for lbl_text in ("Full Name", "Roll Number", "Course"):
        _label(form, lbl_text, fg=SUBTEXT, bg=BG).pack(anchor="w", pady=(8, 2))
        e = _entry(form, w=22)
        e.pack(fill="x")
        fields[lbl_text] = e

    fields["Full Name"].focus_set()

    status = _label(win, "", fg=DANGER, bg=BG)
    status.pack(pady=(4, 0))

    def save():
        name   = fields["Full Name"].get().strip()
        roll   = fields["Roll Number"].get().strip()
        course = fields["Course"].get().strip()

        if not all([name, roll, course]):
            status.config(text="⚠ All fields are required.")
            return
        try:
            insert_student(name, roll, course)

            # save photo if one was picked
            path = photo_path_var.get()
            if path and os.path.exists(path):
                save_student_photo(roll, path)

            if refresh_cb:
                refresh_cb()
            toast(f"Student '{name}' added successfully.", "success")
            win.destroy()
        except Exception as e:
            status.config(text=f"✕ {e}")

    btn(btn_f, "  Save Student", save, color=ACCENT2, fg=BG, w=20).pack(
        side="left", padx=6)
    btn(btn_f, "  Cancel", win.destroy, color=CARD, fg=TEXT, w=10).pack(
        side="left")

    win.bind("<Return>", lambda event: save())


# ═══════════════════════════════════════════════════
#  MODAL — ADD / UPDATE MARKS
# ═══════════════════════════════════════════════════

SUBJECTS = ["Mathematics", "Science", "English", "Computer Science", "History"]


def open_add_marks(refresh_cb=None):
    win = _modal("Add / Update Marks", 440, 500)

    # ── buttons pinned to bottom FIRST ──
    btn_f = tk.Frame(win, bg=BG)
    btn_f.pack(side="bottom", pady=10)

    # ── scrollable canvas for the form ──
    canvas    = tk.Canvas(win, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    form = tk.Frame(canvas, bg=BG)
    form_id = canvas.create_window((0, 0), window=form, anchor="nw")

    def _on_canvas_resize(event):
        canvas.itemconfig(form_id, width=event.width)

    def _on_frame_resize(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>",  _on_canvas_resize)
    form.bind("<Configure>",    _on_frame_resize)

    def _mousewheel(event):
        canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    canvas.bind_all("<MouseWheel>", _mousewheel)

    # ── form content ──
    _label(form, "ADD / UPDATE MARKS", font=FT_HEAD,
           fg=ACCENT, bg=BG).pack(pady=(14, 4))
    tk.Frame(form, bg=BORDER, height=1).pack(fill="x", pady=6)

    _label(form, "Roll Number", fg=SUBTEXT, bg=BG).pack(
        anchor="w", padx=30, pady=(4, 2))
    roll_e = _entry(form)
    roll_e.pack(fill="x", padx=30)
    roll_e.focus_set()

    subject_entries = {}
    for subj in SUBJECTS:
        row = tk.Frame(form, bg=BG)
        row.pack(fill="x", padx=30, pady=(5, 0))
        _label(row, subj, fg=SUBTEXT, bg=BG, width=22, anchor="w").pack(side="left")
        e = _entry(row, w=8)
        e.pack(side="left", padx=(6, 0))
        subject_entries[subj] = e

    status = _label(form, "", fg=DANGER, bg=BG)
    status.pack(pady=(8, 10))

    def save():
        roll = roll_e.get().strip()
        if not roll:
            status.config(text="⚠ Enter a roll number.")
            return
        try:
            student_id = get_student_id_by_roll(roll)
            if not student_id:
                status.config(text="✕ Student not found.")
                return

            subject_marks = {}
            for subj, entry in subject_entries.items():
                val = entry.get().strip()
                if not val:
                    continue
                try:
                    m = int(val)
                except ValueError:
                    status.config(text=f"✕ {subj}: enter a whole number.")
                    return
                if not (0 <= m <= 100):
                    status.config(text=f"✕ {subj}: must be 0–100.")
                    return
                subject_marks[subj] = m

            if not subject_marks:
                status.config(text="⚠ Enter at least one subject's marks.")
                return

            save_student_marks(student_id, subject_marks)
            canvas.unbind_all("<MouseWheel>")
            if refresh_cb:
                refresh_cb()
            toast("Marks saved successfully.", "success")
            win.destroy()
        except Exception as e:
            status.config(text=f"✕ {e}")

    def on_close():
        canvas.unbind_all("<MouseWheel>")
        win.destroy()

    win.protocol("WM_DELETE_WINDOW", on_close)

    btn(btn_f, "  Save Marks", save, color=ACCENT2, fg=BG, w=18).pack(
        side="left", padx=6)
    btn(btn_f, "  Cancel", on_close, color=CARD, fg=TEXT, w=10).pack(side="left")

    win.bind("<Return>", lambda event: save())


# ═══════════════════════════════════════════════════
#  MODAL — SEARCH STUDENT
# ═══════════════════════════════════════════════════

def search_student():
    win = _modal("Search Student", 460, 360)

    # ── buttons pinned to bottom FIRST ──
    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(side="bottom", pady=12)

    _label(win, "SEARCH STUDENT", font=FT_HEAD, fg=ACCENT, bg=BG).pack(pady=(16, 4))
    _sep(win)

    row = tk.Frame(win, bg=BG)
    row.pack(padx=30, pady=(8, 4), fill="x")
    _label(row, "Roll Number", fg=SUBTEXT, bg=BG).pack(anchor="w", pady=(0, 4))
    roll_e = _entry(row)
    roll_e.pack(fill="x")
    roll_e.focus_set()

    # result area: photo + info side by side
    result_outer = _card(win, padx=12, pady=10)
    result_outer.pack(padx=30, pady=(6, 4), fill="x")

    photo_lbl = tk.Label(result_outer, text="📷", fg=SUBTEXT, bg=CARD,
                          font=("Consolas", 22), width=6)
    photo_lbl.pack(side="left", padx=(0, 10))

    info_var = tk.StringVar(value="  Enter a roll number and press Search.")
    tk.Label(result_outer, textvariable=info_var, fg=TEXT, font=FT_MONO,
             bg=CARD, justify="left").pack(side="left", anchor="w")

    def search():
        roll = roll_e.get().strip()
        if not roll:
            info_var.set("  ⚠ Enter a roll number.")
            return
        try:
            student = fetch_student_by_roll(roll)
        except Exception as e:
            info_var.set(f"  ✕ Error: {e}")
            return

        if student:
            info_var.set(
                f"  Name    :  {student[1]}\n"
                f"  Roll No :  {student[2]}\n"
                f"  Course  :  {student[3]}"
            )
            # show photo
            try:
                raw = get_student_photo(roll)
                if raw:
                    img   = Image.open(io.BytesIO(raw)).resize((60, 72), Image.LANCZOS)
                    ph    = ImageTk.PhotoImage(img)
                    photo_lbl.config(image=ph, text="", width=60, height=72)
                    photo_lbl._photo = ph
                else:
                    photo_lbl.config(image="", text="📷", width=6, height=3)
            except Exception:
                photo_lbl.config(image="", text="📷", width=6, height=3)
        else:
            info_var.set("  No student found with that roll number.")
            photo_lbl.config(image="", text="📷", width=6, height=3)

    btn(btn_row, "  Search", search, w=14).pack(side="left", padx=6)
    btn(btn_row, "  Close", win.destroy, color=CARD, fg=TEXT, w=10).pack(side="left")

    win.bind("<Return>", lambda event: search())


# ═══════════════════════════════════════════════════
#  MODAL — MARKSHEET  (with photo)
# ═══════════════════════════════════════════════════

def view_marksheet(prefill_roll=None):
    win = _modal("Student Marksheet", 500, 500)

    # ── buttons pinned to bottom FIRST ──
    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(side="bottom", pady=8)

    _label(win, "MARKSHEET", font=FT_HEAD, fg=ACCENT, bg=BG).pack(pady=(14, 4))
    _sep(win)

    row = tk.Frame(win, bg=BG)
    row.pack(padx=30, pady=(4, 4), fill="x")
    _label(row, "Roll Number", fg=SUBTEXT, bg=BG).pack(anchor="w", pady=(0, 4))
    roll_e = _entry(row)
    roll_e.pack(fill="x")
    if prefill_roll:
        roll_e.insert(0, prefill_roll)
    roll_e.focus_set()

    # photo strip above the text area
    photo_strip = tk.Frame(win, bg=BG)
    photo_strip.pack(padx=30, pady=(0, 4), fill="x")

    sheet_frame = _card(win, padx=12, pady=10)
    sheet_frame.pack(padx=30, pady=(0, 4), fill="both", expand=True)

    sb  = tk.Scrollbar(sheet_frame)
    sb.pack(side="right", fill="y")
    txt = tk.Text(sheet_frame, font=FT_MONO, bg=PANEL, fg=TEXT,
                  relief="flat", bd=0, yscrollcommand=sb.set,
                  state="disabled", height=10)
    txt.pack(fill="both", expand=True)
    sb.config(command=txt.yview)

    txt.tag_config("header", foreground=ACCENT,  font=("Consolas", 11, "bold"))
    txt.tag_config("pass",   foreground=ACCENT2)
    txt.tag_config("fail",   foreground=DANGER)
    txt.tag_config("muted",  foreground=SUBTEXT)

    def _write(text, tag=None):
        txt.config(state="normal")
        txt.insert(tk.END, text, tag or "")
        txt.config(state="disabled")

    def show_marks():
        # clear text
        txt.config(state="normal")
        txt.delete("1.0", tk.END)
        txt.config(state="disabled")

        # clear photo strip
        for w in photo_strip.winfo_children():
            w.destroy()

        roll = roll_e.get().strip()
        if not roll:
            _write("  ⚠ Enter a roll number.", "muted")
            return
        try:
            student    = fetch_student_by_roll(roll)
            student_id = get_student_id_by_roll(roll)
        except Exception as e:
            _write(f"  Error: {e}", "fail")
            return

        if not student or not student_id:
            _write("  Student not found.", "fail")
            return

        # ── show photo in strip ──
        try:
            raw = get_student_photo(roll)
            if raw:
                img   = Image.open(io.BytesIO(raw)).resize((60, 72), Image.LANCZOS)
                ph    = ImageTk.PhotoImage(img)
                p_lbl = tk.Label(photo_strip, image=ph, bg=BG)
                p_lbl._photo = ph
                p_lbl.pack(side="left", padx=(0, 12))
            else:
                tk.Label(photo_strip, text="📷  No Photo",
                         fg=SUBTEXT, font=FT_SMALL, bg=BG).pack(side="left")
        except Exception:
            tk.Label(photo_strip, text="📷  No Photo",
                     fg=SUBTEXT, font=FT_SMALL, bg=BG).pack(side="left")

        # name / course next to photo
        info_f = tk.Frame(photo_strip, bg=BG)
        info_f.pack(side="left")
        _label(info_f, student[1], font=("Consolas", 12, "bold"),
               fg=ACCENT, bg=BG).pack(anchor="w")
        _label(info_f, f"Roll: {student[2]}  |  {student[3]}",
               fg=SUBTEXT, font=FT_SMALL, bg=BG).pack(anchor="w")

        # ── marks ──
        marks = get_marks_by_student(student_id)
        _write(f"  {'─'*38}\n", "muted")
        _write(f"  Name    :  {student[1]}\n", "header")
        _write(f"  Roll No :  {student[2]}\n")
        _write(f"  Course  :  {student[3]}\n")
        _write(f"  {'─'*38}\n", "muted")

        if not marks:
            _write("  No marks on record.\n", "muted")
            return

        total = 0
        for subject, mark in marks:
            tag   = "pass" if mark >= 40 else "fail"
            grade = _grade(mark)
            _write(f"  {subject:<22} {mark:>3}/100   {grade}\n", tag)
            total += mark

        pct        = round(total / len(marks), 1)
        result_tag = "pass" if pct >= 40 else "fail"
        result_txt = "PASS ✓" if pct >= 40 else "FAIL ✗"
        _write(f"  {'─'*38}\n", "muted")
        _write(f"  Total   : {total}\n")
        _write(f"  Average : {pct}%\n")
        _write(f"  Result  : {result_txt}\n", result_tag)

    btn(btn_row, "  Show Marksheet", show_marks, w=18).pack(side="left", padx=6)
    btn(btn_row, "  Close", win.destroy, color=CARD, fg=TEXT, w=10).pack(side="left")

    win.bind("<Return>", lambda event: show_marks())

    if prefill_roll:
        show_marks()


def _grade(mark):
    if mark >= 90: return "A+"
    if mark >= 80: return "A"
    if mark >= 70: return "B+"
    if mark >= 60: return "B"
    if mark >= 50: return "C"
    if mark >= 40: return "D"
    return "F"


# ═══════════════════════════════════════════════════
#  MODAL — TOP RANKERS
# ═══════════════════════════════════════════════════

def view_top_rankers():
    win = _modal("Top Rankers", 520, 440)

    btn(win, "  Close", win.destroy, color=CARD, fg=TEXT, w=12).pack(
        side="bottom", pady=10)

    _label(win, "🏆  TOP RANKERS", font=FT_HEAD, fg=WARN, bg=BG).pack(pady=(16, 4))
    _sep(win)

    try:
        rankers = get_top_rankers(10)
    except Exception as e:
        messagebox.showerror("Error", str(e), parent=win)
        win.destroy()
        return

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Dark.Treeview",
                    background=CARD, foreground=TEXT,
                    fieldbackground=CARD, rowheight=28, font=FT_MONO)
    style.configure("Dark.Treeview.Heading",
                    background=PANEL, foreground=ACCENT,
                    font=("Consolas", 10, "bold"), relief="flat")
    style.map("Dark.Treeview", background=[("selected", HOVER)])

    cols   = ("#", "Name", "Roll No", "Course", "Total")
    widths = [40, 160, 90, 130, 70]
    tree   = ttk.Treeview(win, columns=cols, show="headings",
                           style="Dark.Treeview", height=10)
    for col, w in zip(cols, widths):
        tree.heading(col, text=col)
        tree.column(col, width=w,
                    anchor="center" if col in ("#", "Total") else "w")

    medals = {1: "🥇", 2: "🥈", 3: "🥉"}
    for i, (name, roll, course, total) in enumerate(rankers, 1):
        tree.insert("", "end",
                    values=(medals.get(i, str(i)), name, roll, course, total))

    tree.pack(padx=20, pady=(6, 4), fill="both", expand=True)


# ═══════════════════════════════════════════════════
#  PASS / FAIL ANALYTICS
# ═══════════════════════════════════════════════════

def show_pass_percentage():
    try:
        passed, failed = get_pass_fail_stats()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    total = passed + failed
    if total == 0:
        toast("No result data available.", "warn")
        return

    win = _modal("Result Analytics", 800, 460)

    pct_pass = passed / total * 100
    pct_fail = 100 - pct_pass
    summary  = (f"Total: {total}   |   "
                f"Passed: {passed} ({pct_pass:.1f}%)   |   "
                f"Failed: {failed} ({pct_fail:.1f}%)")
    _label(win, summary, fg=SUBTEXT, font=FT_SMALL, bg=BG).pack(
        side="bottom", pady=(0, 10))

    _label(win, "RESULT ANALYTICS", font=FT_HEAD, fg=ACCENT, bg=BG).pack(pady=(14, 4))
    _sep(win)

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.4, 3.6),
                                    facecolor="#161B22")

    ax1.pie([passed, failed], labels=["Pass", "Fail"],
            autopct="%1.1f%%", startangle=90,
            colors=[ACCENT2, DANGER], explode=(0.05, 0.05),
            textprops={"color": TEXT, "fontsize": 10})
    ax1.set_title("Pass vs Fail", color=ACCENT, pad=10)
    ax1.set_facecolor(PANEL)

    bars = ax2.bar(["Passed", "Failed"], [passed, failed],
                   color=[ACCENT2, DANGER], width=0.4)
    ax2.set_facecolor(PANEL)
    ax2.tick_params(colors=TEXT)
    ax2.spines[:].set_color(BORDER)
    ax2.set_title("Student Count", color=ACCENT, pad=10)
    for bar in bars:
        ax2.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.2,
                 str(int(bar.get_height())),
                 ha="center", color=TEXT, fontsize=10)
    fig.tight_layout(pad=2)

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=16, pady=6)


# ═══════════════════════════════════════════════════
#  EXPORT
# ═══════════════════════════════════════════════════

def export_results():
    try:
        file_path = export_real_data()
        if file_path:
            toast(f"Exported → {file_path}", "success")
        else:
            toast("Export failed.", "error")
    except Exception as e:
        messagebox.showerror("Export Error", str(e))


# ═══════════════════════════════════════════════════
#  RESULT ANALYZER
# ═══════════════════════════════════════════════════

def open_result_analyzer():
    win = _modal("Result Analyzer", 660, 500)

    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(side="bottom", pady=10)

    _label(win, "RESULT ANALYZER", font=FT_HEAD, fg=ACCENT, bg=BG).pack(pady=(16, 4))
    _sep(win)

    row = tk.Frame(win, bg=BG)
    row.pack(padx=30, pady=(6, 4), fill="x")
    _label(row, "Roll Number", fg=SUBTEXT, bg=BG).pack(anchor="w", pady=(0, 4))
    roll_e = _entry(row)
    roll_e.pack(fill="x")
    roll_e.focus_set()

    chart_frame = tk.Frame(win, bg=BG)
    chart_frame.pack(fill="both", expand=True, padx=16, pady=4)

    current_canvas = [None]

    def analyze():
        roll = roll_e.get().strip()
        if not roll:
            toast("Enter a roll number.", "warn")
            return
        try:
            student    = fetch_student_by_roll(roll)
            student_id = get_student_id_by_roll(roll)
        except Exception as e:
            toast(str(e), "error")
            return
        if not student or not student_id:
            toast("Student not found.", "error")
            return

        marks = get_marks_by_student(student_id)
        if not marks:
            toast("No marks found for this student.", "warn")
            return

        subjects = [m[0] for m in marks]
        values   = [m[1] for m in marks]
        colors   = [ACCENT2 if v >= 40 else DANGER for v in values]

        if current_canvas[0]:
            current_canvas[0].get_tk_widget().destroy()

        fig, ax = plt.subplots(figsize=(6.2, 3.2), facecolor=BG)
        bars = ax.bar(subjects, values, color=colors, width=0.5)
        ax.set_facecolor(PANEL)
        ax.axhline(40, color=WARN, linewidth=1.2, linestyle="--",
                   label="Pass mark (40)")
        ax.tick_params(colors=TEXT, labelsize=9)
        ax.spines[:].set_color(BORDER)
        ax.set_ylim(0, 110)
        ax.set_title(f"{student[1]}  —  {student[3]}", color=ACCENT, pad=8)
        ax.legend(facecolor=CARD, edgecolor=BORDER, labelcolor=TEXT, fontsize=8)
        for bar, v in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width() / 2, v + 1.5,
                    str(v), ha="center", color=TEXT, fontsize=9)
        fig.tight_layout()

        c = FigureCanvasTkAgg(fig, master=chart_frame)
        c.draw()
        c.get_tk_widget().pack(fill="both", expand=True)
        current_canvas[0] = c

    btn(btn_row, "  Analyze", analyze, w=14).pack(side="left", padx=6)
    btn(btn_row, "  Close", win.destroy, color=CARD, fg=TEXT, w=10).pack(side="left")

    win.bind("<Return>", lambda event: analyze())


# ═══════════════════════════════════════════════════
#  MANAGE STUDENTS
# ═══════════════════════════════════════════════════

def open_manage_students():
    win = _modal("Manage Students", 600, 480)

    btn_row = tk.Frame(win, bg=BG)
    btn_row.pack(side="bottom", pady=8)

    _label(win, "MANAGE STUDENTS", font=FT_HEAD, fg=ACCENT, bg=BG).pack(pady=(16, 4))
    _sep(win)

    style = ttk.Style()
    style.theme_use("default")
    style.configure("Dark.Treeview",
                    background=CARD, foreground=TEXT,
                    fieldbackground=CARD, rowheight=28, font=FT_MONO)
    style.configure("Dark.Treeview.Heading",
                    background=PANEL, foreground=ACCENT,
                    font=("Consolas", 10, "bold"), relief="flat")
    style.map("Dark.Treeview", background=[("selected", HOVER)])

    cols = ("ID", "Name", "Roll No", "Course")
    tree = ttk.Treeview(win, columns=cols, show="headings",
                        style="Dark.Treeview", height=12)
    for col, w in zip(cols, [50, 190, 100, 170]):
        tree.heading(col, text=col)
        tree.column(col, width=w, anchor="w")
    tree.pack(padx=20, pady=(6, 4), fill="both", expand=True)

    def load():
        tree.delete(*tree.get_children())
        conn = sqlite3.connect("student_portal.db")
        rows = conn.execute(
            "SELECT id, name, roll_no, course FROM students ORDER BY name"
        ).fetchall()
        conn.close()
        for r in rows:
            tree.insert("", "end", values=r)

    def delete_selected():
        sel = tree.selection()
        if not sel:
            toast("Select a student to delete.", "warn")
            return
        vals = tree.item(sel[0])["values"]
        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{vals[1]}' ({vals[2]})?\nThis also removes their marks.",
            parent=win
        ):
            return
        conn = sqlite3.connect("student_portal.db")
        conn.execute("DELETE FROM marks    WHERE student_id = ?", (vals[0],))
        conn.execute("DELETE FROM students WHERE id         = ?", (vals[0],))
        conn.execute("DELETE FROM users    WHERE username   = ?", (str(vals[2]),))
        conn.commit()
        conn.close()
        toast(f"'{vals[1]}' deleted.", "warn")
        load()

    btn(btn_row, "  Refresh",
        load, w=12).pack(side="left", padx=6)
    btn(btn_row, "  Delete Selected",
        delete_selected, color=DANGER, fg=TEXT, w=18).pack(side="left", padx=6)
    btn(btn_row, "  Close",
        win.destroy, color=CARD, fg=TEXT, w=10).pack(side="left", padx=6)

    load()


# ═══════════════════════════════════════════════════
#  ADMIN DASHBOARD
# ═══════════════════════════════════════════════════

def _build_admin(frame):
    # Top bar
    topbar = tk.Frame(frame, bg=PANEL, height=52)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    tk.Frame(topbar, bg=ACCENT, width=4).pack(side="left", fill="y")
    _label(topbar, "  STUDENT PORTAL",
           font=("Consolas", 13, "bold"), fg=ACCENT, bg=PANEL).pack(
        side="left", padx=8)
    name_lbl = _label(topbar, "", fg=SUBTEXT, font=FT_SMALL, bg=PANEL)
    name_lbl.pack(side="left", padx=16)
    btn(topbar, "Logout", _logout, color=DANGER, fg=TEXT, w=10, pad=4).pack(
        side="right", padx=14, pady=10)

    # Body
    body = tk.Frame(frame, bg=BG)
    body.pack(fill="both", expand=True)

    # Sidebar
    sidebar = tk.Frame(body, bg=PANEL, width=200)
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)
    _label(sidebar, "NAVIGATION", fg=SUBTEXT, font=FT_SMALL, bg=PANEL).pack(
        pady=(20, 8), padx=16, anchor="w")
    tk.Frame(sidebar, bg=BORDER, height=1).pack(fill="x", padx=12, pady=2)

    content = tk.Frame(body, bg=BG)
    content.pack(side="left", fill="both", expand=True)

    def nav_btn(icon, text, cmd):
        f   = tk.Frame(sidebar, bg=PANEL, cursor="hand2")
        f.pack(fill="x", pady=1)
        lbl = tk.Label(f, text=f"  {icon}  {text}", font=FT_SMALL,
                       bg=PANEL, fg=TEXT, anchor="w", pady=9)
        lbl.pack(fill="x")
        for widget in (f, lbl):
            widget.bind("<Enter>",
                        lambda e, x=f, y=lbl: (x.config(bg=HOVER),  y.config(bg=HOVER)))
            widget.bind("<Leave>",
                        lambda e, x=f, y=lbl: (x.config(bg=PANEL),  y.config(bg=PANEL)))
            widget.bind("<Button-1>", lambda e: cmd())

    def refresh():
        _refresh_stats(stats_labels)

    nav_btn("＋", "Add Student",      lambda: open_add_student(refresh))
    nav_btn("✎",  "Add / Edit Marks", lambda: open_add_marks(refresh))
    nav_btn("🔍", "Search Student",   search_student)
    nav_btn("📋", "Marksheet",        view_marksheet)
    nav_btn("📊", "Result Analyzer",  open_result_analyzer)
    nav_btn("🏆", "Top Rankers",      view_top_rankers)
    nav_btn("👥", "Manage Students",  open_manage_students)
    nav_btn("📈", "Pass / Fail %",    show_pass_percentage)
    nav_btn("💾", "Export Results",   export_results)

    # Dashboard content
    _label(content, "ADMIN DASHBOARD", font=FT_TITLE,
           fg=ACCENT, bg=BG).pack(pady=(32, 4), padx=30, anchor="w")
    _label(content, "Overview of student portal activity",
           fg=SUBTEXT, font=FT_SMALL, bg=BG).pack(padx=30, anchor="w")
    _sep(content)

    stats_row    = tk.Frame(content, bg=BG)
    stats_row.pack(padx=24, pady=12, anchor="w")
    stats_labels = {}

    def stat_card(parent, title, key, color):
        c = _card(parent, padx=20, pady=14)
        c.pack(side="left", padx=8)
        val = _label(c, "—", font=("Consolas", 26, "bold"), fg=color, bg=CARD)
        val.pack()
        _label(c, title, fg=SUBTEXT, font=FT_SMALL, bg=CARD).pack()
        stats_labels[key] = val

    stat_card(stats_row, "Total Students", "students", ACCENT)
    stat_card(stats_row, "Subjects",       "subjects", WARN)
    stat_card(stats_row, "Pass Rate",      "rate",     ACCENT2)
    _refresh_stats(stats_labels)

    _sep(content)
    _label(content, "QUICK ACTIONS", fg=SUBTEXT, font=FT_SMALL, bg=BG).pack(
        padx=30, anchor="w", pady=(4, 8))
    qa = tk.Frame(content, bg=BG)
    qa.pack(padx=24, anchor="w")

    def qa_btn(text, cmd, color=ACCENT):
        btn(qa, text, cmd, color=color, w=16, pad=6).pack(side="left", padx=6)

    qa_btn("+ Add Student", lambda: open_add_student(refresh))
    qa_btn("✎ Add Marks",   lambda: open_add_marks(refresh))
    qa_btn("📊 Analyzer",   open_result_analyzer, color=WARN)
    qa_btn("💾 Export",     export_results,        color=CARD)

    return name_lbl


def _refresh_stats(labels):
    stu, sub, rate = _get_live_stats()
    labels["students"].config(text=str(stu))
    labels["subjects"].config(text=str(sub))
    labels["rate"].config(text=str(rate))


# ═══════════════════════════════════════════════════
#  STUDENT DASHBOARD  (with photo)
# ═══════════════════════════════════════════════════

def _build_student(frame):
    topbar = tk.Frame(frame, bg=PANEL, height=52)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)
    tk.Frame(topbar, bg=ACCENT2, width=4).pack(side="left", fill="y")
    _label(topbar, "  STUDENT PORTAL",
           font=("Consolas", 13, "bold"), fg=ACCENT2, bg=PANEL).pack(
        side="left", padx=8)
    name_lbl = _label(topbar, "", fg=SUBTEXT, font=FT_SMALL, bg=PANEL)
    name_lbl.pack(side="left", padx=16)
    btn(topbar, "Logout", _logout, color=DANGER, fg=TEXT, w=10, pad=4).pack(
        side="right", padx=14, pady=10)

    body = tk.Frame(frame, bg=BG)
    body.pack(fill="both", expand=True, padx=40, pady=30)

    # ── top row: title left | photo right ──
    top_row = tk.Frame(body, bg=BG)
    top_row.pack(fill="x", anchor="w")

    title_col = tk.Frame(top_row, bg=BG)
    title_col.pack(side="left", fill="x", expand=True)
    _label(title_col, "STUDENT DASHBOARD",
           font=FT_TITLE, fg=ACCENT2, bg=BG).pack(anchor="w")
    _label(title_col, "Access your academic records below.",
           fg=SUBTEXT, font=FT_SMALL, bg=BG).pack(anchor="w", pady=(4, 0))

    # photo card (top right)
    photo_card = _card(top_row, padx=6, pady=6)
    photo_card.pack(side="right", anchor="n")
    _photo_widget(photo_card, current_username,
                  size=(80, 96), bg=CARD).pack()
    _label(photo_card, current_username,
           fg=SUBTEXT, font=FT_SMALL, bg=CARD).pack(pady=(4, 0))

    _sep(body)

    tile_row = tk.Frame(body, bg=BG)
    tile_row.pack(pady=20)

    def tile(icon, title, subtitle, cmd, color):
        c = _card(tile_row, padx=20, pady=20, cursor="hand2")
        c.pack(side="left", padx=10)
        _label(c, icon,     font=("Consolas", 26),        fg=color,   bg=CARD).pack()
        _label(c, title,    font=("Consolas", 11, "bold"), fg=TEXT,    bg=CARD).pack(pady=(6, 2))
        _label(c, subtitle, font=FT_SMALL,                 fg=SUBTEXT, bg=CARD).pack()
        for w in c.winfo_children() + [c]:
            w.bind("<Button-1>", lambda e: cmd())
            w.bind("<Enter>",    lambda e: c.config(highlightbackground=color))
            w.bind("<Leave>",    lambda e: c.config(highlightbackground=BORDER))

    tile("📋", "My Marksheet",  "Subjects & grades",    view_marksheet,       ACCENT)
    tile("📊", "My Result",     "Pass / Fail status",   view_marksheet,       ACCENT2)
    tile("🏆", "Class Rankers", "Top 10 students",      view_top_rankers,     WARN)
    tile("📈", "Analytics",     "My performance chart", open_result_analyzer, ACCENT)

    return name_lbl


# ═══════════════════════════════════════════════════
#  WINDOW LIFECYCLE
# ═══════════════════════════════════════════════════

def _logout():
    global root, login_root
    if root:
        root.destroy()
        root = None
    if login_root:
        login_root.deiconify()


def _close():
    global root, login_root
    if root:
        root.destroy()
        root = None
    if login_root:
        login_root.destroy()
        login_root = None


def start_app(role, username, parent_root=None):
    global root, login_root, current_username, current_role

    login_root       = parent_root
    current_username = username
    current_role     = role

    init_db()

    root = tk.Toplevel(login_root) if login_root else tk.Tk()
    root.title("Student Portal")
    root.configure(bg=BG)
    root.resizable(True, True)
    root.protocol("WM_DELETE_WINDOW", _close)
    _center(root, 880, 580)
    root.minsize(720, 480)

    frame = tk.Frame(root, bg=BG)
    frame.pack(fill="both", expand=True)

    if role == "admin":
        lbl = _build_admin(frame)
    else:
        lbl = _build_student(frame)

    lbl.config(text=f"Logged in as  {username}")

    if not login_root:
        root.mainloop()


# ═══════════════════════════════════════════════════
#  STANDALONE TEST
# ═══════════════════════════════════════════════════

if __name__ == "__main__":
    start_app("admin", "admin")