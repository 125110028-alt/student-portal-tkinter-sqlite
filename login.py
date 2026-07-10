import tkinter as tk
from tkinter import messagebox
import management
from database import connect_db


# ---------------- DATABASE LOGIN CHECK ---------------- #

def check_login(username, password):
    conn = connect_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role FROM users WHERE username = ? AND password = ?",
            (username, password)
        )
        return cursor.fetchone()
    finally:
        conn.close()


# ---------------- STYLING CONSTANTS ---------------- #

BG_MAIN       = "#0F172A"   # deep navy
BG_CARD       = "#1E293B"   # slate card
ACCENT        = "#38BDF8"   # sky blue
ACCENT_HOVER  = "#0EA5E9"
TEXT_PRIMARY  = "#F1F5F9"
TEXT_MUTED    = "#94A3B8"
ERROR_COLOR   = "#F87171"
SUCCESS_COLOR = "#34D399"
ENTRY_BG      = "#0F172A"
BORDER_NORMAL = "#334155"
BORDER_FOCUS  = "#38BDF8"

FONT_TITLE    = ("Georgia", 22, "bold")
FONT_SUBTITLE = ("Georgia", 10, "italic")
FONT_LABEL    = ("Helvetica", 10, "bold")
FONT_ENTRY    = ("Helvetica", 11)
FONT_BUTTON   = ("Helvetica", 11, "bold")
FONT_SMALL    = ("Helvetica", 9)


# ---------------- REUSABLE WIDGETS ---------------- #

def make_entry(parent, show=None):
    """Styled entry with focus border effect."""
    frame = tk.Frame(parent, bg=BORDER_NORMAL, padx=1, pady=1)
    entry = tk.Entry(
        frame,
        show=show,
        font=FONT_ENTRY,
        bg=ENTRY_BG,
        fg=TEXT_PRIMARY,
        insertbackground=ACCENT,
        relief="flat",
        width=28,
        bd=6,
    )
    entry.pack()

    def on_focus_in(e):
        frame.config(bg=BORDER_FOCUS)

    def on_focus_out(e):
        frame.config(bg=BORDER_NORMAL)

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return frame, entry


def make_label(parent, text, font=None, color=None):
    return tk.Label(
        parent,
        text=text,
        font=font or FONT_LABEL,
        bg=BG_CARD,
        fg=color or TEXT_MUTED,
    )


def animate_button(btn, normal_bg, hover_bg):
    btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg))


# ---------------- STATUS BAR ---------------- #

class StatusBar:
    def __init__(self, parent):
        self.label = tk.Label(
            parent,
            text="",
            font=FONT_SMALL,
            bg=BG_CARD,
            fg=TEXT_MUTED,
            anchor="center",
            height=1,
        )
        self.label.pack(fill="x", pady=(0, 2))
        self._after_id = None

    def show(self, msg, color=TEXT_MUTED, auto_clear=4000):
        if self._after_id:
            self.label.after_cancel(self._after_id)
        self.label.config(text=msg, fg=color)
        if auto_clear:
            self._after_id = self.label.after(auto_clear, lambda: self.label.config(text=""))

    def clear(self):
        self.label.config(text="")


# ---------------- LOGIN WINDOW ---------------- #

