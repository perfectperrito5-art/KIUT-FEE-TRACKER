# TODO: Add Programme Year to Exam Clearance Fee

## Task
Allow finance officers to specify the programme year (1/2/3/4/5/all) when adding exam clearance fees.

## Changes Required

### 1. Fix INSERT Query in `add_exam_clearance_fee` (finance_dashboard.py)
- Add year_of_study to the INSERT query
- Currently missing from the query

### 2. Update View `v_student_exam_clearance_status` (migration_exam_clearance_fees.sql)
- Add year_of_study column to the view
- Filter by student's year_of_study

### 3. Add Year Selection to Edit Dialog (finance_dashboard.py)
- Add year combo box to edit_exam_clearance_fee function

## Status
- [ ] Fix INSERT query to include year_of_study
- [ ] Update view to include year_of_study filtering
- [ ] Add year selection to edit dialog

