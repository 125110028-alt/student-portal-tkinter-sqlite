import tkinter as tk
from tkinter import messagebox
from database import insert_marks, get_student_id_by_roll


def open_add_marks_window():
    window = tk.Toplevel()
    window.title("Add Marks")
    window.geometry("400x300")

    tk.Label(window, text="Add Marks", font=("Arial", 16)).pack(pady=10)

    # Roll No
    tk.Label(window, text="Roll Number").pack()
    roll_entry = tk.Entry(window)
    roll_entry.pack(pady=5)

    # Subject
    tk.Label(window, text="Subject").pack()
    subject_entry = tk.Entry(window)
    subject_entry.pack(pady=5)

    # Marks
    tk.Label(window, text="Marks").pack()
    marks_entry = tk.Entry(window)
    marks_entry.pack(pady=5)

    def add_marks():
        roll_no = roll_entry.get().strip()
        subject = subject_entry.get().strip()
        marks = marks_entry.get().strip()

        if roll_no == "" or subject == "" or marks == "":
            messagebox.showerror("Error", "All fields are required")
            return

        student_id = get_student_id_by_roll(roll_no)

        if not student_id:
            messagebox.showerror("Error", "Student not found")
            return

        try:
            insert_marks(student_id, subject, int(marks))
            messagebox.showinfo("Success", "Marks added successfully")

            roll_entry.delete(0, tk.END)
            subject_entry.delete(0, tk.END)
            marks_entry.delete(0, tk.END)

        except:
            messagebox.showerror("Error", "Invalid marks value")

    tk.Button(window, text="Add Marks", command=add_marks).pack(pady=20)