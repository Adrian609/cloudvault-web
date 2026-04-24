# AI Usage

## Tools Used
- ChatGPT
- GitHub Copilot (used occasionally in VS Code)

## How AI Was Used
AI tools were mainly used to get initial structure and guidance for certain parts of the project. However, most of the code required manual adjustments and debugging to make it work correctly in our environment.

## Work Breakdown (AI vs Manual)

- Authentication (login/register): Initially generated using ChatGPT, but modified manually (especially session handling and validation).
- Database models (User, FileRecord, AccessRequest): Created with AI help, but updated manually multiple times after errors.
- File upload and encryption: Logic was partially suggested by AI, but implemented and fixed manually.
- Access request workflow: Designed manually based on assignment requirements, with some help from AI for route structure.
- Debugging: Mostly done manually (indentation issues, DB errors, routing problems).

## Example Prompts Used

1. "How to implement login and registration in Flask with SQLAlchemy"
2. "How to encrypt files in Python using Fernet"
3. "How to build role-based access control in Flask"

## Issues with AI-Generated Code

- Some generated code had indentation problems (tabs vs spaces), which caused runtime errors.
- AI did not consider existing database schema, which caused column mismatch errors.
- Some routes worked logically but didn’t match our workflow requirements, so they were rewritten.

## Fixes Made Manually

- Fixed indentation issues across the project
- Reset database after schema changes
- Added validation for file upload (file type, size, empty files)
- Prevented duplicate access requests
- Prevented users from requesting their own files

## Security Observation

- Initial AI code did not include enough input validation
- File upload needed restrictions to prevent unsafe file types
- Access control needed proper checks at route level (not just UI)


## Reflection

AI tools were helpful for speeding up development, but they were not reliable on their own.
