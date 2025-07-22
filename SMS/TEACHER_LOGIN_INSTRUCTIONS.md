# Teacher Login Instructions

## How to Login as a Teacher

### Step 1: Access the Login Page
- Open your browser and go to: `http://127.0.0.1:8000/accounts/login/`
- You will see the login form with a dropdown for user type selection

### Step 2: Select User Type
- In the "Select User Type" dropdown, choose **"Teacher"**

### Step 3: Enter Credentials
Use one of the following teacher accounts:

#### Test Teacher Account (Created for testing)
- **Username:** `254016`
- **Password:** `254016@#12`

#### Other Available Teacher Accounts
- **Username:** `ama258531` | **Password:** `ama258531`
- **Username:** `ama256802` | **Password:** `ama256802`
- **Username:** `ama252006` | **Password:** `ama252006`
- **Username:** `ama251605` | **Password:** `ama251605`
- **Username:** `new254379` | **Password:** `new254379@#12`

### Step 4: Login
- Click the "Login" button
- You will be redirected to the teacher dashboard at: `http://127.0.0.1:8000/teacher-dashboard/dashboard/`

### Step 5: Access Teacher Profile
- Once logged in, you can access your profile by:
  1. Clicking on your username in the top-right corner
  2. Selecting "My Profile" from the dropdown menu
  3. Or directly visiting: `http://127.0.0.1:8000/teacher-dashboard/profile/`

## Teacher Profile Features

The updated teacher profile page now includes:

### Personal Information Section
- Full name with professional header
- Registration number and join date
- Gender with icons
- Date of birth
- Mobile number
- Subject specialization
- Aadhar number (if available)
- Address
- Additional information

### Login Credentials Section
- Login ID with copy functionality
- Password with show/hide toggle and copy functionality
- Security reminder

### Quick Stats Section
- Total students count
- Total classes count

### Recent Students Section
- List of recently admitted students
- Student names with class and section information

### Interactive Features
- Copy to clipboard functionality for login credentials
- Password visibility toggle
- Responsive design for mobile and desktop
- Professional styling with icons and colors

## Creating Additional Teacher Accounts

To create more teacher accounts, you can:

1. **Using Django Admin:**
   - Go to `http://127.0.0.1:8000/admin/`
   - Login as admin
   - Navigate to "Staffs" → "Staff"
   - Click "Add Staff" to create new teacher accounts

2. **Using Management Command:**
   ```bash
   python manage.py create_test_teacher
   ```

3. **Using the Admin Dashboard:**
   - Login as admin user
   - Go to Staff Management section
   - Add new staff members

## Notes

- Teacher login credentials are automatically generated when a staff record is created
- Login ID is typically the registration number
- Password follows the format: `{registration_number}@#12` for newer accounts
- All teacher accounts have access to the teacher dashboard with student management features
- The profile page shows real data from the database
- Teachers can view and manage students, attendance, exams, and documents through their dashboard
