import tkinter as tk
from tkinter import messagebox
from database import insert_marks, get_student_id_by_roll


# ---------------- ADD MARKS WINDOW ---------------- #
def open_add_marks_window():
    window = tk.Toplevel()
    window.title("Add Marks")
    window.geometry("350x300")
    window.configure(bg="#f4f4f4")

    # Title
    tk.Label(
        window,
        text="Add Student Marks",
        font=("Arial", 16, "bold"),
        bg="#f4f4f4"
    ).pack(pady=15)

    # Roll Number
    tk.Label(window, text="Roll Number", bg="#f4f4f4").pack()
    roll_entry = tk.Entry(window)
    roll_entry.pack(pady=5)

    # Subject
    tk.Label(window, text="Subject", bg="#f4f4f4").pack()
    subject_entry = tk.Entry(window)
    subject_entry.pack(pady=5)

    # Marks
    tk.Label(window, text="Marks", bg="#f4f4f4").pack()
    marks_entry = tk.Entry(window)
    marks_entry.pack(pady=5)

    # ---------------- ADD MARKS FUNCTION ---------------- #
    def add_marks():
        roll_no = roll_entry.get().strip()
        subject = subject_entry.get().strip()
        marks = marks_entry.get().strip()

        # Validation
        if roll_no == "" or subject == "" or marks == "":
            messagebox.showerror("Error", "All fields are required")
            return

        # Convert marks to integer
        try:
            marks = int(marks)
        except ValueError:
            messagebox.showerror("Error", "Marks must be a number")
            return

        # Get student ID
        student_id = get_student_id_by_roll(roll_no)

        if not student_id:
            messagebox.showerror("Error", "Student not found")
            return

        # Insert marks
        insert_marks(student_id, subject, marks)

        messagebox.showinfo("Success", "Marks added successfully!")

        # Clear fields
        roll_entry.delete(0, tk.END)
        subject_entry.delete(0, tk.END)
        marks_entry.delete(0, tk.END)

    # Button
    tk.Button(
        window,
        text="Add Marks",
        command=add_marks,
        bg="#4CAF50",
        fg="white",
        width=15
    ).pack(pady=20)