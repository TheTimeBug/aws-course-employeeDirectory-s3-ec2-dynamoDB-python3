# API Documentation

## Employee Directory API Reference

### Base URL
```
http://localhost:5000  (Development)
https://your-domain.com  (Production)
```

### Authentication
Currently, the API does not implement authentication. In production, consider implementing:
- JWT tokens
- API keys
- OAuth 2.0
- AWS Cognito integration

---

## Web Interface Endpoints

### Employee Management Routes

#### 1. Employee Directory Homepage
```http
GET /
```

**Description:** Display all employees with search and filter capabilities

**Parameters:**
- None (search/filter handled client-side)

**Response:** HTML page with employee listing

**Features:**
- Employee cards with profile pictures
- Search functionality
- Department/position filters
- Statistics dashboard
- Responsive design

---

#### 2. Add New Employee
```http
GET /add
POST /add
```

**GET /add**
- **Description:** Display add employee form
- **Response:** HTML form page

**POST /add**
- **Description:** Create new employee
- **Content-Type:** `multipart/form-data`
- **Form Fields:**
  ```
  first_name: string (required, max 50 chars)
  last_name: string (required, max 50 chars)
  email: string (required, max 100 chars, unique)
  position: string (required, max 100 chars)
  department: string (required, max 50 chars)
  phone: string (optional, max 20 chars)
  hire_date: date (optional, YYYY-MM-DD format)
  profile_picture: file (optional, max 5MB, PNG/JPG/JPEG/GIF)
  ```

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** `/` (employee directory)
- **Flash Message:** "Employee added successfully!"

**Error Response:**
- **Code:** 200 (form redisplay with errors)
- **Flash Message:** Error details

---

#### 3. View Employee Details
```http
GET /employee/<employee_id>
```

**Description:** Display detailed employee information

**Parameters:**
- `employee_id` (string): UUID of the employee

**Success Response:**
- **Code:** 200
- **Content:** HTML page with employee details

**Error Response:**
- **Code:** 302 (Redirect to /)
- **Flash Message:** "Employee not found."

---

#### 4. Edit Employee
```http
GET /edit/<employee_id>
POST /edit/<employee_id>
```

**GET /edit/<employee_id>**
- **Description:** Display edit employee form
- **Response:** HTML form pre-populated with employee data

**POST /edit/<employee_id>**
- **Description:** Update existing employee
- **Content-Type:** `multipart/form-data`
- **Form Fields:** Same as POST /add

**Success Response:**
- **Code:** 302 (Redirect)
- **Location:** `/employee/<employee_id>`
- **Flash Message:** "Employee updated successfully!"

**Error Response:**
- **Code:** 200 (form redisplay with errors)
- **Flash Message:** Error details

---

#### 5. Delete Employee
```http
POST /delete/<employee_id>
```

**Description:** Delete employee and all associated files

**Parameters:**
- `employee_id` (string): UUID of the employee

**Success Response:**
- **Code:** 302 (Redirect to /)
- **Flash Message:** "Employee deleted successfully!"

**Error Response:**
- **Code:** 302 (Redirect to /)
- **Flash Message:** "Failed to delete employee."

---

## JSON API Endpoints

### 1. Get All Employees (JSON)
```http
GET /api/employees
```

**Description:** Retrieve all employees as JSON data

**Response Format:**
```json
[
  {
    "employee_id": "123e4567-e89b-12d3-a456-426614174000",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@company.com",
    "position": "Software Engineer",
    "department": "Engineering",
    "phone": "(555) 123-4567",
    "hire_date": "2023-01-15",
    "profile_picture_url": "https://bucket.s3.region.amazonaws.com/profile-pictures/...",
    "created_at": "2023-01-15T10:30:00.000Z",
    "updated_at": "2023-01-15T10:30:00.000Z"
  }
]
```

**Success Response:**
- **Code:** 200
- **Content-Type:** `application/json`

**Error Response:**
- **Code:** 500
- **Content:**
  ```json
  {
    "error": "Error message description"
  }
  ```

---

## Data Models

### Employee Model
```json
{
  "employee_id": "string (UUID)",
  "first_name": "string (1-50 chars, required)",
  "last_name": "string (1-50 chars, required)",
  "email": "string (valid email, 1-100 chars, required, unique)",
  "position": "string (1-100 chars, required)",
  "department": "string (1-50 chars, required)",
  "phone": "string (0-20 chars, optional)",
  "hire_date": "string (YYYY-MM-DD format, optional)",
  "profile_picture_url": "string (S3 URL, optional)",
  "created_at": "string (ISO 8601 timestamp)",
  "updated_at": "string (ISO 8601 timestamp)"
}
```

### Validation Rules
- **employee_id:** Auto-generated UUID, immutable
- **first_name:** Required, 1-50 characters, letters and spaces only
- **last_name:** Required, 1-50 characters, letters and spaces only
- **email:** Required, valid email format, unique across all employees
- **position:** Required, 1-100 characters
- **department:** Required, 1-50 characters
- **phone:** Optional, 0-20 characters, digits and common phone formatting
- **hire_date:** Optional, valid date in YYYY-MM-DD format
- **profile_picture_url:** Auto-generated from S3 upload
- **created_at:** Auto-generated timestamp, immutable
- **updated_at:** Auto-updated on every modification

---

## File Upload Specifications

