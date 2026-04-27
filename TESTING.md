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

## GitHub Actions CI/CD

The repository includes `.github/workflows/ci-cd.yml`.

It runs automatically on:

- pushes to `main` or `master`
- pull requests into `main` or `master`
- manual runs from the GitHub Actions tab

The workflow:

- installs dependencies from `requirements.txt`
- runs `python -m pytest -q` on Python 3.11 and 3.12
- runs coverage with `python -m pytest --cov=. --cov-report=term-missing --cov-report=xml`
- uploads `coverage.xml` as a workflow artifact
- includes a deploy job placeholder that runs only after tests pass on `main` or `master`
