# CloudVault Web

## Project Overview
CloudVault Web is a secure multi-user web application that allows users to upload, encrypt, store, and retrieve files. Admin users can manage accounts and approve or deny access requests.

## System Description
- Backend: Flask (Python)
- Database: SQLite (SQLAlchemy)
- Authentication: Flask-Login
- Encryption: Fernet (cryptography)

## User Roles
- User:
  - Upload files
  - View own files
  - Request access to other files
- Admin:
  - View all users
  - Approve/Deny access requests

## Workflows

### Workflow 1: Upload File
User logs in → uploads file → file is encrypted → saved in database

### Workflow 2: Access Request
User requests file → admin reviews → approves/denies → user downloads if approved

## Features
- User registration and login
- Role-based access control
- File upload with encryption
- Access request workflow
- Admin panel
