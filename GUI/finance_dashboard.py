"""
Finance Dashboard for KIUT Fee Tracker
Finance officer interface for managing payments, verifications, and exam clearance fees
"""
import tkinter as tk
from tkinter import ttk, messagebox
from GUI.db_config import execute_query, get_connection
import hashlib
from datetime import datetime


class FinanceDashboard:
    """Finance dashboard for payment verification and exam clearance fee management"""
    
    def __init__(self, parent, app):
        self.parent = parent
        self.app = app
        self.user = app.current_user
        self.setup_ui()
        self.load_data()
    
    def setup_ui(self):
        """Setup finance dashboard UI"""
        # Top header
        header_frame = tk.Frame(self.parent, bg="#16a085", height=60)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Welcome label
        welcome_label = tk.Label(
            header_frame,
            text=f"Finance Dashboard - Welcome, {self.user['username']}",
            font=("Arial", 16, "bold"),
            bg="#16a085",
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
        self.create_pending_payments_tab()
        self.create_verified_payments_tab()
        self.create_exam_clearance_fees_tab()
        self.create_students_tab()
    
    def create_pending_payments_tab(self):
        """Create pending payments verification tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Pending Payments")
        
        # Info label
        info_label = tk.Label(
            tab,
            text="Review and verify pending payment receipts",
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
            text="Refresh",
            command=lambda: self.load_pending_payments(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Search
        tk.Label(toolbar, text="Search:", bg="#ecf0f1").pack(side=tk.LEFT, padx=5)
        self.payment_search = tk.Entry(toolbar, width=20)
        self.payment_search.pack(side=tk.LEFT, padx=5)
        tk.Button(
            toolbar,
            text="Search",
            command=lambda: self.search_pending_payments(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Student", "Reg No", "Amount", "Date", "Method", "Reference", "Receipt", "Flags")
        self.pending_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 50, "Student": 150, "Reg No": 100, "Amount": 100, "Date": 100, "Method": 80, "Reference": 120, "Receipt": 60, "Flags": 150}
        for col in columns:
            self.pending_tree.heading(col, text=col)
            self.pending_tree.column(col, width=col_widths.get(col, 120))
        
        self.pending_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.pending_tree.yview)
        self.pending_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Action buttons
        btn_frame = tk.Frame(tab, bg="#ecf0f1")
        btn_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            btn_frame,
            text="Verify Selected",
            bg="#27ae60",
            fg="white",
            command=lambda: self.verify_payment(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Reject Selected",
            bg="#e74c3c",
            fg="white",
            command=lambda: self.reject_payment(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="View Receipt",
            bg="#3498db",
            fg="white",
            command=lambda: self.view_receipt(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        self.load_pending_payments(tab)
    
    def load_pending_payments(self, tab):
        """Load pending payments"""
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        
        query = """
            SELECT p.payment_id, p.amount_paid, p.payment_date, p.method, 
                   p.reference_no, p.receipt_path, p.receipt_flags, s.full_name, s.reg_no,
                   fs.description, sfo.academic_year
            FROM payments p
            JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
            JOIN students s ON sfo.student_id = s.student_id
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE p.receipt_checked = 0
            ORDER BY p.payment_date DESC
        """
        
        results = execute_query(query, fetch=True)
        
        # Configure color tags for flagged rows
        self.pending_tree.tag_configure('flagged', background='#ffebee')
        self.pending_tree.tag_configure('normal', background='white')
        
        if results:
            for row in results:
                # Parse flags from JSON
                flags = ""
                has_flags = False
                if row['receipt_flags']:
                    try:
                        import json
                        flag_list = json.loads(row['receipt_flags'])
                        flags = ", ".join(flag_list) if flag_list else ""
                        has_flags = len(flag_list) > 0 if flag_list else False
                    except:
                        flags = str(row['receipt_flags'])
                
                item_id = self.pending_tree.insert("", tk.END, values=(
                    row['payment_id'],
                    row['full_name'],
                    row['reg_no'],
                    f"{float(row['amount_paid']):,.2f}",
                    row['payment_date'],
                    row['method'],
                    row['reference_no'] or 'N/A',
                    "View" if row['receipt_path'] else "None",
                    flags
                ))
                
                # Apply color tag if has flags
                if has_flags:
                    self.pending_tree.item(item_id, tags=('flagged',))
                else:
                    self.pending_tree.item(item_id, tags=('normal',))
    
    def search_pending_payments(self, tab):
        """Search pending payments"""
        search_term = self.payment_search.get().strip()
        
        for item in self.pending_tree.get_children():
            self.pending_tree.delete(item)
        
        if search_term:
            query = """
                SELECT p.payment_id, p.amount_paid, p.payment_date, p.method, 
                       p.reference_no, p.receipt_path, p.receipt_flags, s.full_name, s.reg_no,
                       fs.description, sfo.academic_year
                FROM payments p
                JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
                JOIN students s ON sfo.student_id = s.student_id
                JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
                WHERE p.receipt_checked = 0 
                  AND (s.full_name LIKE %s OR s.reg_no LIKE %s OR p.reference_no LIKE %s)
                ORDER BY p.payment_date DESC
            """
            search_pattern = f"%{search_term}%"
            results = execute_query(query, (search_pattern, search_pattern, search_pattern), fetch=True)
        else:
            # Use the same query as load_pending_payments when no search term
            query = """
                SELECT p.payment_id, p.amount_paid, p.payment_date, p.method, 
                       p.reference_no, p.receipt_path, p.receipt_flags, s.full_name, s.reg_no,
                       fs.description, sfo.academic_year
                FROM payments p
                JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
                JOIN students s ON sfo.student_id = s.student_id
                JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
                WHERE p.receipt_checked = 0
                ORDER BY p.payment_date DESC
            """
            results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                # Parse flags from JSON
                flags = ""
                has_flags = False
                if row['receipt_flags']:
                    try:
                        import json
                        flag_list = json.loads(row['receipt_flags'])
                        flags = ", ".join(flag_list) if flag_list else ""
                        has_flags = len(flag_list) > 0 if flag_list else False
                    except:
                        flags = str(row['receipt_flags'])
                
                item_id = self.pending_tree.insert("", tk.END, values=(
                    row['payment_id'],
                    row['full_name'],
                    row['reg_no'],
                    f"{float(row['amount_paid']):,.2f}",
                    row['payment_date'],
                    row['method'],
                    row['reference_no'] or 'N/A',
                    "View" if row['receipt_path'] else "None",
                    flags
                ))
                
                # Apply color tag if has flags
                if has_flags:
                    self.pending_tree.item(item_id, tags=('flagged',))
                else:
                    self.pending_tree.item(item_id, tags=('normal',))
    
    def verify_payment(self, parent):
        """Verify selected payment"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a payment to verify")
            return
        
        item = self.pending_tree.item(selection[0])
        payment_id = item['values'][0]
        
        # Show verification dialog
        dialog = tk.Toplevel(self.parent)
        dialog.title("Verify Payment")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        
        # Get payment details
        query = """
            SELECT p.*, s.full_name, s.reg_no, fs.description, sfo.academic_year
            FROM payments p
            JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
            JOIN students s ON sfo.student_id = s.student_id
            JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            WHERE p.payment_id = %s
        """
        payment = execute_query(query, (payment_id,), fetch=True)
        
        if not payment:
            messagebox.showerror("Error", "Payment not found")
            return
        
        payment = payment[0]
        
        # Payment info
        info_frame = tk.LabelFrame(dialog, text="Payment Information", font=("Arial", 10, "bold"), padx=10, pady=10)
        info_frame.pack(fill=tk.X, padx=10, pady=10)
        
        info_text = f"""
Student: {payment['full_name']}
Reg No: {payment['reg_no']}
Amount: TZS {float(payment['amount_paid']):,.2f}
Date: {payment['payment_date']}
Method: {payment['method']}
Reference: {payment['reference_no'] or 'N/A'}
Fee: {payment['description']} ({payment['academic_year']})
        """
        
        tk.Label(info_frame, text=info_text, justify=tk.LEFT, font=("Arial", 10)).pack()
        
        # Comment
        tk.Label(dialog, text="Comment (optional):").pack(anchor="w", padx=10)
        comment_entry = tk.Entry(dialog, width=50)
        comment_entry.pack(padx=10, pady=5)
        
        def approve():
            self._process_verification(payment_id, "APPROVED", comment_entry.get())
            dialog.destroy()
            self.load_pending_payments(parent)
        
        def reject():
            if not comment_entry.get().strip():
                messagebox.showwarning("Warning", "Please provide a reason for rejection")
                return
            self._process_verification(payment_id, "REJECTED", comment_entry.get())
            dialog.destroy()
            self.load_pending_payments(parent)
        
        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="Approve", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), 
                  command=approve, width=12).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Reject", bg="#e74c3c", fg="white", font=("Arial", 11, "bold"), 
                  command=reject, width=12).pack(side=tk.LEFT, padx=10)
    
    def _process_verification(self, payment_id, decision, comment):
        """Process payment verification"""
        conn = get_connection()
        if not conn:
            messagebox.showerror("Error", "Database connection failed")
            return
        
        try:
            cursor = conn.cursor()
            
            # Get obligation_id first
            cursor.execute("SELECT obligation_id FROM payments WHERE payment_id = %s", (payment_id,))
            obligation_result = cursor.fetchone()
            obligation_id = obligation_result[0] if obligation_result else None
            
            # Only mark payment as checked (verified) when APPROVED, not when REJECTED
            if decision == "APPROVED":
                cursor.execute("UPDATE payments SET receipt_checked = 1 WHERE payment_id = %s", (payment_id,))
            # When REJECTED, receipt_checked remains 0 (so student sees it as Pending)
            
            # Insert verification record
            insert_verification = """
                INSERT INTO finance_verifications 
                (obligation_id, verified_by, decision, comment, is_final, verified_at)
                VALUES (%s, %s, %s, %s, 1, NOW())
            """
            cursor.execute(insert_verification, (
                obligation_id,
                self.user['username'],
                decision,
                comment
            ))
            
            # If approved, check if obligation is now fully paid
            if decision == "APPROVED" and obligation_id:
                # Check total paid vs expected
                cursor.execute("""
                    SELECT fs.amount as expected, COALESCE(SUM(p.amount_paid), 0) as paid
                    FROM student_fee_obligations sfo
                    JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
                    LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id AND p.receipt_checked = 1
                    WHERE sfo.obligation_id = %s
                    GROUP BY sfo.obligation_id
                """, (obligation_id,))
                
                result = cursor.fetchone()
                if result:
                    expected = float(result[0])
                    paid = float(result[1])
                    
                    if paid >= expected:
                        cursor.execute("UPDATE student_fee_obligations SET is_cleared = 1 WHERE obligation_id = %s", (obligation_id,))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            messagebox.showinfo("Success", f"Payment {decision}d successfully!")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process verification: {str(e)}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
    
    def reject_payment(self, parent):
        """Reject selected payment"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a payment to reject")
            return
        
        item = self.pending_tree.item(selection[0])
        payment_id = item['values'][0]
        
        # Ask for reason
        dialog = tk.Toplevel(self.parent)
        dialog.title("Reject Payment")
        dialog.geometry("400x200")
        dialog.transient(self.parent)
        
        tk.Label(dialog, text="Please provide a reason for rejection:").pack(pady=10)
        reason_entry = tk.Entry(dialog, width=40)
        reason_entry.pack(pady=10)
        
        def confirm_reject():
            if not reason_entry.get().strip():
                messagebox.showwarning("Warning", "Please provide a reason")
                return
            self._process_verification(payment_id, "REJECTED", reason_entry.get())
            dialog.destroy()
            self.load_pending_payments(parent)
        
        tk.Button(dialog, text="Reject Payment", bg="#e74c3c", fg="white", command=confirm_reject).pack(pady=20)
    
    def view_receipt(self, parent):
        """View receipt image"""
        selection = self.pending_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a payment")
            return
        
        item = self.pending_tree.item(selection[0])
        # Get receipt path from database
        query = "SELECT receipt_path FROM payments WHERE payment_id = %s"
        result = execute_query(query, (item['values'][0],), fetch=True)
        
        if not result or not result[0]['receipt_path']:
            messagebox.showinfo("Info", "No receipt uploaded for this payment")
            return
        
        receipt_path = result[0]['receipt_path']
        
        # Try to open the receipt
        import os
        full_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), receipt_path)
        
        if os.path.exists(full_path):
            try:
                os.system(f"xdg-open '{full_path}'")
            except:
                messagebox.showinfo("Receipt", f"Receipt file: {receipt_path}")
        else:
            messagebox.showinfo("Receipt", f"Receipt file not found: {receipt_path}")
    
    def create_verified_payments_tab(self):
        """Create verified payments tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Verified Payments")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_verified_payments(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Student", "Reg No", "Amount", "Date", "Method", "Reference", "Status")
        self.verified_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.verified_tree.heading(col, text=col)
            self.verified_tree.column(col, width=120)
        
        self.verified_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.load_verified_payments(tab)
    
    def load_verified_payments(self, tab):
        """Load verified payments"""
        for item in self.verified_tree.get_children():
            self.verified_tree.delete(item)
        
        query = """
            SELECT p.payment_id, p.amount_paid, p.payment_date, p.method, 
                   p.reference_no, s.full_name, s.reg_no, fv.decision
            FROM payments p
            JOIN student_fee_obligations sfo ON p.obligation_id = sfo.obligation_id
            JOIN students s ON sfo.student_id = s.student_id
            JOIN finance_verifications fv ON sfo.obligation_id = fv.obligation_id
            WHERE p.receipt_checked = 1 AND fv.is_final = 1
            ORDER BY p.payment_date DESC
        """
        
        results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                self.verified_tree.insert("", tk.END, values=(
                    row['payment_id'],
                    row['full_name'],
                    row['reg_no'],
                    f"{float(row['amount_paid']):,.2f}",
                    row['payment_date'],
                    row['method'],
                    row['reference_no'] or 'N/A',
                    row['decision']
                ))
    
    def create_exam_clearance_fees_tab(self):
        """Create exam clearance fees management tab"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Exam Clearance Fees")
        
        # Info label
        info_label = tk.Label(
            tab,
            text="Set exam clearance fees for each programme. This is the MINIMUM amount required to sit for an exam.\nThis is DIFFERENT from the full yearly/total fee for the programme.",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#e74c3c"
        )
        info_label.pack(pady=10)
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(
            toolbar,
            text="Add Exam Clearance Fee",
            bg="#27ae60",
            fg="white",
            command=lambda: self.add_exam_clearance_fee(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_exam_clearance_fees(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Edit Selected",
            bg="#3498db",
            fg="white",
            command=lambda: self.edit_exam_clearance_fee(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Delete Selected",
            bg="#e74c3c",
            fg="white",
            command=lambda: self.delete_exam_clearance_fee(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        columns = ("ID", "Exam Name", "Semester", "Academic Year", "Programme", "Year", "Clearance Fee", "Created At")
        self.clearance_fee_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        col_widths = {"ID": 40, "Exam Name": 100, "Semester": 70, "Academic Year": 90, "Programme": 150, "Year": 50, "Clearance Fee": 100, "Created At": 90}
        for col in columns:
            self.clearance_fee_tree.heading(col, text=col)
            self.clearance_fee_tree.column(col, width=col_widths.get(col, 120))
        
        self.clearance_fee_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tab, orient=tk.VERTICAL, command=self.clearance_fee_tree.yview)
        self.clearance_fee_tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.load_exam_clearance_fees(tab)
    
    def load_exam_clearance_fees(self, tab):
        """Load exam clearance fees"""
        for item in self.clearance_fee_tree.get_children():
            self.clearance_fee_tree.delete(item)
        
        # Check if table exists
        check_query = """
            SELECT COUNT(*) as cnt 
            FROM information_schema.tables 
            WHERE table_schema = 'My_Financials' AND table_name = 'exam_clearance_fees'
        """
        table_exists = execute_query(check_query, fetch=True)
        
        if not table_exists or table_exists[0]['cnt'] == 0:
            tk.Label(
                tab,
                text="Exam clearance fees table not found. Please run the migration first.",
                bg="#ecf0f1",
                fg="red",
                font=("Arial", 12)
            ).pack(pady=20)
            return
        
        query = """
            SELECT ecf.exam_fee_id, ecf.exam_name, ecf.semester, ecf.academic_year,
                   ecf.programme_id, ecf.year_of_study, p.name as programme_name, ecf.exam_fee_amount, ecf.created_at
            FROM exam_clearance_fees ecf
            JOIN programmes p ON ecf.programme_id = p.programme_id
            ORDER BY ecf.academic_year DESC, ecf.semester, p.name, ecf.year_of_study
        """
        
        results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                date_str = row['created_at'].strftime('%Y-%m-%d') if row['created_at'] else 'N/A'
                year_str = f"Year {row['year_of_study']}" if row['year_of_study'] else "All"
                self.clearance_fee_tree.insert("", tk.END, values=(
                    row['exam_fee_id'],
                    row['exam_name'],
                    row['semester'],
                    row['academic_year'],
                    row['programme_name'],
                    year_str,
                    f"{float(row['exam_fee_amount']):,.2f}",
                    date_str
                ))
        else:
            tk.Label(
                tab,
                text="No exam clearance fees set. Click 'Add Exam Clearance Fee' to create one.",

                bg="#ecf0f1",
                fg="#7f8c8d",
                font=("Arial", 10)
            ).pack(pady=20)
    
    def add_exam_clearance_fee(self, parent):
        """Add new exam clearance fee"""
        # Get available exams
        exams_query = "SELECT exam_id, exam_name, semester, academic_year FROM exams ORDER BY academic_year DESC, semester"
        exams = execute_query(exams_query, fetch=True)
        
        # Get available programmes
        programmes_query = "SELECT programme_id, name FROM programmes ORDER BY name"
        programmes = execute_query(programmes_query, fetch=True)
        
        if not exams:
            messagebox.showwarning("Warning", "No exams found. Please create an exam first (via Admin dashboard).")
            return
        
        if not programmes:
            messagebox.showwarning("Warning", "No programmes found. Please create programmes first (via Admin dashboard).")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Exam Clearance Fee")
        dialog.geometry("500x450")
        dialog.transient(self.parent)
        
        # Info
        tk.Label(
            dialog,
            text="Set the MINIMUM fee amount required for a student to sit for an exam.\nThis is DIFFERENT from the full yearly fee.",
            font=("Arial", 9),
            fg="#e74c3c",
            wraplength=450
        ).pack(pady=10)
        
        # Form
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10)
        
        # Exam selection
        tk.Label(form_frame, text="Exam:", bg="white").grid(row=0, column=0, sticky="w", pady=10)
        exam_var = tk.StringVar()
        exam_map = {}
        exam_options = []
        for e in exams:
            option = f"{e['exam_name']} - {e['semester']} ({e['academic_year']})"
            exam_options.append(option)
            exam_map[option] = e['exam_id']
        
        exam_combo = ttk.Combobox(form_frame, textvariable=exam_var, values=exam_options, width=35, state="readonly")
        exam_combo.grid(row=0, column=1, pady=10, padx=10)
        if exam_options:
            exam_combo.current(0)
        
        # Programme selection
        tk.Label(form_frame, text="Programme:", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        prog_var = tk.StringVar()
        prog_map = {}
        prog_options = []
        for p in programmes:
            prog_options.append(p['name'])
            prog_map[p['name']] = p['programme_id']
        
        prog_combo = ttk.Combobox(form_frame, textvariable=prog_var, values=prog_options, width=35, state="readonly")
        prog_combo.grid(row=1, column=1, pady=10, padx=10)
        if prog_options:
            prog_combo.current(0)
        
        # Year of Study selection (1,2,3,4,5,All)
        tk.Label(form_frame, text="Year:", bg="white").grid(row=2, column=0, sticky="w", pady=10)
        year_var = tk.StringVar(value="All")
        year_options = ["All", "1", "2", "3", "4", "5"]
        year_combo = ttk.Combobox(form_frame, textvariable=year_var, values=year_options, width=33, state="readonly")
        year_combo.grid(row=2, column=1, pady=10, padx=10)
        
        # Clearance fee amount
        tk.Label(form_frame, text="Clearance Fee (TZS):", bg="white").grid(row=3, column=0, sticky="w", pady=10)
        fee_entry = tk.Entry(form_frame, width=38)
        fee_entry.grid(row=3, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Example: 50000", bg="white", fg="#7f8c8d", font=("Arial", 8)).grid(row=4, column=1, sticky="w")
        
        def save():
            exam_option = exam_var.get()
            prog_name = prog_var.get()
            year_value = year_var.get()
            fee_amount = fee_entry.get().strip()
            
            if not exam_option:
                messagebox.showerror("Error", "Please select an exam")
                return
            
            if not prog_name:
                messagebox.showerror("Error", "Please select a programme")
                return
            
            try:
                fee_amount = float(fee_amount)
                if fee_amount < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid fee amount")
                return
            
            exam_id = exam_map.get(exam_option)
            programme_id = prog_map.get(prog_name)
            
            # Parse year - "All" means NULL (applies to all years)
            year_of_study = int(year_value) if year_value not in ("All", "") else None
            
            if not exam_id or not programme_id:
                messagebox.showerror("Error", "Invalid exam or programme selected")
                return
            
            # Check if already exists (including year_of_study check)
            check_query = """
                SELECT exam_fee_id FROM exam_clearance_fees 
                WHERE exam_name = %s AND semester = %s AND academic_year = %s AND programme_id = %s AND (year_of_study = %s OR (year_of_study IS NULL AND %s IS NULL))
            """
            # Parse exam_option to get exam details (format: "exam_name - semester (academic_year)")
            exam_parts = exam_option.split(" - ")
            exam_name = exam_parts[0] if exam_parts else ""
            semester_academic = exam_parts[1].split(" (") if len(exam_parts) > 1 else ["", ""]
            semester = semester_academic[0] if semester_academic else ""
            academic_year = semester_academic[1].replace(")", "") if len(semester_academic) > 1 else ""
            
            existing = execute_query(check_query, (exam_name, semester, academic_year, programme_id, year_of_study, year_of_study), fetch=True)
            
            if existing:
                messagebox.showerror("Error", "A clearance fee already exists for this exam and programme combination.\nUse 'Edit' to modify existing fees.")
                return
            
            # Insert - including year_of_study
            insert_query = """
                INSERT INTO exam_clearance_fees (exam_name, semester, academic_year, programme_id, year_of_study, exam_fee_amount)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            result = execute_query(insert_query, (exam_name, semester, academic_year, programme_id, year_of_study, fee_amount))
            
            if result:
                year_display = f"Year {year_of_study}" if year_of_study else "All Years"
                messagebox.showinfo("Success", f"Exam clearance fee set successfully! Year: {year_display}!\n\nProgramme: {prog_name}\nExam: {exam_option}\nFee: TZS {fee_amount:,.2f}")
                dialog.destroy()
                self.load_exam_clearance_fees(parent)
            else:
                messagebox.showerror("Error", "Failed to add exam clearance fee")
        
        tk.Button(
            dialog,
            text="Save Exam Clearance Fee",
            bg="#27ae60",
            fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).pack(pady=20)
    
    def edit_exam_clearance_fee(self, parent):
        """Edit selected exam clearance fee"""
        selection = self.clearance_fee_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a clearance fee to edit")
            return
        
        item = self.clearance_fee_tree.item(selection[0])
        fee_id = item['values'][0]
        
        # Get current values
        query = "SELECT * FROM exam_clearance_fees WHERE exam_fee_id = %s"
        fee_data = execute_query(query, (fee_id,), fetch=True)
        
        if not fee_data:
            messagebox.showerror("Error", "Clearance fee not found")
            return
        
        fee_data = fee_data[0]
        
        # Get exams and programmes
        exams_query = "SELECT exam_id, exam_name, semester, academic_year FROM exams ORDER BY academic_year DESC"
        exams = execute_query(exams_query, fetch=True)
        
        programmes_query = "SELECT programme_id, name FROM programmes ORDER BY name"
        programmes = execute_query(programmes_query, fetch=True)
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Exam Clearance Fee")
        dialog.geometry("500x400")
        dialog.transient(self.parent)
        
        # Form
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10)
        
        # Exam (disabled for editing)
        tk.Label(form_frame, text="Exam:", bg="white").grid(row=0, column=0, sticky="w", pady=10)
        exam_var = tk.StringVar()
        exam_map = {}
        exam_options = []
        for e in exams:
            option = f"{e['exam_name']} - {e['semester']} ({e['academic_year']})"
            exam_options.append(option)
            exam_map[option] = e['exam_id']
        
        exam_combo = ttk.Combobox(form_frame, textvariable=exam_var, values=exam_options, width=35, state="readonly")
        exam_combo.grid(row=0, column=1, pady=10, padx=10)
        
        # Set current exam - find matching exam from dropdown options
        current_exam = f"{fee_data['exam_name']} - {fee_data['semester']} ({fee_data['academic_year']})"
        exam_var.set(current_exam)
        
        # Programme (disabled for editing)
        tk.Label(form_frame, text="Programme:", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        prog_var = tk.StringVar()
        prog_map = {}
        prog_options = []
        for p in programmes:
            prog_options.append(p['name'])
            prog_map[p['name']] = p['programme_id']
        
        prog_combo = ttk.Combobox(form_frame, textvariable=prog_var, values=prog_options, width=35, state="readonly")
        prog_combo.grid(row=1, column=1, pady=10, padx=10)
        
        # Set current programme
        for pname, pid in prog_map.items():
            if pid == fee_data['programme_id']:
                prog_var.set(pname)
                break
        
        # Year of Study selection (1,2,3,4,5,All) - Add this field
        tk.Label(form_frame, text="Year:", bg="white").grid(row=2, column=0, sticky="w", pady=10)
        year_var = tk.StringVar()
        year_options = ["All", "1", "2", "3", "4", "5"]
        year_combo = ttk.Combobox(form_frame, textvariable=year_var, values=year_options, width=33, state="readonly")
        year_combo.grid(row=2, column=1, pady=10, padx=10)
        
        # Set current year_of_study
        current_year = fee_data.get('year_of_study')
        if current_year:
            year_var.set(str(current_year))
        else:
            year_var.set("All")
        
        # Clearance fee amount
        tk.Label(form_frame, text="Clearance Fee (TZS):", bg="white").grid(row=3, column=0, sticky="w", pady=10)
        fee_entry = tk.Entry(form_frame, width=38)
        fee_entry.grid(row=3, column=1, pady=10, padx=10)
        fee_entry.insert(0, str(fee_data['exam_fee_amount']))
        
        def save():
            year_value = year_var.get()
            fee_amount = fee_entry.get().strip()
            
            # Parse year - "All" means NULL (applies to all years)
            year_of_study = int(year_value) if year_value not in ("All", "") else None
            
            try:
                fee_amount = float(fee_amount)
                if fee_amount < 0:
                    raise ValueError()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid fee amount")
                return
            
            update_query = """
                UPDATE exam_clearance_fees SET exam_fee_amount = %s, year_of_study = %s
                WHERE exam_fee_id = %s
            """
            result = execute_query(update_query, (fee_amount, year_of_study, fee_id))
            
            if result:
                messagebox.showinfo("Success", "Exam clearance fee updated successfully!")
                dialog.destroy()
                self.load_exam_clearance_fees(parent)
            else:
                messagebox.showerror("Error", "Failed to update exam clearance fee")
        
        tk.Button(
            dialog,
            text="Update Exam Clearance Fee",
            bg="#3498db",
            fg="white",
            font=("Arial", 10, "bold"),
            command=save
        ).pack(pady=20)
    
    def delete_exam_clearance_fee(self, parent):
        """Delete selected exam clearance fee"""
        selection = self.clearance_fee_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a clearance fee to delete")
            return
        
        item = self.clearance_fee_tree.item(selection[0])
        fee_id = item['values'][0]
        exam_name = item['values'][1]
        prog_name = item['values'][4]
        
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the clearance fee for:\n\nExam: {exam_name}\nProgramme: {prog_name}\n\nThis action cannot be undone."
        )
        
        if confirm:
            query = "DELETE FROM exam_clearance_fees WHERE exam_fee_id = %s"
            result = execute_query(query, (fee_id,))
            
            if result:
                messagebox.showinfo("Success", "Exam clearance fee deleted successfully!")
                self.load_exam_clearance_fees(parent)
            else:
                messagebox.showerror("Error", "Failed to delete exam clearance fee")
    
    def create_students_tab(self):
        """Create students management tab for finance"""
        tab = tk.Frame(self.notebook, bg="#ecf0f1")
        self.notebook.add(tab, text="Students")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg="#ecf0f1")
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="Refresh",
            command=lambda: self.load_students(tab)
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="Assign Special Fee",
            bg="#e67e22",
            fg="white",
            command=lambda: self.assign_special_fee(tab)
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
        columns = ("ID", "Reg No", "Full Name", "Programme", "Year", "Status", "Balance")
        self.student_tree = ttk.Treeview(tab, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.student_tree.heading(col, text=col)
            self.student_tree.column(col, width=120)
        
        self.student_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.load_students(tab)
    
    def load_students(self, tab):
        """Load students with balance"""
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        query = """
            SELECT s.student_id, s.reg_no, s.full_name, s.programme, s.year_of_study, s.status,
                   COALESCE(SUM(fs.amount), 0) as total_due,
                   COALESCE(SUM(p.amount_paid), 0) as total_paid
            FROM students s
            LEFT JOIN student_fee_obligations sfo ON s.student_id = sfo.student_id
            LEFT JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
            LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id AND p.receipt_checked = 1
            GROUP BY s.student_id
            ORDER BY s.full_name
        """
        
        results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                balance = float(row['total_due']) - float(row['total_paid'])
                self.student_tree.insert("", tk.END, values=(
                    row['student_id'],
                    row['reg_no'],
                    row['full_name'],
                    row['programme'],
                    row['year_of_study'],
                    row['status'],
                    f"{balance:,.2f}"
                ))
    
    def search_students(self, tab):
        """Search students"""
        search_term = self.student_search.get().strip()
        
        for item in self.student_tree.get_children():
            self.student_tree.delete(item)
        
        if search_term:
            query = """
                SELECT s.student_id, s.reg_no, s.full_name, s.programme, s.year_of_study, s.status,
                       COALESCE(SUM(fs.amount), 0) as total_due,
                       COALESCE(SUM(p.amount_paid), 0) as total_paid
                FROM students s
                LEFT JOIN student_fee_obligations sfo ON s.student_id = sfo.student_id
                LEFT JOIN fee_structures fs ON sfo.fee_id = fs.fee_id
                LEFT JOIN payments p ON sfo.obligation_id = p.obligation_id AND p.receipt_checked = 1
                WHERE s.reg_no LIKE %s OR s.full_name LIKE %s OR s.programme LIKE %s
                GROUP BY s.student_id
                ORDER BY s.full_name
            """
            search_pattern = f"%{search_term}%"
            results = execute_query(query, (search_pattern, search_pattern, search_pattern), fetch=True)
        else:
            results = execute_query(query, fetch=True)
        
        if results:
            for row in results:
                balance = float(row['total_due']) - float(row['total_paid'])
                self.student_tree.insert("", tk.END, values=(
                    row['student_id'],
                    row['reg_no'],
                    row['full_name'],
                    row['programme'],
                    row['year_of_study'],
                    row['status'],
                    f"{balance:,.2f}"
                ))
    
    def assign_special_fee(self, parent):
        """Assign a special/different fee structure to a specific student (for repeating students, etc.)"""
        # Get students
        student_query = "SELECT * FROM students WHERE status = 'ACTIVE' ORDER BY full_name"
        students = execute_query(student_query, fetch=True)
        
        if not students:
            messagebox.showwarning("Warning", "No active students found.")
            return
        
        # Get fee structures
        fee_query = "SELECT * FROM fee_structures ORDER BY programme, year_of_study, semester"
        fee_structures = execute_query(fee_query, fetch=True)
        
        if not fee_structures:
            messagebox.showwarning("Warning", "No fee structures found. Please add fee structures first.")
            return
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Assign Special Fee to Student")
        dialog.geometry("550x550")
        dialog.transient(self.parent)
        
        # Info
        info_label = tk.Label(
            dialog,
            text="Assign a DIFFERENT fee structure to a specific student.\nUse this for students who are repeating modules (e.g., a Year 2 student repeating Year 1 modules).",
            font=("Arial", 10),
            bg="#ecf0f1",
            fg="#e74c3c",
            wraplength=500
        )
        info_label.pack(pady=10)
        
        # Form
        form_frame = tk.Frame(dialog, bg="white")
        form_frame.pack(pady=10)
        
        # Student selection
        tk.Label(form_frame, text="Select Student:", bg="white").grid(row=0, column=0, sticky="w", pady=10)
        student_var = tk.StringVar()
        student_map = {}
        student_options = []
        for s in students:
            option = f"{s['reg_no']} - {s['full_name']}"
            student_options.append(option)
            student_map[option] = s
        
        student_combo = ttk.Combobox(form_frame, textvariable=student_var, values=student_options, width=35, state="readonly")
        student_combo.grid(row=0, column=1, pady=10, padx=10)
        if student_options:
            student_combo.current(0)
        
        # Fee structure selection
        tk.Label(form_frame, text="Select Fee Structure:", bg="white").grid(row=1, column=0, sticky="w", pady=10)
        fee_var = tk.StringVar()
        fee_map = {}
        fee_options = []
        for fs in fee_structures:
            option = f"{fs['programme']} - Year {fs['year_of_study']} - {fs['semester']} (TZS {fs['amount']:,.0f})"
            fee_options.append(option)
            fee_map[option] = fs
        
        fee_combo = ttk.Combobox(form_frame, textvariable=fee_var, values=fee_options, width=35, state="readonly")
        fee_combo.grid(row=1, column=1, pady=10, padx=10)
        if fee_options:
            fee_combo.current(0)
        
        # Academic Year
        tk.Label(form_frame, text="Academic Year:", bg="white").grid(row=2, column=0, sticky="w", pady=10)
        academic_year_entry = tk.Entry(form_frame, width=38)
        academic_year_entry.grid(row=2, column=1, pady=10, padx=10)
        academic_year_entry.insert(0, "2024/2025")
        
        # Reason
        tk.Label(form_frame, text="Reason (required):", bg="white").grid(row=3, column=0, sticky="nw", pady=10)
        reason_text = tk.Text(form_frame, width=30, height=4)
        reason_text.grid(row=3, column=1, pady=10, padx=10)
        
        tk.Label(form_frame, text="Example: Repeating Year 1 module while in Year 2", bg="white", fg="#7f8c8d", font=("Arial", 8)).grid(row=4, column=1, sticky="w")
        
        def save():
            student_option = student_var.get()
            fee_option = fee_var.get()
            academic_year = academic_year_entry.get().strip()
            reason = reason_text.get("1.0", tk.END).strip()
            
            if not student_option:
                messagebox.showerror("Error", "Please select a student")
                return
            
            if not fee_option:
                messagebox.showerror("Error", "Please select a fee structure")
                return
            
            if not academic_year:
                messagebox.showerror("Error", "Please enter academic year")
                return
            
            if not reason:
                messagebox.showerror("Error", "Please provide a reason for this special assignment")
                return
            
            student = student_map.get(student_option)
            fee_structure = fee_map.get(fee_option)
            
            if not student or not fee_structure:
                messagebox.showerror("Error", "Invalid selection")
                return
            
            student_id = student['student_id']
            fee_id = fee_structure['fee_id']
            
            # Check if student already has an obligation for this fee and year
            check_query = """
                SELECT obligation_id FROM student_fee_obligations 
                WHERE student_id = %s AND fee_id = %s AND academic_year = %s
            """
            existing = execute_query(check_query, (student_id, fee_id, academic_year), fetch=True)
            
            if existing:
                messagebox.showwarning("Warning", "This student already has this fee obligation for the selected academic year.")
                return
            
            # Create the special fee obligation
            conn = get_connection()
            if not conn:
                messagebox.showerror("Error", "Database connection failed")
                return
            
            try:
                cursor = conn.cursor()
                
                insert_query = """
                    INSERT INTO student_fee_obligations (student_id, fee_id, academic_year, is_cleared)
                    VALUES (%s, %s, %s, 0)
                """
                cursor.execute(insert_query, (student_id, fee_id, academic_year))
                
                # Get the new obligation_id
                cursor.execute("SELECT LAST_INSERT_ID() as obligation_id")
                result = cursor.fetchone()
                obligation_id = result[0] if result else None
                
                # Insert verification record with the reason
                if obligation_id:
                    verify_query = """
                        INSERT INTO finance_verifications 
                        (obligation_id, verified_by, decision, comment, is_final, verified_at)
                        VALUES (%s, %s, %s, %s, 1, NOW())
                    """
                    cursor.execute(verify_query, (
                        obligation_id,
                        self.user['username'],
                        "SPECIAL_ASSIGNMENT",
                        f"Special Fee Assignment: {reason}"
                    ))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                messagebox.showinfo("Success", 
                    f"Special fee assigned successfully!\n\n"
                    f"Student: {student['full_name']}\n"
                    f"Fee: TZS {fee_structure['amount']:,.2f}\n"
                    f"Academic Year: {academic_year}\n"
                    f"Reason: {reason}\n\n"
                    f"The student can now view and pay this special fee.")
                dialog.destroy()
                self.load_students(parent)
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to assign special fee: {str(e)}")
                try:
                    conn.rollback()
                    conn.close()
                except:
                    pass
        
        tk.Button(
            dialog,
            text="Assign Special Fee",
            bg="#e67e22",
            fg="white",
            font=("Arial", 11, "bold"),
            command=save,
            width=20,
            pady=10
        ).pack(pady=20)
    
    def load_data(self):
        """Load initial data"""
        pass
