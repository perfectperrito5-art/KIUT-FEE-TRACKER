# Receipt Upload Enhancement Plan

## Features to Add:
1. **Receipt Image Upload** - Allow students to upload receipt images (jpg, png, pdf)
2. **Receipt Details Input** - Input fields for:
   - Student Full Name (from receipt)
   - Registration Number (from receipt) 
   - Payment Date (from receipt)
   - Payment Description
   - Amount Paid
   - Reference/Transaction Number
   - Payment Method
3. **Security Features** (already in backend):
   - File hash to detect duplicates
   - File size/type validation
   - Amount mismatch detection
   - Name/ID mismatch detection
   - Duplicate receipt detection

## Files to Modify:
1. GUI/student_dashboard.py - Update make_payment() method
2. Create receipts folder for storing images

## Migration:
- Run migration_add_user_id.sql first (if not done)
- Ensure receipts folder exists with proper permissions
