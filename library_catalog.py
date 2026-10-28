
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from datetime import date, timedelta, datetime
import json
import csv
import os

# ================= CONFIGURATION =================

APP_TITLE = "LIBRA | Library Management System"
DATA_FILE = "library_books.json"
HISTORY_FILE = "library_history.csv"

BG = "#F3F6FC"
NAVY = "#142442"
NAVY_LIGHT = "#203A65"
BLUE = "#4263EB"
GREEN = "#16865D"
ORANGE = "#D97706"
RED = "#E54862"
PURPLE = "#7950D9"
WHITE = "#FFFFFF"
TEXT = "#172B4D"
MUTED = "#73839D"


# ================= BOOK CLASSES =================

class LibraryItem:
    def __init__(self, book_id, title, author, category):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.category = category
        self.status = "Available"
        self.borrower = ""
        self.issue_date = ""
        self.due_date = ""

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "category": self.category,
            "status": self.status,
            "borrower": self.borrower,
            "issue_date": self.issue_date,
            "due_date": self.due_date
        }


class Book(LibraryItem):
    def __init__(self, book_id, title, author, category):
        super().__init__(book_id, title, author, category)

    @classmethod
    def from_dict(cls, data):
        book = cls(
            data["book_id"],
            data["title"],
            data["author"],
            data["category"]
        )
        book.status = data.get("status", "Available")
        book.borrower = data.get("borrower", "")
        book.issue_date = data.get("issue_date", "")
        book.due_date = data.get("due_date", "")
        return book


# ================= SAMPLE BOOKS =================

SAMPLE_BOOKS = [
    ("B101", "Python Programming", "Reema Thareja", "Programming"),
    ("B102", "Let Us C", "Yashavant Kanetkar", "Programming"),
    ("B103", "Data Structures Using C", "Reema Thareja",
     "Computer Science"),
    ("B104", "Database System Concepts", "Abraham Silberschatz",
     "Database"),
    ("B105", "Clean Code", "Robert C. Martin",
     "Software Engineering"),
    ("B106", "The Alchemist", "Paulo Coelho", "Fiction"),
    ("B107", "Rich Dad Poor Dad", "Robert Kiyosaki", "Finance"),
    ("B108", "Artificial Intelligence", "Stuart Russell",
     "Computer Science"),
    ("B109", "Head First Java", "Kathy Sierra", "Programming"),
    ("B110", "Operating System Concepts", "Abraham Silberschatz",
     "Computer Science"),
]


def add_sample_books(app):
    """Add the 10 sample books without creating duplicates."""
    existing_ids = {book.book_id for book in app.books}
    added = 0

    for book_id, title, author, category in SAMPLE_BOOKS:
        if book_id not in existing_ids:
            book = Book(book_id, title, author, category)
            app.books.append(book)
            existing_ids.add(book_id)
            added += 1

    if added:
        app.save_books()

    return added


# ================= MAIN APPLICATION =================

