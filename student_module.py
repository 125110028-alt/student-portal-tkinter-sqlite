import tkinter as tk
from tkinter import messagebox
from database import insert_student


def open_add_student_window():
    window = tk.Toplevel()
    window.title("Add Student")
    window.geometry("400x300")
    window.configure(bg="white")

    # Title
    tk.Label(
        window,
        text="Add Student",
        font=("Arial", 16, "bold"),
        bg="white"
    ).pack(pady=15)

    # Name
    tk.Label(window, text="Name", bg="white").pack()
    name_entry = tk.Entry(window)
    name_entry.pack(pady=5)

    # Roll No
    tk.Label(window, text="Roll Number", bg="white").pack()
    roll_entry = tk.Entry(window)
    roll_entry.pack(pady=5)

    # Course
    tk.Label(window, text="Course", bg="white").pack()
    course_entry = tk.Entry(window)
    course_entry.pack(pady=5)

    # Button function
    def add_student():
        name = name_entry.get().strip()
        roll = roll_entry.get().strip()
        course = course_entry.get().strip()

        if name == "" or roll == "" or course == "":
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            insert_student(name, roll, course)
            messagebox.showinfo("Success", "Student added successfully")

            # Clear fields
            name_entry.delete(0, tk.END)
            roll_entry.delete(0, tk.END)
            course_entry.delete(0, tk.END)

        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Add Button
    tk.Button(
        window,
        text="Add Student",
        command=add_student,
        width=15
    ).pack(pady=20)

    window.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox
from database import fetch_students, update_student, delete_student


def view_students_window():
    window = tk.Toplevel()
    window.title("Student List")
    window.geometry("600x400")

    tk.Label(window, text="All Students", font=("Arial", 16)).pack(pady=10)

    columns = ("ID", "Name", "Roll No", "Course")
    tree = ttk.Treeview(window, columns=columns, show="headings")

    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=120)

    tree.pack(fill="both", expand=True)

    # Load data
    def load_data():
        for row in tree.get_children():
            tree.delete(row)

        students = fetch_students()
        for student in students:
            tree.insert("", tk.END, values=student)

    load_data()

    # DELETE FUNCTION
    def delete_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a student first")
            return

        values = tree.item(selected[0], "values")
        roll_no = values[2]

        delete_student(roll_no)
        messagebox.showinfo("Success", "Student deleted")

        load_data()

    # UPDATE FUNCTION
    def update_selected():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a student first")
            return

        values = tree.item(selected[0], "values")
        roll_no = values[2]

        # Open update window
        update_win = tk.Toplevel(window)
        update_win.title("Update Student")

        tk.Label(update_win, text="Name").pack()
        name_entry = tk.Entry(update_win)
        name_entry.insert(0, values[1])
        name_entry.pack()

        tk.Label(update_win, text="Course").pack()
        course_entry = tk.Entry(update_win)
        course_entry.insert(0, values[3])
        course_entry.pack()

        def save_update():
            new_name = name_entry.get()
            new_course = course_entry.get()

            update_student(roll_no, new_name, new_course)
            messagebox.showinfo("Success", "Student updated")

            update_win.destroy()
            load_data()

        tk.Button(update_win, text="Save", command=save_update).pack(pady=10)

    # Buttons
    tk.Button(window, text="Update Selected", command=update_selected).pack(pady=5)
    tk.Button(window, text="Delete Selected", command=delete_selected).pack(pady=5)



# For testing directly
if __name__ == "__main__":
    open_add_student_window()