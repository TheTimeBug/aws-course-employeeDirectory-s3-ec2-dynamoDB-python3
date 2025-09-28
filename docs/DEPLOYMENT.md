# Deployment Guide

## Employee Directory Deployment Documentation

### Overview
This guide covers deploying the Employee Directory application to various environments including local development, AWS EC2, Docker containers, and serverless architectures.

---

## Prerequisites

### System Requirements
- **Python:** 3.8 or higher
- **Operating System:** Windows, macOS, or Linux
- **Memory:** Minimum 512MB RAM (2GB recommended)
- **Storage:** Minimum 1GB free space
- **Network:** Internet access for AWS services

### AWS Requirements
- **AWS Account** with appropriate permissions
- **AWS CLI** installed and configured
- **IAM User/Role** with necessary permissions:
  - DynamoDB: CreateTable, DescribeTable, PutItem, GetItem, UpdateItem, DeleteItem, Scan, Query
  - S3: CreateBucket, ListBucket, GetObject, PutObject, DeleteObject
  - CloudWatch: PutMetricData (optional, for monitoring)

### Development Tools
- **Git** (for version control)
- **Text Editor/IDE** (VS Code recommended)
- **Web Browser** (for testing)

---

## Local Development Deployment

### 1. Environment Setup

#### Clone Repository
```bash
git clone <repository-url>
cd aws-course-employeeDirectory-s3-ec2-dynamoDB-python3
```

#### Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configuration

#### Environment Variables
Create `.env` file from template:
```bash
cp .env.example .env
```

Edit `.env` file:
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Application Settings
FLASK_ENV=development
FLASK_SECRET_KEY=your-secret-key-for-development

# AWS Resources
DYNAMODB_TABLE_NAME=employees
S3_BUCKET_NAME=employee-directory-files-dev
```

#### AWS Configuration (Alternative)
```bash
# Configure AWS CLI
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format
```

### 3. AWS Resources Setup
```bash
python setup_aws.py
```

This script will:
- Create DynamoDB table with proper schema
- Create S3 bucket with correct permissions
- Verify connectivity and configurations

### 4. Run Application
```bash
# Development server
python app.py

# Production-like server (using Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### Access Application
- **URL:** http://localhost:5000
- **Admin Interface:** Available through web UI
- **API Endpoints:** http://localhost:5000/api/employees

### 5. Development Utilities
```bash
# Create sample data
python dev_utils.py

# Health check
python -c "from app.employee_service import EmployeeService; print(EmployeeService().health_check())"
```

---

## AWS EC2 Deployment

### 1. EC2 Instance Setup

#### Launch EC2 Instance
1. **AMI:** Amazon Linux 2 or Ubuntu 20.04 LTS
2. **Instance Type:** t3.micro (free tier) or t3.small (recommended)
3. **Security Group:** 
   - HTTP (80)
   - HTTPS (443)
   - SSH (22) - restrict to your IP
   - Custom TCP (5000) - for development

#### Connect to Instance
```bash
ssh -i your-key.pem ec2-user@your-instance-ip
```

### 2. Server Configuration

#### Install System Dependencies
```bash
# Amazon Linux 2
sudo yum update -y
sudo yum install python3 python3-pip git nginx -y

# Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-venv git nginx -y
```

#### Setup Application
```bash
# Clone repository
git clone <repository-url>
cd aws-course-employeeDirectory-s3-ec2-dynamoDB-python3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### 3. Environment Configuration

#### IAM Role (Recommended)
Create IAM role with necessary permissions and attach to EC2 instance:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "dynamodb:CreateTable",
                "dynamodb:DescribeTable",
                "dynamodb:PutItem",
                "dynamodb:GetItem",
                "dynamodb:UpdateItem",
                "dynamodb:DeleteItem",
                "dynamodb:Scan",
                "dynamodb:Query"
            ],
            "Resource": "arn:aws:dynamodb:*:*:table/employees*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject"
            ],
            "Resource": [
                "arn:aws:s3:::employee-directory-files*",
                "arn:aws:s3:::employee-directory-files*/*"
            ]
        }
    ]
}
```

#### Environment Variables (Alternative)
```bash
# Create environment file
sudo vim /etc/environment

# Add variables
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
FLASK_ENV=production
```

### 4. Application Service

#### Create Systemd Service
```bash
sudo vim /etc/systemd/system/employee-directory.service
```

