"""
Student Dashboard for KIUT Fee Tracker
Student interface for viewing obligations and making payments
"""
import tkinter as tk
from tkinter import ttk, messagebox
from GUI.db_config import execute_query
from GUI.student_profile_window import StudentProfileFrame


class StudentDashboard:
    """Student dashboard for fee management"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.user = app.current_user
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup student dashboard UI"""
        # Top header
        header_frame = tk.Frame(self.parent, bg="#8e44ad", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Welcome label
        welcome_label = tk.Label(
            header_frame,
            text=f"Student Dashboard - Welcome, {self.user['username']}",
            font=("Arial", 16, "bold"),
            bg="#8e44ad",
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
        self.create_profile_tab()
        self.create_obligations_tab()
        self.create_payments_tab()
        self.create_exam_clearance_tab()
    
    def create_profile_tab(self):
        """Create student profile tab with integrated view"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="My Profile")
        
        # Use the integrated profile frame
        self.profile_frame = StudentProfileFrame(tab, self.app)
    
    def create_obligations_tab(self):
        """Create fee obligations tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="My Fee Obligations")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_obligations(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Academic Year", "Fee Description", "Amount", "Paid", "Balance", "Status")
        self.obligation_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.obligation_tree.heading(col, text=col)
            self.obligation_tree.column(col, width=120)
        
        self.obligation_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Summary frame
        self.summary_frame = tk.Frame(tab, bg="#ecf0f1")
        self.summary_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.load_obligations(tab)
    
    def create_payments_tab(self):
        """Create payments history tab with make payment functionality"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="My Payments")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="Make Payment",
            bg="#27ae60",
            fg="white",
            command=lambda: self.make_payment(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_payments(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Amount", "Date", "Method", "Reference", "Status")
        self.payment_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.payment_tree.heading(col, text=col)
            self.payment_tree.column(col, width=130)
        
        self.payment_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.load_payments(tab)
    
    def create_exam_clearance_tab(self):
        """Create exam clearance tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Exam Clearance")
        
        # Info
        info_label = tk.Label(
            tab,
            text="Your exam financial eligibility status:\nThe 'Amount Remaining' column shows how much you need to pay to become eligible for each exam.",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        info_label.pack(pady=10)
        
        # Treeview with new columns
        columns = ("Exam Name", "Semester", "Academic Year", "Clearance Fee", "Amount Paid", "Amount Remaining", "Eligibility Status", "Reason")
        self.clearance_tree = ttk.Treeview(tab, columns=columns, show="headings", height=12)
        
        col_widths = {"Exam Name": 100, "Semester": 80, "Academic Year": 100, "Clearance Fee": 100, "Amount Paid": 100, "Amount Remaining": 120, "Eligibility Status": 120, "Reason": 150}
        for col in columns:
            self.clearance_tree.heading(col, text=col)
            self.clearance_tree.column(col, width=col_widths.get(col, 120))
        
        self.clearance_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.clearance_tree.yview)
        self.clearance_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Refresh button
        tk.Button(
            tab,
            text="Refresh",
            command=lambda: self.load_exam_clearance(tab)
        ).pack(pady=10)
        
        self.load_exam_clearance(tab)
    
    def load_data(self):
        """Load student data"""
        pass
    
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
    
    def load_obligations(self, tab):
        """Load fee obligations"""
        for item in self.obligation_tree.get_children():
            self.obligation_tree.delete(item)
        
        student_id = self.get_student_id()
        
        if not student_id:
            for widget in self.summary_frame.winfo_children():
                widget.destroy()
            tk.Label(
                self.summary_frame,
                text="⚠️ No student profile linked to this account. Please contact the administrator.",
                bg="#ecf0f1",
                fg="#e74c3c",
                font=("Arial", 11, "bold")
            ).pack()
            tk.Label(
                self.summary_frame,
                text="Your user account is not linked to a student record. Please contact the finance department.",
                bg="#ecf0f1",
                fg="#7f8c8d"
            ).pack()
            return
        
        query = """
            SELECT sfo.obligation_id, sfo.academic_year, fs.description, fs.amount,
                   COALESCE(SUM(p.amount_paid), 0) as total_paid, sfo.is_cleared
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id AND p.receipt_checked = 1
            WHERE sfo.student_id = %s
            GROUP BY sfo.obligation_id
            ORDER BY sfo.academic_year DESC
        """
        
        results = execute_query(query, (student_id,), fetch=True)
        
        total_due = 0
        total_paid = 0
        
        if results:
            for row in results:
                amount = float(row['amount'])
                paid = float(row['total_paid'])
                balance = amount - paid
                
                total_due += amount
                total_paid += paid
                
                status = "Cleared" if row['is_cleared'] else "Not Cleared"
                
                self.obligation_tree.insert("", tk.END, values=(
                    row['obligation_id'],
                    row['academic_year'],
                    row['description'] or 'Fee',
                    f"{amount:.2f}",
                    f"{paid:.2f}",
                    f"{balance:.2f}",
                    status
                ))
        else:
            # No obligations found - show helpful message
            for widget in self.summary_frame.winfo_children():
                widget.destroy()
            
            tk.Label(
                self.summary_frame,
                text="⚠️ No Fee Obligations Found",
                bg="#ecf0f1",
                fg="#e74c3c",
                font=("Arial", 12, "bold")
            ).pack(pady=(10, 5))
            
            tk.Label(
                self.summary_frame,
                text="Your fee obligations have not been created yet.\nPlease contact the finance department or administrator.",
                bg="#ecf0f1",
                fg="#7f8c8d",
                justify=tk.CENTER
            ).pack()
            
            # Also show info in tree area
            tk.Label(
                tab,
                text="💡 Your fee obligations will appear here once the finance department assigns them to you.\n\nContact: finance@kiut.ac.tz or visit the finance office.",
                bg="#ecf0f1",
                fg="#3498db",
                font=("Arial", 10),
                justify=tk.CENTER
            ).pack(pady=50)
            return
        
        # Update summary
        for widget in self.summary_frame.winfo_children():
            widget.destroy()
        
        tk.Label(
            self.summary_frame,
            text=f"Total Due: {total_due:.2f} | Total Paid: {total_paid:.2f} | Balance: {total_due - total_paid:.2f}",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1"
        ).pack()
    
    def load_payments(self, tab):
        """Load payment history"""
        for item in self.payment_tree.get_children():
            self.payment_tree.delete(item)
        
        student_id = self.get_student_id()
        
        if not student_id:
            return
        
        query = """
            SELECT p.payment_id, p.amount_paid, p.payment_date, p.method, 
                   p.reference_no, p.receipt_checked
            FROM payments p
            JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
            WHERE sfo.student_id = %s
            ORDER BY p.payment_date DESC
        """
        
        results = execute_query(query, (student_id,), fetch=True)
        
        if results:
            for row in results:
                status = "Verified" if row['receipt_checked'] == 1 else "Pending"
                self.payment_tree.insert("", tk.END, values=(
                    row['payment_id'],
                    f"{row['amount_paid']:.2f}",
                    row['payment_date'],
                    row['method'],
                    row['reference_no'] or 'N/A',
                    status
                ))
    
    def load_exam_clearance(self, tab):
        """Load exam clearance status with amount remaining"""
        for item in self.clearance_tree.get_children():
            self.clearance_tree.delete(item)
        
        student_id = self.get_student_id()
        
        if not student_id:
            return
        
        # First check if the new exam_clearance_fees table exists
        check_query = """
            SELECT COUNT(*) as cnt 
            FROM information_schema.tables 
            WHERE table_schema = 'My_Financials' AND table_name = 'exam_clearance_fees'
        """
        table_exists = execute_query(check_query, fetch=True)
        
        if table_exists and table_exists[0]['cnt'] > 0:
            # First get student's programme and year_of_study (students table has 'programme' not 'programme_id')
            student_query = "SELECT programme, year_of_study FROM students WHERE student_id = %s"
            student_data = execute_query(student_query, (student_id,), fetch=True)
            programme_name = student_data[0]['programme'] if student_data else None
            year_of_study = student_data[0]['year_of_study'] if student_data else None
            
            # Get programme_id from programmes table using programme name
            programme_id = None
            if programme_name:
                prog_query = "SELECT programme_id FROM programmes WHERE name = %s"
                prog_result = execute_query(prog_query, (programme_name,), fetch=True)
                programme_id = prog_result[0]['programme_id'] if prog_result else None
            
            if not programme_id:
                # No programme assigned - show message
                tk.Label(tab, text="Your programme is not set. Please contact the administrator.", bg="#ecf0f1", fg="#e74c3c").pack()
                return
            
            # Use the new query with exam clearance fees - filtered by student's programme AND year
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
                        WHEN ecf.exam_fee_amount IS NULL THEN 'Fee not set for your programme/year'
                        WHEN COALESCE(SUM(p.amount_paid), 0) >= ecf.exam_fee_amount THEN 'Cleared - You can sit for this exam'
                        ELSE CONCAT('Need TZS ', FORMAT(GREATEST(0, ecf.exam_fee_amount - COALESCE(SUM(p.amount_paid), 0)), 0), ' more to be eligible')
                    END AS reason,
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
            """
            results = execute_query(query, (programme_id, year_of_study, student_id), fetch=True)
        else:
            # Fallback to old method using v_exam_financial_eligibility
            query = """
                SELECT e.exam_name, e.semester, e.academic_year, efe.eligibility_status, efe.reason
                FROM v_exam_financial_eligibility efe
                JOIN exams e ON efe.exam_id = e.exam_id
                WHERE efe.student_id = %s
                ORDER BY e.academic_year DESC, e.semester
            """
            results = execute_query(query, (student_id,), fetch=True)
            
            # Convert to new format
            if results:
                new_results = []
                for row in results:
                    new_results.append({
                        'exam_name': row['exam_name'],
                        'semester': row['semester'],
                        'academic_year': row['academic_year'],
                        'exam_fee_amount': 0,
                        'total_paid': 0,
                        'eligibility_status': row['eligibility_status'],
                        'reason': row['reason'],
                        'amount_remaining': 0
                    })
                results = new_results
        
        if results:
            for row in results:
                clearance_fee = float(row.get('exam_fee_amount', 0) or 0)
                total_paid = float(row.get('total_paid', 0) or 0)
                amount_remaining = float(row.get('amount_remaining', 0) or 0)
                eligibility = row.get('eligibility_status', 'UNKNOWN')
                
                # Format eligibility status for display
                if eligibility == 'ELIGIBLE':
                    status_display = "Eligible"
                elif eligibility == 'NOT_ELIGIBLE':
                    status_display = "Not Eligible"
                elif eligibility == 'NOT_SET':
                    status_display = "Fee Not Set"
                else:
                    status_display = eligibility
                
                self.clearance_tree.insert("", tk.END, values=(
                    row['exam_name'],
                    row['semester'],
                    row['academic_year'],
                    f"{clearance_fee:,.2f}" if clearance_fee > 0 else "Not Set",
                    f"{total_paid:,.2f}",
                    f"{amount_remaining:,.2f}" if amount_remaining > 0 else "0.00",
                    status_display,
                    row.get('reason', '-')
                ))
        else:
            tk.Label(
                tab,
                text="No exam records found.",
                bg="#ecf0f1"
            ).pack()
    
    def make_payment(self, parent):
        """Make a new payment with receipt upload and security validation"""
        student_id = self.get_student_id()
        
        if not student_id:
            messagebox.showerror("Error", "No student profile linked to this account. Please contact the administrator.")
            return
        
        # First check if there are any obligations at all
        check_query = """
            SELECT COUNT(*) as cnt FROM student_fee_obligations WHERE student_id = %s
        """
        check_result = execute_query(check_query, (student_id,), fetch=True)
        
        if not check_result or check_result[0]['cnt'] == 0:
            messagebox.showwarning("No Fee Obligations", 
                "⚠️ You don't have any fee obligations yet.\n\n"
                "Please contact the finance department or administrator to have your fees assigned.")
            return
        
        # Get student info from database for auto-fill
        student_query = "SELECT full_name, reg_no FROM students WHERE student_id = %s"
        student_info = execute_query(student_query, (student_id,), fetch=True)
        
        if not student_info:
            messagebox.showerror("Error", "Student information not found")
            return
        
        student_name = student_info[0]['full_name']
        student_reg_no = student_info[0]['reg_no']
        
        # Get pending obligations with full details from database
        query = """
            SELECT sfo.obligation_id, sfo.academic_year, fs.description, fs.amount,
                   COALESCE(SUM(p.amount_paid), 0) as total_paid
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id
            WHERE sfo.student_id = %s AND sfo.is_cleared = 0
            GROUP BY sfo.obligation_id
            HAVING fs.amount > total_paid
        """
        
        obligations = execute_query(query, (student_id,), fetch=True)
        
        if not obligations:
            messagebox.showinfo("Info", "All your fee obligations are cleared! No pending payments.")
            return
        
        # Show payment dialog with receipt upload
        dialog = tk.Toplevel(self.parent)
        dialog.title("Submit Payment with Receipt")
        dialog.geometry("600x750")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Create canvas for scrolling
        canvas = tk.Canvas(dialog)
        scrollbar = ttk.Scrollbar(dialog, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, padx=20, pady=20)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main frame inside scrollable area
        main_frame = tk.Frame(scrollable_frame)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Submit Payment with Receipt",
            font=("Arial", 16, "bold"),
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))
        
        # Info text
        info_label = tk.Label(
            main_frame,
            text="Please upload your payment receipt and fill in all details accurately.\nFalse information will be flagged and may result in suspension.",
            font=("Arial", 9),
            fg="#e74c3c",
            wraplength=500,
            justify="center"
        )
        info_label.pack(pady=(0, 15))
        
        # ==================== SECTION 1: Fee Obligation ====================
        sec1 = tk.LabelFrame(main_frame, text="1. Select Fee Obligation", font=("Arial", 10, "bold"), padx=10, pady=10)
        sec1.pack(fill=tk.X, pady=(0, 10))
        
        obligation_var = tk.StringVar()
        obligation_combo = ttk.Combobox(
            sec1,
            textvariable=obligation_var,
            values=[self._format_obligation(o) for o in obligations],
            width=50,
            state="readonly"
        )
        obligation_combo.pack(pady=5)
        obligation_combo.current(0)
        
        # ==================== SECTION 2: Receipt Image Upload ====================
        sec2 = tk.LabelFrame(main_frame, text="2. Upload Receipt Image", font=("Arial", 10, "bold"), padx=10, pady=10)
        sec2.pack(fill=tk.X, pady=(0, 10))
        
        receipt_path_var = tk.StringVar()
        
        def browse_receipt():
            from tkinter import filedialog
            filename = filedialog.askopenfilename(
                title="Select Receipt Image",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png"),
                    ("PDF files", "*.pdf"),
                    ("All files", "*.*")
                ]
            )
            if filename:
                receipt_path_var.set(filename)
                receipt_label.config(text=filename.split("/")[-1][:40] + "..." if len(filename) > 40 else filename.split("/")[-1])
        
        receipt_btn = tk.Button(sec2, text="Browse...", command=browse_receipt, bg="#3498db", fg="white")
        receipt_btn.pack(pady=5)
        
        receipt_label = tk.Label(sec2, text="No file selected", font=("Arial", 9), fg="#7f8c8d")
        receipt_label.pack(pady=5)
        
        tk.Label(sec2, text="Supported: JPG, PNG, PDF (Max 5MB)", font=("Arial", 8), fg="#7f8c8d").pack()
        
        # ==================== SECTION 3: Payment Details from Receipt ====================
        sec3 = tk.LabelFrame(main_frame, text="3. Payment Details (from your receipt)", font=("Arial", 10, "bold"), padx=10, pady=10)
        sec3.pack(fill=tk.X, pady=(0, 10))
        
        # Student Name (from receipt)
        tk.Label(sec3, text="Student Name (as on receipt):", anchor="w").pack(fill=tk.X)
        receipt_name_entry = tk.Entry(sec3, font=("Arial", 11))
        receipt_name_entry.pack(fill=tk.X, pady=(2, 10))
        receipt_name_entry.insert(0, student_name)
        
        # Registration Number (from receipt)
        tk.Label(sec3, text="Registration Number (as on receipt):", anchor="w").pack(fill=tk.X)
        receipt_reg_entry = tk.Entry(sec3, font=("Arial", 11))
        receipt_reg_entry.pack(fill=tk.X, pady=(2, 10))
        receipt_reg_entry.insert(0, student_reg_no)
        
        # Payment Date (from receipt)
        tk.Label(sec3, text="Payment Date (YYYY-MM-DD):", anchor="w").pack(fill=tk.X)
        payment_date_entry = tk.Entry(sec3, font=("Arial", 11))
        payment_date_entry.pack(fill=tk.X, pady=(2, 10))
        import datetime
        payment_date_entry.insert(0, datetime.date.today().strftime('%Y-%m-%d'))
        
        # Amount Paid
        tk.Label(sec3, text="Amount Paid (TZS):", anchor="w").pack(fill=tk.X)
        amount_entry = tk.Entry(sec3, font=("Arial", 11))
        amount_entry.pack(fill=tk.X, pady=(2, 10))
        
        # Show expected amount
        expected_label = tk.Label(sec3, text="", font=("Arial", 9), fg="#7f8c8d")
        expected_label.pack()
        
        # Reference Number
        tk.Label(sec3, text="Reference/Transaction Number:", anchor="w").pack(fill=tk.X)
        ref_entry = tk.Entry(sec3, font=("Arial", 11))
        ref_entry.pack(fill=tk.X, pady=(2, 10))
        
        # Payment Method
        tk.Label(sec3, text="Payment Method:", anchor="w").pack(fill=tk.X, pady=(5, 0))
        method_var = tk.StringVar(value="WAKALA/CASH")
        method_frame = tk.Frame(sec3)
        method_frame.pack(fill=tk.X, pady=5)
        
        for method in ["WAKALA/CASH", "BANK", "MOBILE_BANKING"]:
            rb = tk.Radiobutton(
                method_frame,
                text=method,
                variable=method_var,
                value=method,
                font=("Arial", 10)
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Payment Description
        tk.Label(sec3, text="Payment Description:", anchor="w").pack(fill=tk.X, pady=(10, 0))
        desc_entry = tk.Entry(sec3, font=("Arial", 11))
        desc_entry.pack(fill=tk.X, pady=(2, 10))
        desc_entry.insert(0, "Tuition Fee Payment")
        
        def update_expected(*args):
            try:
                idx = obligation_combo.current()
                if idx >= 0 and idx < len(obligations):
                    o = obligations[idx]
                    expected = float(o['amount'])
                    paid = float(o['total_paid'])
                    balance = expected - paid
                    expected_label.config(text=f"Expected: TZS {expected:,.2f} | Already Paid: TZS {paid:,.2f} | Balance: TZS {balance:,.2f}")
                    amount_entry.delete(0, tk.END)
                    amount_entry.insert(0, str(int(balance)))
            except:
                pass
        
        obligation_combo.bind('<<ComboboxSelected>>', update_expected)
        update_expected()
        
        # ==================== Buttons ====================
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=20)
        
        def submit_payment_with_receipt():
            """Submit payment with receipt image and security validation"""
            selected = obligation_combo.get()
            if not selected:
                messagebox.showerror("Error", "Please select a fee obligation")
                return
            
            obligation_id = int(selected.split(":")[0])
            
            # Validate receipt image
            receipt_path = receipt_path_var.get()
            if not receipt_path:
                messagebox.showwarning("Warning", "Please upload a receipt image")
                return
            
            # Validate required fields
            receipt_name = receipt_name_entry.get().strip()
            receipt_reg = receipt_reg_entry.get().strip()
            payment_date = payment_date_entry.get().strip()
            
            if not receipt_name:
                messagebox.showerror("Error", "Please enter student name from receipt")
                return
            
            if not receipt_reg:
                messagebox.showerror("Error", "Please enter registration number from receipt")
                return
            
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid amount")
                return
            
            reference = ref_entry.get().strip()
            if not reference:
                messagebox.showwarning("Warning", "Please enter a reference number")
                return
            
            if len(reference) < 3:
                messagebox.showwarning("Warning", "Reference number seems too short")
                return
            
            # Validate payment date format
            try:
                from datetime import datetime
                datetime.strptime(payment_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Use YYYY-MM-DD")
                return
            
            # Copy receipt to receipts folder and get relative path
            import os
            import shutil
            import hashlib
            
            # Create receipts directory if not exists
            receipts_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "receipts")
            if not os.path.exists(receipts_dir):
                os.makedirs(receipts_dir)
            
            # Generate unique filename using hash
            file_hash = hashlib.md5(f"{student_id}_{obligation_id}_{reference}".encode()).hexdigest()[:10]
            file_ext = os.path.splitext(receipt_path)[1].lower()
            new_filename = f"receipt_{student_id}_{obligation_id}_{file_hash}{file_ext}"
            dest_path = os.path.join(receipts_dir, new_filename)
            
            # Copy file
            try:
                shutil.copy2(receipt_path, dest_path)
                relative_receipt_path = f"receipts/{new_filename}"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save receipt: {str(e)}")
                return
            
            # Submit payment with receipt
            result = self._submit_payment_with_receipt(
                student_id=student_id,
                obligation_id=obligation_id,
                receipt_path=relative_receipt_path,
                amount_paid=amount,
                reference_no=reference,
                payment_date=payment_date,
                student_name=receipt_name,
                student_reg_no=receipt_reg,
                method=method_var.get()
            )
            
            if result['success']:
                flags = result.get('flags', [])
                if flags:
                    flag_msg = f"\n\nSecurity Flags: {', '.join(flags)}"
                    messagebox.showwarning("Success", f"Payment submitted successfully!\n\n{result['message']}{flag_msg}\n\nPlease wait for finance department verification.")
                else:
                    messagebox.showinfo("Success", f"Payment submitted successfully!\n\n{result['message']}\n\nIt will be verified by the finance department.")
                dialog.destroy()
                self.refresh_all_tabs()
            else:
                messagebox.showerror("Error", result.get('message', 'Failed to submit payment'))
        
        tk.Button(
            btn_frame,
            text="Submit Payment",
            command=submit_payment_with_receipt,
            bg="#27ae60",
            fg="white",
            font=("Arial", 12, "bold"),
            width=18,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 11),
            width=12,
            pady=10
        ).pack(side=tk.LEFT, padx=5)
    
    def _format_obligation(self, o):
        """Format obligation for display"""
        desc = o['description'] or 'Fee'
        return f"{o['obligation_id']}: ID | {o['academic_year']} | {desc[:20]} | Due: {float(o['amount']):,.0f}"
    
    def _submit_payment_db(self, student_id, obligation_id, amount, method, reference_no):
        """Submit payment with validation based on backend logic"""
        import datetime
        
        feedback = {
            "status": None,
            "message": "",
            "flags": []
        }
        
        allowed_methods = ['WAKALA/CASH', 'BANK', 'MOBILE_BANKING']
        if method not in allowed_methods:
            feedback["status"] = "error"
            feedback["message"] = f"Invalid payment method: {method}"
            return feedback
        
        if amount <= 0:
            feedback["status"] = "error"
            feedback["message"] = "Amount must be positive"
            return feedback
        
        query = """
            SELECT sfo.obligation_id, fs.amount AS expected_amount, sfo.is_cleared
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE sfo.obligation_id=%s AND sfo.student_id=%s
        """
        obligation = execute_query(query, (obligation_id, student_id), fetch=True)
        
        if not obligation:
            feedback["status"] = "error"
            feedback["message"] = "Obligation not found"
            return feedback
        
        expected = float(obligation[0]['expected_amount'])
        cleared = obligation[0]['is_cleared']
        
        if cleared:
            feedback["status"] = "error"
            feedback["message"] = "This obligation is already cleared"
            return feedback
        
        query = """
            SELECT * FROM payments
            WHERE obligation_id=%s AND reference_no=%s
        """
        duplicate = execute_query(query, (obligation_id, reference_no), fetch=True)
        
        if duplicate:
            feedback["status"] = "warning"
            feedback["message"] = "Duplicate reference number detected"
            feedback["flags"].append("DUPLICATE_REFERENCE")
        
        if amount < expected:
            feedback["flags"].append("UNDERPAID")
            feedback["message"] = f"Amount is less than expected. Expected: {expected}, Paid: {amount}"
            feedback["status"] = "warning"
        elif amount > expected:
            feedback["flags"].append("OVERPAID")
            feedback["message"] = f"Amount exceeds expected. Expected: {expected}, Paid: {amount}"
            feedback["status"] = "warning"
        else:
            feedback["status"] = "success"
            feedback["message"] = f"Payment of TZS {amount:,.2f} matches expected amount"
        
        return feedback
    
    def _submit_payment_with_receipt(self, student_id, obligation_id, receipt_path, amount_paid, reference_no, payment_date, student_name, student_reg_no, method):
        """
        Submit payment with receipt image and all security validations.
        """
        import os
        import hashlib
        
        flags = []
        
        # 1. Validate receipt file
        if receipt_path:
            full_receipt_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), receipt_path)
            
            if not os.path.exists(full_receipt_path):
                return {"success": False, "message": "Receipt file not found", "flags": ["MISSING_FILE"]}
            
            # File size check (5MB max)
            file_size = os.path.getsize(full_receipt_path)
            if file_size > 5 * 1024 * 1024:
                flags.append("FILE_TOO_LARGE")
            
            # File type check
            file_ext = os.path.splitext(full_receipt_path)[1].lower()
            if file_ext not in ['.jpg', '.jpeg', '.png', '.pdf']:
                flags.append("UNSUPPORTED_FILE_TYPE")
            
            # Compute file hash for duplicate detection
            sha256_hash = hashlib.sha256()
            with open(full_receipt_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            file_hash = sha256_hash.hexdigest()
        else:
            file_size = 0
            file_ext = None
            file_hash = None
        
        # 2. Check expected obligation amount
        query = """
            SELECT sfo.obligation_id, fs.amount AS expected_amount, sfo.is_cleared
            FROM student_fee_obligations sfo
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE sfo.obligation_id = %s AND sfo.student_id = %s
        """
        obligation = execute_query(query, (obligation_id, student_id), fetch=True)
        
        if not obligation:
            return {"success": False, "message": "Obligation not found for this student", "flags": ["INVALID_OBLIGATION"]}
        
        expected_amount = float(obligation[0]['expected_amount'])
        cleared = obligation[0]['is_cleared']
        
        if cleared:
            return {"success": False, "message": "This obligation is already cleared", "flags": ["ALREADY_CLEARED"]}
        
        # 3. Check amount mismatch
        if amount_paid != expected_amount:
            flags.append("AMOUNT_MISMATCH")
        
        # 4. Check for duplicate receipt by hash
        if file_hash:
            check_hash_query = """
                SELECT payment_id FROM payments 
                WHERE obligation_id = %s AND receipt_hash = %s
            """
            duplicate_hash = execute_query(check_hash_query, (obligation_id, file_hash), fetch=True)
            if duplicate_hash:
                flags.append("DUPLICATE_RECEIPT")
        
        # 5. Check for duplicate reference number
        check_ref_query = """
            SELECT payment_id FROM payments 
            WHERE obligation_id = %s AND reference_no = %s
        """
        duplicate_ref = execute_query(check_ref_query, (obligation_id, reference_no), fetch=True)
        if duplicate_ref:
            flags.append("DUPLICATE_REFERENCE")
        
        # 6. Compare student info from receipt with database
        student_query = "SELECT full_name, reg_no FROM students WHERE student_id = %s"
        student = execute_query(student_query, (student_id,), fetch=True)
        
        if student:
            db_name = student[0]['full_name']
            db_reg = student[0]['reg_no']
            
            if student_name.lower() != db_name.lower():
                flags.append("NAME_MISMATCH")
            if student_reg_no.upper() != db_reg.upper():
                flags.append("ID_MISMATCH")
        
        # 7. Insert payment record with all receipt details
        import json
        
        insert_query = """
            INSERT INTO payments (
                obligation_id, amount_paid, payment_date, method, reference_no,
                receipt_path, receipt_uploaded_at, receipt_checked, receipt_flags,
                receipt_file_size, receipt_file_type, receipt_hash,
                receipt_reference_no, receipt_payment_date, receipt_student_name, receipt_student_id,
                created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, NOW(), %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        receipt_flags_json = json.dumps(flags) if flags else None
        
        result = execute_query(insert_query, (
            obligation_id,
            amount_paid,
            payment_date,
            method,
            reference_no,
            receipt_path,
            0,  # receipt_checked
            receipt_flags_json,
            file_size,
            file_ext.replace('.', '') if file_ext else None,
            file_hash,
            reference_no,
            payment_date,
            student_name,
            student_reg_no
        ))
        
        if not result:
            return {"success": False, "message": "Failed to save payment record", "flags": flags}
        
        # 8. Update structured flags in student_fee_obligations
        self._update_student_flags(student_id, obligation_id, flags)
        
        # Generate response message
        if not flags:
            message = "Payment submitted successfully! Your receipt has been uploaded and is pending verification."
        else:
            message = f"Payment submitted with {len(flags)} security flag(s). Please wait for finance department review."
        
        return {
            "success": True,
            "message": message,
            "flags": flags
        }
    
    def _update_student_flags(self, student_id, obligation_id, flags):
        """Update structured flags in student_fee_obligations"""
        flag_cheating = 1 if 'CHEATING_SUSPECTED' in flags else 0
        flag_duplicate = 1 if 'DUPLICATE_RECEIPT' in flags else 0
        flag_mismatch = 1 if any(f in flags for f in ['AMOUNT_MISMATCH', 'NAME_MISMATCH', 'ID_MISMATCH']) else 0
        
        update_query = """
            UPDATE student_fee_obligations
            SET flag_cheating = %s, flag_duplicate = %s, flag_mismatch = %s
            WHERE student_id = %s AND obligation_id = %s
        """
        
        execute_query(update_query, (flag_cheating, flag_duplicate, flag_mismatch, student_id, obligation_id))
    
    def _force_payment_insert(self, student_id, obligation_id, amount, method, reference_no, flags):
        """Force insert payment even with warnings"""
        import datetime
        
        payment_date = datetime.date.today().strftime('%Y-%m-%d')
        
        query = """
            INSERT INTO payments (obligation_id, amount_paid, payment_date, method, reference_no, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """
        
        execute_query(query, (obligation_id, amount, payment_date, method, reference_no))
    
    def refresh_all_tabs(self):
        """Refresh all tab data"""
        if hasattr(self, 'profile_frame') and self.profile_frame:
            try:
                self.profile_frame.load_data()
            except:
                pass
        
        try:
            tabs = self.notebook.tabs()
            if len(tabs) > 1:
                self.load_obligations(self.notebook.nametowidget(tabs[1]))
        except:
            pass
        
        try:
            tabs = self.notebook.tabs()
            if len(tabs) > 2:
                self.load_payments(self.notebook.nametowidget(tabs[2]))
        except:
            pass
