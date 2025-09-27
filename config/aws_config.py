"""
AWS Configuration Settings
"""

import os
from typing import Dict, Any

class AWSConfig:
    """AWS Configuration class"""
    
    # AWS Credentials (preferably set as environment variables)
    AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY', '')
    AWS_SESSION_TOKEN = os.getenv('AWS_SESSION_TOKEN', '')  # For temporary credentials
    AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
    
    # DynamoDB Configuration
    DYNAMODB_TABLE_NAME = os.getenv('DYNAMODB_TABLE_NAME', 'employees')
    DYNAMODB_ENDPOINT_URL = os.getenv('DYNAMODB_ENDPOINT_URL', None)  # For local DynamoDB
    
    # S3 Configuration
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', 'employee-directory-files')
    S3_ENDPOINT_URL = os.getenv('S3_ENDPOINT_URL', None)  # For local S3 (like localstack)
    S3_PROFILE_PICTURES_PREFIX = 'profile-pictures/'
    
    # Application Configuration
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_FILE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    @classmethod
    def get_aws_config(cls) -> Dict[str, Any]:
        """Get AWS configuration dictionary"""
        config = {
            'region_name': cls.AWS_REGION,
        }
        
        # Add credentials if available
        if cls.AWS_ACCESS_KEY_ID and cls.AWS_SECRET_ACCESS_KEY:
            config['aws_access_key_id'] = cls.AWS_ACCESS_KEY_ID
            config['aws_secret_access_key'] = cls.AWS_SECRET_ACCESS_KEY
            
            if cls.AWS_SESSION_TOKEN:
                config['aws_session_token'] = cls.AWS_SESSION_TOKEN
        
        return config
    
    @classmethod
    def get_dynamodb_config(cls) -> Dict[str, Any]:
        """Get DynamoDB specific configuration"""
        config = cls.get_aws_config()
        
        if cls.DYNAMODB_ENDPOINT_URL:
            config['endpoint_url'] = cls.DYNAMODB_ENDPOINT_URL
            
        return config
    
    @classmethod
    def get_s3_config(cls) -> Dict[str, Any]:
        """Get S3 specific configuration"""
        config = cls.get_aws_config()
        
        if cls.S3_ENDPOINT_URL:
            config['endpoint_url'] = cls.S3_ENDPOINT_URL
            
        return config

# DynamoDB Table Schema
EMPLOYEE_TABLE_SCHEMA = {
    'TableName': AWSConfig.DYNAMODB_TABLE_NAME,
    'KeySchema': [
        {
            'AttributeName': 'employee_id',
            'KeyType': 'HASH'  # Partition key
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 'employee_id',
            'AttributeType': 'S'  # String
        }
    ],
    'BillingMode': 'PAY_PER_REQUEST'  # On-demand billing
}

# Global Secondary Index for email queries (optional)
EMAIL_GSI_SCHEMA = {
    'IndexName': 'email-index',
    'KeySchema': [
        {
            'AttributeName': 'email',
            'KeyType': 'HASH'
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }
    ],
    'Projection': {
        'ProjectionType': 'ALL'
    }
}