"""
Clean Student Profile View for KIUT Fee Tracker
Integrated into dashboard with compact, responsive card-based layout
"""
import tkinter as tk
from tkinter import ttk, messagebox
from GUI.db_config import execute_query


class StudentProfileFrame:
    """Integrated student profile frame for the dashboard"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.user = app.current_user
        self.student_id = self.get_student_id()
        self.setup_ui()
        self.load_data()
    
    def get_student_id(self):
        """Get student ID for current user using user_id link"""
        # First, try to find by user_id (the proper way after migration)
        query = "SELECT student_id FROM students WHERE user_id = %s"
        result = execute_query(query, (self.user['id'],), fetch=True)
        
        if result:
            return result[0]['student_id']
        
        # Fallback: try to find by reg_no (for old accounts before migration)
        query = "SELECT student_id FROM students WHERE reg_no = %s"
        result = execute_query(query, (self.user['username'],), fetch=True)
        
        if result:
            return result[0]['student_id']
        
        # No match found - student profile not linked
        return None
    
    def setup_ui(self):
        """Setup compact profile UI"""
        # Main container with canvas for potential scrolling
        main_frame = tk.Frame(self.parent, bg="#ecf0f1")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # === Compact Header with Info ===
        header_frame = tk.Frame(main_frame, bg="#8e44ad", pady=5, padx=10)
        header_frame.pack(fill=tk.X)
        
        # Left: Initials + Name + Reg (all inline)
        left_header = tk.Frame(header_frame, bg="#8e44ad")
        left_header.pack(side=tk.LEFT)
        
        # Compact Initials (smaller size)
        self.initials_label = tk.Label(
            left_header,
            text="ST",
            font=("Arial", 11, "bold"),
            bg="#9b59b6",
            fg="white",
            width=4,
            height=1,
            relief=tk.RAISED
        )
        self.initials_label.pack(side=tk.LEFT, padx=(0, 8))
        
        # Name and Reg info
        info_frame = tk.Frame(left_header, bg="#8e44ad")
        info_frame.pack(side=tk.LEFT)
        
        # Name row with status inline
        name_row = tk.Frame(info_frame, bg="#8e44ad")
        name_row.pack(anchor="w")
        
        self.name_label = tk.Label(
            name_row,
            text="Student Name",
            font=("Arial", 11, "bold"),
            bg="#8e44ad",
            fg="white"
        )
        self.name_label.pack(side=tk.LEFT)
        
        # Status badge (inline with name)
        self.status_label = tk.Label(
            name_row,
            text="ACTIVE",
            font=("Arial", 8, "bold"),
            bg="#27ae60",
            fg="white",
            padx=6,
            pady=1
        )
        self.status_label.pack(side=tk.LEFT, padx=8)
        
        # Registration number
        self.reg_label = tk.Label(
            info_frame,
            text="Reg No: -",
            font=("Arial", 9),
            bg="#8e44ad",
            fg="#d5c4e8"
        )
        self.reg_label.pack(anchor="w")
        
        # === Stats Row (4 compact cards) ===
        stats_frame = tk.Frame(main_frame, bg="#ecf0f1", pady=10)
        stats_frame.pack(fill=tk.X)
        
        stats_frame.columnconfigure(0, weight=1)
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(2, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        
        # Create stat cards
        self.create_stat_card(stats_frame, "Total Due", "TZS 0", "#e74c3c", 0)
        self.create_stat_card(stats_frame, "Total Paid", "TZS 0", "#27ae60", 1)
        self.create_stat_card(stats_frame, "Balance", "TZS 0", "#f39c12", 2)
        self.create_stat_card(stats_frame, "Eligibility", "Pending", "#9b59b6", 3)
        
        # === Two Column Layout ===
        content_frame = tk.Frame(main_frame, bg="#ecf0f1")
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=2)
        
        # === Left Column: Personal Info Card ===
        left_col = tk.Frame(content_frame, bg="#ecf0f1")
        left_col.grid(row=0, column=0, sticky="nsew", padx=(0, 2))
        
        self.personal_card = self.create_compact_card(left_col, "Personal Information")
        
        # === Right Column: Payments & Obligations ===
        right_col = tk.Frame(content_frame, bg="#ecf0f1")
        right_col.grid(row=0, column=1, sticky="nsew", padx=(2, 0))
        
        # Obligations card
        obligations_card = self.create_compact_card(right_col, "Fee Obligations")
        self.obligations_tree = self.create_treeview(
            obligations_card,
            ("ID", "Academic Year", "Description", "Amount", "Paid", "Balance", "Status"),
            height=5
        )
        
        # Payments card
        payments_card = self.create_compact_card(right_col, "Recent Payments")
        self.payments_tree = self.create_treeview(
            payments_card,
            ("Date", "Amount", "Method", "Reference", "Status"),
            height=4
        )
        
        # Exam eligibility card
        exam_card = self.create_compact_card(right_col, "Exam Eligibility")
        self.exam_tree = self.create_treeview(
            exam_card,
            ("Exam", "Semester", "Year", "Status"),
            height=4
        )
    
    def create_stat_card(self, parent, title, value, color, column):
        """Create a compact stat card"""
        card = tk.Frame(parent, bg="white", relief=tk.FLAT, borderwidth=1)
        card.grid(row=0, column=column, padx=5, sticky="ew")
        
        # Color indicator
        color_bar = tk.Frame(card, bg=color, height=3)
        color_bar.pack(fill=tk.X)
        
        # Title
        tk.Label(
            card,
            text=title,
            font=("Arial", 9),
            bg="white",
            fg="#7f8c8d"
        ).pack(pady=(5, 0))
        
        # Value
        value_label = tk.Label(
            card,
            text=value,
            font=("Arial", 11, "bold"),
            bg="white",
            fg=color
        )
        value_label.pack(pady=2)
        
        return value_label
    
    def create_compact_card(self, parent, title):
        """Create a compact card container"""
        card = tk.Frame(parent, bg="white", relief=tk.FLAT, borderwidth=1)
        card.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Title bar
        title_bar = tk.Frame(card, bg="#34495e")
        title_bar.pack(fill=tk.X)
        
        tk.Label(
            title_bar,
            text=title,
            font=("Arial", 10, "bold"),
            bg="#34495e",
            fg="white",
            pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        # Content frame
        content = tk.Frame(card, bg="white", padx=5, pady=5)
        content.pack(fill=tk.BOTH, expand=True)
        
        return content
    
    def create_treeview(self, parent, columns, height):
        """Create a compact treeview"""
        tree = ttk.Treeview(parent, columns=columns, show="headings", height=height)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=80)
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=scrollbar.set)
        
        return tree
    
    def load_data(self):
        """Load all student data"""
        if not self.student_id:
            self.show_no_data_message()
            return
        
        self.load_student_info()
        self.load_financial_summary()
        self.load_obligations()
        self.load_payments()
        self.load_exam_eligibility()
    
    def show_no_data_message(self):
        """Show message when no student data is found"""
        for widget in self.parent.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.parent,
            text="No student profile found.\nPlease contact administrator.",
            font=("Arial", 14),
            bg="#ecf0f1",
            fg="#e74c3c",
            pady=50
        ).pack()
    
    def load_student_info(self):
        """Load and display student personal information"""
        query = """
            SELECT * FROM students WHERE student_id = %s
        """
        results = execute_query(query, (self.student_id,), fetch=True)
        
        if results:
            self.student_data = results[0]
            
            # Update header
            name = self.student_data['full_name']
            self.name_label.config(text=name)
            self.initials_label.config(text=self.get_initials(name))
            self.reg_label.config(text=f"Reg No: {self.student_data['reg_no']}")
            
            # Update status badge
            status = self.student_data['status']
            self.status_label.config(text=status)
            
            if status == 'ACTIVE':
                self.status_label.config(bg="#27ae60")
            elif status == 'SUSPENDED':
                self.status_label.config(bg="#e74c3c")
            else:
                self.status_label.config(bg="#3498db")
            
            # Update personal info card
            fields = [
                ("Programme:", self.student_data['programme']),
                ("Year:", f"Year {self.student_data['year_of_study']}"),
                ("Reg No:", self.student_data['reg_no']),
                ("Status:", self.student_data['status']),
            ]
            
            for widget in self.personal_card.winfo_children():
                widget.destroy()
            
            for i, (label, value) in enumerate(fields):
                row = tk.Frame(self.personal_card, bg="white")
                row.pack(fill=tk.X, pady=2)
                
                tk.Label(
                    row,
                    text=label,
                    font=("Arial", 9),
                    bg="white",
                    fg="#7f8c8d",
                    width=10,
                    anchor="w"
                ).pack(side=tk.LEFT)
                
                tk.Label(
                    row,
                    text=value,
                    font=("Arial", 9, "bold"),
                    bg="white",
                    fg="#2c3e50"
                ).pack(side=tk.LEFT)
    
    def get_initials(self, name):
        """Get initials from name"""
        words = name.split()
        if len(words) >= 2:
            return f"{words[0][0]}{words[1][0]}".upper()
        return name[:2].upper() if name else "ST"
    
    def load_financial_summary(self):
        """Load and display financial summary"""
        query = """
            SELECT 
                SUM(fs.amount) as total_due,
                COALESCE(SUM(p.amount_paid), 0) as total_paid,
                COUNT(DISTINCT sfo.obligation_id) as total_obligations,
                SUM(CASE WHEN sfo.is_cleared = 1 THEN 1 ELSE 0 END) as cleared_count
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id
            WHERE sfo.student_id = %s
            GROUP BY sfo.student_id
        """
        
        results = execute_query(query, (self.student_id,), fetch=True)
        
        if results:
            row = results[0]
            total_due = float(row['total_due'] or 0)
            total_paid = float(row['total_paid'] or 0)
            balance = total_due - total_paid
            
            # Update stat cards
            self.stat_due_val = total_due
            self.stat_paid_val = total_paid
            
            # Find and update stat card values (they're stored in the frame)
            # We'll update via load_obligations
    
    def load_obligations(self):
        """Load fee obligations"""
        for item in self.obligations_tree.get_children():
            self.obligations_tree.delete(item)
        
        query = """
            SELECT sfo.obligation_id, sfo.academic_year, fs.description, fs.amount,
                   COALESCE(SUM(p.amount_paid), 0) as total_paid, sfo.is_cleared
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id
            WHERE sfo.student_id = %s
            GROUP BY sfo.obligation_id
            ORDER BY sfo.academic_year DESC
        """
        
        results = execute_query(query, (self.student_id,), fetch=True)
        
        total_due = 0
        total_paid = 0
        
        if results:
            for row in results:
                amount = float(row['amount'])
                paid = float(row['total_paid'])
                balance = amount - paid
                
                total_due += amount
                total_paid += paid
                
                status = "Cleared" if row['is_cleared'] else "Pending"
                
                self.obligations_tree.insert("", tk.END, values=(
                    row['obligation_id'],
                    row['academic_year'],
                    (row['description'] or 'Fee')[:20],
                    f"{amount:,.0f}",
                    f"{paid:,.0f}",
                    f"{balance:,.0f}",
                    status
                ))
        
        # Update summary stats
        self.update_stat_cards(total_due, total_paid)
    
    def update_stat_cards(self, total_due, total_paid):
        """Update the stat card values"""
        balance = total_due - total_paid
        
        # Find and update stat labels
        for widget in self.parent.winfo_children():
            self._update_stats_recursive(widget, total_due, total_paid, balance)
    
    def _update_stats_recursive(self, widget, total_due, total_paid, balance):
        """Recursively find and update stat labels"""
        try:
            for child in widget.winfo_children():
                if isinstance(child, tk.Frame):
                    # Check if this is a stat card
                    for subchild in child.winfo_children():
                        if hasattr(subchild, 'cget'):
                            try:
                                text = subchild.cget('text')
                                if text == "Total Due":
                                    # Find the value label in the same frame
                                    for label in child.winfo_children():
                                        if isinstance(label, tk.Label) and hasattr(label, 'cget'):
                                            if 'bold' in label.cget('font'):
                                                label.config(text=f"TZS {total_due:,.0f}")
                                elif text == "Total Paid":
                                    for label in child.winfo_children():
                                        if isinstance(label, tk.Label) and hasattr(label, 'cget'):
                                            if 'bold' in label.cget('font'):
                                                label.config(text=f"TZS {total_paid:,.0f}")
                                elif text == "Balance":
                                    for label in child.winfo_children():
                                        if isinstance(label, tk.Label) and hasattr(label, 'cget'):
                                            if 'bold' in label.cget('font'):
                                                color = "#27ae60" if balance <= 0 else "#e74c3c"
                                                label.config(text=f"TZS {balance:,.0f}", fg=color)
                            except:
                                pass
                self._update_stats_recursive(child, total_due, total_paid, balance)
        except:
            pass
    
    def load_payments(self):
        """Load recent payments"""
        for item in self.payments_tree.get_children():
            self.payments_tree.delete(item)
        
        query = """
            SELECT p.payment_id, p.amount_paid, p.payment_date, p.method, 
                   p.reference_no, p.receipt_checked
            FROM payments p
            JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
            WHERE sfo.student_id = %s
            ORDER BY p.payment_date DESC
            LIMIT 5
        """
        
        results = execute_query(query, (self.student_id,), fetch=True)
        
        if results:
            for row in results:
                status = "✓ Verified" if row['receipt_checked'] == 1 else "⏳ Pending"
                status_color = "#27ae60" if row['receipt_checked'] == 1 else "#f39c12"
                
                self.payments_tree.insert("", tk.END, values=(
                    str(row['payment_date']),
                    f"{float(row['amount_paid']):,.0f}",
                    row['method'],
                    (row['reference_no'] or 'N/A')[:15],
                    status
                ))
    
    def load_exam_eligibility(self):
        """Load exam eligibility status with amount remaining"""
        for item in self.exam_tree.get_children():
            self.exam_tree.delete(item)
        
        # Check if exam_clearance_fees table exists
        check_query = """
            SELECT COUNT(*) as cnt 
            FROM information_schema.tables 
            WHERE table_schema = 'My_Financials' AND table_name = 'exam_clearance_fees'
        """
        table_exists = execute_query(check_query, fetch=True)
        
        if table_exists and table_exists[0]['cnt'] > 0:
            # First get student's programme and year_of_study (students table has 'programme' not 'programme_id')
            student_query = "SELECT programme, year_of_study FROM students WHERE student_id = %s"
            student_data = execute_query(student_query, (self.student_id,), fetch=True)
            programme_name = student_data[0]['programme'] if student_data else None
            year_of_study = student_data[0]['year_of_study'] if student_data else None
            
            # Get programme_id from programmes table using programme name
            programme_id = None
            if programme_name:
                prog_query = "SELECT programme_id FROM programmes WHERE name = %s"
                prog_result = execute_query(prog_query, (programme_name,), fetch=True)
                programme_id = prog_result[0]['programme_id'] if prog_result else None
            
            if not programme_id:
                self.exam_tree.insert("", tk.END, values=("-", "-", "-", "Programme not set"))
                self.update_eligibility_stat(0, 1)
                return
            
            # Use new query with exam clearance fees - filtered by student's programme AND year
            query = """
                SELECT 
                    e.exam_name,
                    e.semester, 
                    e.academic_year,
                    ecf.exam_fee_amount,
                    COALESCE(SUM(p.amount_paid), 0) as total_paid,
                    CASE 
                        WHEN ecf.exam_fee_amount IS NULL THEN 'NOT_SET'
                        WHEN COALESCE(SUM(p.amount_paid), 0) >= ecf.exam_fee_amount THEN 'ELIGIBLE'
                        ELSE 'NOT_ELIGIBLE'
                    END AS eligibility_status,
                    CASE 
                        WHEN ecf.exam_fee_amount IS NULL THEN 0
                        ELSE GREATEST(0, ecf.exam_fee_amount - COALESCE(SUM(p.amount_paid), 0))
                    END AS amount_remaining
                FROM exams e
                INNER JOIN exam_clearance_fees ecf ON e.exam_name = ecf.exam_name 
                    AND e.semester = ecf.semester 
                    AND e.academic_year = ecf.academic_year
                    AND (ecf.programme_id = %s OR ecf.programme_id IS NULL)
                    AND (ecf.year_of_study = %s OR ecf.year_of_study IS NULL)
                LEFT JOIN student_fee_obligations sfo ON sfo.student_id = %s
                LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id AND p.receipt_checked = 1
                GROUP BY e.exam_id, e.exam_name, e.semester, e.academic_year, ecf.exam_fee_amount
                ORDER BY e.academic_year DESC, e.semester
                LIMIT 5
            """
            results = execute_query(query, (programme_id, year_of_study, self.student_id), fetch=True)
        else:
            # Fallback to old method
            query = """
                SELECT e.exam_name, e.semester, e.academic_year, efe.eligibility_status, efe.reason
                FROM v_exam_financial_eligibility efe
                JOIN exams e ON efe.exam_id = e.exam_id
                WHERE efe.student_id = %s
                ORDER BY e.academic_year DESC, e.semester
                LIMIT 5
            """
            results = execute_query(query, (self.student_id,), fetch=True)
            
            # Convert to new format
            if results:
                new_results = []
                for row in results:
                    new_results.append({
                        'exam_name': row.get('exam_name', 'UE'),
                        'semester': row['semester'],
                        'academic_year': row['academic_year'],
                        'exam_fee_amount': 0,
                        'total_paid': 0,
                        'eligibility_status': row['eligibility_status'],
                        'amount_remaining': 0
                    })
                results = new_results
        
        if results:
            eligible_count = 0
            for row in results:
                eligibility = row.get('eligibility_status', 'UNKNOWN')
                amount_remaining = float(row.get('amount_remaining', 0) or 0)
                
                if eligibility == 'ELIGIBLE':
                    eligible_count += 1
                    status_display = "Eligible"
                elif eligibility == 'NOT_ELIGIBLE':
                    status_display = f"Need {amount_remaining:,.0f}"
                elif eligibility == 'NOT_SET':
                    status_display = "Fee Not Set"
                else:
                    status_display = eligibility
                
                self.exam_tree.insert("", tk.END, values=(
                    row.get('exam_name', 'UE'),
                    row['semester'],
                    row['academic_year'],
                    status_display
                ))
            
            # Update eligibility stat
            self.update_eligibility_stat(eligible_count, len(results))
        else:
            self.exam_tree.insert("", tk.END, values=("-", "-", "-", "No records"))
            self.update_eligibility_stat(0, 0)
    
    def update_eligibility_stat(self, eligible, total):
        """Update eligibility stat card"""
        # This would need to be called after UI is built
        pass
