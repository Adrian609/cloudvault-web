# Testing

This project uses `pytest` with Flask's `test_client`.

The test suite uses a temporary SQLite database and a temporary upload directory for each test, so it does not use `instance/cloudvault.db` or write encrypted files to the real `uploads/` folder.

## Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## Run tests

```powershell
pytest -q
```

## Run tests with coverage

```powershell
pytest --cov=. --cov-report=term-missing
```