class LibraryManagementSystem:

    def __init__(self, root):
        self.root = root
        self.root.title(APP_TITLE)
        self.root.geometry("1450x850")
        self.root.minsize(1100, 700)
        self.root.configure(bg=BG)

        self.books = []
        self.load_books()

        # Add sample books before creating the table.
        add_sample_books(self)

        self.build_styles()
        self.build_interface()
        self.refresh_catalog()

    # ================= DATA STORAGE =================

    def load_books(self):
        if not os.path.exists(DATA_FILE):
            self.books = []
            return

        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            self.books = [Book.from_dict(item) for item in data]

        except (json.JSONDecodeError, OSError, KeyError, TypeError):
            messagebox.showwarning(
                "Data Warning",
                "Saved book data could not be read. "
                "The application will start with sample data."
            )
            self.books = []

    def save_books(self):
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as file:
                json.dump(
                    [book.to_dict() for book in self.books],
                    file,
                    indent=4,
                    ensure_ascii=False
                )
        except OSError as error:
            messagebox.showerror(
                "Save Error", f"Could not save books:\n{error}"
            )

    def log_activity(self, action, book, details=""):
        file_exists = os.path.exists(HISTORY_FILE)

        try:
            with open(
                HISTORY_FILE, "a", newline="", encoding="utf-8"
            ) as file:
                writer = csv.writer(file)

                if not file_exists:
                    writer.writerow([
                        "Date", "Time", "Action",
                        "Book ID", "Book Title", "Details"
                    ])

                now = datetime.now()
                writer.writerow([
                    now.strftime("%Y-%m-%d"),
                    now.strftime("%H:%M:%S"),
                    action,
                    book.book_id,
                    book.title,
                    details
                ])
        except OSError as error:
            messagebox.showwarning(
                "History Warning",
                f"Could not write activity history:\n{error}"
            )

    # ================= STYLES =================

    def build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        style.configure(
            "Treeview",
            background=WHITE,
            foreground=TEXT,
            rowheight=35,
            fieldbackground=WHITE,
            font=("Segoe UI", 10),
            borderwidth=0
        )

        style.configure(
            "Treeview.Heading",
            background="#E9EFF9",
            foreground=NAVY,
            font=("Segoe UI", 10, "bold"),
            padding=10,
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", "#DCE6FF")],
            foreground=[("selected", NAVY)]
        )

        style.configure(
            "TCombobox",
            padding=7,
            font=("Segoe UI", 10)
        )

    # ================= BUILD INTERFACE =================

    def build_interface(self):
        self.main = tk.Frame(self.root, bg=BG)
        self.main.pack(fill="both", expand=True)

        self.build_sidebar()

        self.content = tk.Frame(self.main, bg=BG)
        self.content.pack(side="left", fill="both", expand=True)

        self.build_header()
        self.build_dashboard_cards()
        self.build_form()
        self.build_search()
        self.build_table()

    def build_sidebar(self):
        sidebar = tk.Frame(self.main, bg=NAVY, width=235)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        logo = tk.Frame(sidebar, bg=NAVY)
        logo.pack(fill="x", padx=20, pady=(32, 35))

        tk.Label(
            logo,
            text="▤ LIBRA",
            bg=NAVY,
            fg=WHITE,
            font=("Segoe UI", 23, "bold")
        ).pack(anchor="w")

        tk.Label(
            logo,
            text="LIBRARY MANAGEMENT",
            bg=NAVY,
            fg="#AFC7F7",
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", pady=(8, 0))

        buttons = [
            ("▦   Dashboard", self.go_dashboard),
            ("＋   Add a Book", self.focus_book_id),
            ("↻   Refresh Catalog", self.refresh_catalog),
            ("⇩   Export CSV", self.export_csv),
            ("◷   Activity History", self.show_history),
            ("✕   Delete Selected", self.delete_selected),
        ]

        for label, command in buttons:
            tk.Button(
                sidebar,
                text=label,
                command=command,
                bg=NAVY_LIGHT,
                fg=WHITE,
                activebackground=BLUE,
                activeforeground=WHITE,
                font=("Segoe UI", 10, "bold"),
                relief="flat",
                bd=0,
                anchor="w",
                padx=20,
                pady=15,
                cursor="hand2"
            ).pack(fill="x", padx=7, pady=3)

        tk.Frame(
            sidebar, bg="#304568", height=1
        ).pack(fill="x", padx=18, pady=25)

        tk.Label(
            sidebar,
            text=(
                "PROJECT TECHNOLOGIES\n\n"
                "Python 3.x\n"
                "Tkinter GUI\n"
                "Object-Oriented Programming\n"
                "JSON + CSV Storage"
            ),
            bg=NAVY,
            fg="#C7D6F3",
            font=("Segoe UI", 10),
            justify="left",
            anchor="w"
        ).pack(fill="x", padx=22)

    def build_header(self):
        header = tk.Frame(self.content, bg=BG)
        header.pack(fill="x", padx=30, pady=(25, 15))

        title_area = tk.Frame(header, bg=BG)
        title_area.pack(side="left")

        tk.Label(
            title_area,
            text="Library Dashboard",
            bg=BG,
            fg=NAVY,
            font=("Segoe UI", 25, "bold")
        ).pack(anchor="w")

        tk.Label(
            title_area,
            text="Organize books, track issues and manage returns.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 11)
        ).pack(anchor="w", pady=(5, 0))

        tk.Label(
            header,
            text="TODAY  •  " + date.today().strftime("%d %b %Y"),
            bg="#E4EBFF",
            fg=BLUE,
            font=("Segoe UI", 10, "bold"),
            padx=15,
            pady=12
        ).pack(side="right", anchor="n")

    def build_dashboard_cards(self):
        self.cards_frame = tk.Frame(self.content, bg=BG)
        self.cards_frame.pack(fill="x", padx=30, pady=(5, 15))

        card_info = [
            ("TOTAL BOOKS", "total", BLUE, "▤"),
            ("AVAILABLE", "available", GREEN, "✓"),
            ("ISSUED", "issued", ORANGE, "↗"),
            ("OVERDUE", "overdue", RED, "!"),
            ("CATEGORIES", "categories", PURPLE, "▦"),
        ]

        self.card_values = {}

        for index, (label, key, color, symbol) in enumerate(card_info):
            card = tk.Frame(
                self.cards_frame,
                bg=WHITE,
                highlightbackground="#E1E8F3",
                highlightthickness=1
            )

            card.grid(
                row=0, column=index, sticky="nsew",
                padx=(0 if index == 0 else 6, 0)
            )

            self.cards_frame.grid_columnconfigure(
                index, weight=1, uniform="cards"
            )

            top = tk.Frame(card, bg=WHITE)
            top.pack(fill="x", padx=15, pady=(17, 8))

            tk.Label(
                top,
                text=label,
                bg=WHITE,
                fg=MUTED,
                font=("Segoe UI", 9, "bold")
            ).pack(side="left")

            tk.Label(
                top,
                text=symbol,
                bg=WHITE,
                fg=color,
                font=("Segoe UI", 15, "bold")
            ).pack(side="right")

            value = tk.Label(
                card,
                text="0",
                bg=WHITE,
                fg=NAVY,
                font=("Segoe UI", 23, "bold")
            )
            value.pack(anchor="w", padx=15, pady=(0, 12))
            self.card_values[key] = value

            tk.Frame(
                card, bg=color, height=4
            ).pack(side="bottom", fill="x")

    def build_form(self):
        outer = tk.Frame(self.content, bg=BG)
        outer.pack(fill="x", padx=30, pady=(0, 15))

        form = tk.LabelFrame(
            outer,
            text="  BOOK DETAILS  ",
            bg=WHITE,
            fg=NAVY,
            font=("Segoe UI", 10, "bold"),
            bd=1,
            relief="solid",
            padx=15,
            pady=12
        )
        form.pack(fill="x")

        self.entries = {}

        fields = [
            ("Book ID", "book_id", 0, 0),
            ("Book Title", "title", 0, 2),
            ("Author Name", "author", 1, 0),
            ("Category", "category", 1, 2),
        ]

        for label, key, row, col in fields:
            tk.Label(
                form,
                text=label,
                bg=WHITE,
                fg=TEXT,
                font=("Segoe UI", 10, "bold")
            ).grid(
                row=row, column=col,
                sticky="w", padx=(5, 10), pady=8
            )

            entry = tk.Entry(
                form,
                font=("Segoe UI", 11),
                bg="#FBFCFF",
                fg=TEXT,
                relief="solid",
                bd=1
            )

            entry.grid(
                row=row, column=col + 1,
                sticky="ew", padx=(0, 20), pady=7, ipady=7
            )

            self.entries[key] = entry

        form.grid_columnconfigure(1, weight=1)
        form.grid_columnconfigure(3, weight=1)

        buttons = [
            ("＋ Add Book", GREEN, self.add_book),
            ("✎ Update", BLUE, self.update_book),
            ("Issue Book", ORANGE, self.issue_book),
            ("Return Book", GREEN, self.return_book),
            ("Clear Form", "#64748B", self.clear_form),
        ]

        button_row = tk.Frame(form, bg=WHITE)
        button_row.grid(
            row=2, column=0, columnspan=4,
            sticky="w", pady=(8, 0)
        )

        for label, color, command in buttons:
            tk.Button(
                button_row,
                text=label,
                command=command,
                bg=color,
                fg=WHITE,
                activebackground=color,
                activeforeground=WHITE,
                relief="flat",
                bd=0,
                font=("Segoe UI", 10, "bold"),
                padx=15,
                pady=10,
                cursor="hand2"
            ).pack(side="left", padx=(4, 5))

    def build_search(self):
        search = tk.Frame(self.content, bg=BG)
        search.pack(fill="x", padx=30, pady=(0, 12))

        tk.Label(
            search,
            text="BOOK COLLECTION",
            bg=BG,
            fg=NAVY,
            font=("Segoe UI", 12, "bold")
        ).pack(side="left", padx=(3, 18))

        self.search_var = tk.StringVar()

        self.search_entry = tk.Entry(
            search,
            textvariable=self.search_var,
            font=("Segoe UI", 10),
            width=20,
            relief="solid",
            bd=1
        )
        self.search_entry.pack(
            side="left", ipady=8, padx=(0, 10)
        )
        self.search_entry.bind(
            "<Return>", lambda event: self.search_books()
        )

        self.category_var = tk.StringVar(value="All")
        self.category_combo = ttk.Combobox(
            search,
            textvariable=self.category_var,
            values=["All"],
            state="readonly",
            width=15
        )
        self.category_combo.pack(
            side="left", padx=(0, 10), ipady=3
        )

        self.status_var = tk.StringVar(value="All")
        self.status_combo = ttk.Combobox(
            search,
            textvariable=self.status_var,
            values=["All", "Available", "Issued", "Overdue"],
            state="readonly",
            width=13
        )
        self.status_combo.pack(
            side="left", padx=(0, 10), ipady=3
        )

        tk.Button(
            search,
            text="Search",
            command=self.search_books,
            bg=BLUE,
            fg=WHITE,
            relief="flat",
            padx=18,
            pady=9,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=(0, 7))

        tk.Button(
            search,
            text="Reset",
            command=self.reset_search,
            bg="#64748B",
            fg=WHITE,
            relief="flat",
            padx=18,
            pady=9,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

    def build_table(self):
        table_frame = tk.Frame(self.content, bg=WHITE)
        table_frame.pack(
            fill="both", expand=True, padx=30, pady=(0, 20)
        )

        columns = (
            "ID", "Title", "Author", "Category",
            "Status", "Borrower", "Issue Date", "Due Date"
        )

        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            selectmode="browse"
        )

        widths = {
            "ID": 85,
            "Title": 200,
            "Author": 155,
            "Category": 145,
            "Status": 100,
            "Borrower": 135,
            "Issue Date": 110,
            "Due Date": 110
        }

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(
                col, width=widths[col],
                minwidth=70, anchor="center"
            )

        y_scroll = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=self.tree.yview
        )

        x_scroll = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=self.tree.xview
        )

        self.tree.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        self.tree.tag_configure("available", foreground=GREEN)
        self.tree.tag_configure("issued", foreground=ORANGE)
        self.tree.tag_configure("overdue", foreground=RED)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    # ================= HELPER FUNCTIONS =================

    def get_book_by_id(self, book_id):
        for book in self.books:
            if book.book_id.lower() == book_id.lower():
                return book
        return None

    def get_form_values(self):
        return {
            key: entry.get().strip()
            for key, entry in self.entries.items()
        }

    def selected_book(self):
        selection = self.tree.selection()

        if selection:
            values = self.tree.item(selection[0], "values")
            if values:
                return self.get_book_by_id(values[0])

        book_id = self.entries["book_id"].get().strip()
        if book_id:
            return self.get_book_by_id(book_id)

        return None

    def on_select(self, event=None):
        selection = self.tree.selection()
        if not selection:
            return

        values = self.tree.item(selection[0], "values")
        if not values:
            return

        book = self.get_book_by_id(values[0])
        if book:
            self.fill_form(book)

    def fill_form(self, book):
        values = {
            "book_id": book.book_id,
            "title": book.title,
            "author": book.author,
            "category": book.category
        }

        for key, value in values.items():
            self.entries[key].delete(0, tk.END)
            self.entries[key].insert(0, value)

    def clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

        for item in self.tree.selection():
            self.tree.selection_remove(item)

        self.entries["book_id"].focus_set()

    def focus_book_id(self):
        self.clear_form()
        self.entries["book_id"].focus_set()

    def go_dashboard(self):
        self.reset_search()
        self.clear_form()

    # ================= ADD BOOK =================

    def add_book(self):
        values = self.get_form_values()

        if not all(values.values()):
            messagebox.showwarning(
                "Missing Information",
                "Please fill in all four book fields."
            )
            return

        if self.get_book_by_id(values["book_id"]):
            messagebox.showerror(
                "Duplicate Book ID",
                "This Book ID already exists."
            )
            return

        book = Book(
            values["book_id"],
            values["title"],
            values["author"],
            values["category"]
        )

        self.books.append(book)
        self.save_books()
        self.log_activity("Added", book)
        self.refresh_catalog()
        self.clear_form()

        messagebox.showinfo(
            "Success",
            f"'{book.title}' added successfully."
        )

    # ================= UPDATE BOOK =================

    def update_book(self):
        values = self.get_form_values()

        if not all(values.values()):
            messagebox.showwarning(
                "Missing Information",
                "Select a book and fill in all fields."
            )
            return

        book = self.get_book_by_id(values["book_id"])

        if not book:
            messagebox.showerror(
                "Not Found",
                "Book ID not found. Select a book first."
            )
            return

        book.title = values["title"]
        book.author = values["author"]
        book.category = values["category"]

        self.save_books()
        self.log_activity("Updated", book)
        self.refresh_catalog()

        messagebox.showinfo(
            "Updated", "Book details updated successfully."
        )

    # ================= DELETE BOOK =================

    def delete_selected(self):
        book = self.selected_book()

        if not book:
            messagebox.showwarning(
                "Select Book",
                "Please select a book from the table."
            )
            return

        if not messagebox.askyesno(
            "Confirm Delete",
            f"Delete '{book.title}' ({book.book_id})?"
        ):
            return

        self.log_activity("Deleted", book)
        self.books.remove(book)
        self.save_books()
        self.refresh_catalog()
        self.clear_form()

        messagebox.showinfo(
            "Deleted", "Book deleted successfully."
        )

    # ================= ISSUE BOOK =================

    def issue_book(self):
        book_id = self.entries["book_id"].get().strip()
        book = self.get_book_by_id(book_id)

        if not book:
            messagebox.showerror(
                "Not Found",
                "Enter a valid Book ID or select a book."
            )
            return

        if book.status != "Available":
            messagebox.showwarning(
                "Unavailable", "This book is already issued."
            )
            return

        borrower = simpledialog.askstring(
            "Issue Book",
            "Enter borrower's name:",
            parent=self.root
        )

        if borrower is None:
            return

        borrower = borrower.strip()

        if not borrower:
            messagebox.showwarning(
                "Required", "Borrower's name cannot be empty."
            )
            return

        book.status = "Issued"
        book.borrower = borrower
        book.issue_date = date.today().isoformat()
        book.due_date = (
            date.today() + timedelta(days=14)
        ).isoformat()

        self.save_books()
        self.log_activity("Issued", book, f"Borrower: {borrower}")
        self.refresh_catalog()

        messagebox.showinfo(
            "Book Issued",
            f"Book: {book.title}\n"
            f"Borrower: {borrower}\n"
            f"Due date: {book.due_date}"
        )

    # ================= RETURN BOOK =================

    def return_book(self):
        book_id = self.entries["book_id"].get().strip()
        book = self.get_book_by_id(book_id)

        if not book:
            messagebox.showerror(
                "Not Found",
                "Enter a valid Book ID or select a book."
            )
            return

        if book.status == "Available":
            messagebox.showinfo(
                "Already Available",
                "This book is not currently issued."
            )
            return

        previous_borrower = book.borrower

        book.status = "Available"
        book.borrower = ""
        book.issue_date = ""
        book.due_date = ""

        self.save_books()
        self.log_activity(
            "Returned", book,
            f"Previous borrower: {previous_borrower}"
        )
        self.refresh_catalog()

        messagebox.showinfo(
            "Returned",
            f"'{book.title}' has been returned successfully."
        )

    # ================= OVERDUE CHECK =================

    def is_overdue(self, book):
        if book.status != "Issued" or not book.due_date:
            return False

        try:
            due = date.fromisoformat(book.due_date)
            return due < date.today()
        except ValueError:
            return False

    # ================= REFRESH CATALOG =================

    def refresh_catalog(self):
        if not hasattr(self, "tree"):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in self.books:
            status = (
                "Overdue" if self.is_overdue(book)
                else book.status
            )

            self.tree.insert(
                "",
                tk.END,
                values=(
                    book.book_id,
                    book.title,
                    book.author,
                    book.category,
                    status,
                    book.borrower,
                    book.issue_date,
                    book.due_date
                ),
                tags=(status.lower(),)
            )

        total = len(self.books)
        available = sum(
            1 for book in self.books
            if book.status == "Available"
        )
        issued = sum(
            1 for book in self.books
            if book.status == "Issued"
        )
        overdue = sum(
            1 for book in self.books
            if self.is_overdue(book)
        )
        categories = len(set(
            book.category for book in self.books
        ))

        stats = {
            "total": total,
            "available": available,
            "issued": issued,
            "overdue": overdue,
            "categories": categories
        }

        for key, value in stats.items():
            self.card_values[key].config(text=str(value))

        category_list = ["All"] + sorted(
            set(book.category for book in self.books)
        )

        self.category_combo["values"] = category_list

        if self.category_var.get() not in category_list:
            self.category_var.set("All")

        self.apply_filters()

    # ================= SEARCH AND FILTER =================

    def apply_filters(self):
        query = self.search_var.get().strip().lower()
        category = self.category_var.get()
        selected_status = self.status_var.get()

        for item in self.tree.get_children():
            self.tree.delete(item)

        for book in self.books:
            status = (
                "Overdue" if self.is_overdue(book)
                else book.status
            )

            searchable = " ".join([
                book.book_id,
                book.title,
                book.author,
                book.category,
                book.borrower
            ]).lower()

            if query and query not in searchable:
                continue

            if category != "All" and book.category != category:
                continue

            if selected_status != "All" and status != selected_status:
                continue

            self.tree.insert(
                "",
                tk.END,
                values=(
                    book.book_id,
                    book.title,
                    book.author,
                    book.category,
                    status,
                    book.borrower,
                    book.issue_date,
                    book.due_date
                ),
                tags=(status.lower(),)
            )

    def search_books(self):
        self.apply_filters()

    def reset_search(self):
        self.search_var.set("")
        self.category_var.set("All")
        self.status_var.set("All")
        self.refresh_catalog()

    # ================= CSV EXPORT =================

    def export_csv(self):
        if not self.books:
            messagebox.showinfo(
                "No Data", "There are no books to export."
            )
            return

        path = filedialog.asksaveasfilename(
            title="Export Book Catalog",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv")],
            initialfile="library_catalog.csv"
        )

        if not path:
            return

        try:
            with open(
                path, "w", newline="", encoding="utf-8-sig"
            ) as file:
                writer = csv.writer(file)

                writer.writerow([
                    "Book ID", "Title", "Author", "Category",
                    "Status", "Borrower", "Issue Date", "Due Date"
                ])

                for book in self.books:
                    status = (
                        "Overdue" if self.is_overdue(book)
                        else book.status
                    )

                    writer.writerow([
                        book.book_id,
                        book.title,
                        book.author,
                        book.category,
                        status,
                        book.borrower,
                        book.issue_date,
                        book.due_date
                    ])

            messagebox.showinfo(
                "Export Complete",
                f"CSV saved successfully:\n{path}"
            )

        except OSError as error:
            messagebox.showerror("Export Error", str(error))

    # ================= ACTIVITY HISTORY =================

    def show_history(self):
        window = tk.Toplevel(self.root)
        window.title("Library Activity History")
        window.geometry("950x500")
        window.configure(bg=BG)

        tk.Label(
            window,
            text="Activity History",
            bg=BG,
            fg=NAVY,
            font=("Segoe UI", 18, "bold")
        ).pack(anchor="w", padx=20, pady=15)

        columns = (
            "Date", "Time", "Action",
            "Book ID", "Book Title", "Details"
        )

        frame = tk.Frame(window, bg=WHITE)
        frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        history_tree = ttk.Treeview(
            frame, columns=columns, show="headings"
        )

        widths = {
            "Date": 110,
            "Time": 100,
            "Action": 100,
            "Book ID": 90,
            "Book Title": 220,
            "Details": 250
        }

        for col in columns:
            history_tree.heading(col, text=col)
            history_tree.column(
                col, width=widths[col], anchor="center"
            )

        scrollbar = ttk.Scrollbar(
            frame, orient="vertical",
            command=history_tree.yview
        )

        history_tree.configure(yscrollcommand=scrollbar.set)
        history_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        if os.path.exists(HISTORY_FILE):
            try:
                with open(
                    HISTORY_FILE, "r", newline="", encoding="utf-8"
                ) as file:
                    reader = csv.reader(file)
                    next(reader, None)

                    for row in reader:
                        if len(row) == len(columns):
                            history_tree.insert(
                                "", tk.END, values=row
                            )
            except OSError as error:
                messagebox.showerror(
                    "History Error", str(error), parent=window
                )
        else:
            history_tree.insert(
                "", tk.END,
                values=("-", "-", "No activity yet",
                        "-", "-", "-")
            )


# ================= RUN APPLICATION =================

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()


