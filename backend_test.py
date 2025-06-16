#!/usr/bin/env python3
import requests
import json
import base64
import os
import time
import random
import string
from datetime import datetime

# Get the backend URL from the frontend .env file
BACKEND_URL = "https://aa978b51-74a8-4971-ad43-e082746155c1.preview.emergentagent.com/api"

# Admin credentials
ADMIN_EMAIL = "admin@twoem.com"
ADMIN_PASSWORD = "TwoemAdmin2025!"

# Test user credentials
TEST_USER_EMAIL = f"test.user.{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestUser2025!"
TEST_USER_FULLNAME = "Test User"

# Store tokens and IDs for use across tests
admin_token = None
user_token = None
test_file_id = None
test_eulogy_id = None

def print_separator(title):
    """Print a separator with a title for better test output readability."""
    print("\n" + "=" * 80)
    print(f" {title} ".center(80, "="))
    print("=" * 80 + "\n")

def random_string(length=10):
    """Generate a random string for test data."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def test_health_check():
    """Test the health check endpoint."""
    print_separator("Testing Health Check Endpoint")
    
    response = requests.get(f"{BACKEND_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    print("✅ Health check endpoint is working")
    return True

def test_user_registration():
    """Test user registration endpoint."""
    print_separator("Testing User Registration")
    
    # Create a test user
    user_data = {
        "email": TEST_USER_EMAIL,
        "full_name": TEST_USER_FULLNAME,
        "password": TEST_USER_PASSWORD,
        "is_admin": False
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/register", json=user_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["email"] == TEST_USER_EMAIL
    assert response.json()["full_name"] == TEST_USER_FULLNAME
    print("✅ User registration endpoint is working")
    return True

def test_user_login():
    """Test user login endpoint."""
    print_separator("Testing User Login")
    
    # Login with test user
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user"]["email"] == TEST_USER_EMAIL
    
    # Store the token for later use
    global user_token
    user_token = response.json()["access_token"]
    print("✅ User login endpoint is working")
    return True

def test_admin_login():
    """Test admin login endpoint."""
    print_separator("Testing Admin Login")
    
    # Login with admin credentials
    login_data = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["user"]["email"] == ADMIN_EMAIL
    assert response.json()["user"]["is_admin"] == True
    
    # Store the admin token for later use
    global admin_token
    admin_token = response.json()["access_token"]
    print("✅ Admin login endpoint is working")
    return True

def test_get_current_user():
    """Test get current user endpoint."""
    print_separator("Testing Get Current User")
    
    # Get current user info with user token
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/auth/me", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["email"] == TEST_USER_EMAIL
    assert response.json()["full_name"] == TEST_USER_FULLNAME
    print("✅ Get current user endpoint is working")
    return True

def test_services_listing():
    """Test services listing endpoint."""
    print_separator("Testing Services Listing")
    
    response = requests.get(f"{BACKEND_URL}/services")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    print("✅ Services listing endpoint is working")
    return True

def test_contact_submission():
    """Test contact form submission endpoint."""
    print_separator("Testing Contact Form Submission")
    
    # Submit a contact form
    contact_data = {
        "name": "Test Contact",
        "email": f"contact.{int(time.time())}@example.com",
        "message": "This is a test contact message from the automated test script."
    }
    
    response = requests.post(f"{BACKEND_URL}/contact", json=contact_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["name"] == contact_data["name"]
    assert response.json()["email"] == contact_data["email"]
    assert response.json()["message"] == contact_data["message"]
    print("✅ Contact form submission endpoint is working")
    return True

def test_admin_contact_listing():
    """Test admin contact listing endpoint."""
    print_separator("Testing Admin Contact Listing")
    
    # Get contacts with admin token
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{BACKEND_URL}/contact", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json()[:2], indent=2)}")  # Show only first 2 contacts
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("✅ Admin contact listing endpoint is working")
    return True

def test_file_upload():
    """Test file upload endpoint."""
    print_separator("Testing File Upload")
    
    # Create a test file (text file with random content)
    file_content = f"This is a test file created at {datetime.now().isoformat()}\n"
    file_content += f"Random content: {random_string(100)}"
    
    # Convert to base64
    base64_content = base64.b64encode(file_content.encode()).decode()
    
    # Prepare file data
    file_data = {
        "filename": f"test_file_{int(time.time())}.txt",
        "file_type": "text/plain",
        "file_size": len(file_content),
        "description": "Test file uploaded by automated test script",
        "content": base64_content,
        "is_public": True
    }
    
    # Upload file with user token
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.post(f"{BACKEND_URL}/files", json=file_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["filename"] == file_data["filename"]
    
    # Store the file ID for later use
    global test_file_id
    test_file_id = response.json()["id"]
    print("✅ File upload endpoint is working")
    return True

def test_file_listing():
    """Test file listing endpoint."""
    print_separator("Testing File Listing")
    
    # Get files with user token
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/files", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json()[:2], indent=2)}")  # Show only first 2 files
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("✅ File listing endpoint is working")
    return True

def test_file_download():
    """Test file download endpoint."""
    print_separator("Testing File Download")
    
    if not test_file_id:
        print("❌ No file ID available for download test")
        return False
    
    # Download file with user token
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{BACKEND_URL}/files/{test_file_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('Content-Type')}")
    print(f"Content Disposition: {response.headers.get('Content-Disposition')}")
    print(f"Content Length: {len(response.content)} bytes")
    
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "application/octet-stream"
    assert "attachment" in response.headers.get('Content-Disposition', '')
    print("✅ File download endpoint is working")
    return True

def test_eulogy_upload():
    """Test eulogy upload endpoint."""
    print_separator("Testing Eulogy Upload")
    
    # Create a test PDF-like content (just text for testing)
    eulogy_content = f"This is a test eulogy created at {datetime.now().isoformat()}\n"
    eulogy_content += f"In memory of Test Person\n"
    eulogy_content += f"Random content: {random_string(100)}"
    
    # Convert to base64
    base64_content = base64.b64encode(eulogy_content.encode()).decode()
    
    # Prepare eulogy data
    eulogy_data = {
        "title": "Test Eulogy",
        "deceased_name": "Test Person",
        "description": "Test eulogy uploaded by automated test script",
        "content": base64_content
    }
    
    # Upload eulogy with user token
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.post(f"{BACKEND_URL}/eulogies", json=eulogy_data, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["title"] == eulogy_data["title"]
    assert response.json()["deceased_name"] == eulogy_data["deceased_name"]
    
    # Store the eulogy ID for later use
    global test_eulogy_id
    test_eulogy_id = response.json()["id"]
    print("✅ Eulogy upload endpoint is working")
    return True

def test_eulogy_listing():
    """Test eulogy listing endpoint."""
    print_separator("Testing Eulogy Listing")
    
    response = requests.get(f"{BACKEND_URL}/eulogies")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json()[:2], indent=2)}")  # Show only first 2 eulogies
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    print("✅ Eulogy listing endpoint is working")
    return True

def test_eulogy_download():
    """Test eulogy download endpoint."""
    print_separator("Testing Eulogy Download")
    
    if not test_eulogy_id:
        print("❌ No eulogy ID available for download test")
        return False
    
    response = requests.get(f"{BACKEND_URL}/eulogies/{test_eulogy_id}")
    print(f"Status Code: {response.status_code}")
    print(f"Content Type: {response.headers.get('Content-Type')}")
    print(f"Content Disposition: {response.headers.get('Content-Disposition')}")
    print(f"Content Length: {len(response.content)} bytes")
    
    assert response.status_code == 200
    assert response.headers.get('Content-Type') == "application/pdf"
    assert "attachment" in response.headers.get('Content-Disposition', '')
    print("✅ Eulogy download endpoint is working")
    return True

def test_admin_cleanup_expired():
    """Test admin cleanup expired eulogies endpoint."""
    print_separator("Testing Admin Cleanup Expired Eulogies")
    
    # Cleanup expired eulogies with admin token
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.post(f"{BACKEND_URL}/admin/cleanup-expired", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert "message" in response.json()
    print("✅ Admin cleanup expired eulogies endpoint is working")
    return True

def test_admin_delete_file():
    """Test admin delete file endpoint."""
    print_separator("Testing Admin Delete File")
    
    if not test_file_id:
        print("❌ No file ID available for delete test")
        return False
    
    # Delete file with admin token
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.delete(f"{BACKEND_URL}/admin/files/{test_file_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "File deleted successfully"
    print("✅ Admin delete file endpoint is working")
    return True

def test_admin_delete_eulogy():
    """Test admin delete eulogy endpoint."""
    print_separator("Testing Admin Delete Eulogy")
    
    if not test_eulogy_id:
        print("❌ No eulogy ID available for delete test")
        return False
    
    # Delete eulogy with admin token
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.delete(f"{BACKEND_URL}/admin/eulogies/{test_eulogy_id}", headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.json()}")
    
    assert response.status_code == 200
    assert response.json()["message"] == "Eulogy deleted successfully"
    print("✅ Admin delete eulogy endpoint is working")
    return True

def run_all_tests():
    """Run all tests in sequence."""
    print_separator("TWOEM Backend API Tests")
    
    tests = [
        ("Health Check", test_health_check),
        ("User Registration", test_user_registration),
        ("User Login", test_user_login),
        ("Admin Login", test_admin_login),
        ("Get Current User", test_get_current_user),
        ("Services Listing", test_services_listing),
        ("Contact Submission", test_contact_submission),
        ("Admin Contact Listing", test_admin_contact_listing),
        ("File Upload", test_file_upload),
        ("File Listing", test_file_listing),
        ("File Download", test_file_download),
        ("Eulogy Upload", test_eulogy_upload),
        ("Eulogy Listing", test_eulogy_listing),
        ("Eulogy Download", test_eulogy_download),
        ("Admin Cleanup Expired", test_admin_cleanup_expired),
        ("Admin Delete File", test_admin_delete_file),
        ("Admin Delete Eulogy", test_admin_delete_eulogy)
    ]
    
    results = {}
    all_passed = True
    
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
            if not result:
                all_passed = False
        except Exception as e:
            print(f"❌ Error in {name}: {str(e)}")
            results[name] = False
            all_passed = False
    
    print_separator("Test Results Summary")
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    if all_passed:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n❌ Some tests failed. See details above.")
    
    return all_passed

if __name__ == "__main__":
    run_all_tests()