```ini
[Unit]
Description=Employee Directory Flask Application
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/aws-course-employeeDirectory-s3-ec2-dynamoDB-python3
Environment=PATH=/home/ec2-user/aws-course-employeeDirectory-s3-ec2-dynamoDB-python3/venv/bin
ExecStart=/home/ec2-user/aws-course-employeeDirectory-s3-ec2-dynamoDB-python3/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### Start Service
```bash
sudo systemctl daemon-reload
sudo systemctl enable employee-directory
sudo systemctl start employee-directory
sudo systemctl status employee-directory
```

### 5. Nginx Configuration

#### Create Nginx Configuration
```bash
sudo vim /etc/nginx/sites-available/employee-directory
```

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ec2-user/aws-course-employeeDirectory-s3-ec2-dynamoDB-python3/app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    client_max_body_size 10M;
}
```

#### Enable Site
```bash
# Ubuntu
sudo ln -s /etc/nginx/sites-available/employee-directory /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Amazon Linux
sudo vim /etc/nginx/nginx.conf  # Add server block
sudo nginx -t
sudo systemctl restart nginx
```

### 6. SSL Certificate (Optional)

#### Using Let's Encrypt
```bash
# Install Certbot
sudo yum install certbot python3-certbot-nginx -y  # Amazon Linux
sudo apt install certbot python3-certbot-nginx -y  # Ubuntu

# Obtain certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 7. Setup AWS Resources
```bash
# Run setup script
cd /home/ec2-user/aws-course-employeeDirectory-s3-ec2-dynamoDB-python3
source venv/bin/activate
python setup_aws.py
```

---

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/employees || exit 1

# Run application
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### 2. Create Docker Compose
```yaml
version: '3.8'

services:
  employee-directory:
    build: .
    ports:
      - "5000:5000"
    environment:
      - AWS_ACCESS_KEY_ID=${AWS_ACCESS_KEY_ID}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET_ACCESS_KEY}
      - AWS_REGION=${AWS_REGION}
      - DYNAMODB_TABLE_NAME=employees
      - S3_BUCKET_NAME=employee-directory-files
      - FLASK_ENV=production
    volumes:
      - ./uploads:/app/uploads
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/employees"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - employee-directory
    restart: unless-stopped
```

### 3. Build and Run
```bash
# Build image
docker build -t employee-directory .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f employee-directory

# Scale application
docker-compose up -d --scale employee-directory=3
```

### 4. Production Docker Setup
```bash
# Build production image
docker build -t employee-directory:production -f Dockerfile.prod .

# Run with production settings
docker run -d \
  --name employee-directory-prod \
  -p 80:5000 \
  -e AWS_ACCESS_KEY_ID=your_key \
  -e AWS_SECRET_ACCESS_KEY=your_secret \
  -e AWS_REGION=us-east-1 \
  -e FLASK_ENV=production \
  --restart unless-stopped \
  employee-directory:production
