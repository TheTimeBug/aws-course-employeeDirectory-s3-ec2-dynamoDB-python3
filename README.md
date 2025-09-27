# Employee Directory Application

A modern web-based Employee Directory system built with Flask, AWS DynamoDB, and S3. This application provides complete CRUD (Create, Read, Update, Delete) operations for managing employee information with profile picture storage.

## Features

### Core Functionality
- **Add New Employee**: Create employee profiles with personal and work information
- **View Employee**: Display detailed employee information and profile pictures
- **Update Employee**: Edit existing employee data and profile pictures
- **Delete Employee**: Remove employees and their associated files
- **Employee Listing**: Browse all employees with search and filter capabilities

### Advanced Features
- **Profile Pictures**: Upload and manage employee profile pictures stored in AWS S3
- **Document Management**: Upload and manage employee documents (resumes, contracts, etc.)
- **Search & Filter**: Search employees by name, email, department, or position
- **Statistics Dashboard**: View employee counts, department breakdown, and storage usage
- **Responsive Design**: Mobile-friendly interface using Bootstrap 5
- **Data Validation**: Comprehensive input validation and error handling
- **AWS Integration**: Secure integration with DynamoDB and S3

## Technology Stack

### Backend
- **Flask**: Python web framework for the application server
- **AWS DynamoDB**: NoSQL database for employee data storage
- **AWS S3**: Object storage for profile pictures and documents
- **Boto3**: AWS SDK for Python integration

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Bootstrap 5**: Responsive CSS framework
- **JavaScript**: Client-side interactivity
- **Font Awesome**: Icon library

## Architecture

```
Employee Directory Application
├── Flask Web Server (app.py)
├── Service Layer (employee_service.py)
├── Database Layer (database.py) → AWS DynamoDB
├── Storage Layer (storage.py) → AWS S3
├── Data Models (models/employee.py)
├── Web Templates (templates/)
└── Configuration (config/aws_config.py)
```

## AWS Services Configuration

### DynamoDB Table
- **Table Name**: `employees`
- **Primary Key**: `employee_id` (String)
- **Billing Mode**: Pay-per-request
- **Attributes**: All employee fields stored as document

### S3 Bucket
- **Bucket Name**: `employee-directory-files`
- **Structure**:
  - `profile-pictures/`: Employee profile images
  - `documents/`: Employee documents and files

## Prerequisites

### System Requirements
- Python 3.8 or higher
- AWS Account with appropriate permissions
- Modern web browser

### AWS Permissions Required
The application requires the following AWS permissions:

#### DynamoDB Permissions
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
            "Resource": "arn:aws:dynamodb:*:*:table/employees"
        }
    ]
}
```

#### S3 Permissions
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:CreateBucket",
                "s3:ListBucket",
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:GetBucketLocation"
            ],
            "Resource": [
                "arn:aws:s3:::employee-directory-files",
                "arn:aws:s3:::employee-directory-files/*"
            ]
        }
    ]
}
```

## Installation & Setup