def start_login():
    root = tk.Tk()
    root.title("Student Portal")
    root.geometry("460x520")
    root.configure(bg=BG_MAIN)
    root.resizable(False, False)

    # ── Center on screen ──
    root.update_idletasks()
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - 460) // 2
    y = (sh - 520) // 2
    root.geometry(f"460x520+{x}+{y}")

    # ── Outer padding frame ──
    outer = tk.Frame(root, bg=BG_MAIN)
    outer.place(relx=0.5, rely=0.5, anchor="center")

    # ── Card frame ──
    card = tk.Frame(outer, bg=BG_CARD, padx=40, pady=36)
    card.pack()

    # ── Logo / Icon row ──
    icon_frame = tk.Frame(card, bg=BG_CARD)
    icon_frame.pack(pady=(0, 6))

    icon_canvas = tk.Canvas(
        icon_frame, width=54, height=54,
        bg=BG_CARD, highlightthickness=0
    )
    icon_canvas.pack()
    # Draw a simple graduation cap icon
    icon_canvas.create_oval(4, 4, 50, 50, fill="#1D3461", outline=ACCENT, width=2)
    icon_canvas.create_polygon(27, 14, 10, 24, 27, 34, 44, 24, fill=ACCENT)
    icon_canvas.create_rectangle(38, 24, 42, 36, fill=ACCENT, outline="")
    icon_canvas.create_oval(36, 35, 44, 42, fill=ACCENT, outline="")

    # ── Title ──
    tk.Label(
        card, text="Student Portal",
        font=FONT_TITLE, bg=BG_CARD, fg=TEXT_PRIMARY
    ).pack(pady=(8, 2))

    tk.Label(
        card, text="Sign in to your account",
        font=FONT_SUBTITLE, bg=BG_CARD, fg=TEXT_MUTED
    ).pack(pady=(0, 22))

    # ── Divider ──
    tk.Frame(card, bg=BORDER_NORMAL, height=1, width=320).pack(pady=(0, 20))

    # ── Username ──
    make_label(card, "USERNAME").pack(anchor="w")
    u_frame, username_entry = make_entry(card)
    u_frame.pack(pady=(4, 14))
    username_entry.focus_set()

    # ── Password ──
    make_label(card, "PASSWORD").pack(anchor="w")
    p_container = tk.Frame(card, bg=BG_CARD)
    p_container.pack(pady=(4, 6))

    p_frame, password_entry = make_entry(p_container, show="•")
    p_frame.pack(side="left")

    show_pw = tk.BooleanVar(value=False)

    def toggle_password():
        if show_pw.get():
            password_entry.config(show="")
            eye_btn.config(text="🙈")
        else:
            password_entry.config(show="•")
            eye_btn.config(text="👁")

    eye_btn = tk.Button(
        p_container,
        text="👁",
        font=("Helvetica", 13),
        bg=BG_CARD,
        fg=TEXT_MUTED,
        activebackground=BG_CARD,
        activeforeground=ACCENT,
        relief="flat",
        bd=0,
        cursor="hand2",
        command=lambda: [show_pw.set(not show_pw.get()), toggle_password()],
    )
    eye_btn.pack(side="left", padx=(6, 0))

    # ── Status bar ──
    status = StatusBar(card)

    # ── Login button ──
    login_btn = tk.Button(
        card,
        text="LOG IN",
        font=FONT_BUTTON,
        bg=ACCENT,
        fg=BG_MAIN,
        activebackground=ACCENT_HOVER,
        activeforeground=BG_MAIN,
        relief="flat",
        width=26,
        height=2,
        cursor="hand2",
        bd=0,
    )
    login_btn.pack(pady=(14, 6))
    animate_button(login_btn, ACCENT, ACCENT_HOVER)

    # ── Footer note ──
    tk.Label(
        card,
        text="Contact admin if you forgot your credentials.",
        font=FONT_SMALL,
        bg=BG_CARD,
        fg=TEXT_MUTED,
    ).pack(pady=(10, 0))

    # ── Loading indicator ──
    loading_label = tk.Label(
        card, text="", font=FONT_SMALL, bg=BG_CARD, fg=ACCENT
    )
    loading_label.pack()

    # ── Login logic ──
    def login_action(event=None):
        username = username_entry.get().strip()
        password = password_entry.get().strip()

        if not username or not password:
            status.show("⚠  Both fields are required.", color=ERROR_COLOR)
            return

        # Visual feedback while logging in
        login_btn.config(state="disabled", text="Checking...")
        loading_label.config(text="Please wait…")
        root.update_idletasks()

        try:
            result = check_login(username, password)
        except Exception as e:
            login_btn.config(state="normal", text="LOG IN")
            loading_label.config(text="")
            status.show(f"Database error: {e}", color=ERROR_COLOR)
            return

        login_btn.config(state="normal", text="LOG IN")
        loading_label.config(text="")

        if result is None:
            # Shake the card to indicate failure
            _shake(root, card)
            status.show("✕  Invalid username or password.", color=ERROR_COLOR)
            password_entry.delete(0, tk.END)
            password_entry.focus_set()
            return

        role = result[0]
        status.show(f"✓  Welcome, {username}!", color=SUCCESS_COLOR, auto_clear=0)
        root.update_idletasks()

        try:
            root.withdraw()
            management.start_app(role, username, root)
        except Exception as e:
            root.deiconify()
            status.show(f"Error opening portal: {e}", color=ERROR_COLOR)

    login_btn.config(command=login_action)
    root.bind("<Return>", login_action)

    def on_close():
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    root.mainloop()


# ---------------- SHAKE ANIMATION ---------------- #

def _shake(root, widget, times=6, distance=8, delay=40):
    """Horizontal shake animation for wrong password feedback."""
    orig_x = widget.winfo_x()
    orig_y = widget.winfo_y()

    def step(i, direction):
        if i >= times:
            widget.place(x=orig_x, y=orig_y)
            widget.pack()
            return
        widget.place(x=orig_x + direction * distance, y=orig_y)
        root.after(delay, lambda: step(i + 1, -direction))

    widget.pack_forget()
    step(0, 1)


# ---------------- ENTRY POINT ---------------- #

if __name__ == "__main__":
    start_login()