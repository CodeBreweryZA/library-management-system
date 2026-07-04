import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
from datetime import datetime, date

# -------------------------
# Database Setup
# -------------------------
def setup_database():
    conn = sqlite3.connect("library.db")
    cursor = conn.cursor()

    # Create tables
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            quantity INTEGER NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS borrowed_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_name TEXT NOT NULL,
            book_id INTEGER,
            borrow_date TEXT,
            return_date TEXT,
            fine REAL DEFAULT 0,
            FOREIGN KEY(book_id) REFERENCES books(id)
        )
    """)

    # Insert sample books if empty
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ("Python Programming", 3),
            ("Data Science Essentials", 2),
            ("Machine Learning Basics", 4),
            ("Database Systems", 1),
            ("Web Development Guide", 5)
        ]
        cursor.executemany("INSERT INTO books (title, quantity) VALUES (?, ?)", sample_books)

    # Insert sample borrowed records if empty
    cursor.execute("SELECT COUNT(*) FROM borrowed_books")
    if cursor.fetchone()[0] == 0:
        sample_borrowed = [
            ("Alice", 1, "10/20/25", "10/25/25", 0),
            ("Bob", 2, "10/18/25", "10/22/25", 10),
            ("Charlie", 3, "10/19/25", "10/21/25", 0)
        ]
        cursor.executemany("""
            INSERT INTO borrowed_books (student_name, book_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?)
        """, sample_borrowed)

    conn.commit()
    conn.close()


# -------------------------
# Main Application Class
# -------------------------
class LibraryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.conn = sqlite3.connect("library.db")
        self.create_widgets()
        self.refresh_book_list()
        self.refresh_table()

    # -------------------------
    # UI Components
    # -------------------------
    def create_widgets(self):
        # Borrow Book Form
        form_frame = ttk.LabelFrame(self.root, text="Borrow Book")
        form_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        ttk.Label(form_frame, text="Student Name:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.student_name_entry = ttk.Entry(form_frame)
        self.student_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Select Book:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.book_combobox = ttk.Combobox(form_frame, state="readonly")
        self.book_combobox.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Borrow Date:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.borrow_date_entry = DateEntry(form_frame, date_pattern="mm/dd/yy")
        self.borrow_date_entry.set_date(date.today())
        self.borrow_date_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Return Date:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.return_date_entry = DateEntry(form_frame, date_pattern="mm/dd/yy")
        self.return_date_entry.set_date(date.today())
        self.return_date_entry.grid(row=3, column=1, padx=5, pady=5)

        # Buttons
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        self.add_button = tk.Button(button_frame, text="Add", bg="green", fg="white", command=self.add_record)
        self.add_button.grid(row=0, column=0, padx=5)

        self.delete_button = tk.Button(button_frame, text="Delete", bg="red", fg="white", command=self.delete_record)
        self.delete_button.grid(row=0, column=1, padx=5)

        self.clear_button = tk.Button(button_frame, text="Clear", bg="grey", fg="white", command=self.clear_form)
        self.clear_button.grid(row=0, column=2, padx=5)

        # Search and Table
        search_frame = ttk.Frame(self.root)
        search_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        ttk.Label(search_frame, text="Search:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        self.search_entry.bind("<KeyRelease>", lambda e: self.refresh_table())

        self.record_count_label = ttk.Label(search_frame, text="Total Records: 0")
        self.record_count_label.grid(row=0, column=2, padx=5, pady=5)

        # Table
        table_frame = ttk.Frame(self.root)
        table_frame.grid(row=2, column=0, padx=10, pady=5)

        columns = ("ID", "Student", "Book", "Borrow Date", "Return Date", "Fine")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100 if col != "ID" else 50)

        style = ttk.Style()
        style.configure("Treeview.Heading", background="blue", foreground="white", font=("Arial", 10, "bold"))
        style.map("Treeview", background=[("selected", "lightblue")])

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

    # -------------------------
    # Data Operations
    # -------------------------
    def refresh_book_list(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title FROM books WHERE quantity > 0")
        books = cursor.fetchall()
        self.book_combobox['values'] = [f"{book[0]} - {book[1]}" for book in books]

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search_text = self.search_entry.get().lower()
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT bb.id, bb.student_name, b.title, bb.borrow_date, bb.return_date, bb.fine
            FROM borrowed_books bb
            JOIN books b ON bb.book_id = b.id
        """)
        records = cursor.fetchall()
        filtered = [r for r in records if search_text in r[1].lower() or search_text in r[2].lower()]
        for record in filtered:
            tag = "fine" if record[5] > 0 else ""
            self.tree.insert("", "end", values=record, tags=(tag,))
        self.tree.tag_configure("fine", background="red")
        self.record_count_label.config(text=f"Total Records: {len(filtered)}")

    def add_record(self):
        student = self.student_name_entry.get().strip()
        book_info = self.book_combobox.get()
        borrow_date = self.borrow_date_entry.get_date()
        return_date = self.return_date_entry.get_date()

        if not student or not book_info:
            messagebox.showerror("Error", "Please fill all fields.")
            return
        if borrow_date < date.today():
            messagebox.showerror("Error", "Borrow date cannot be in the past.")
            return
        if return_date < borrow_date:
            messagebox.showerror("Error", "Return date cannot be before borrow date.")
            return

        book_id = int(book_info.split(" - ")[0])
        fine = 0
        if return_date < date.today():
            days_late = (date.today() - return_date).days
            fine = days_late * 5

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO borrowed_books (student_name, book_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?)
        """, (student, book_id, borrow_date.strftime("%m/%d/%y"), return_date.strftime("%m/%d/%y"), fine))
        cursor.execute("UPDATE books SET quantity = quantity - 1 WHERE id = ?", (book_id,))
        self.conn.commit()
        self.refresh_book_list()
        self.refresh_table()
        self.clear_form()

    def delete_record(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Select a record to delete.")
            return
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to delete this record?")
        if confirm:
            record = self.tree.item(selected[0])['values']
            borrow_id = record[0]
            cursor = self.conn.cursor()
            cursor.execute("SELECT book_id FROM borrowed_books WHERE id = ?", (borrow_id,))
            book_id = cursor.fetchone()[0]
            cursor.execute("DELETE FROM borrowed_books WHERE id = ?", (borrow_id,))
            cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE id = ?", (book_id,))
            self.conn.commit()
            self.refresh_book_list()
            self.refresh_table()

    def clear_form(self):
        self.student_name_entry.delete(0, tk.END)
        self.borrow_date_entry.set_date(date.today())
        self.return_date_entry.set_date(date.today())
        self.book_combobox.set("")


# -------------------------
# Run Application
# -------------------------
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = LibraryApp(root)
    root.mainloop()