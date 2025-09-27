"""
S3 Storage Layer
Handles all S3 operations for employee files (profile pictures, documents)
"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional, List, Dict, Any
from config.aws_config import AWSConfig
import logging
import mimetypes
import os
from urllib.parse import quote
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EmployeeStorage:
    """S3 storage operations for employee files"""
    
    def __init__(self):
        """Initialize S3 connection"""
        try:
            self.s3_client = boto3.client('s3', **AWSConfig.get_s3_config())
            self.bucket_name = AWSConfig.S3_BUCKET_NAME
        except Exception as e:
            logger.error(f"Failed to initialize S3: {str(e)}")
            raise
    
    def upload_profile_picture(self, file_obj, employee_id: str, filename: str) -> Optional[str]:
        """
        Upload employee profile picture to S3
        
        Args:
            file_obj: File object to upload
            employee_id: Employee ID for organizing files
            filename: Original filename
            
        Returns:
            str: S3 object URL if successful, None otherwise
        """
        try:
            # Generate unique filename to avoid conflicts
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"{employee_id}_{uuid.uuid4().hex}{file_extension}"
            s3_key = f"{AWSConfig.S3_PROFILE_PICTURES_PREFIX}{unique_filename}"
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Upload file to S3
            extra_args = {
                'ContentType': content_type,
                'Metadata': {
                    'employee_id': employee_id,
                    'original_filename': filename
                }
            }
            
            # For public access (uncomment if needed)
            # extra_args['ACL'] = 'public-read'
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Generate object URL
            object_url = f"https://{self.bucket_name}.s3.{AWSConfig.AWS_REGION}.amazonaws.com/{s3_key}"
            
            logger.info(f"Profile picture uploaded successfully: {s3_key}")
            return object_url
            
        except ClientError as e:
            logger.error(f"S3 ClientError uploading profile picture: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading profile picture: {str(e)}")
            return None
    
    def delete_profile_picture(self, employee_id: str) -> bool:
        """
        Delete employee profile picture from S3
        
        Args:
            employee_id: Employee ID to find and delete picture for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # List objects with employee_id prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{AWSConfig.S3_PROFILE_PICTURES_PREFIX}{employee_id}_"
            )
            
            if 'Contents' not in response:
                logger.info(f"No profile picture found for employee {employee_id}")
                return True
            
            # Delete all objects (should be only one, but just in case)
            objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
            
            if objects_to_delete:
                delete_response = self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                
                logger.info(f"Deleted {len(objects_to_delete)} profile picture(s) for employee {employee_id}")
            
            return True
            
        except ClientError as e:
            logger.error(f"S3 ClientError deleting profile picture: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting profile picture: {str(e)}")
            return False
    
    def get_profile_picture_url(self, employee_id: str) -> Optional[str]:
        """
        Get profile picture URL for employee
        
        Args:
            employee_id: Employee ID to get picture URL for
            
        Returns:
            str: Pre-signed URL if found, None otherwise
        """
        try:
            # List objects with employee_id prefix
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{AWSConfig.S3_PROFILE_PICTURES_PREFIX}{employee_id}_"
            )
            
            if 'Contents' not in response or not response['Contents']:
                logger.info(f"No profile picture found for employee {employee_id}")
                return None
            
            # Get the first (should be only) object
            s3_key = response['Contents'][0]['Key']
            
            # Generate pre-signed URL (valid for 1 hour)
            presigned_url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': s3_key},
                ExpiresIn=3600  # 1 hour
            )
            
            return presigned_url
            
        except ClientError as e:
            logger.error(f"S3 ClientError getting profile picture URL: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting profile picture URL: {str(e)}")
            return None
    
    def upload_document(self, file_obj, employee_id: str, filename: str, document_type: str = 'general') -> Optional[str]:
        """
        Upload employee document to S3
        
        Args:
            file_obj: File object to upload
            employee_id: Employee ID for organizing files
            filename: Original filename
            document_type: Type of document (resume, contract, etc.)
            
        Returns:
            str: S3 object URL if successful, None otherwise
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(filename)[1].lower()
            unique_filename = f"{employee_id}_{document_type}_{uuid.uuid4().hex}{file_extension}"
            s3_key = f"documents/{unique_filename}"
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(filename)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Upload file to S3
            extra_args = {
                'ContentType': content_type,
                'Metadata': {
                    'employee_id': employee_id,
                    'document_type': document_type,
                    'original_filename': filename
                }
            }
            
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs=extra_args
            )
            
            # Generate object URL
            object_url = f"https://{self.bucket_name}.s3.{AWSConfig.AWS_REGION}.amazonaws.com/{s3_key}"
            
            logger.info(f"Document uploaded successfully: {s3_key}")
            return object_url
            
        except ClientError as e:
            logger.error(f"S3 ClientError uploading document: {e.response['Error']['Message']}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading document: {str(e)}")
            return None
    
    def list_employee_documents(self, employee_id: str) -> List[Dict[str, Any]]:
        """
        List all documents for an employee
        
        Args:
            employee_id: Employee ID to list documents for
            
        Returns:
            List of document information dictionaries
        """
        try:
            documents = []
            
            # List objects with employee_id prefix in documents folder
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"documents/{employee_id}_"
            )
            
            if 'Contents' in response:
                for obj in response['Contents']:
                    # Get object metadata
                    try:
                        head_response = self.s3_client.head_object(
                            Bucket=self.bucket_name,
                            Key=obj['Key']
                        )
                        
                        # Generate pre-signed URL
                        presigned_url = self.s3_client.generate_presigned_url(
                            'get_object',
                            Params={'Bucket': self.bucket_name, 'Key': obj['Key']},
                            ExpiresIn=3600  # 1 hour
                        )
                        
                        document_info = {
                            'key': obj['Key'],
                            'filename': head_response.get('Metadata', {}).get('original_filename', 'Unknown'),
                            'document_type': head_response.get('Metadata', {}).get('document_type', 'general'),
                            'size': obj['Size'],
                            'last_modified': obj['LastModified'].isoformat(),
                            'url': presigned_url
                        }
                        
                        documents.append(document_info)
                        
                    except ClientError as e:
                        logger.warning(f"Error getting metadata for {obj['Key']}: {e.response['Error']['Message']}")
                        continue
            
            logger.info(f"Found {len(documents)} documents for employee {employee_id}")
            return documents
            
        except ClientError as e:
            logger.error(f"S3 ClientError listing documents: {e.response['Error']['Message']}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error listing documents: {str(e)}")
            return []
    
    def delete_document(self, s3_key: str) -> bool:
        """
        Delete a document from S3
        
        Args:
            s3_key: S3 object key to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=s3_key)
            logger.info(f"Document deleted successfully: {s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"S3 ClientError deleting document: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting document: {str(e)}")
            return False
    
    def delete_all_employee_files(self, employee_id: str) -> bool:
        """
        Delete all files for an employee (profile pictures and documents)
        
        Args:
            employee_id: Employee ID to delete all files for
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            objects_to_delete = []
            
            # Find profile pictures
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"{AWSConfig.S3_PROFILE_PICTURES_PREFIX}{employee_id}_"
            )
            
            if 'Contents' in response:
                objects_to_delete.extend([{'Key': obj['Key']} for obj in response['Contents']])
            
            # Find documents
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=f"documents/{employee_id}_"
            )
            
            if 'Contents' in response:
                objects_to_delete.extend([{'Key': obj['Key']} for obj in response['Contents']])
            
            # Delete all objects
            if objects_to_delete:
                delete_response = self.s3_client.delete_objects(
                    Bucket=self.bucket_name,
                    Delete={'Objects': objects_to_delete}
                )
                
                logger.info(f"Deleted {len(objects_to_delete)} file(s) for employee {employee_id}")
            else:
                logger.info(f"No files found for employee {employee_id}")
            
            return True
            
        except ClientError as e:
            logger.error(f"S3 ClientError deleting employee files: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting employee files: {str(e)}")
            return False
    
    def health_check(self) -> bool:
        """
        Check if S3 connection is healthy
        
        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            # Try to list objects in bucket (limit to 1)
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                MaxKeys=1
            )
            return True
        except Exception as e:
            logger.error(f"S3 health check failed: {str(e)}")
            return False
    
    def get_bucket_info(self) -> Dict[str, Any]:
        """
        Get bucket information and statistics
        
        Returns:
            Dictionary with bucket information
        """
        try:
            # Get bucket location
            location_response = self.s3_client.get_bucket_location(Bucket=self.bucket_name)
            location = location_response.get('LocationConstraint', 'us-east-1')
            
            # Count objects and calculate total size
            total_objects = 0
            total_size = 0
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket_name):
                if 'Contents' in page:
                    total_objects += len(page['Contents'])
                    total_size += sum(obj['Size'] for obj in page['Contents'])
            
            return {
                'bucket_name': self.bucket_name,
                'region': location,
                'total_objects': total_objects,
                'total_size_bytes': total_size,
                'total_size_mb': round(total_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error getting bucket info: {str(e)}")
            return {
                'bucket_name': self.bucket_name,
                'error': str(e)
            }