### 1. Clone or Download the Project
```bash
git clone <repository-url>
cd aws-course-employeeDirectory-s3-ec2-dynamoDB-python3
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure AWS Credentials

#### Option A: Environment Variables
Create a `.env` file in the project root:
```bash
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1
DYNAMODB_TABLE_NAME=employees
S3_BUCKET_NAME=employee-directory-files
```

#### Option B: AWS CLI Configuration
```bash
aws configure
```

#### Option C: IAM Roles (for EC2 deployment)
Configure IAM roles with the required permissions when deploying to EC2.

### 5. Setup AWS Resources
Run the setup script to create DynamoDB table and S3 bucket:
```bash
python setup_aws.py
```

### 6. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Configuration Options

### Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| `AWS_ACCESS_KEY_ID` | AWS Access Key ID | - |
| `AWS_SECRET_ACCESS_KEY` | AWS Secret Access Key | - |
| `AWS_SESSION_TOKEN` | AWS Session Token (for temporary credentials) | - |
| `AWS_REGION` | AWS Region | `us-east-1` |
| `DYNAMODB_TABLE_NAME` | DynamoDB table name | `employees` |
| `DYNAMODB_ENDPOINT_URL` | DynamoDB endpoint (for local testing) | - |
| `S3_BUCKET_NAME` | S3 bucket name | `employee-directory-files` |
| `S3_ENDPOINT_URL` | S3 endpoint (for local testing) | - |

### Application Settings
- **Maximum file size**: 5MB for profile pictures
- **Supported image formats**: PNG, JPG, JPEG, GIF
- **Profile picture prefix**: `profile-pictures/`
- **Document storage prefix**: `documents/`

## Usage Guide

### Adding a New Employee
1. Click "Add New Employee" button
2. Fill in required fields (marked with *)
3. Optionally upload a profile picture
4. Click "Add Employee" to save

### Viewing Employee Details
1. Click "View" button on any employee card
2. See complete employee information
3. View profile picture and documents
4. Access edit/delete options

### Updating Employee Information
1. Click "Edit" button on employee card or detail page
2. Modify any field as needed
3. Upload new profile picture if desired
4. Click "Save Changes"

### Deleting an Employee
1. Click "Delete" button on employee card or detail page
2. Confirm deletion in the dialog
3. Employee and all associated files will be removed

### Searching and Filtering
- Use the search box to find employees by name, email, department, or position
- Use department dropdown to filter by specific department
- Use position dropdown to filter by job title
- Combine filters for more specific results

## API Endpoints

### Web Routes
- `GET /` - Employee directory homepage
- `GET /add` - Add employee form
- `POST /add` - Create new employee
- `GET /employee/<id>` - View employee details
- `GET /edit/<id>` - Edit employee form
- `POST /edit/<id>` - Update employee
- `POST /delete/<id>` - Delete employee

### API Routes
- `GET /api/employees` - Get all employees as JSON

## File Structure

```
aws-course-employeeDirectory-s3-ec2-dynamoDB-python3/
├── app.py                          # Main Flask application
├── setup_aws.py                    # AWS resources setup script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .env.example                    # Environment variables template
├── app/
│   ├── __init__.py
│   ├── employee_service.py         # Service layer
│   ├── database.py                 # DynamoDB operations
│   ├── storage.py                  # S3 operations
│   ├── models/
│   │   ├── __init__.py
│   │   └── employee.py             # Employee data model
│   ├── templates/
│   │   ├── base.html               # Base template
│   │   ├── index.html              # Employee listing
│   │   ├── add_employee.html       # Add employee form
│   │   ├── view_employee.html      # Employee details
│   │   └── edit_employee.html      # Edit employee form
│   └── static/                     # Static files (CSS, JS, images)
└── config/
    ├── __init__.py
    └── aws_config.py               # AWS configuration
```

## Deployment

### Local Development
Follow the installation steps above for local development.

### EC2 Deployment
1. Launch an EC2 instance with appropriate IAM role
2. Install Python and dependencies
3. Clone the application code
4. Configure environment variables
5. Run setup script
6. Start the application with Gunicorn:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker Deployment
Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

## Security Considerations

### Data Protection
- Employee data is stored securely in DynamoDB
- Profile pictures are stored in S3 with controlled access
- Input validation prevents injection attacks
- File upload restrictions prevent malicious uploads

### AWS Security
- Use IAM roles instead of hardcoded credentials when possible
- Implement least-privilege access principles
- Enable S3 bucket versioning and backup
- Monitor AWS CloudTrail for audit logs

### Application Security
- Validate all user inputs
- Sanitize file uploads
- Use HTTPS in production
- Implement proper error handling

## Troubleshooting

### Common Issues

#### AWS Credentials Not Found
```
Error: AWS credentials not configured
Solution: Set environment variables or configure AWS CLI
```

#### DynamoDB Table Not Found
```
Error: ResourceNotFoundException
Solution: Run python setup_aws.py to create the table
```

#### S3 Bucket Access Denied
```
Error: Access Denied
Solution: Check S3 permissions and bucket policy
```

#### Image Upload Fails
```
Error: File too large or invalid format
Solution: Check file size (<5MB) and format (PNG, JPG, JPEG, GIF)
```

### Debug Mode
Enable debug mode for development:
```python
app.run(debug=True)
```

### Logs
Check application logs for detailed error information:
```bash
tail -f application.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For support and questions:
- Check the troubleshooting section
- Review AWS documentation for DynamoDB and S3
- Check Flask documentation for web framework issues

## Version History

- **v1.0.0** - Initial release with basic CRUD operations
- **v1.1.0** - Added profile picture support
- **v1.2.0** - Added document management
- **v1.3.0** - Enhanced search and filtering
- **v1.4.0** - Improved UI and responsive design

---

**Built with ❤️ using Flask, AWS DynamoDB, and S3**