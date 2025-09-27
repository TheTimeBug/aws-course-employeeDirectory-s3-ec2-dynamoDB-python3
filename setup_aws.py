"""
AWS Setup Script
Creates DynamoDB table and S3 bucket if they don't exist
"""

import boto3
from botocore.exceptions import ClientError
from config.aws_config import AWSConfig, EMPLOYEE_TABLE_SCHEMA
import sys

def create_dynamodb_table():
    """Create DynamoDB table for employees"""
    try:
        dynamodb = boto3.client('dynamodb', **AWSConfig.get_dynamodb_config())
        
        # Check if table already exists
        try:
            response = dynamodb.describe_table(TableName=AWSConfig.DYNAMODB_TABLE_NAME)
            print(f"DynamoDB table '{AWSConfig.DYNAMODB_TABLE_NAME}' already exists.")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceNotFoundException':
                raise e
        
        # Create table
        print(f"Creating DynamoDB table '{AWSConfig.DYNAMODB_TABLE_NAME}'...")
        response = dynamodb.create_table(**EMPLOYEE_TABLE_SCHEMA)
        
        # Wait for table to be created
        waiter = dynamodb.get_waiter('table_exists')
        waiter.wait(TableName=AWSConfig.DYNAMODB_TABLE_NAME)
        
        print(f"DynamoDB table '{AWSConfig.DYNAMODB_TABLE_NAME}' created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating DynamoDB table: {str(e)}")
        return False

def create_s3_bucket():
    """Create S3 bucket for storing employee files"""
    try:
        s3_client = boto3.client('s3', **AWSConfig.get_s3_config())
        
        # Check if bucket already exists
        try:
            s3_client.head_bucket(Bucket=AWSConfig.S3_BUCKET_NAME)
            print(f"S3 bucket '{AWSConfig.S3_BUCKET_NAME}' already exists.")
            return True
        except ClientError as e:
            if e.response['Error']['Code'] != '404':
                print(f"Error checking S3 bucket: {str(e)}")
                return False
        
        # Create bucket
        print(f"Creating S3 bucket '{AWSConfig.S3_BUCKET_NAME}'...")
        
        if AWSConfig.AWS_REGION == 'us-east-1':
            # us-east-1 doesn't need LocationConstraint
            s3_client.create_bucket(Bucket=AWSConfig.S3_BUCKET_NAME)
        else:
            s3_client.create_bucket(
                Bucket=AWSConfig.S3_BUCKET_NAME,
                CreateBucketConfiguration={'LocationConstraint': AWSConfig.AWS_REGION}
            )
        
        # Set bucket policy for public read access to profile pictures (optional)
        # Uncomment if you want profile pictures to be publicly accessible
        # bucket_policy = {
        #     "Version": "2012-10-17",
        #     "Statement": [
        #         {
        #             "Sid": "PublicReadGetObject",
        #             "Effect": "Allow",
        #             "Principal": "*",
        #             "Action": "s3:GetObject",
        #             "Resource": f"arn:aws:s3:::{AWSConfig.S3_BUCKET_NAME}/{AWSConfig.S3_PROFILE_PICTURES_PREFIX}*"
        #         }
        #     ]
        # }
        # 
        # s3_client.put_bucket_policy(
        #     Bucket=AWSConfig.S3_BUCKET_NAME,
        #     Policy=json.dumps(bucket_policy)
        # )
        
        print(f"S3 bucket '{AWSConfig.S3_BUCKET_NAME}' created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating S3 bucket: {str(e)}")
        return False

def setup_aws_resources():
    """Setup all required AWS resources"""
    print("Setting up AWS resources for Employee Directory application...")
    print("=" * 60)
    
    # Validate AWS configuration
    if not AWSConfig.AWS_ACCESS_KEY_ID or not AWSConfig.AWS_SECRET_ACCESS_KEY:
        print("WARNING: AWS credentials not found in environment variables.")
        print("Make sure to set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY")
        print("Or configure AWS CLI with 'aws configure'")
        print()
    
    success = True
    
    # Create DynamoDB table
    print("1. Setting up DynamoDB table...")
    if not create_dynamodb_table():
        success = False
    print()
    
    # Create S3 bucket
    print("2. Setting up S3 bucket...")
    if not create_s3_bucket():
        success = False
    print()
    
    if success:
        print("✅ AWS resources setup completed successfully!")
        print("\nNext steps:")
        print("1. Set environment variables for AWS credentials if not done already")
        print("2. Run: pip install -r requirements.txt")
        print("3. Run: python app.py")
    else:
        print("❌ Some AWS resources failed to setup. Please check the errors above.")
        sys.exit(1)

if __name__ == '__main__':
    setup_aws_resources()