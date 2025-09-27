"""
Employee Service Layer
Combines database and storage operations for complete employee management
"""

from typing import List, Optional, Dict, Any
from app.database import EmployeeDatabase
from app.storage import EmployeeStorage
from app.models.employee import Employee
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmployeeService:
    """Service layer for employee management operations"""
    
    def __init__(self):
        """Initialize database and storage connections"""
        try:
            self.db = EmployeeDatabase()
            self.storage = EmployeeStorage()
        except Exception as e:
            logger.error(f"Failed to initialize EmployeeService: {str(e)}")
            raise
    
    def add_employee(self, employee: Employee) -> bool:
        """
        Add new employee to the system
        
        Args:
            employee: Employee object to add
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate employee data
            is_valid, errors = employee.validate()
            if not is_valid:
                logger.error(f"Employee validation failed: {errors}")
                return False
            
            # Check if employee with same email already exists
            existing_employee = self.db.get_employee_by_email(employee.email)
            if existing_employee:
                logger.error(f"Employee with email {employee.email} already exists")
                return False
            
            # Add employee to database
            success = self.db.create_employee(employee)
            if success:
                logger.info(f"Employee {employee.employee_id} added successfully")
                return True
            else:
                logger.error(f"Failed to add employee {employee.employee_id}")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error adding employee: {str(e)}")
            return False
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID
        
        Args:
            employee_id: Employee ID to retrieve
            
        Returns:
            Employee object if found, None otherwise
        """
        try:
            employee = self.db.get_employee(employee_id)
            if employee:
                # Update profile picture URL with current pre-signed URL
                profile_url = self.storage.get_profile_picture_url(employee_id)
                if profile_url:
                    employee.profile_picture_url = profile_url
            
            return employee
            
        except Exception as e:
            logger.error(f"Unexpected error getting employee: {str(e)}")
            return None
    
    def update_employee(self, employee: Employee) -> bool:
        """
        Update existing employee
        
        Args:
            employee: Employee object with updated data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate employee data
            is_valid, errors = employee.validate()
            if not is_valid:
                logger.error(f"Employee validation failed: {errors}")
                return False
            
            # Check if employee exists
            existing_employee = self.db.get_employee(employee.employee_id)
            if not existing_employee:
                logger.error(f"Employee {employee.employee_id} not found for update")
                return False
            
            # Check if email is being changed and if new email already exists
            if existing_employee.email != employee.email:
                email_exists = self.db.get_employee_by_email(employee.email)
                if email_exists and email_exists.employee_id != employee.employee_id:
                    logger.error(f"Employee with email {employee.email} already exists")
                    return False
            
            # Update employee in database
            success = self.db.update_employee(employee)
            if success:
                logger.info(f"Employee {employee.employee_id} updated successfully")
                return True
            else:
                logger.error(f"Failed to update employee {employee.employee_id}")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error updating employee: {str(e)}")
            return False
    
    def delete_employee(self, employee_id: str) -> bool:
        """
        Delete employee and all associated files
        
        Args:
            employee_id: Employee ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if employee exists
            employee = self.db.get_employee(employee_id)
            if not employee:
                logger.error(f"Employee {employee_id} not found for deletion")
                return False
            
            # Delete all associated files from S3
            storage_success = self.storage.delete_all_employee_files(employee_id)
            if not storage_success:
                logger.warning(f"Failed to delete some files for employee {employee_id}")
            
            # Delete employee from database
            db_success = self.db.delete_employee(employee_id)
            
            if db_success:
                logger.info(f"Employee {employee_id} deleted successfully")
                return True
            else:
                logger.error(f"Failed to delete employee {employee_id} from database")
                return False
                
        except Exception as e:
            logger.error(f"Unexpected error deleting employee: {str(e)}")
            return False
    
    def get_all_employees(self) -> List[Employee]:
        """
        Get all employees with updated profile picture URLs
        
        Returns:
            List of Employee objects
        """
        try:
            employees = self.db.get_all_employees()
            
            # Update profile picture URLs for all employees
            for employee in employees:
                profile_url = self.storage.get_profile_picture_url(employee.employee_id)
                if profile_url:
                    employee.profile_picture_url = profile_url
            
            return employees
            
        except Exception as e:
            logger.error(f"Unexpected error getting all employees: {str(e)}")
            return []
    
    def search_employees_by_department(self, department: str) -> List[Employee]:
        """
        Search employees by department
        
        Args:
            department: Department name to search for
            
        Returns:
            List of Employee objects
        """
        try:
            employees = self.db.search_employees_by_department(department)
            
            # Update profile picture URLs
            for employee in employees:
                profile_url = self.storage.get_profile_picture_url(employee.employee_id)
                if profile_url:
                    employee.profile_picture_url = profile_url
            
            return employees
            
        except Exception as e:
            logger.error(f"Unexpected error searching employees by department: {str(e)}")
            return []
    
    def search_employees_by_position(self, position: str) -> List[Employee]:
        """
        Search employees by position
        
        Args:
            position: Position title to search for
            
        Returns:
            List of Employee objects
        """
        try:
            employees = self.db.search_employees_by_position(position)
            
            # Update profile picture URLs
            for employee in employees:
                profile_url = self.storage.get_profile_picture_url(employee.employee_id)
                if profile_url:
                    employee.profile_picture_url = profile_url
            
            return employees
            
        except Exception as e:
            logger.error(f"Unexpected error searching employees by position: {str(e)}")
            return []
    
    def upload_profile_picture(self, file_obj, employee_id: str, filename: str) -> Optional[str]:
        """
        Upload profile picture for employee
        
        Args:
            file_obj: File object to upload
            employee_id: Employee ID
            filename: Original filename
            
        Returns:
            str: Profile picture URL if successful, None otherwise
        """
        try:
            # Check if employee exists
            employee = self.db.get_employee(employee_id)
            if not employee:
                logger.error(f"Employee {employee_id} not found for profile picture upload")
                return None
            
            # Delete existing profile picture if any
            self.storage.delete_profile_picture(employee_id)
            
            # Upload new profile picture
            profile_url = self.storage.upload_profile_picture(file_obj, employee_id, filename)
            
            if profile_url:
                # Update employee record with new profile picture URL
                employee.profile_picture_url = profile_url
                self.db.update_employee(employee)
                logger.info(f"Profile picture uploaded for employee {employee_id}")
            
            return profile_url
            
        except Exception as e:
            logger.error(f"Unexpected error uploading profile picture: {str(e)}")
            return None
    
    def delete_profile_picture(self, employee_id: str) -> bool:
        """
        Delete profile picture for employee
        
        Args:
            employee_id: Employee ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if employee exists
            employee = self.db.get_employee(employee_id)
            if not employee:
                logger.error(f"Employee {employee_id} not found for profile picture deletion")
                return False
            
            # Delete profile picture from S3
            storage_success = self.storage.delete_profile_picture(employee_id)
            
            if storage_success:
                # Update employee record to remove profile picture URL
                employee.profile_picture_url = ""
                self.db.update_employee(employee)
                logger.info(f"Profile picture deleted for employee {employee_id}")
            
            return storage_success
            
        except Exception as e:
            logger.error(f"Unexpected error deleting profile picture: {str(e)}")
            return False
    
    def upload_document(self, file_obj, employee_id: str, filename: str, document_type: str = 'general') -> Optional[str]:
        """
        Upload document for employee
        
        Args:
            file_obj: File object to upload
            employee_id: Employee ID
            filename: Original filename
            document_type: Type of document
            
        Returns:
            str: Document URL if successful, None otherwise
        """
        try:
            # Check if employee exists
            employee = self.db.get_employee(employee_id)
            if not employee:
                logger.error(f"Employee {employee_id} not found for document upload")
                return None
            
            # Upload document
            document_url = self.storage.upload_document(file_obj, employee_id, filename, document_type)
            
            if document_url:
                logger.info(f"Document uploaded for employee {employee_id}: {filename}")
            
            return document_url
            
        except Exception as e:
            logger.error(f"Unexpected error uploading document: {str(e)}")
            return None
    
    def get_employee_documents(self, employee_id: str) -> List[Dict[str, Any]]:
        """
        Get all documents for an employee
        
        Args:
            employee_id: Employee ID
            
        Returns:
            List of document information dictionaries
        """
        try:
            # Check if employee exists
            employee = self.db.get_employee(employee_id)
            if not employee:
                logger.error(f"Employee {employee_id} not found for document listing")
                return []
            
            # Get documents from storage
            documents = self.storage.list_employee_documents(employee_id)
            return documents
            
        except Exception as e:
            logger.error(f"Unexpected error getting employee documents: {str(e)}")
            return []
    
    def delete_document(self, s3_key: str) -> bool:
        """
        Delete a document
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            return self.storage.delete_document(s3_key)
            
        except Exception as e:
            logger.error(f"Unexpected error deleting document: {str(e)}")
            return False
    
    def get_departments(self) -> List[str]:
        """
        Get list of all unique departments
        
        Returns:
            List of department names
        """
        try:
            employees = self.db.get_all_employees()
            departments = list(set(emp.department for emp in employees if emp.department))
            departments.sort()
            return departments
            
        except Exception as e:
            logger.error(f"Unexpected error getting departments: {str(e)}")
            return []
    
    def get_positions(self) -> List[str]:
        """
        Get list of all unique positions
        
        Returns:
            List of position titles
        """
        try:
            employees = self.db.get_all_employees()
            positions = list(set(emp.position for emp in employees if emp.position))
            positions.sort()
            return positions
            
        except Exception as e:
            logger.error(f"Unexpected error getting positions: {str(e)}")
            return []
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get employee directory statistics
        
        Returns:
            Dictionary with statistics
        """
        try:
            employees = self.db.get_all_employees()
            
            # Basic counts
            total_employees = len(employees)
            departments = self.get_departments()
            positions = self.get_positions()
            
            # Department breakdown
            dept_counts = {}
            for emp in employees:
                dept = emp.department or 'Unknown'
                dept_counts[dept] = dept_counts.get(dept, 0) + 1
            
            # Employees with profile pictures
            with_pictures = sum(1 for emp in employees if emp.profile_picture_url)
            
            # Storage statistics
            storage_info = self.storage.get_bucket_info()
            
            return {
                'total_employees': total_employees,
                'total_departments': len(departments),
                'total_positions': len(positions),
                'employees_with_pictures': with_pictures,
                'department_breakdown': dept_counts,
                'storage_info': storage_info
            }
            
        except Exception as e:
            logger.error(f"Unexpected error getting statistics: {str(e)}")
            return {}
    
    def health_check(self) -> Dict[str, bool]:
        """
        Check health of all services
        
        Returns:
            Dictionary with health status of each service
        """
        try:
            db_healthy = self.db.health_check()
            storage_healthy = self.storage.health_check()
            
            return {
                'database': db_healthy,
                'storage': storage_healthy,
                'overall': db_healthy and storage_healthy
            }
            
        except Exception as e:
            logger.error(f"Unexpected error in health check: {str(e)}")
            return {
                'database': False,
                'storage': False,
                'overall': False,
                'error': str(e)
            }