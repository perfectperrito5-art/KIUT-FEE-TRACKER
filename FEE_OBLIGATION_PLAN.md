# TODO: Implement Fee Obligation Assignment System

## Understanding the Issue
- Fee structures are created by admin but NOT automatically assigned to students
- Students need fee obligations to be created so they can see and pay their fees
- The system should match students by: programme + year of study + semester
- Special cases (repeating students) need manual handling by finance

## Implementation Plan

### Step 1: Add "Assign Fee Obligations" feature in Admin Dashboard
- Add a new tab or button in Admin Dashboard
- Admin can select a fee structure and assign it to matching students

### Step 2: Create automatic matching logic
- Match students by: programme + year_of_study + semester
- Create fee obligations automatically for matching students
- Track which obligations were auto-generated vs manually assigned

### Step 3: Handle special cases for finance
- Finance can manually assign different fee structures to individual students
- Add reason/comment field for why a student has different fee
- Display clear messages about fee obligations in student dashboard

### Step 4: Update student dashboard
- Show clear status when no obligations exist
- Display "Contact finance" message when there are issues

## Files to Edit:
- GUI/admin_dashboard.py - Add assign fee obligations functionality
- GUI/student_dashboard.py - Improve error messages when no obligations

## Status: PENDING IMPLEMENTATION

