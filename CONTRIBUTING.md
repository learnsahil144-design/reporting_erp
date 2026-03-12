# Contributing to Reporting ERP

First off, thank you for considering contributing to Reporting ERP! It's people like you that make this tool better for everyone.

## 🌈 Our Vision
To provide the most flexible and easy-to-use daily reporting system for creative teams.

## 🛠 Development Workflow

1.  **Fork the repo** and create your branch from `main`.
2.  **Set up the environment**:
    ```bash
    pip install -r requirements.txt
    python manage.py migrate
    ```
3.  **Run tests**:
    ```bash
    python manage.py test
    ```
4.  **Coding Style**:
    - We follow PEP 8 for Python.
    - Use clear, descriptive variable names.
    - Add comments for complex logic.
5.  **Commit Messages**:
    - Start with a verb (e.g., "Add", "Fix", "Update").
    - Be concise but descriptive.

## 🧪 Testing Guidelines
- If you add a new feature, please add corresponding unit tests in `reports/tests.py`.
- Ensure all automated tests pass before submitting a Pull Request.

## 🛡 Security
- Do not commit any `.env` files or sensitive credentials.
- Follow the guidelines in [SECURITY.md](./SECURITY.md).

## 📝 Documentation
- Update `DOCUMENTATION.md` if you change the architecture or add new models.
- Update `USER_GUIDE.md` if the user interface or workflow changes.

---
*Thank you for your contributions!*
