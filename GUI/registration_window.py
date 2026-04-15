"""
Registration Window for KIUT Fee Tracker
Allows new users to register with secure password hashing
"""
import tkinter as tk
from tkinter import ttk, messagebox
import hashlib
from GUI.db_config import execute_query


class RegistrationWindow:
    """Registration window for new users"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the registration UI"""
        # Main frame
        main_frame = tk.Frame(self.parent, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="KIUT Fee Tracker - Registration",
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=20)
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack(pady=20)
        
        # Username (Registration Number)
        tk.Label(
            form_frame,
            text="Registration No:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=0, column=0, sticky="w", pady=10)
        
        self.reg_no_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
        self.reg_no_entry.grid(row=0, column=1, pady=10, padx=10)
        
        # Full Name
        tk.Label(
            form_frame,
            text="Full Name:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=1, column=0, sticky="w", pady=10)
        
        self.full_name_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
        self.full_name_entry.grid(row=1, column=1, pady=10, padx=10)
        
        # Programme
        tk.Label(
            form_frame,
            text="Programme:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=2, column=0, sticky="w", pady=10)
        
        self.programme_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
        self.programme_entry.grid(row=2, column=1, pady=10, padx=10)
        
        # Year of Study
        tk.Label(
            form_frame,
            text="Year of Study:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=3, column=0, sticky="w", pady=10)
        
        self.year_var = tk.StringVar(value="1")
        year_combo = ttk.Combobox(
            form_frame, 
            textvariable=self.year_var,
            values=["1", "2", "3", "4", "5"],
            width=23,
            state="readonly"
        )
        year_combo.grid(row=3, column=1, pady=10, padx=10)
        
        # Password
        tk.Label(
            form_frame,
            text="Password:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=4, column=0, sticky="w", pady=10)
        
        self.password_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.grid(row=4, column=1, pady=10, padx=10)
        
        # Confirm Password
        tk.Label(
            form_frame,
            text="Confirm Password:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=5, column=0, sticky="w", pady=10)
        
        self.confirm_password_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, show="*")
        self.confirm_password_entry.grid(row=5, column=1, pady=10, padx=10)
        
        # Role selection - Only students can self-register
        # Finance and Admin accounts must be created by Admin
        tk.Label(
            form_frame,
            text="Role:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=6, column=0, sticky="w", pady=10)
        
        self.role_var = tk.StringVar(value="student")
        role_frame = tk.Frame(form_frame, bg="#f0f0f0")
        role_frame.grid(row=6, column=1, pady=10, padx=10, sticky="w")
        
        # Only allow student registration for security
        # Admin and Finance accounts are created by Admin
        tk.Label(
            role_frame,
            text="Student",
            font=("Arial", 11, "bold"),
            bg="#f0f0f0",
            fg="#27ae60"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            role_frame,
            text="(Finance & Admin accounts are created by Administrator)",
            font=("Arial", 9),
            bg="#f0f0f0",
            fg="#7f8c8d"
        ).pack(side=tk.LEFT, padx=10)
        
        # Register button
        register_btn = tk.Button(
            main_frame,
            text="Register",
            font=("Arial", 12, "bold"),
            bg="#27ae60",
            fg="white",
            width=15,
            height=2,
            command=self.register
        )
        register_btn.pack(pady=20)
        
        # Login link
        login_frame = tk.Frame(main_frame, bg="#f0f0f0")
        login_frame.pack(pady=10)
        
        tk.Label(
            login_frame,
            text="Already have an account?",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)
        
        login_link = tk.Label(
            login_frame,
            text="Login here",
            font=("Arial", 10, "underline"),
            bg="#f0f0f0",
            fg="#3498db",
            cursor="hand2"
        )
        login_link.pack(side=tk.LEFT, padx=5)
        login_link.bind("<Button-1>", lambda e: self.app.show_login())
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register(self):
        """Handle registration"""
        # Get all form values
        reg_no = self.reg_no_entry.get().strip()
        full_name = self.full_name_entry.get().strip()
        programme = self.programme_entry.get().strip()
        year = self.year_var.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()
        role = self.role_var.get()
        
        # Validation
        if not reg_no or not full_name or not programme or not password:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if len(reg_no) < 3:
            messagebox.showerror("Error", "Registration number must be at least 3 characters")
            return
        
        if len(full_name) < 3:
            messagebox.showerror("Error", "Full name must be at least 3 characters")
            return
        
        if len(programme) < 2:
            messagebox.showerror("Error", "Please enter a valid programme")
            return
        
        if len(password) < 4:
            messagebox.showerror("Error", "Password must be at least 4 characters")
            return
        
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        # Check if username (reg_no) already exists in users table
        check_query = "SELECT id FROM users WHERE username = %s"
        existing_user = execute_query(check_query, (reg_no,), fetch=True)
        
        if existing_user:
            messagebox.showerror("Error", "A user with this registration number already exists. Please contact administrator if this is your correct number.")
            return
        
        # Check if student with this reg_no already exists
        check_student_query = "SELECT student_id FROM students WHERE reg_no = %s"
        existing_student = execute_query(check_student_query, (reg_no,), fetch=True)
        
        # Hash password
        hashed_password = self.hash_password(password)
        
        # Insert new user
        insert_user_query = "INSERT INTO users (username, password, role) VALUES (%s, %s, %s)"
        user_result = execute_query(insert_user_query, (reg_no, hashed_password, role))
        
        if not user_result:
            messagebox.showerror("Error", "Failed to create user account. Please try again.")
            return
        
        # Get the user_id we just created
        user_id_result = execute_query("SELECT LAST_INSERT_ID() as id", fetch=True)
        if not user_id_result:
            messagebox.showerror("Error", "Failed to get user ID. Please try again.")
            return
        user_id = user_id_result[0]['id']
        
        # Now create student record linked to this user
        if existing_student:
            # Student exists but user didn't - link them
            update_query = "UPDATE students SET user_id = %s WHERE reg_no = %s"
            execute_query(update_query, (user_id, reg_no))
        else:
            # Create new student record linked to user
            insert_student_query = """
                INSERT INTO students (reg_no, full_name, programme, year_of_study, status, user_id)
                VALUES (%s, %s, %s, %s, 'ACTIVE', %s)
            """
            student_result = execute_query(insert_student_query, (reg_no, full_name, programme, year, user_id))
            
            if not student_result:
                # Rollback: delete the user we just created
                execute_query("DELETE FROM users WHERE id = %s", (user_id,))
                messagebox.showerror("Error", "Failed to create student profile. Please try again.")
                return
        
        messagebox.showinfo("Success", "Registration successful! Your profile is now linked to your student record. Please login.")
        self.app.show_login()

