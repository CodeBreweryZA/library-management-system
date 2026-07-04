# Library Management System

A desktop GUI application built with Python Tkinter and SQLite for managing library books and student borrowing records.

## Features

- **Book Management** – Add, update, and track book inventory
- **Borrow / Return Books** – Issue books to students and process returns
- **Fine Calculation** – Automatic overdue fine computation
- **Search** – Search books by title or student by name
- **Student Records** – View borrowing history per student

## Getting Started

1. Ensure Python 3 is installed.
2. Install the required dependency:
   ```
   pip install tkcalendar
   ```
3. Run the application:
   ```
   python library_app.py
   ```

The SQLite database (`library.db`) is created automatically on first run with sample data.

## Technologies Used

- Python 3
- Tkinter (GUI framework)
- SQLite (embedded database)
- tkcalendar (date picker widget)
