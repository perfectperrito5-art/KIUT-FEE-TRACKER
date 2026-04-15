"""
Main GUI Application for KIUT Fee Tracker
Entry point for the Tkinter GUI
"""
import tkinter as tk
from tkinter import messagebox
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from GUI.login_window import LoginWindow
from GUI.registration_window import RegistrationWindow


class FeeTrackerApp:
    """Main application class"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("KIUT Fee Tracker")
        self.root.geometry("900x600")
        self.root.configure(bg="#f0f0f0")
        
        # Center the window
        self.center_window()
        
        # Current logged in user
        self.current_user = None
        
        # Show login window first
        self.show_login()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def show_login(self):
        """Show login window"""
        self.clear_window()
        LoginWindow(self.root, self)
    
    def show_registration(self):
        """Show registration window"""
        self.clear_window()
        RegistrationWindow(self.root, self)
    
    def show_dashboard(self, user_data):
        """Show appropriate dashboard based on user role"""
        self.current_user = user_data
        self.clear_window()
        
        role = user_data['role']
        
        if role == 'admin':
            from GUI.admin_dashboard import AdminDashboard
            AdminDashboard(self.root, self)
        elif role == 'finance':
            from GUI.finance_dashboard import FinanceDashboard
            FinanceDashboard(self.root, self)
        elif role == 'student':
            from GUI.student_dashboard import StudentDashboard
            StudentDashboard(self.root, self)
        else:
            messagebox.showerror("Error", "Unknown user role")
            self.show_login()
    
    def clear_window(self):
        """Clear all widgets from window"""
        for widget in self.root.winfo_children():
            widget.destroy()
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.show_login()
    
    def run(self):
        """Run the application"""
        self.root.mainloop()


def main():
    """Main entry point"""
    app = FeeTrackerApp()
    app.run()


if __name__ == "__main__":
    main()