```

---

## AWS ECS Deployment

### 1. Create Task Definition
```json
{
  "family": "employee-directory",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::account:role/ecsTaskRole",
  "containerDefinitions": [
    {
      "name": "employee-directory",
      "image": "your-account.dkr.ecr.region.amazonaws.com/employee-directory:latest",
      "portMappings": [
        {
          "containerPort": 5000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "AWS_REGION",
          "value": "us-east-1"
        },
        {
          "name": "DYNAMODB_TABLE_NAME",
          "value": "employees"
        },
        {
          "name": "S3_BUCKET_NAME",
          "value": "employee-directory-files"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/employee-directory",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### 2. Create ECS Service
```bash
# Create cluster
aws ecs create-cluster --cluster-name employee-directory-cluster

# Register task definition
aws ecs register-task-definition --cli-input-json file://task-definition.json

# Create service
aws ecs create-service \
  --cluster employee-directory-cluster \
  --service-name employee-directory-service \
  --task-definition employee-directory:1 \
  --desired-count 2 \
  --launch-type FARGATE \
  --network-configuration "awsvpcConfiguration={subnets=[subnet-12345,subnet-67890],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
```

---

## AWS Lambda Deployment (Serverless)

### 1. Install Serverless Framework
```bash
npm install -g serverless
pip install serverless-wsgi
```

### 2. Create serverless.yml
```yaml
service: employee-directory

provider:
  name: aws
  runtime: python3.9
  region: us-east-1
  iamRoleStatements:
    - Effect: Allow
      Action:
        - dynamodb:*
      Resource: "arn:aws:dynamodb:*:*:table/employees*"
    - Effect: Allow
      Action:
        - s3:*
      Resource: 
        - "arn:aws:s3:::employee-directory-files*"
        - "arn:aws:s3:::employee-directory-files*/*"

functions:
  app:
    handler: wsgi_handler.handler
    events:
      - http:
          path: /
          method: ANY
      - http:
          path: /{proxy+}
          method: ANY
    environment:
      DYNAMODB_TABLE_NAME: employees
      S3_BUCKET_NAME: employee-directory-files

plugins:
  - serverless-wsgi
  - serverless-python-requirements

custom:
  wsgi:
    app: app.app
    packRequirements: false
  pythonRequirements:
    dockerizePip: non-linux
```

### 3. Create WSGI Handler
```python
# wsgi_handler.py
import serverless_wsgi
from app import app

def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
```

### 4. Deploy
```bash
# Deploy to AWS
serverless deploy

# Deploy specific function
serverless deploy function -f app

# View logs
serverless logs -f app -t
```

---

## Environment-Specific Configurations

### Development Environment
```python
# config/development.py
DEBUG = True
TESTING = False
WTF_CSRF_ENABLED = False
UPLOAD_FOLDER = 'uploads'
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
```

### Production Environment
```python
# config/production.py
DEBUG = False
TESTING = False
WTF_CSRF_ENABLED = True
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
PERMANENT_SESSION_LIFETIME = 1800  # 30 minutes
```

### Testing Environment
```python
# config/testing.py
DEBUG = True
TESTING = True
WTF_CSRF_ENABLED = False
DYNAMODB_ENDPOINT_URL = 'http://localhost:8000'
S3_ENDPOINT_URL = 'http://localhost:9000'
```

---

## Monitoring and Logging

### Application Logging
```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logging(app):
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        file_handler = RotatingFileHandler(
            'logs/employee_directory.log',
            maxBytes=10240000,
            backupCount=10
        )
        
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Employee Directory startup')
```

### AWS CloudWatch Integration
```python
# Install: pip install watchtower
import watchtower
import logging

# CloudWatch handler
cloudwatch_handler = watchtower.CloudWatchLogsHandler(
    log_group='employee-directory',
    stream_name='application-logs'
)

app.logger.addHandler(cloudwatch_handler)
```

---

## Health Checks and Monitoring

### Application Health Check
```python
@app.route('/health')
def health_check():
    try:
        service = EmployeeService()
        health = service.health_check()
        
        if health['overall']:
            return jsonify({'status': 'healthy', 'details': health}), 200
        else:
            return jsonify({'status': 'unhealthy', 'details': health}), 503
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
```

### System Monitoring
```bash
# Install monitoring tools
pip install psutil

# Create monitoring script
python monitoring.py
```

---

## Backup and Recovery

### Data Backup
```python
# backup_script.py
import boto3
import json
from datetime import datetime

def backup_dynamodb():
    """Backup DynamoDB data"""
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('employees')
    
    response = table.scan()
    items = response['Items']
    
    # Handle pagination
    while 'LastEvaluatedKey' in response:
        response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
        items.extend(response['Items'])
    
    # Save backup
    backup_file = f"backup_employees_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_file, 'w') as f:
        json.dump(items, f, default=str, indent=2)
    
    return backup_file

def backup_s3_files():
    """Backup S3 files"""
    # Implementation for S3 backup
    pass
```

### Automated Backups
```bash
# Cron job for daily backups
0 2 * * * /path/to/venv/bin/python /path/to/backup_script.py
```

---

## Troubleshooting

### Common Issues

#### 1. AWS Credentials Error
```
Error: Unable to locate credentials
Solution: 
- Check AWS credentials configuration
- Verify IAM permissions
- Ensure environment variables are set
```

#### 2. DynamoDB Table Not Found
```
Error: ResourceNotFoundException
Solution:
- Run python setup_aws.py
- Verify table name in configuration
- Check AWS region settings
```

#### 3. S3 Access Denied
```
Error: Access Denied
Solution:
- Check S3 bucket permissions
- Verify IAM policies
- Ensure bucket exists in correct region
```

#### 4. File Upload Issues
```
Error: File upload failed
Solutions:
- Check file size limits
- Verify file type restrictions
- Check S3 bucket permissions
- Monitor disk space
```

### Log Analysis
```bash
# View recent logs
tail -f logs/employee_directory.log

# Search for errors
grep -i error logs/employee_directory.log

# Monitor system resources
top
df -h
free -m
```

---

## Performance Optimization

### Database Optimization
- Implement pagination for large datasets
- Use DynamoDB Global Secondary Indexes for common queries
- Enable DynamoDB auto-scaling

### File Storage Optimization
- Implement image compression
- Use CloudFront CDN for static assets
- Enable S3 transfer acceleration

### Application Optimization
- Implement caching (Redis/ElastiCache)
- Use connection pooling
- Optimize static asset delivery
- Implement lazy loading for images

---

This deployment guide provides comprehensive instructions for deploying the Employee Directory application across various environments and platforms.