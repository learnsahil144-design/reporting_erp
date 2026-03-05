# 🛡️ Project Security Overview

This ERP system has been significantly hardened with industry-standard security measures to protect user data and maintain system integrity.

## 🚀 Implemented Security Measures

### 1. 🔐 Authentication & Session Hardening
- **Argon2 Hashing**: Upgraded from standard PBKDF2 to **Argon2**, the winner of the Password Hashing Competition, which is highly resistant to GPU/ASIC-based cracking.
- **Brute-Force Protection**: Integrated `django-axes` to automatically lockout IP addresses after 5 failed login attempts.
- **Session Expiration**: Sessions now expire when the browser is closed, and have a maximum age of 24 hours.
- **Secure Cookies**: In production, cookies are set to `Secure`, `HttpOnly`, and `SameSite='Lax'` to prevent XSS and CSRF attacks.

### 2. 🛡️ Network & Header Security
- **Strict Transport Security (HSTS)**: Forced SSL/TLS for all connections (1-year duration).
- **X-Frame-Options**: Set to `DENY` to prevent clickjacking attacks via iframes.
- **Content-Type Sniffing Protection**: Prevents browsers from interpreting files as a different MIME type (X-Content-Type-Options: nosniff).
- **Referrer Policy**: Set to `same-origin` to prevent leaking sensitive internal URL paths.

### 3. 🔍 Auditing & Monitoring
- **Security Audit Logs**: Created a dedicated `security_audit.log` file using Django signals.
- **Real-time Logging**: All failed login attempts, successful logins, and logouts are logged with IP addresses for administrator review.

### 4. 🎭 Obfuscation
- **Management Portal**: The default `/admin/` URL has been changed to a more secure, non-obvious path to prevent automated bot scanning.

## 💡 Future Recommendations

1. **SSL/TLS Certificate**: Ensure the production server is using a valid SSL certificate (e.g., via Let's Encrypt).
2. **Web Application Firewall (WAF)**: Consider using a WAF (like Cloudflare) for additional DDoS and L7 protection.
3. **Multi-Factor Authentication (MFA)**: For highly sensitive environments, consider adding `django-two-factor-auth`.
4. **Regular Dependency Audits**: Run `pip audit` regularly to check for vulnerabilities in third-party packages.

---
*Report security vulnerabilities to: admin@letsupp.com*

## 🌩️ Server-Level Security (OS Hardening)

To ensure "nobody enters your server" through this project, follow these server-side best practices:

### 1. 🛡️ Firewall & Network
- **Restrict Ports**: Only open ports `80` (HTTP), `443` (HTTPS), and `22` (SSH).
- **SSH Key Authentication**: Disable password-based SSH login. Use RSA/Ed25519 keys instead.
- **Fail2Ban**: Install `fail2ban` on the server to block IPs that repeatedly fail SSH or Web logins.

### 2. 🐳 Docker Container Isolation
- **Non-Root User**: The project is configured to run as the `django` user inside the container. Never run as `root`.
- **Resource Limits**: Limit CPU and Memory for the container in `docker-compose.yml` to prevent DoS via resource exhaustion.
- **Read-Only FS**: In production, consider mounting the app directory as read-only.

### 3. 🔑 Environment & Secrets
- **Never Commit .env**: Ensure `.env` is never uploaded to public repositories.
- **Strong Secret Key**: Use a unique, long, and random `SECRET_KEY`.
- **Database Access**: Ensure the database port (`5432`) is **not** exposed to the public internet. It should only be accessible within the Docker network.

### 4. 🚀 Production Deployment Audit
Before going live, run:
```bash
python manage.py check --deploy --settings=media_reporting.settings.prod
```
This command checks for missing security settings (like HSTS, Secure Cookies, etc.).
