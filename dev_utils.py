"""
Development utilities and helper scripts
"""

import os
import json
from datetime import datetime
from app.models.employee import Employee
from app.employee_service import EmployeeService
import uuid

def create_sample_employees():
    """Create sample employees for testing"""
    service = EmployeeService()
    
    sample_employees = [
        {
            'employee_id': str(uuid.uuid4()),
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'john.doe@company.com',
            'position': 'Software Engineer',
            'department': 'Engineering',
            'phone': '(555) 123-4567',
            'hire_date': '2023-01-15'
        },
        {
            'employee_id': str(uuid.uuid4()),
            'first_name': 'Jane',
            'last_name': 'Smith',
            'email': 'jane.smith@company.com',
            'position': 'Product Manager',
            'department': 'Product',
            'phone': '(555) 234-5678',
            'hire_date': '2022-11-01'
        },
        {
            'employee_id': str(uuid.uuid4()),
            'first_name': 'Mike',
            'last_name': 'Johnson',
            'email': 'mike.johnson@company.com',
            'position': 'UI/UX Designer',
            'department': 'Design',
            'phone': '(555) 345-6789',
            'hire_date': '2023-03-20'
        },
        {
            'employee_id': str(uuid.uuid4()),
            'first_name': 'Sarah',
            'last_name': 'Wilson',
            'email': 'sarah.wilson@company.com',
            'position': 'Marketing Specialist',
            'department': 'Marketing',
            'phone': '(555) 456-7890',
            'hire_date': '2022-09-10'
        },
        {
            'employee_id': str(uuid.uuid4()),
            'first_name': 'David',
            'last_name': 'Brown',
            'email': 'david.brown@company.com',
            'position': 'DevOps Engineer',
            'department': 'Engineering',
            'phone': '(555) 567-8901',
            'hire_date': '2023-02-28'
        }
    ]
    
    for emp_data in sample_employees:
        employee = Employee(**emp_data)
        success = service.add_employee(employee)
        if success:
            print(f"✅ Created employee: {employee.full_name}")
        else:
            print(f"❌ Failed to create employee: {employee.full_name}")

def export_all_employees():
    """Export all employees to JSON file"""
    service = EmployeeService()
    employees = service.get_all_employees()
    
    employees_data = [emp.to_dict() for emp in employees]
    
    filename = f"employees_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(filename, 'w') as f:
        json.dump(employees_data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(employees)} employees to {filename}")

def check_system_health():
    """Check system health and AWS connections"""
    service = EmployeeService()
    health = service.health_check()
    
    print("🏥 System Health Check")
    print("=" * 30)
    print(f"Database (DynamoDB): {'✅ Healthy' if health['database'] else '❌ Unhealthy'}")
    print(f"Storage (S3): {'✅ Healthy' if health['storage'] else '❌ Unhealthy'}")
    print(f"Overall System: {'✅ Healthy' if health['overall'] else '❌ Unhealthy'}")
    
    if not health['overall']:
        print("\n⚠️  System issues detected. Check AWS credentials and connectivity.")

def get_statistics():
    """Get and display system statistics"""
    service = EmployeeService()
    stats = service.get_statistics()
    
    print("📊 Employee Directory Statistics")
    print("=" * 35)
    print(f"Total Employees: {stats.get('total_employees', 0)}")
    print(f"Total Departments: {stats.get('total_departments', 0)}")
    print(f"Total Positions: {stats.get('total_positions', 0)}")
    print(f"Employees with Pictures: {stats.get('employees_with_pictures', 0)}")
    
    print("\n📈 Department Breakdown:")
    dept_breakdown = stats.get('department_breakdown', {})
    for dept, count in sorted(dept_breakdown.items()):
        print(f"  {dept}: {count} employees")
    
    storage_info = stats.get('storage_info', {})
    if storage_info:
        print(f"\n💾 Storage Information:")
        print(f"  Bucket: {storage_info.get('bucket_name', 'N/A')}")
        print(f"  Region: {storage_info.get('region', 'N/A')}")
        print(f"  Total Files: {storage_info.get('total_objects', 0)}")
        print(f"  Total Size: {storage_info.get('total_size_mb', 0)} MB")

if __name__ == '__main__':
    print("🚀 Employee Directory Development Utilities")
    print("=" * 45)
    
    while True:
        print("\nAvailable commands:")
        print("1. Create sample employees")
        print("2. Export all employees")
        print("3. Check system health")
        print("4. Get statistics")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == '1':
            create_sample_employees()
        elif choice == '2':
            export_all_employees()
        elif choice == '3':
            check_system_health()
        elif choice == '4':
            get_statistics()
        elif choice == '5':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")