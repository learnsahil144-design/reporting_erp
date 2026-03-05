# 📊 Media Reporting ERP

A robust, secure, and professional **Daily Reporting System** built with Django. This ERP is designed for media houses and content teams to track productivity, manage team-specific tasks, and generate performance audits.

---

## 🚀 Quick Start (Docker - Recommended)

The easiest way to get the project running is using Docker.

1. **Clone the repository**
2. **Create a `.env` file** (copy from `.env.example` or use the one provided)
3. **Run with Docker Compose:**
   ```bash
   docker-compose up -d --build
   ```
4. **Create a Superuser:**
   ```bash
   docker exec -it reporting_app python manage.py createsuperuser
   ```
5. **Access the app:**
   - Web App: [http://localhost:9001](http://localhost:9001)
   - Admin Panel: [http://localhost:9001/management-portal/](http://localhost:9001/management-portal/)

---

## 🌩️ Deployment via Docker Hub

This project is published on Docker Hub. You can deploy it to any server with a single command:

```bash
docker pull tsgdevelopments/reporting-erp:latest
```

### 🛰️ Simple Deployment (Docker Compose)
1. Copy [docker-compose.prod.yml](docker-compose.prod.yml) and [.env.prod.example](.env.prod.example) to your server.
2. Rename `.env.prod.example` to `.env.prod`.
3. Fill in your production secrets in `.env.prod`.
4. Run:
```bash
docker compose -f docker-compose.prod.yml up -d
```

---

## 🛠 Features

### 👤 For Users
- **Dynamic Forms**: Submits reports with fields specific to your team (e.g., Video Editors see different tasks than Content Writers).
- **Interactive Calendar**: Visual tracking of submitted (Green) and missed (Red) report days.
- **Report Preview**: Users can click on calendar dates to view their previous submissions.
- **Late Detection**: Automatically flags reports submitted after the actual date.

### 🛡️ For Admins
- **Unified Overview**: Search and filter all reports by team, user, or date.
- **Advanced Export**: Download reports to Professional Excel sheets using Pandas.
- **Dynamic Field Management**: Add or remove report fields through the admin panel without touching code.
- **Broadcast Notices**: Post announcements that appear on every user's dashboard.

---

## 🛡️ Security Hardening

This project is configured with high-level security measures:
- **Argon2 Hashing**: Advanced password security.
- **Brute-Force Protection**: `django-axes` blocks IP addresses after multiple failed logins.
- **Content Security Policy (CSP)**: Prevents XSS and unauthorized script execution.
- **Secure Cookies**: Enforced `HttpOnly` and `SameSite` flags.
- **Management Obfuscation**: The admin login is hidden at a custom URL to prevent bot discovery.

---

## 💻 Technical Stack

- **Backend**: Django 5.0.6 (Python 3.11)
- **Database**: PostgreSQL
- **Server**: Gunicorn + WhiteNoise (Static Management)
- **Frontend**: Bootstrap 5, FullCalendar.js
- **Containerization**: Docker & Docker Compose

---

## 🛠 Important Commands

### 🐳 Docker Commands
| Command | Description |
| :--- | :--- |
| `docker-compose up -d` | Start the system in background |
| `docker-compose down` | Stop and remove containers |
| `docker-compose logs -f web` | View real-time application logs |
| `docker exec -it reporting_app bash` | Access the container terminal |

### 🏗 Django Management
| Command | Description |
| :--- | :--- |
| `python manage.py migrate` | Apply database changes |
| `python manage.py collectstatic` | Prepare images/CSS for production |
| `python manage.py check --deploy` | Run security audit for production |
| `python manage.py shell` | Open Python interactive shell with Django context |

---

## � Creating a Superuser

A superuser has full access to the administration panel. You need this to manage users, teams, and dynamic fields.

### 🐳 If using Docker:
Run this command while your containers are running:
```bash
docker exec -it reporting_app python manage.py createsuperuser
```

### 💻 If running Locally:
Run this in your terminal from the project root:
```bash
python manage.py createsuperuser
```

> [!NOTE]
> Once created, you can log in at: `http://localhost:9001/management-portal/`

---

## �📁 Project Structure

```text
reporting_erp/
├── media_reporting/      # Core settings & URLs
│   ├── settings/         # Base, Dev, and Prod configs
├── reports/              # Main app (models, views, forms)
│   ├── templates/        # HTML templates
│   ├── signals.py        # Security & Audit logging
├── static/               # CSS, JS, and Images
├── Dockerfile            # Container definition
├── docker-compose.yml    # Services (App + DB)
└── security_audit.log    # Real-time login/security logs
```

---

## 📜 License
This project is licensed under the MIT License.

## 🛡️ Vulnerability Reporting
See [SECURITY.md](SECURITY.md) for reporting security issues.
