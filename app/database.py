"""
DynamoDB Database Layer
Handles all DynamoDB operations for employee data
"""

import boto3
from botocore.exceptions import ClientError
from typing import List, Optional, Dict, Any
from app.models.employee import Employee
from config.aws_config import AWSConfig
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmployeeDatabase:
    """DynamoDB database operations for employees"""
    
    def __init__(self):
        """Initialize DynamoDB connection"""
        try:
            self.dynamodb = boto3.resource('dynamodb', **AWSConfig.get_dynamodb_config())
            self.table = self.dynamodb.Table(AWSConfig.DYNAMODB_TABLE_NAME)
        except Exception as e:
            logger.error(f"Failed to initialize DynamoDB: {str(e)}")
            raise
    
    def create_employee(self, employee: Employee) -> bool:
        """
        Create a new employee record
        
        Args:
            employee: Employee object to create
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Validate employee data
            is_valid, errors = employee.validate()
            if not is_valid:
                logger.error(f"Employee validation failed: {errors}")
                return False
            
            # Check if employee already exists
            if self.get_employee(employee.employee_id):
                logger.error(f"Employee with ID {employee.employee_id} already exists")
                return False
            
            # Add employee to DynamoDB
            response = self.table.put_item(Item=employee.to_dict())
            logger.info(f"Employee {employee.employee_id} created successfully")
            return True
            
        except ClientError as e:
            logger.error(f"DynamoDB ClientError creating employee: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating employee: {str(e)}")
            return False
    
    def get_employee(self, employee_id: str) -> Optional[Employee]:
        """
        Get employee by ID
        
        Args:
            employee_id: Employee ID to search for
            
        Returns:
            Employee object if found, None otherwise
        """
        try:
            response = self.table.get_item(Key={'employee_id': employee_id})
            
            if 'Item' in response:
                return Employee.from_dict(response['Item'])
            else:
                logger.info(f"Employee {employee_id} not found")
                return None
                
        except ClientError as e:
            logger.error(f"DynamoDB ClientError getting employee: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting employee: {str(e)}")
            return None
    
    def update_employee(self, employee: Employee) -> bool:
        """
        Update existing employee record
        
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
            if not self.get_employee(employee.employee_id):
                logger.error(f"Employee {employee.employee_id} not found for update")
                return False
            
            # Update timestamp
            employee.update_timestamp()
            
            # Update employee in DynamoDB
            response = self.table.put_item(Item=employee.to_dict())
            logger.info(f"Employee {employee.employee_id} updated successfully")
            return True
            
        except ClientError as e:
            logger.error(f"DynamoDB ClientError updating employee: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating employee: {str(e)}")
            return False
    
    def delete_employee(self, employee_id: str) -> bool:
        """
        Delete employee by ID
        
        Args:
            employee_id: Employee ID to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if employee exists
            if not self.get_employee(employee_id):
                logger.error(f"Employee {employee_id} not found for deletion")
                return False
            
            # Delete employee from DynamoDB
            response = self.table.delete_item(Key={'employee_id': employee_id})
            logger.info(f"Employee {employee_id} deleted successfully")
            return True
            
        except ClientError as e:
            logger.error(f"DynamoDB ClientError deleting employee: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting employee: {str(e)}")
            return False
    
    def get_all_employees(self) -> List[Employee]:
        """
        Get all employees
        
        Returns:
            List of Employee objects
        """
        try:
            employees = []
            
            # Scan table for all items
            response = self.table.scan()
            
            # Convert items to Employee objects
            for item in response.get('Items', []):
                employee = Employee.from_dict(item)
                employees.append(employee)
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
                for item in response.get('Items', []):
                    employee = Employee.from_dict(item)
                    employees.append(employee)
            
            logger.info(f"Retrieved {len(employees)} employees")
            return employees
            
        except ClientError as e:
            logger.error(f"DynamoDB ClientError getting all employees: {e.response['Error']['Message']}")
            return []
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
            employees = []
            
            # Scan with filter expression
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('department').eq(department)
            )
            
            # Convert items to Employee objects
            for item in response.get('Items', []):
                employee = Employee.from_dict(item)
                employees.append(employee)
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    FilterExpression=boto3.dynamodb.conditions.Attr('department').eq(department)
                )
                for item in response.get('Items', []):
                    employee = Employee.from_dict(item)
                    employees.append(employee)
            
            logger.info(f"Found {len(employees)} employees in department '{department}'")
            return employees
            
        except ClientError as e:
            logger.error(f"DynamoDB ClientError searching employees: {e.response['Error']['Message']}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching employees: {str(e)}")
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
            employees = []
            
            # Scan with filter expression
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('position').contains(position)
            )
            
            # Convert items to Employee objects
            for item in response.get('Items', []):
                employee = Employee.from_dict(item)
                employees.append(employee)
            
            # Handle pagination if needed
            while 'LastEvaluatedKey' in response:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    FilterExpression=boto3.dynamodb.conditions.Attr('position').contains(position)
                )
                for item in response.get('Items', []):
                    employee = Employee.from_dict(item)
                    employees.append(employee)
            
            logger.info(f"Found {len(employees)} employees with position containing '{position}'")
            return employees
            
        except ClientError as e:
            logger.error(f"DynamoDB ClientError searching employees: {e.response['Error']['Message']}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching employees: {str(e)}")
            return []
    
    def get_employee_by_email(self, email: str) -> Optional[Employee]:
        """
        Get employee by email (requires scanning, not efficient for large datasets)
        
        Args:
            email: Employee email to search for
            
        Returns:
            Employee object if found, None otherwise
        """
        try:
            # Scan with filter expression
            response = self.table.scan(
                FilterExpression=boto3.dynamodb.conditions.Attr('email').eq(email)
            )
            
            # Return first match (emails should be unique)
            items = response.get('Items', [])
            if items:
                return Employee.from_dict(items[0])
            else:
                logger.info(f"Employee with email {email} not found")
                return None
                
        except ClientError as e:
            logger.error(f"DynamoDB ClientError getting employee by email: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting employee by email: {str(e)}")
            return None
    
    def health_check(self) -> bool:
        """
        Check if DynamoDB connection is healthy
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            # Try to describe the table
            response = self.table.meta.client.describe_table(TableName=AWSConfig.DYNAMODB_TABLE_NAME)
            return response['Table']['TableStatus'] == 'ACTIVE'
        except Exception as e:
            logger.error(f"DynamoDB health check failed: {str(e)}")
            return False