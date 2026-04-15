"""
Admin Dashboard for KIUT Fee Tracker
Comprehensive admin management interface
"""
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from GUI.db_config import execute_query, get_connection


class AdminDashboard:
    """Admin dashboard with full management capabilities"""

    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.user = app.current_user
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        """Setup admin dashboard UI"""
        # Top header
        header_frame = tk.Frame(self.parent, bg="#2c3e50", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)

        # Welcome label
        welcome_label = tk.Label(
            header_frame,
            text=f"Admin Dashboard - Welcome, {self.user['username']}",
            font=("Arial", 16, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        welcome_label.pack(side=tk.LEFT, padx=20)

        # Logout button
        logout_btn = tk.Button(
            header_frame,
            text="Logout",
            font=("Arial", 10),
            bg="#e74c3c",
            fg="white",
            command=self.app.logout
        )
        logout_btn.pack(side=tk.RIGHT, padx=20)

        # Main content area with tabs
        self.notebook = ttk.Notebook(self.parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create tabs
        self.create_faculties_tab()
        self.create_programmes_tab()
        self.create_students_tab()
        self.create_fee_structures_tab()
        self.create_fee_obligations_tab()
        self.create_exams_tab()
        self.create_finance_users_tab()
        self.create_reports_tab()

    def create_faculties_tab(self):
        """Create faculties management tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Faculties")

        # Info label
        info_label = tk.Label(
            tab,
            text="Manage Faculties - Each faculty contains different programmes/courses",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        info_label.pack(pady=10)

        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=5)

        tk.Button(
            toolbar,
            text="Add Faculty",
            bg="#27ae60",
            fg="white",
            command=lambda: self.add_faculty(tab)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_faculties(tab)
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            toolbar,
            text="Delete Selected",
            bg="#e74c3c",
            fg="white",
            command=lambda: self.delete_faculty(tab)
        ).pack(side=tk.LEFT, padx=5)

        # Treeview
        columns = ("ID", "Faculty Name", "Description", "Created At")
        self.faculty_tree = ttk.Treeview(tab, columns=columns, show="headings", height=18)

        for col in columns:
            self.faculty_tree.heading(col, text=col)
            self.faculty_tree.column(col, width=180)

        self.faculty_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.faculty_tree.yview)
        self.faculty_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.load_faculties(tab)

    def load_faculties(self, tab):
        """Load faculties into treeview"""
        for item in self.faculty_tree.get_children():
            self.faculty_tree.delete(item)

        query = "SELECT * FROM faculties ORDER BY faculty_id DESC"
        faculties = execute_query(query, fetch=True)

        if faculties:
            for faculty in faculties:
                date_str = faculty['created_at'].strftime('%Y-%m-%d') if faculty['created_at'] else 'N/A'
                desc = faculty['description'] or ''
                if len(desc) > 50:
                    desc = desc[:50] + '...'
                self.faculty_tree.insert("", tk.END, values=(
                    faculty['faculty_id'],
                    faculty['name'],
                    desc,
                    date_str
                ))

    def add_faculty(self, parent):
        """Add new faculty"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Faculty")
        dialog.geometry("450x300")
        dialog.transient(self.parent)

        # Info
        tk.Label(
            dialog,
            text="Create a new Faculty (e.g., Faculty of Science, Faculty of Business)",
            font=("Arial", 10),
            fg="#7f8c8d"
        ).pack(pady=10)
        
        # Form
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Faculty Name:", bg="white").grid(row=0, column=0, sticky="w", pady=10)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Description:", bg="white").grid(row=1, column=0, sticky="nw", pady=10)
        desc_text = tk.Text(form_frame, width=30, height=5)
        desc_text.grid(row=1, column=1, pady=10, padx=10)
        
        def save():
            name = name_entry.get().strip()
            description = desc_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter faculty name")
                return
            
            if len(name) < 3:
                messagebox.showerror("Error", "Faculty name must be at least 3 characters")
                return
            
            # Check if faculty exists
            check_query = "SELECT faculty_id FROM faculties WHERE name = %s"
            existing = execute_query(check_query, (name,), fetch=True)
            
            if existing:
                messagebox.showerror("Error", "A faculty with this name already exists")
                return
            
            # Insert faculty
            insert_query = "INSERT INTO faculties (name, description) VALUES (%s, %s)"
            result = execute_query(insert_query, (name, description))
            
            if result:
                messagebox.showinfo("Success", "Faculty added successfully!")
                dialog.destroy()
                self.load_faculties(parent)
            else:
                messagebox.showerror("Error", "Failed to add faculty")
        
        tk.Button(
            dialog,
            text="Add Faculty",
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).pack(pady=20)
    
    def delete_faculty(self, parent):
        """Delete selected faculty"""
        selection = self.faculty_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a faculty to delete")
            return
        
        item = self.faculty_tree.item(selection[0])
        faculty_id = item['values'][0]
        faculty_name = item['values'][1]
        
        # Check if there are programmes in this faculty
        check_prog = "SELECT COUNT(*) as count FROM programmes WHERE faculty_id = %s"
        prog_result = execute_query(check_prog, (faculty_id,), fetch=True)
        
        if prog_result and prog_result[0]['count'] > 0:
            messagebox.showwarning("Warning", f"Cannot delete '{faculty_name}'. It has {prog_result[0]['count']} programme(s) attached. Please delete the programmes first.")
            return
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete faculty '{faculty_name}'?\n\nThis action cannot be undone."
        )
        
        if confirm:
            query = "DELETE FROM faculties WHERE faculty_id = %s"
            result = execute_query(query, (faculty_id,))
            
            if result:
                messagebox.showinfo("Success", "Faculty deleted successfully!")
                self.load_faculties(parent)
            else:
                messagebox.showerror("Error", "Failed to delete faculty")
    
    def create_programmes_tab(self):
        """Create programmes management tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Programmes")
        
        # Info label
        info_label = tk.Label(
            tab,
            text="Manage Programmes/Courses - Add programmes to faculties",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        info_label.pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            toolbar,
            text="Add Programme",
            bg="#27ae60",
            fg="white",
            command=lambda: self.add_programme(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_programmes(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Delete Selected",
            bg="#e74c3c",
            fg="white",
            command=lambda: self.delete_programme(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter by faculty
        tk.Label(toolbar, text="Filter by Faculty:", bg="#ecf0f1").pack(side=tk.LEFT, padx=(20, 5))
        self.programme_faculty_filter = ttk.Combobox(toolbar, width=25, state="readonly")
        self.programme_faculty_filter.pack(side=tk.LEFT, padx=5)
        self.programme_faculty_filter.bind('<<ComboboxSelected>>', lambda e: self.load_programmes(tab))
        
        # Treeview
        columns = ("ID", "Programme Name", "Faculty", "Description")
        self.programme_tree = ttk.Treeview(tab, columns=columns, show="headings", height=18)
        
        for col in columns:
            self.programme_tree.heading(col, text=col)
            self.programme_tree.column(col, width=180)
        
        self.programme_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.programme_tree.yview)
        self.programme_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_programmes(tab)
    
    def load_programmes(self, tab):
        """Load programmes into treeview"""
        for item in self.programme_tree.get_children():
            self.programme_tree.delete(item)
        
        # Load faculties for filter
        faculty_query = "SELECT faculty_id, name FROM faculties ORDER BY name"
        faculties = execute_query(faculty_query, fetch=True)
        
        faculty_options = ["All Faculties"]
        faculty_map = {}
        if faculties:
            for f in faculties:
                faculty_options.append(f['name'])
                faculty_map[f['name']] = f['faculty_id']
        
        self.programme_faculty_filter['values'] = faculty_options
        if not self.programme_faculty_filter.get():
            self.programme_faculty_filter.current(0)
        
        # Get selected faculty filter
        selected_faculty = self.programme_faculty_filter.get()
        
        if selected_faculty == "All Faculties" or not selected_faculty:
            query = """
                SELECT p.programme_id, p.name, p.description, f.name as faculty_name
                FROM programmes p
                LEFT JOIN faculties f ON p.faculty_id = f.faculty_id
                ORDER BY p.programme_id DESC
            """
            programmes = execute_query(query, fetch=True)
        else:
            faculty_id = faculty_map.get(selected_faculty)
            query = """
                SELECT p.programme_id, p.name, p.description, f.name as faculty_name
                FROM programmes p
                LEFT JOIN faculties f ON p.faculty_id = f.faculty_id
                WHERE p.faculty_id = %s
                ORDER BY p.programme_id DESC
            """
            programmes = execute_query(query, (faculty_id,), fetch=True) if faculty_id else []
        
        if programmes:
            for prog in programmes:
                desc = prog['description'] or ''
                if len(desc) > 40:
                    desc = desc[:40] + '...'
                self.programme_tree.insert("", tk.END, values=(
                    prog['programme_id'],
                    prog['name'],
                    prog['faculty_name'] or 'N/A',
                    desc
                ))
    
    def add_programme(self, parent):
        """Add new programme"""
        # First check if there are faculties
        faculties = execute_query("SELECT faculty_id, name FROM faculties ORDER BY name", fetch=True)
        
        if not faculties:
            messagebox.showwarning("Warning", "Please add at least one faculty first before adding programmes.")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Programme")
        dialog.geometry("450x350")
        dialog.transient(self.parent)
        
        # Form
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Programme Name:", bg="white").grid(row=0, column=0, sticky="w", pady=10)
        name_entry = tk.Entry(form_frame, width=30)
        name_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Faculty:", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        faculty_var = tk.StringVar()
        faculty_combo = ttk.Combobox(form_frame, textvariable=faculty_var, values=[f['name'] for f in faculties], width=28, state="readonly")
        faculty_combo.grid(row=1, column=1, pady=10, padx=10)
        if faculties:
            faculty_combo.current(0)
        
        tk.Label(form_frame, text="Description:", bg="white").grid(row=2, column=0, sticky="nw", pady=10)
        desc_text = tk.Text(form_frame, width=30, height=5)
        desc_text.grid(row=2, column=1, pady=10, padx=10)
        
        def save():
            name = name_entry.get().strip()
            faculty_name = faculty_var.get()
            description = desc_text.get("1.0", tk.END).strip()
            
            if not name:
                messagebox.showerror("Error", "Please enter programme name")
                return
            
            if not faculty_name:
                messagebox.showerror("Error", "Please select a faculty")
                return
            
            # Get faculty_id
            faculty_id = None
            for f in faculties:
                if f['name'] == faculty_name:
                    faculty_id = f['faculty_id']
                    break
            
            if not faculty_id:
                messagebox.showerror("Error", "Invalid faculty selected")
                return
            
            # Check if programme exists in this faculty
            check_query = "SELECT programme_id FROM programmes WHERE name = %s AND faculty_id = %s"
            existing = execute_query(check_query, (name, faculty_id), fetch=True)
            
            if existing:
                messagebox.showerror("Error", "A programme with this name already exists in this faculty")
                return
            
            # Insert programme
            insert_query = "INSERT INTO programmes (name, faculty_id, description) VALUES (%s, %s, %s)"
            result = execute_query(insert_query, (name, faculty_id, description))
            
            if result:
                messagebox.showinfo("Success", "Programme added successfully!")
                dialog.destroy()
                self.load_programmes(parent)
            else:
                messagebox.showerror("Error", "Failed to add programme")
        
        tk.Button(
            dialog,
            text="Add Programme",
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).pack(pady=20)
    
    def delete_programme(self, parent):
        """Delete selected programme"""
        selection = self.programme_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a programme to delete")
            return
        
        item = self.programme_tree.item(selection[0])
        programme_id = item['values'][0]
        programme_name = item['values'][1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete programme '{programme_name}'?\n\nThis action cannot be undone."
        )
        
        if confirm:
            query = "DELETE FROM programmes WHERE programme_id = %s"
            result = execute_query(query, (programme_id,))
            
            if result:
                messagebox.showinfo("Success", "Programme deleted successfully!")
                self.load_programmes(parent)
            else:
                messagebox.showerror("Error", "Failed to delete programme")
    
    def create_students_tab(self):
        """Create students management tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Students")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="Add Student",
            command=lambda: self.add_student(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_students(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Search
        tk.Label(toolbar, text="Search:", bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        self.student_search = tk.Entry(toolbar, width=20)
        self.student_search.pack(side=tk.LEFT, padx=5)
        tk.Button(
            toolbar,
            text="Search",
            command=lambda: self.search_students(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Reg No", "Full Name", "Programme", "Year", "Status")
        self.student_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.student_tree.yview)
        self.student_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_students(tab)
    
    def create_fee_structures_tab(self):
        """Create fee structures management tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Fee Structures")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="Add Fee Structure",
            command=lambda: self.add_fee_structure(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_fee_structures(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Programme", "Year", "Semester", "Amount", "Description")
        self.fee_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.fee_tree.heading(col, text=col)
            self.fee_tree.column(col, width=130)
        
        self.fee_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.load_fee_structures(tab)
    
    def create_exams_tab(self):
        """Create exams management tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Exams")
        
        # Info label
        info_label = tk.Label(
            tab,
            text="Exams: Select faculties that will sit for each exam. The system will identify programmes in those faculties.",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        info_label.pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            toolbar,
            text="Add Exam",
            bg="#27ae60",
            fg="white",
            command=lambda: self.add_exam(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_exams(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Delete Selected",
            bg="#e74c3c",
            fg="white",
            command=lambda: self.delete_exam(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Exam Name", "Semester", "Academic Year", "Start Date", "End Date", "Faculties")
        self.exam_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 50, "Exam Name": 100, "Semester": 80, "Academic Year": 100, "Start Date": 100, "End Date": 100, "Faculties": 250}
        for col in columns:
            self.exam_tree.heading(col, text=col)
            self.exam_tree.column(col, width=col_widths.get(col, 150))
        
        self.exam_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.exam_tree.yview)
        self.exam_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_exams(tab)
    
    def create_finance_users_tab(self):
        """Create finance users management tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Finance Users")
        
        # Info label
        info_label = tk.Label(
            tab,
            text="Manage Finance Department Users - Only Admin can create Finance accounts",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        info_label.pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            toolbar,
            text="Add Finance User",
            bg="#27ae60",
            fg="white",
            command=lambda: self.add_finance_user(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_finance_users(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Delete Selected",
            bg="#e74c3c",
            fg="white",
            command=lambda: self.delete_finance_user(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Username", "Role", "Created At")
        self.finance_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.finance_tree.heading(col, text=col)
            self.finance_tree.column(col, width=150)
        
        self.finance_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.finance_tree.yview)
        self.finance_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_finance_users(tab)
    
    def load_finance_users(self, tab):
        """Load finance users into treeview"""
        for item in self.finance_tree.get_children():
            self.finance_tree.delete(item)
        
        query = "SELECT id, username, role, created_at FROM users WHERE role = 'finance' ORDER BY id DESC"
        users = execute_query(query, fetch=True)
        
        if users:
            for user in users:
                date_str = user['created_at'].strftime('%Y-%m-%d %H:%M') if user['created_at'] else 'N/A'
                self.finance_tree.insert("", tk.END, values=(
                    user['id'],
                    user['username'],
                    user['role'],
                    date_str
                ))
    
    def add_finance_user(self, parent):
        """Add new finance user"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Finance User")
        dialog.geometry("400x300")
        dialog.transient(self.parent)
        
        # Info
        tk.Label(
            dialog,
            text="Create a new Finance account.\nFinance users can verify payments.",
            font=("Arial", 10),
            fg="#7f8c8d"
        ).pack(pady=10)
        
        # Form
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10)
        
        tk.Label(form_frame, text="Username:", bg="white").grid(row=0, column=0, sticky="w", pady=10)
        username_entry = tk.Entry(form_frame, width=25)
        username_entry.grid(row=0, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Password:", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        password_entry = tk.Entry(form_frame, width=25, show="*")
        password_entry.grid(row=1, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Confirm Password:", bg="white").grid(row=2, column=0, sticky="w", pady=10)
        confirm_entry = tk.Entry(form_frame, width=25, show="*")
        confirm_entry.grid(row=2, column=1, pady=10, padx=10)
        
        def save():
            username = username_entry.get().strip()
            password = password_entry.get()
            confirm = confirm_entry.get()
            
            if not username or not password:
                messagebox.showerror("Error", "Please fill in all fields")
                return
            
            if len(username) < 3:
                messagebox.showerror("Error", "Username must be at least 3 characters")
                return
            
            if len(password) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
            
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match")
                return
            
            # Check if username exists
            check_query = "SELECT id FROM users WHERE username = %s"
            existing = execute_query(check_query, (username,), fetch=True)
            
            if existing:
                messagebox.showerror("Error", "Username already exists")
                return
            
            # Hash password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Insert finance user
            insert_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, 'finance')"
            result = execute_query(insert_query, (username, hashed_password))
            
            if result:
                messagebox.showinfo("Success", "Finance user created successfully!")
                dialog.destroy()
                self.load_finance_users(parent)
            else:
                messagebox.showerror("Error", "Failed to create finance user")
        
        tk.Button(
            dialog,
            text="Create Finance User",
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).pack(pady=20)
    
    def delete_finance_user(self, parent):
        """Delete selected finance user"""
        selection = self.finance_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a finance user to delete")
            return
        
        item = self.finance_tree.item(selection[0])
        user_id = item['values'][0]
        username = item['values'][1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete finance user '{username}'?\n\nThis action cannot be undone."
        )
        
        if confirm:
            query = "DELETE FROM users WHERE id = %s AND role = 'finance'"
            result = execute_query(query, (user_id,))
            
            if result:
                messagebox.showinfo("Success", "Finance user deleted successfully!")
                self.load_finance_users(parent)
            else:
                messagebox.showerror("Error", "Failed to delete finance user")
    
    def create_reports_tab(self):
        """Create reports tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Reports")
        
        # Report buttons
        btn_frame = tk.Frame(tab, bg="#ecf0f1")
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="Payment Summary Report",
            width=25,
            height=2,
            command=self.payment_summary_report
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Student Fee Status Report",
            width=25,
            height=2,
            command=self.student_fee_status_report
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Exam Clearance Report",
            width=25,
            height=2,
            command=self.exam_clearance_report
        ).pack(pady=10)
        
        tk.Button(
            btn_frame,
            text="Finance Verification Report",
            width=25,
            height=2,
            command=self.verification_report
        ).pack(pady=10)
    
    def load_data(self):
        """Load initial data"""
        pass
    
    def load_students(self, tab):
        """Load students into treeview"""
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        query = "SELECT * FROM students ORDER BY student_id DESC"
        students = execute_query(query, fetch=True)
        
        if students:
            for student in students:
                self.student_tree.insert("", tk.END, values=(
                    student['student_id'],
                    student['reg_no'],
                    student['full_name'],
                    student['programme'],
                    student['year_of_study'],
                    student['status']
                ))
    
    def search_students(self, tab):
        """Search students"""
        search_term = self.student_search.get().strip()
        
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        if search_term:
            query = """
                SELECT * FROM students 
                WHERE reg_no LIKE %s OR full_name LIKE %s OR programme LIKE %s
                ORDER BY student_id DESC
            """
            search_pattern = f"%{search_term}%"
            students = execute_query(query, (search_pattern, search_pattern, search_pattern), fetch=True)
        else:
            students = execute_query("SELECT * FROM students ORDER BY student_id DESC", fetch=True)
        
        if students:
            for student in students:
                self.student_tree.insert("", tk.END, values=(
                    student['student_id'],
                    student['reg_no'],
                    student['full_name'],
                    student['programme'],
                    student['year_of_study'],
                    student['status']
                ))
    
    def add_student(self, parent):
        """Add new student with user linking"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Student")
        dialog.geometry("400x450")
        dialog.transient(self.parent)
        
        # Info label
        info_label = tk.Label(
            dialog,
            text="Note: If a user account exists with the same Registration Number,\nit will be automatically linked to this student profile.",
            font=("Arial", 9),
            fg="#7f8c8d",
            wraplength=350
        )
        info_label.grid(row=0, column=0, columnspan=2, padx=10, pady=5)
        
        # Form fields
        fields = [
            ("Registration Number:", "reg_no"),
            ("Full Name:", "full_name"),
            ("Programme:", "programme"),
            ("Year of Study:", "year_of_study"),
        ]
        
        entries = {}
        
        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i+1, column=0, sticky="w", padx=10, pady=10)
            entry = tk.Entry(dialog, width=25)
            entry.grid(row=i+1, column=1, padx=10, pady=10)
            entries[key] = entry
        
        # Status
        tk.Label(dialog, text="Status:").grid(row=5, column=0, sticky="w", padx=10, pady=10)
        status_var = tk.StringVar(value="ACTIVE")
        status_combo = ttk.Combobox(dialog, textvariable=status_var, values=["ACTIVE", "SUSPENDED", "GRADUATED"], width=22)
        status_combo.grid(row=5, column=1, padx=10, pady=10)
        
        def save():
            reg_no = entries['reg_no'].get().strip()
            full_name = entries['full_name'].get().strip()
            programme = entries['programme'].get().strip()
            year = entries['year_of_study'].get().strip()
            status = status_var.get()
            
            if not reg_no or not full_name or not programme or not year:
                messagebox.showerror("Error", "Please fill all fields")
                return
            
            try:
                year = int(year)
            except ValueError:
                messagebox.showerror("Error", "Year must be a number")
                return
            
            # Check if student with this reg_no already exists
            check_query = "SELECT student_id FROM students WHERE reg_no = %s"
            existing = execute_query(check_query, (reg_no,), fetch=True)
            
            if existing:
                messagebox.showerror("Error", "A student with this registration number already exists")
                return
            
            # Check if there's a user with this username (reg_no) to link
            user_query = "SELECT id FROM users WHERE username = %s"
            user_result = execute_query(user_query, (reg_no,), fetch=True)
            user_id = None
            if user_result:
                user_id = user_result[0]['id']
            
            # Insert student with optional user_id link
            if user_id:
                query = """
                    INSERT INTO students (reg_no, full_name, programme, year_of_study, status, user_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                result = execute_query(query, (reg_no, full_name, programme, year, status, user_id))
            else:
                query = """
                    INSERT INTO students (reg_no, full_name, programme, year_of_study, status)
                    VALUES (%s, %s, %s, %s, %s)
                """
                result = execute_query(query, (reg_no, full_name, programme, year, status))
            
            if result:
                if user_id:
                    messagebox.showinfo("Success", f"Student added successfully!\n\nNote: This student has been linked to existing user account.")
                else:
                    messagebox.showinfo("Success", "Student added successfully!\n\nNote: No user account found with this registration number.\nStudent can self-register to create a linked account.")
                dialog.destroy()
                self.load_students(parent)
            else:
                messagebox.showerror("Error", "Failed to add student")
        
        tk.Button(dialog, text="Save", command=save, bg="#27ae60", fg="white").grid(
            row=6, column=0, columnspan=2, pady=20
        )
    
    def load_fee_structures(self, tab):
        """Load fee structures into treeview"""
        for item in self.fee_tree.get_children():
            self.fee_tree.delete(item)
        
        query = "SELECT * FROM fee_structures ORDER BY fee_id DESC"
        fees = execute_query(query, fetch=True)
        
        if fees:
            for fee in fees:
                self.fee_tree.insert("", tk.END, values=(
                    fee['fee_id'],
                    fee['programme'],
                    fee['year_of_study'],
                    fee['semester'],
                    fee['amount'],
                    fee['description']
                ))
    
    def create_fee_obligations_tab(self):
        """Create fee obligations management tab - assign fee structures to students"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Fee Obligations")
        
        # Info label
        info_label = tk.Label(
            tab,
            text="Assign Fee Structures to Students - Create fee obligations based on programme, year, and semester.\nStudents in the same programme and year will automatically share the same fee structure.",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        info_label.pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            toolbar,
            text="Assign Fee to Students",
            bg="#27ae60",
            fg="white",
            command=lambda: self.assign_fee_obligation(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_fee_obligations(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Delete Selected",
            bg="#e74c3c",
            fg="white",
            command=lambda: self.delete_fee_obligation(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter section
        filter_frame = tk.Frame(tab, bg="#ecf0f1")
        filter_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(filter_frame, text="Filter by Academic Year:", bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        self.obligation_year_filter = ttk.Combobox(filter_frame, width=15, state="readonly")
        self.obligation_year_filter.pack(side=tk.LEFT, padx=5)
        self.obligation_year_filter.bind('<<ComboboxSelected>>', lambda e: self.load_fee_obligations(tab))
        
        tk.Label(filter_frame, text="Filter by Status:", bg="#ecf0f1").pack(side=tk.LEFT, padx=(20, 5))
        self.obligation_status_filter = ttk.Combobox(filter_frame, width=15, state="readonly", values=["All", "Not Cleared", "Cleared"])
        self.obligation_status_filter.set("All")
        self.obligation_status_filter.pack(side=tk.LEFT, padx=5)
        self.obligation_status_filter.bind('<<ComboboxSelected>>', lambda e: self.load_fee_obligations(tab))
        
        # Treeview
        columns = ("ID", "Student", "Reg No", "Programme", "Year", "Fee Description", "Amount", "Academic Year", "Semester", "Status", "Assigned By")
        self.obligation_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 50, "Student": 150, "Reg No": 100, "Programme": 120, "Year": 50, 
                      "Fee Description": 150, "Amount": 100, "Academic Year": 100, "Semester": 80, "Status": 80, "Assigned By": 100}
        for col in columns:
            self.obligation_tree.heading(col, text=col)
            self.obligation_tree.column(col, width=col_widths.get(col, 100))
        
        self.obligation_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.obligation_tree.yview)
        self.obligation_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_fee_obligations(tab)
    
    def load_fee_obligations(self, tab):
        """Load fee obligations into treeview with filters"""
        for item in self.obligation_tree.get_children():
            self.obligation_tree.delete(item)
        
        # Build query based on filters
        year_filter = self.obligation_year_filter.get()
        status_filter = self.obligation_status_filter.get()
        
        query = """
            SELECT sfo.obligation_id, sfo.academic_year, sfo.is_cleared, sfo.created_at,
                   s.student_id, s.full_name, s.reg_no, s.programme, s.year_of_study,
                   fs.description, fs.amount, fs.semester
            FROM student_fee_obligations sfo
            JOIN students s ON sfo.student_id = s.student_id
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE 1=1
        """
        
        params = []
        
        if year_filter and year_filter != "All":
            query += " AND sfo.academic_year = %s"
            params.append(year_filter)
        
        if status_filter == "Cleared":
            query += " AND sfo.is_cleared = 1"
        elif status_filter == "Not Cleared":
            query += " AND sfo.is_cleared = 0"
        
        query += " ORDER BY sfo.obligation_id DESC"
        
        results = execute_query(query, tuple(params) if params else None, fetch=True)
        
        if results:
            # Load academic years for filter if not loaded
            if not self.obligation_year_filter['values']:
                year_query = "SELECT DISTINCT academic_year FROM student_fee_obligations ORDER BY academic_year DESC"
                years = execute_query(year_query, fetch=True)
                year_options = ["All"]
                if years:
                    for y in years:
                        if y['academic_year']:
                            year_options.append(y['academic_year'])
                self.obligation_year_filter['values'] = year_options
                if year_options:
                    self.obligation_year_filter.current(0)
            
            for row in results:
                status = "Cleared" if row['is_cleared'] else "Not Cleared"
                date_str = row['created_at'].strftime('%Y-%m-%d') if row['created_at'] else 'N/A'
                
                self.obligation_tree.insert("", tk.END, values=(
                    row['obligation_id'],
                    row['full_name'],
                    row['reg_no'],
                    row['programme'],
                    row['year_of_study'],
                    row['description'] or 'Fee',
                    f"{float(row['amount']):,.2f}",
                    row['academic_year'] or 'N/A',
                    row['semester'] or 'N/A',
                    status,
                    date_str
                ))
        else:
            tk.Label(
                tab,
                text="No fee obligations found. Click 'Assign Fee to Students' to create obligations for students.",
                bg="#ecf0f1",
                fg="#7f8c8d",
                font=("Arial", 10)
            ).pack(pady=20)
    
    def assign_fee_obligation(self, parent):
        """Assign fee structure to students - creates fee obligations"""
        # Get fee structures
        fee_query = "SELECT * FROM fee_structures ORDER BY programme, year_of_study, semester"
        fee_structures = execute_query(fee_query, fetch=True)
        
        if not fee_structures:
            messagebox.showwarning("Warning", "No fee structures found. Please add fee structures first in the 'Fee Structures' tab.")
            return
        
        # Get students
        student_query = "SELECT * FROM students WHERE status = 'ACTIVE' ORDER BY programme, year_of_study, full_name"
        students = execute_query(student_query, fetch=True)
        
        if not students:
            messagebox.showwarning("Warning", "No active students found. Please add students first.")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Assign Fee Structure to Students")
        dialog.geometry("700x600")
        dialog.transient(self.parent)
        
        # Info
        info_label = tk.Label(
            dialog,
            text="Select a fee structure and assign it to students.\nThe system will match students by programme + year of study + semester.\nThis will create fee obligations for matching students.",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50",
            wraplength=650
        )
        info_label.pack(pady=10)
        
        # Main content frame
        content_frame = tk.Frame(dialog, bg="white")
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Left side - Fee Structure Selection
        left_frame = tk.LabelFrame(content_frame, text="1. Select Fee Structure", font=("Arial", 10, "bold"), padx=10, pady=10)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        
        # Fee structure list
        fee_columns = ("Programme", "Year", "Semester", "Amount")
        fee_list = ttk.Treeview(left_frame, columns=fee_columns, show="headings", height=10)
        
        for col in fee_columns:
            fee_list.heading(col, text=col)
            fee_list.column(col, width=80)
        
        fee_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        fee_map = {}
        for fs in fee_structures:
            key = f"{fs['programme']}_{fs['year_of_study']}_{fs['semester']}"
            fee_map[key] = fs['fee_id']
            fee_list.insert("", tk.END, values=(
                fs['programme'],
                fs['year_of_study'],
                fs['semester'],
                f"{float(fs['amount']):,.2f}"
            ))
        
        # Select first by default
        if fee_structures:
            fee_list.selection_set(fee_list.get_children()[0])
        
        # Right side - Academic Year and Preview
        right_frame = tk.LabelFrame(content_frame, text="2. Set Academic Year", font=("Arial", 10, "bold"), padx=10, pady=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))
        
        tk.Label(right_frame, text="Academic Year:", bg="white").pack(anchor="w")
        academic_year_entry = tk.Entry(right_frame, width=25)
        academic_year_entry.pack(pady=5, anchor="w")
        academic_year_entry.insert(0, "2024/2025")
        
        tk.Label(right_frame, text="Example: 2024/2025, 2025/2026", bg="white", fg="#7f8c8d", font=("Arial", 8)).pack(anchor="w")
        
        # Preview section
        preview_frame = tk.LabelFrame(right_frame, text="3. Preview Matching Students", font=("Arial", 10, "bold"), padx=10, pady=10)
        preview_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        preview_columns = ("Reg No", "Name", "Programme", "Year")
        preview_tree = ttk.Treeview(preview_frame, columns=preview_columns, show="headings", height=10)
        
        for col in preview_columns:
            preview_tree.heading(col, text=col)
            preview_tree.column(col, width=80)
        
        preview_tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        def update_preview(*args):
            """Update preview based on selected fee structure"""
            for item in preview_tree.get_children():
                preview_tree.delete(item)
            
            selected = fee_list.selection()
            if not selected:
                return
            
            item = fee_list.item(selected[0])
            prog, year, sem = item['values'][0], item['values'][1], item['values'][2]
            
            # Find matching students
            for s in students:
                if s['programme'] == prog and s['year_of_study'] == year:
                    preview_tree.insert("", tk.END, values=(
                        s['reg_no'],
                        s['full_name'][:20],
                        s['programme'][:15],
                        s['year_of_study']
                    ))
        
        fee_list.bind('<<SelectionChanged>>', update_preview)
        update_preview()  # Initial load
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg="white")
        btn_frame.pack(pady=15)
        
        def assign_to_all():
            """Assign fee structure to all matching students"""
            selected = fee_list.selection()
            if not selected:
                messagebox.showwarning("Warning", "Please select a fee structure")
                return
            
            item = fee_list.item(selected[0])
            prog, year, sem = item['values'][0], item['values'][1], item['values'][2]
            amount = item['values'][3]
            
            academic_year = academic_year_entry.get().strip()
            if not academic_year:
                messagebox.showerror("Error", "Please enter academic year")
                return
            
            fee_id = fee_map.get(f"{prog}_{year}_{sem}")
            
            if not fee_id:
                messagebox.showerror("Error", "Fee structure not found")
                return
            
            # Find students matching the fee structure
            matching_students = []
            for s in students:
                if s['programme'] == prog and s['year_of_study'] == year:
                    matching_students.append(s)
            
            if not matching_students:
                messagebox.showwarning("Warning", "No students match the selected fee structure (Programme: {}, Year: {})".format(prog, year))
                return
            
            # Check which students already have obligations for this fee
            existing_query = """
                SELECT student_id FROM student_fee_obligations 
                WHERE fee_id = %s AND academic_year = %s
            """
            existing = execute_query(existing_query, (fee_id, academic_year), fetch=True)
            existing_ids = [e['student_id'] for e in existing] if existing else []
            
            # Filter out students who already have this obligation
            new_students = [s for s in matching_students if s['student_id'] not in existing_ids]
            
            if not new_students:
                messagebox.showinfo("Info", f"All {len(matching_students)} students in this programme/year already have this fee obligation for {academic_year}.\n\nNo new obligations were created.")
                return
            
            # Confirm
            confirm = messagebox.askyesno(
                "Confirm Assignment",
                f"Create fee obligations for {len(new_students)} students?\n\n"
                f"Fee Structure: {prog} - Year {year} - {sem}\n"
                f"Amount: TZS {amount}\n"
                f"Academic Year: {academic_year}\n\n"
                f"{len(matching_students) - len(new_students)} students already have this obligation and will be skipped."
            )
            
            if not confirm:
                return
            
            # Create obligations
            conn = get_connection()
            if not conn:
                messagebox.showerror("Error", "Database connection failed")
                return
            
            try:
                cursor = conn.cursor()
                created_count = 0
                
                for s in new_students:
                    # Check if student already has obligation for this fee and year
                    check_query = """
                        SELECT obligation_id FROM student_fee_obligations 
                        WHERE student_id = %s AND fee_id = %s AND academic_year = %s
                    """
                    cursor.execute(check_query, (s['student_id'], fee_id, academic_year))
                    if cursor.fetchone():
                        continue  # Skip - already exists
                    
                    insert_query = """
                        INSERT INTO student_fee_obligations (student_id, fee_id, academic_year, is_cleared)
                        VALUES (%s, %s, %s, 0)
                    """
                    cursor.execute(insert_query, (s['student_id'], fee_id, academic_year))
                    created_count += 1
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Success", f"Successfully created {created_count} fee obligations!\n\nStudents can now view and pay their fees.")
                dialog.destroy()
                self.load_fee_obligations(parent)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to create obligations: {str(e)}")
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
        
        tk.Button(
            btn_frame,
            text="Assign to Matching Students",
            bg="#27ae60",
            fg="white",
            font=("Arial", 11, "bold"),
            command=assign_to_all,
            width=25,
            pady=10
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11),
            command=dialog.destroy,
            width=15,
            pady=10
        ).pack(side=tk.LEFT, padx=10)
    
    def delete_fee_obligation(self, parent):
        """Delete selected fee obligation"""
        selection = self.obligation_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a fee obligation to delete")
            return
        
        item = self.obligation_tree.item(selection[0])
        obligation_id = item['values'][0]
        student_name = item['values'][1]
        
        # Check if there are payments made
        check_query = """
            SELECT COUNT(*) as cnt FROM payments WHERE obligation_id = %s
        """
        payment_check = execute_query(check_query, (obligation_id,), fetch=True)
        
        if payment_check and payment_check[0]['cnt'] > 0:
            messagebox.showwarning("Warning", "Cannot delete this fee obligation. There are payments associated with it.")
            return
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the fee obligation for:\n\nStudent: {student_name}\nObligation ID: {obligation_id}\n\nThis action cannot be undone."
        )
        
        if confirm:
            query = "DELETE FROM student_fee_obligations WHERE obligation_id = %s"
            result = execute_query(query, (obligation_id,))
            
            if result:
                messagebox.showinfo("Success", "Fee obligation deleted successfully!")
                self.load_fee_obligations(parent)
            else:
                messagebox.showerror("Error", "Failed to delete fee obligation")
    
    def add_fee_structure(self, parent):
        """Add new fee structure"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Fee Structure")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        
        entries = {}
        
        fields = [
            ("Programme:", "programme"),
            ("Year of Study:", "year"),
            ("Amount:", "amount"),
            ("Description:", "description"),
        ]
        
        for i, (label, key) in enumerate(fields):
            tk.Label(dialog, text=label).grid(row=i, column=0, sticky="w", padx=10, pady=10)
            entry = tk.Entry(dialog, width=25)
            entry.grid(row=i, column=1, padx=10, pady=10)
            entries[key] = entry
        
        # Semester
        tk.Label(dialog, text="Semester:").grid(row=4, column=0, sticky="w", padx=10, pady=10)
        semester_var = tk.StringVar(value="SEM1")
        semester_combo = ttk.Combobox(dialog, textvariable=semester_var, values=["SEM1", "SEM2"], width=22)
        semester_combo.grid(row=4, column=1, padx=10, pady=10)
        
        def save():
            programme = entries['programme'].get().strip()
            year = entries['year'].get().strip()
            amount = entries['amount'].get().strip()
            description = entries['description'].get().strip()
            semester = semester_var.get()
            
            if not programme or not year or not amount:
                messagebox.showerror("Error", "Please fill required fields")
                return
            
            try:
                amount = float(amount)
                year = int(year)
            except ValueError:
                messagebox.showerror("Error", "Invalid number format")
                return
            
            query = """
                INSERT INTO fee_structures (programme, year_of_study, semester, amount, description)
                VALUES (%s, %s, %s, %s, %s)
            """
            result = execute_query(query, (programme, year, semester, amount, description))
            
            if result:
                messagebox.showinfo("Success", "Fee structure added successfully!")
                dialog.destroy()
                self.load_fee_structures(parent)
            else:
                messagebox.showerror("Error", "Failed to add fee structure")
        
        tk.Button(dialog, text="Save", command=save, bg="#27ae60", fg="white").grid(
            row=5, column=0, columnspan=2, pady=20
        )
    
    def load_exams(self, tab):
        """Load exams into treeview"""
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)
        
        query = "SELECT * FROM exams ORDER BY exam_id DESC"
        exams = execute_query(query, fetch=True)
        
        if exams:
            for exam in exams:
                start_date = exam['start_date'].strftime('%Y-%m-%d') if exam['start_date'] else 'Not set'
                end_date = exam['end_date'].strftime('%Y-%m-%d') if exam['end_date'] else 'Not set'
                
                # Get faculties for this exam
                fac_query = """
                    SELECT f.name 
                    FROM exam_faculties ef
                    JOIN faculties f ON ef.faculty_id = f.faculty_id
                    WHERE ef.exam_id = %s
                """
                faculties = execute_query(fac_query, (exam['exam_id'],), fetch=True)
                
                if faculties and len(faculties) > 0:
                    faculty_names = ", ".join([f['name'] for f in faculties])
                else:
                    faculty_names = "None selected"
                
                # Truncate if too long
                if len(faculty_names) > 40:
                    faculty_names = faculty_names[:40] + "..."
                
                self.exam_tree.insert("", tk.END, values=(
                    exam['exam_id'],
                    exam['exam_name'],
                    exam['semester'],
                    exam['academic_year'],
                    start_date,
                    end_date,
                    faculty_names
                ))
    
    def add_exam(self, parent):
        """Add new exam with faculty selection"""
        # First check if there are faculties
        faculties = execute_query("SELECT faculty_id, name FROM faculties ORDER BY name", fetch=True)
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Exam")
        dialog.geometry("500x500")
        dialog.transient(self.parent)
        
        # Info
        tk.Label(
            dialog,
            text="Create an exam and select which faculties will sit for it.\nThe system will automatically identify programmes in those faculties.",
            font=("Arial", 10),
            fg="#7f8c8d",
            wraplength=450
        ).pack(pady=10)
        
        # Form
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10)
        
        # Exam Name
        tk.Label(form_frame, text="Exam Name:", bg="white").grid(row=0, column=0, sticky="w", pady=10)
        exam_name_var = tk.StringVar(value="UE")
        exam_name_combo = ttk.Combobox(form_frame, textvariable=exam_name_var, values=["CAT1", "CAT2", "UE", "SEMESTER_EXAM"], width=28, state="readonly")
        exam_name_combo.grid(row=0, column=1, pady=10, padx=10)
        
        # Semester
        tk.Label(form_frame, text="Semester:", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        semester_var = tk.StringVar(value="SEM1")
        semester_combo = ttk.Combobox(form_frame, textvariable=semester_var, values=["SEM1", "SEM2"], width=28, state="readonly")
        semester_combo.grid(row=1, column=1, pady=10, padx=10)
        
        # Academic Year
        tk.Label(form_frame, text="Academic Year:", bg="white").grid(row=2, column=0, sticky="w", pady=10)
        year_entry = tk.Entry(form_frame, width=30)
        year_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Start Date
        tk.Label(form_frame, text="Start Date (YYYY-MM-DD):", bg="white").grid(row=3, column=0, sticky="w", pady=10)
        start_date_entry = tk.Entry(form_frame, width=30)
        start_date_entry.grid(row=3, column=1, pady=10, padx=10)
        
        # End Date
        tk.Label(form_frame, text="End Date (YYYY-MM-DD):", bg="white").grid(row=4, column=0, sticky="w", pady=10)
        end_date_entry = tk.Entry(form_frame, width=30)
        end_date_entry.grid(row=4, column=1, pady=10, padx=10)
        
        # Faculty Selection
        tk.Label(form_frame, text="Select Faculties:", bg="white").grid(row=5, column=0, sticky="nw", pady=10)
        
        # Faculty listbox with scrollbar
        faculty_frame = tk.Frame(form_frame)
        faculty_frame.grid(row=5, column=1, pady=10, padx=10)
        
        faculty_scroll = tk.Scrollbar(faculty_frame, orient=tk.VERTICAL)
        faculty_listbox = tk.Listbox(faculty_frame, selectmode=tk.MULTIPLE, height=6, width=30, yscrollcommand=faculty_scroll.set)
        faculty_scroll.config(command=faculty_listbox.yview)
        faculty_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        faculty_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        faculty_map = {}
        if faculties:
            for f in faculties:
                faculty_listbox.insert(tk.END, f['name'])
                faculty_map[f['name']] = f['faculty_id']
        else:
            tk.Label(faculty_frame, text="No faculties available", fg="red").pack()
        
        # "Select All" button
        tk.Button(
            form_frame,
            text="Select All",
            command=lambda: faculty_listbox.select_set(0, tk.END),
            font=("Arial", 8)
        ).grid(row=6, column=1, sticky="e", padx=10)
        
        def save():
            exam_name = exam_name_var.get()
            semester = semester_var.get()
            academic_year = year_entry.get().strip()
            start_date = start_date_entry.get().strip()
            end_date = end_date_entry.get().strip()
            
            if not academic_year:
                messagebox.showerror("Error", "Please enter academic year")
                return
            
            # Use a persistent connection to get LAST_INSERT_ID properly
            conn = get_connection()
            if not conn:
                messagebox.showerror("Error", "Database connection failed")
                return
            
            try:
                cursor = conn.cursor()
                
                # Insert exam
                insert_exam = """
                    INSERT INTO exams (exam_name, semester, academic_year, start_date, end_date)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_exam, (
                    exam_name, 
                    semester, 
                    academic_year, 
                    start_date if start_date else None,
                    end_date if end_date else None
                ))
                
                # Get the new exam_id using the same connection
                cursor.execute("SELECT LAST_INSERT_ID() as exam_id")
                exam_id_result = cursor.fetchone()
                
                if not exam_id_result:
                    messagebox.showerror("Error", "Failed to get exam ID")
                    return
                
                exam_id = exam_id_result[0]
                
                # Get selected faculties
                selected_indices = faculty_listbox.curselection()
                if selected_indices:
                    for idx in selected_indices:
                        faculty_name = faculty_listbox.get(idx)
                        faculty_id = faculty_map.get(faculty_name)
                        if faculty_id:
                            # Insert into exam_faculties
                            insert_faculty = "INSERT INTO exam_faculties (exam_id, faculty_id) VALUES (%s, %s)"
                            cursor.execute(insert_faculty, (exam_id, faculty_id))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Success", f"Exam '{exam_name}' added successfully!\n\nSelected faculties will sit for this exam.")
                dialog.destroy()
                self.load_exams(parent)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add exam: {str(e)}")
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
        
        tk.Button(
            dialog,
            text="Save Exam",
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).pack(pady=20)
    
    def delete_exam(self, parent):
        """Delete selected exam"""
        selection = self.exam_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an exam to delete")
            return
        
        item = self.exam_tree.item(selection[0])
        exam_id = item['values'][0]
        exam_name = item['values'][1]
        
        # Confirm deletion
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete exam '{exam_name}' (ID: {exam_id})?\n\nThis action cannot be undone."
        )
        
        if confirm:
            # Delete exam_faculties first (due to foreign key)
            delete_faculties = "DELETE FROM exam_faculties WHERE exam_id = %s"
            execute_query(delete_faculties, (exam_id,))
            
            query = "DELETE FROM exams WHERE exam_id = %s"
            result = execute_query(query, (exam_id,))
            
            if result:
                messagebox.showinfo("Success", "Exam deleted successfully!")
                self.load_exams(parent)
            else:
                messagebox.showerror("Error", "Failed to delete exam")
    
    def payment_summary_report(self):
        """Show payment summary report"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Payment Summary Report")
        dialog.geometry("800x500")
        
        # Treeview
        tree = ttk.Treeview(dialog, columns=("Student", "Total Required", "Total Paid", "Balance"), show="headings")
        tree.heading("Student", text="Student Name")
        tree.heading("Total Required", text="Total Required")
        tree.heading("Total Paid", text="Total Paid")
        tree.heading("Balance", text="Balance")
        
        for col in tree["columns"]:
            tree.column(col, width=150)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        query = """
            SELECT s.full_name, 
                   COALESCE(SUM(fs.amount), 0) as total_required,
                   COALESCE(SUM(p.amount_paid), 0) as total_paid
            FROM students s
            LEFT JOIN student_fee_obligations sfo ON s.student_id = sfo.student_id
            LEFT JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id
            GROUP BY s.student_id
        """
        
        results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                balance = float(row['total_required']) - float(row['total_paid'])
                tree.insert("", tk.END, values=(
                    row['full_name'],
                    f"{row['total_required']:.2f}",
                    f"{row['total_paid']:.2f}",
                    f"{balance:.2f}"
                ))
    
    def student_fee_status_report(self):
        """Show student fee status report"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Student Fee Status Report")
        dialog.geometry("900x500")
        
        # Treeview
        columns = ("Reg No", "Name", "Programme", "Year", "Academic Year", "Amount", "Paid", "Balance", "Status")
        tree = ttk.Treeview(dialog, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        query = """
            SELECT s.reg_no, s.full_name, s.programme, s.year_of_study,
                   sfo.academic_year, fs.amount,
                   COALESCE(SUM(p.amount_paid), 0) as total_paid,
                   sfo.is_cleared
            FROM students s
            JOIN student_fee_obligations sfo ON s.student_id = sfo.student_id
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id
            GROUP BY sfo.obligation_id
            ORDER BY s.student_id
        """
        
        results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                balance = float(row['amount']) - float(row['total_paid'])
                status = "Cleared" if row['is_cleared'] else "Not Cleared"
                tree.insert("", tk.END, values=(
                    row['reg_no'],
                    row['full_name'],
                    row['programme'],
                    row['year_of_study'],
                    row['academic_year'],
                    f"{row['amount']:.2f}",
                    f"{row['total_paid']:.2f}",
                    f"{balance:.2f}",
                    status
                ))
    
    def exam_clearance_report(self):
        """Show exam clearance report"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Exam Clearance Report")
        dialog.geometry("850x500")
        
        # Treeview
        columns = ("Student", "Exam Name", "Semester", "Academic Year", "Eligibility", "Reason")
        tree = ttk.Treeview(dialog, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=140)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        query = """
            SELECT s.full_name, e.exam_name, e.semester, e.academic_year,
                  efe.eligibility_status, efe.reason
            FROM v_exam_financial_eligibility efe
            JOIN students s ON efe.student_id = s.student_id
            JOIN exams e ON efe.exam_id = e.exam_id
        """
        
        results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                tree.insert("", tk.END, values=(
                    row['full_name'],
                    row['exam_name'],
                    row['semester'],
                    row['academic_year'],
                    row['eligibility_status'],
                    row['reason']
                ))
    
    def verification_report(self):
        """Show finance verification report"""
        dialog = tk.Toplevel(self.parent)
        dialog.title("Finance Verification Report")
        dialog.geometry("900x500")
        
        # Treeview
        columns = ("Student", "Academic Year", "Verified By", "Decision", "Comment", "Date")
        tree = ttk.Treeview(dialog, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=130)
        
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        query = """
            SELECT s.full_name, sfo.academic_year, fv.verified_by,
                   fv.decision, fv.comment, fv.verified_at
            FROM finance_verifications fv
            JOIN student_fee_obligations sfo ON fv.obligation_id = sfo.obligation_id
            JOIN students s ON sfo.student_id = s.student_id
            WHERE fv.is_final = 1
            ORDER BY fv.verified_at DESC
        """
        
        results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                date_str = row['verified_at'].strftime('%Y-%m-%d %H:%M') if row['verified_at'] else ''
                tree.insert("", tk.END, values=(
                    row['full_name'],
                    row['academic_year'],
                    row['verified_by'] or 'N/A',
                    row['decision'],
                    row['comment'] or '',
                    date_str
                ))

