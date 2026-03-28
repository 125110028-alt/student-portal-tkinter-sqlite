import tkinter as tk


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Student Portal")
        self.geometry("800x500")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frames = {}

        for F in (LoginPage, AdminDashboard, StudentDashboard):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginPage)

    def show_frame(self, page):
        frame = self.frames[page]
        frame.tkraise()


# ---------------- LOGIN PAGE ---------------- #
class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Login", font=("Arial", 16)).pack(pady=20)

        self.username = tk.Entry(self)
        self.username.pack(pady=5)

        self.password = tk.Entry(self, show="*")
        self.password.pack(pady=5)

        tk.Button(self, text="Login",
                  command=lambda: self.login(controller)).pack(pady=10)

    def login(self, controller):
        from login import check_login

        username = self.username.get()
        password = self.password.get()

        result = check_login(username, password)

        if result:
            role = result[0]

            if role == "admin":
                controller.show_frame(AdminDashboard)

            elif role == "student":
                controller.frames[StudentDashboard].set_user(username)
                controller.show_frame(StudentDashboard)


# ---------------- ADMIN DASHBOARD ---------------- #
class AdminDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        tk.Label(self, text="Admin Dashboard", font=("Arial", 16)).pack(pady=20)

        from student_module import open_add_student_window
        from student_module import view_students_window
        from marks_module import open_add_marks_window

        tk.Button(self, text="Add Student",
                  command=open_add_student_window).pack(pady=5)

        tk.Button(self, text="View Students",
                  command=view_students_window).pack(pady=5)

        tk.Button(self, text="Add Marks",
                  command=open_add_marks_window).pack(pady=5)

        tk.Button(self, text="Logout",
                  command=lambda: controller.show_frame(LoginPage)).pack(pady=20)


# ---------------- STUDENT DASHBOARD ---------------- #
class StudentDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)

        self.label = tk.Label(self, text="Student Dashboard", font=("Arial", 16))
        self.label.pack(pady=20)

        self.info = tk.Label(self, text="")
        self.info.pack()

        tk.Button(self, text="Logout",
                  command=lambda: controller.show_frame(LoginPage)).pack(pady=20)

    def set_user(self, username):
        from database import fetch_student_by_roll

        student = fetch_student_by_roll(username)

        if student:
            self.info.config(text=f"Name: {student[1]}\nCourse: {student[3]}")