### Profile Picture Upload
- **Field Name:** `profile_picture`
- **Allowed Types:** PNG, JPG, JPEG, GIF
- **Maximum Size:** 5MB
- **Storage Location:** AWS S3 bucket
- **Naming Convention:** `{employee_id}_{uuid}.{extension}`
- **Access:** Pre-signed URLs (1-hour expiration)

### File Processing
1. Validate file type and size
2. Generate unique filename
3. Upload to S3 with metadata
4. Generate pre-signed URL
5. Store URL in employee record
6. Clean up any previous profile picture

---

## Error Handling

### HTTP Status Codes
- **200 OK:** Successful GET requests, form validation errors
- **302 Found:** Successful redirects after POST operations
- **404 Not Found:** Employee not found
- **500 Internal Server Error:** Server-side errors

### Error Response Format

#### HTML Responses (Web Interface)
Errors are displayed using Flask's flash messaging system:
```html
<div class="alert alert-danger">
  Error message displayed to user
</div>
```

#### JSON Responses (API)
```json
{
  "error": "Detailed error message",
  "code": "ERROR_CODE",
  "timestamp": "2023-01-15T10:30:00.000Z"
}
```

### Common Error Messages
- **Validation Errors:**
  - "First name is required"
  - "Invalid email format"
  - "Employee with this email already exists"
  - "Profile picture must be smaller than 5MB"

- **System Errors:**
  - "Failed to connect to database"
  - "File upload failed"
  - "Employee not found"
  - "Internal server error"

---

## Request/Response Examples

### 1. Add Employee (Success)
**Request:**
```http
POST /add
Content-Type: multipart/form-data

first_name=John
last_name=Doe
email=john.doe@company.com
position=Software Engineer
department=Engineering
phone=(555) 123-4567
hire_date=2023-01-15
profile_picture=[binary file data]
```

**Response:**
```http
HTTP/1.1 302 Found
Location: /
Set-Cookie: session=...

[Redirect to employee directory with success message]
```

### 2. Get Employee (JSON API)
**Request:**
```http
GET /api/employees
Accept: application/json
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

[
  {
    "employee_id": "123e4567-e89b-12d3-a456-426614174000",
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@company.com",
    "position": "Software Engineer",
    "department": "Engineering",
    "phone": "(555) 123-4567",
    "hire_date": "2023-01-15",
    "profile_picture_url": "https://employee-bucket.s3.us-east-1.amazonaws.com/profile-pictures/john_doe_abc123.jpg",
    "created_at": "2023-01-15T10:30:00.000Z",
    "updated_at": "2023-01-15T10:30:00.000Z"
  }
]
```

### 3. Validation Error
**Request:**
```http
POST /add
Content-Type: multipart/form-data

first_name=
email=invalid-email
position=Software Engineer
department=Engineering
```

**Response:**
```http
HTTP/1.1 200 OK
Content-Type: text/html

[HTML form page with error messages:
- "First name is required"
- "Invalid email format"]
```

---

## Rate Limiting & Performance

### Current Implementation
- No rate limiting implemented
- Suitable for internal/small-scale usage

### Production Recommendations
- Implement rate limiting (e.g., 100 requests per minute per IP)
- Add caching for employee listings
- Optimize database queries with pagination
- Use CDN for static assets

### Performance Considerations
- **Database:** DynamoDB provides consistent performance
- **File Storage:** S3 provides scalable file storage
- **Search/Filter:** Currently client-side, consider server-side for large datasets
- **Profile Pictures:** Pre-signed URLs expire after 1 hour

---

## Security Considerations

### Current Security Measures
- Input validation and sanitization
- File type and size restrictions
- SQL injection prevention (NoSQL database)
- XSS protection via template escaping

### Production Security Recommendations
- Implement authentication and authorization
- Add CSRF protection
- Use HTTPS for all communications
- Implement API rate limiting
- Add request logging and monitoring
- Sanitize file uploads more thoroughly
- Implement proper session management

### AWS Security
- Use IAM roles instead of access keys when possible
- Enable S3 bucket versioning and MFA delete
- Configure VPC and security groups properly
- Enable CloudTrail for audit logging
- Use AWS Secrets Manager for sensitive configuration

---

## SDK Examples

### Python (using requests)
```python
import requests

# Get all employees
response = requests.get('http://localhost:5000/api/employees')
employees = response.json()

# Add new employee
employee_data = {
    'first_name': 'Jane',
    'last_name': 'Smith',
    'email': 'jane.smith@company.com',
    'position': 'Product Manager',
    'department': 'Product'
}

with open('profile.jpg', 'rb') as f:
    files = {'profile_picture': f}
    response = requests.post(
        'http://localhost:5000/add', 
        data=employee_data, 
        files=files
    )
```

### JavaScript (using fetch)
```javascript
// Get all employees
fetch('/api/employees')
  .then(response => response.json())
  .then(employees => console.log(employees));

// Add new employee
const formData = new FormData();
formData.append('first_name', 'Jane');
formData.append('last_name', 'Smith');
formData.append('email', 'jane.smith@company.com');
formData.append('position', 'Product Manager');
formData.append('department', 'Product');

fetch('/add', {
  method: 'POST',
  body: formData
})
.then(response => {
  if (response.redirected) {
    window.location.href = response.url;
  }
});
```

---

This API documentation provides comprehensive information for integrating with and extending the Employee Directory application.