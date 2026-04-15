"""
Login Window for KIUT Fee Tracker
Secure login with password hashing
"""
import tkinter as tk
from tkinter import messagebox
import hashlib
from GUI.db_config import execute_query


class LoginWindow:
    """Login window for existing users"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the login UI"""
        # Main frame
        main_frame = tk.Frame(self.parent, bg="#f0f0f0")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="KIUT Fee Tracker",
            font=("Arial", 28, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=30)
        
        subtitle_label = tk.Label(
            main_frame,
            text="Login to your account",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#7f8c8d"
        )
        subtitle_label.pack(pady=10)
        
        # Form frame
        form_frame = tk.Frame(main_frame, bg="#f0f0f0")
        form_frame.pack(pady=30)
        
        # Username
        tk.Label(
            form_frame,
            text="Registration number:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=0, column=0, sticky="e", pady=15, padx=10)
        
        self.username_entry = tk.Entry(form_frame, font=("Arial", 12), width=25)
        self.username_entry.grid(row=0, column=1, pady=15, padx=10)
        
        # Password
        tk.Label(
            form_frame,
            text="Password:",
            font=("Arial", 12),
            bg="#f0f0f0"
        ).grid(row=1, column=0, sticky="e", pady=15, padx=10)
        
        self.password_entry = tk.Entry(form_frame, font=("Arial", 12), width=25, show="*")
        self.password_entry.grid(row=1, column=1, pady=15, padx=10)
        
        # Login button
        login_btn = tk.Button(
            main_frame,
            text="Login",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            width=15,
            height=2,
            command=self.login
        )
        login_btn.pack(pady=20)
        
        # Register link
        register_frame = tk.Frame(main_frame, bg="#f0f0f0")
        register_frame.pack(pady=10)
        
        tk.Label(
            register_frame,
            text="Don't have an account?",
            font=("Arial", 10),
            bg="#f0f0f0"
        ).pack(side=tk.LEFT)
        
        register_link = tk.Label(
            register_frame,
            text="Register here",
            font=("Arial", 10, "underline"),
            bg="#f0f0f0",
            fg="#3498db",
            cursor="hand2"
        )
        register_link.pack(side=tk.LEFT, padx=5)
        register_link.bind("<Button-1>", lambda e: self.app.show_registration())
        
        # Bind Enter key to login
        self.password_entry.bind("<Return>", lambda e: self.login())
        self.username_entry.bind("<Return>", lambda e: self.login())
    
    def hash_password(self, password):
        """Hash password using SHA256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def login(self):
        """Handle login"""
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter username and password")
            return
        
        # Hash the password
        hashed_password = self.hash_password(password)
        
        # Check credentials
        query = "SELECT id, username, role FROM users WHERE username = %s AND password = %s"
        result = execute_query(query, (username, hashed_password), fetch=True)
        
        if result:
            user_data = {
                'id': result[0]['id'],
                'username': result[0]['username'],
                'role': result[0]['role']
            }
            self.app.show_dashboard(user_data)
        else:
            messagebox.showerror("Error", "Invalid username or password")
            self.password_entry.delete(0, tk.END)

