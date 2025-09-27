"""
Employee Model
Represents an employee in the directory system
"""

from datetime import datetime
from typing import Optional, Dict, Any
import json

class Employee:
    """Employee model class"""
    
    def __init__(
        self,
        employee_id: str,
        first_name: str,
        last_name: str,
        email: str,
        position: str,
        department: str,
        phone: Optional[str] = None,
        hire_date: Optional[str] = None,
        profile_picture_url: Optional[str] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        self.employee_id = employee_id
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.position = position
        self.department = department
        self.phone = phone or ""
        self.hire_date = hire_date or ""
        self.profile_picture_url = profile_picture_url or ""
        
        # Timestamps
        current_time = datetime.utcnow().isoformat()
        self.created_at = created_at or current_time
        self.updated_at = updated_at or current_time
    
    @property
    def full_name(self) -> str:
        """Get employee's full name"""
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert employee to dictionary for DynamoDB storage"""
        return {
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'position': self.position,
            'department': self.department,
            'phone': self.phone,
            'hire_date': self.hire_date,
            'profile_picture_url': self.profile_picture_url,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Employee':
        """Create Employee instance from dictionary"""
        return cls(
            employee_id=data.get('employee_id', ''),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            email=data.get('email', ''),
            position=data.get('position', ''),
            department=data.get('department', ''),
            phone=data.get('phone', ''),
            hire_date=data.get('hire_date', ''),
            profile_picture_url=data.get('profile_picture_url', ''),
            created_at=data.get('created_at', ''),
            updated_at=data.get('updated_at', '')
        )
    
    def to_json(self) -> str:
        """Convert employee to JSON string"""
        return json.dumps(self.to_dict(), indent=2)
    
    def update_timestamp(self):
        """Update the updated_at timestamp"""
        self.updated_at = datetime.utcnow().isoformat()
    
    def validate(self) -> tuple[bool, list]:
        """
        Validate employee data
        Returns (is_valid, errors_list)
        """
        errors = []
        
        # Required fields validation
        if not self.employee_id:
            errors.append("Employee ID is required")
        
        if not self.first_name or not self.first_name.strip():
            errors.append("First name is required")
        
        if not self.last_name or not self.last_name.strip():
            errors.append("Last name is required")
        
        if not self.email or not self.email.strip():
            errors.append("Email is required")
        elif '@' not in self.email or '.' not in self.email:
            errors.append("Invalid email format")
        
        if not self.position or not self.position.strip():
            errors.append("Position is required")
        
        if not self.department or not self.department.strip():
            errors.append("Department is required")
        
        # Length validations
        if len(self.first_name) > 50:
            errors.append("First name must be 50 characters or less")
        
        if len(self.last_name) > 50:
            errors.append("Last name must be 50 characters or less")
        
        if len(self.email) > 100:
            errors.append("Email must be 100 characters or less")
        
        if len(self.position) > 100:
            errors.append("Position must be 100 characters or less")
        
        if len(self.department) > 50:
            errors.append("Department must be 50 characters or less")
        
        if self.phone and len(self.phone) > 20:
            errors.append("Phone number must be 20 characters or less")
        
        return len(errors) == 0, errors
    
    def __str__(self) -> str:
        """String representation of employee"""
        return f"Employee({self.employee_id}: {self.full_name} - {self.position})"
    
    def __repr__(self) -> str:
        """Detailed string representation"""
        return (f"Employee(id='{self.employee_id}', name='{self.full_name}', "
                f"email='{self.email}', position='{self.position}', "
                f"department='{self.department}')")
    
    def __eq__(self, other) -> bool:
        """Check equality based on employee_id"""
        if not isinstance(other, Employee):
            return False
        return self.employee_id == other.employee_id