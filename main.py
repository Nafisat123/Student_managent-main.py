import sqlite3
import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import csv

# Database class for managing the SQLite database
class Database:
    def __init__(self):
        """Initialize the database connection and create the table if it doesn't exist."""
        self.conn = sqlite3.connect('student_management.db')
        self.cursor = self.conn.cursor()
        self.initialize_db()

    def initialize_db(self):
        """Create the students table with constraints if it doesn't already exist."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                course TEXT NOT NULL,
                grade REAL NOT NULL CHECK(grade >= 0 AND grade <= 100)
            )
        ''')
        self.conn.commit()

    def add_student(self, first_name, last_name, course, grade):
        """Add a new student to the database."""
        self.cursor.execute("INSERT INTO students (first_name, last_name, course, grade) VALUES (?, ?, ?, ?)",
                            (first_name, last_name, course, grade))
        self.conn.commit()

    def update_student(self, student_id, first_name, last_name, course, grade):
        """Update an existing student's information."""
        self.cursor.execute(
            "UPDATE students SET first_name = ?, last_name = ?, course = ?, grade = ? WHERE id = ?",
            (first_name, last_name, course, grade, student_id))
        self.conn.commit()

    def delete_student(self, student_id):
        """Delete a student record from the database."""
        self.cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        self.conn.commit()

    def get_all_students(self):
        """Retrieve all student records from the database."""
        self.cursor.execute("SELECT * FROM students")
        return self.cursor.fetchall()

    def search_students(self, search_text):
        """Search for students by first or last name."""
        self.cursor.execute("SELECT * FROM students WHERE first_name LIKE ? OR last_name LIKE ?",
                            (f'%{search_text}%', f'%{search_text}%'))
        return self.cursor.fetchall()

    def export_to_csv(self, file_path):
        """Export student records to a CSV file."""
        self.cursor.execute("SELECT * FROM students")
        rows = self.cursor.fetchall()
        with open(file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "First Name", "Last Name", "Course", "Grade"])
            writer.writerows(rows)

    def __del__(self):
        """Close the database connection when the object is deleted."""
        self.conn.close()

# GUI application class for student management system
class StudentManagementApp:
    def __init__(self, root):
        """Initialize the GUI and set up the database connection."""
        self.root = root
        self.root.title("Student Management System")
        self.root.geometry("800x500")

        # Initialize the database
        self.db = Database()

        # Create GUI components
        self.create_widgets()
        self.load_students()

    def create_widgets(self):
        """Create and place GUI components."""
        # Labels and Entry widgets
        tk.Label(self.root, text="First Name").grid(row=0, column=0, padx=10, pady=10)
        self.first_name_entry = tk.Entry(self.root)
        self.first_name_entry.grid(row=0, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Last Name").grid(row=1, column=0, padx=10, pady=10)
        self.last_name_entry = tk.Entry(self.root)
        self.last_name_entry.grid(row=1, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Course").grid(row=2, column=0, padx=10, pady=10)
        self.course_entry = tk.Entry(self.root)
        self.course_entry.grid(row=2, column=1, padx=10, pady=10)

        tk.Label(self.root, text="Grade").grid(row=3, column=0, padx=10, pady=10)
        self.grade_entry = tk.Entry(self.root)
        self.grade_entry.grid(row=3, column=1, padx=10, pady=10)

        # Buttons
        tk.Button(self.root, text="Add Student", command=self.add_student).grid(row=4, column=0, padx=10, pady=10)
        tk.Button(self.root, text="Update Student", command=self.update_student).grid(row=4, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Delete Student", command=self.delete_student).grid(row=4, column=2, padx=10, pady=10)
        tk.Button(self.root, text="Export to CSV", command=self.export_to_csv).grid(row=4, column=3, padx=10, pady=10)

        # Search functionality
        tk.Label(self.root, text="Search").grid(row=5, column=0, padx=10, pady=10)
        self.search_entry = tk.Entry(self.root)
        self.search_entry.grid(row=5, column=1, padx=10, pady=10)
        tk.Button(self.root, text="Search", command=self.search_students).grid(row=5, column=2, padx=10, pady=10)

        # Student list display
        self.tree = ttk.Treeview(self.root, columns=("ID", "First Name", "Last Name", "Course", "Grade"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("First Name", text="First Name")
        self.tree.heading("Last Name", text="Last Name")
        self.tree.heading("Course", text="Course")
        self.tree.heading("Grade", text="Grade")
        self.tree.grid(row=6, column=0, columnspan=4, padx=10, pady=10)

        # Bind selection event
        self.tree.bind("<ButtonRelease-1>", self.select_student)

    def load_students(self):
        """Load and display all student records in the Treeview."""
        for row in self.db.get_all_students():
            self.tree.insert("", "end", values=row)

    def add_student(self):
        """Add a new student record to the database."""
        try:
            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            course = self.course_entry.get()
            grade = float(self.grade_entry.get())

            # Validate input
            if not first_name or not last_name or not course or not (0 <= grade <= 100):
                raise ValueError("Invalid input")

            # Add student
            self.db.add_student(first_name, last_name, course, grade)
            messagebox.showinfo("Success", "Student added successfully")
            self.refresh_students()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid data: {e}")

    def update_student(self):
        """Update the selected student's record."""
        try:
            selected_item = self.tree.selection()[0]
            selected_student = self.tree.item(selected_item, "values")
            student_id = selected_student[0]

            first_name = self.first_name_entry.get()
            last_name = self.last_name_entry.get()
            course = self.course_entry.get()
            grade = float(self.grade_entry.get())

            # Validate input
            if not first_name or not last_name or not course or not (0 <= grade <= 100):
                raise ValueError("Invalid input")

            # Update student
            self.db.update_student(student_id, first_name, last_name, course, grade)
            messagebox.showinfo("Success", "Student updated successfully")
            self.refresh_students()
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid data: {e}")

    def delete_student(self):
        """Delete the selected student's record."""
        try:
            selected_item = self.tree.selection()[0]
            selected_student = self.tree.item(selected_item, "values")
            student_id = selected_student[0]

            # Delete student
            self.db.delete_student(student_id)
            messagebox.showinfo("Success", "Student deleted successfully")
            self.refresh_students()
        except IndexError:
            messagebox.showwarning("Warning", "No student selected")

    def search_students(self):
        """Search for students by name and update the Treeview with the results."""
        search_text = self.search_entry.get()
        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in self.db.search_students(search_text):
            self.tree.insert("", "end", values=row)

    def export_to_csv(self):
        """Export student records to a CSV file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.db.export_to_csv(file_path)
            messagebox.showinfo("Success", "Data exported successfully")

    def select_student(self, event):
        """Populate entry fields with the data of the selected student."""
        try:
            selected_item = self.tree.selection()[0]
            selected_student = self.tree.item(selected_item, "values")

            # Fill entry fields with selected student's data
            self.first_name_entry.delete(0, tk.END)
            self.first_name_entry.insert(tk.END, selected_student[1])

            self.last_name_entry.delete(0, tk.END)
            self.last_name_entry.insert(tk.END, selected_student[2])

            self.course_entry.delete(0, tk.END)
            self.course_entry.insert(tk.END, selected_student[3])

            self.grade_entry.delete(0, tk.END)
            self.grade_entry.insert(tk.END, selected_student[4])
        except IndexError:
            pass

    def refresh_students(self):
        """Refresh the Treeview with all student records."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.load_students()

# Main application execution
if __name__ == "__main__":
    root = tk.Tk()
    app = StudentManagementApp(root)
    root.mainloop()
I