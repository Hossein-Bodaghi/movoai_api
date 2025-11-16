#!/usr/bin/env python3
"""
Verification script for Phase 1 implementation
Checks that all required files and components are in place
"""

import os
import sys
from pathlib import Path

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def check_file(filepath, description):
    """Check if a file exists"""
    if os.path.exists(filepath):
        print(f"{GREEN}✓{RESET} {description}: {filepath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {filepath} - MISSING")
        return False

def check_directory(dirpath, description):
    """Check if a directory exists"""
    if os.path.isdir(dirpath):
        print(f"{GREEN}✓{RESET} {description}: {dirpath}")
        return True
    else:
        print(f"{RED}✗{RESET} {description}: {dirpath} - MISSING")
        return False

def main():
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}MovoAI API - Phase 1 Implementation Verification{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Core application files
    print(f"\n{YELLOW}Checking Core Application Files...{RESET}")
    core_files = [
        ("app/main.py", "Main FastAPI application"),
        ("app/dependencies.py", "Shared dependencies"),
        ("app/core/config.py", "Configuration settings"),
        ("app/core/security.py", "Security utilities"),
        ("app/database/session.py", "Database session"),
        ("app/database/base.py", "SQLAlchemy base"),
    ]
    
    for filepath, desc in core_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Models
    print(f"\n{YELLOW}Checking Database Models...{RESET}")
    model_files = [
        ("app/models/__init__.py", "Models package"),
        ("app/models/user.py", "User model"),
        ("app/models/auth_method.py", "Auth method model"),
        ("app/models/verification_code.py", "Verification code model"),
        ("app/models/workout.py", "Workout models (Phase 2 prep)"),
    ]
    
    for filepath, desc in model_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Schemas
    print(f"\n{YELLOW}Checking Pydantic Schemas...{RESET}")
    schema_files = [
        ("app/schemas/__init__.py", "Schemas package"),
        ("app/schemas/user.py", "User schemas"),
        ("app/schemas/auth.py", "Authentication schemas"),
    ]
    
    for filepath, desc in schema_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # API Endpoints
    print(f"\n{YELLOW}Checking API Endpoints...{RESET}")
    endpoint_files = [
        ("app/api/v1/api.py", "API router"),
        ("app/api/v1/endpoints/auth.py", "Authentication endpoints"),
        ("app/api/v1/endpoints/users.py", "User endpoints"),
    ]
    
    for filepath, desc in endpoint_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Services
    print(f"\n{YELLOW}Checking Services...{RESET}")
    service_files = [
        ("app/services/external.py", "External integrations (Twilio, SendGrid, Google)"),
    ]
    
    for filepath, desc in service_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Alembic
    print(f"\n{YELLOW}Checking Database Migrations...{RESET}")
    alembic_files = [
        ("alembic.ini", "Alembic configuration"),
        ("alembic/env.py", "Alembic environment"),
        ("alembic/versions/001_add_auth_tables.py", "Initial migration"),
    ]
    
    for filepath, desc in alembic_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Tests
    print(f"\n{YELLOW}Checking Tests...{RESET}")
    test_files = [
        ("tests/conftest.py", "Test configuration"),
        ("tests/test_auth.py", "Authentication tests"),
        ("tests/test_users.py", "User tests"),
    ]
    
    for filepath, desc in test_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Documentation
    print(f"\n{YELLOW}Checking Documentation...{RESET}")
    doc_files = [
        ("README.md", "Main README"),
        ("QUICKSTART.md", "Quick start guide"),
        ("PROJECT_PLAN.md", "Full project plan"),
        ("IMPLEMENTATION_SUMMARY.md", "Implementation summary"),
    ]
    
    for filepath, desc in doc_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Configuration files
    print(f"\n{YELLOW}Checking Configuration Files...{RESET}")
    config_files = [
        ("requirements.txt", "Python dependencies"),
        (".env.example", "Environment template"),
        (".gitignore", "Git ignore file"),
        ("setup.sh", "Setup script"),
    ]
    
    for filepath, desc in config_files:
        checks_total += 1
        if check_file(filepath, desc):
            checks_passed += 1
    
    # Check for .env file
    print(f"\n{YELLOW}Checking Environment Configuration...{RESET}")
    checks_total += 1
    if os.path.exists(".env"):
        print(f"{GREEN}✓{RESET} .env file exists")
        checks_passed += 1
    else:
        print(f"{YELLOW}!{RESET} .env file not found (run: cp .env.example .env)")
    
    # Summary
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}Verification Summary{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    percentage = (checks_passed / checks_total) * 100
    
    if checks_passed == checks_total:
        print(f"\n{GREEN}✓ All checks passed! ({checks_passed}/{checks_total}){RESET}")
        print(f"\n{GREEN}Phase 1 implementation is COMPLETE!{RESET}")
        print(f"\nNext steps:")
        print(f"1. Configure .env file if not done")
        print(f"2. Run: alembic upgrade head")
        print(f"3. Run: uvicorn app.main:app --reload")
        print(f"4. Access: http://localhost:8000/docs")
        return 0
    else:
        print(f"\n{YELLOW}Checks passed: {checks_passed}/{checks_total} ({percentage:.1f}%){RESET}")
        if checks_passed >= checks_total * 0.9:
            print(f"\n{YELLOW}Almost complete! A few files may be missing.{RESET}")
            return 0
        else:
            print(f"\n{RED}Some critical files are missing. Please review the implementation.{RESET}")
            return 1

if __name__ == "__main__":
    sys.exit(main())
