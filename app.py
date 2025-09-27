"""
Employee Directory Application
Main Flask application file
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
import os
from app.employee_service import EmployeeService
from app.models.employee import Employee
import uuid

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Initialize services
employee_service = EmployeeService()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Display all employees"""
    try:
        employees = employee_service.get_all_employees()
        return render_template('index.html', employees=employees)
    except Exception as e:
        flash(f'Error loading employees: {str(e)}', 'error')
        return render_template('index.html', employees=[])

@app.route('/add', methods=['GET', 'POST'])
def add_employee():
    """Add new employee"""
    if request.method == 'POST':
        try:
            # Get form data
            employee_data = {
                'employee_id': str(uuid.uuid4()),
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'position': request.form['position'],
                'department': request.form['department'],
                'phone': request.form.get('phone', ''),
                'hire_date': request.form.get('hire_date', '')
            }
            
            # Handle file upload
            profile_picture_url = None
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    profile_picture_url = employee_service.upload_profile_picture(
                        file, employee_data['employee_id'], filename
                    )
            
            employee_data['profile_picture_url'] = profile_picture_url
            
            # Create employee
            employee = Employee(**employee_data)
            result = employee_service.add_employee(employee)
            
            if result:
                flash('Employee added successfully!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Failed to add employee.', 'error')
                
        except Exception as e:
            flash(f'Error adding employee: {str(e)}', 'error')
    
    return render_template('add_employee.html')

@app.route('/employee/<employee_id>')
def view_employee(employee_id):
    """View employee details"""
    try:
        employee = employee_service.get_employee(employee_id)
        if employee:
            return render_template('view_employee.html', employee=employee)
        else:
            flash('Employee not found.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error loading employee: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/edit/<employee_id>', methods=['GET', 'POST'])
def edit_employee(employee_id):
    """Edit employee details"""
    if request.method == 'POST':
        try:
            # Get current employee
            current_employee = employee_service.get_employee(employee_id)
            if not current_employee:
                flash('Employee not found.', 'error')
                return redirect(url_for('index'))
            
            # Update employee data
            employee_data = {
                'employee_id': employee_id,
                'first_name': request.form['first_name'],
                'last_name': request.form['last_name'],
                'email': request.form['email'],
                'position': request.form['position'],
                'department': request.form['department'],
                'phone': request.form.get('phone', ''),
                'hire_date': request.form.get('hire_date', ''),
                'profile_picture_url': current_employee.profile_picture_url
            }
            
            # Handle new profile picture
            if 'profile_picture' in request.files:
                file = request.files['profile_picture']
                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Delete old picture if exists
                    if current_employee.profile_picture_url:
                        employee_service.delete_profile_picture(employee_id)
                    
                    # Upload new picture
                    profile_picture_url = employee_service.upload_profile_picture(
                        file, employee_id, filename
                    )
                    employee_data['profile_picture_url'] = profile_picture_url
            
            # Update employee
            employee = Employee(**employee_data)
            result = employee_service.update_employee(employee)
            
            if result:
                flash('Employee updated successfully!', 'success')
                return redirect(url_for('view_employee', employee_id=employee_id))
            else:
                flash('Failed to update employee.', 'error')
                
        except Exception as e:
            flash(f'Error updating employee: {str(e)}', 'error')
    
    # GET request - show edit form
    try:
        employee = employee_service.get_employee(employee_id)
        if employee:
            return render_template('edit_employee.html', employee=employee)
        else:
            flash('Employee not found.', 'error')
            return redirect(url_for('index'))
    except Exception as e:
        flash(f'Error loading employee: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/delete/<employee_id>', methods=['POST'])
def delete_employee(employee_id):
    """Delete employee"""
    try:
        result = employee_service.delete_employee(employee_id)
        if result:
            flash('Employee deleted successfully!', 'success')
        else:
            flash('Failed to delete employee.', 'error')
    except Exception as e:
        flash(f'Error deleting employee: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/api/employees')
def api_employees():
    """API endpoint to get all employees as JSON"""
    try:
        employees = employee_service.get_all_employees()
        employees_data = [employee.to_dict() for employee in employees]
        return jsonify(employees_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)