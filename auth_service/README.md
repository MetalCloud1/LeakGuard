<h1 align="center">
 <b>🔐Authentication Service🗡️</b>
</h1>

This microservice provides **user authentication and authorization** for the scalable microservices template.
It is designed to be **modular**, **secure**, and **extensible**, serving as the central entry point for handling user identities across the entire system.<br><br>

<h2 id="features" align="center">
✨Features
</h2>
<div style="font-size:17px;">
<ol>
✅ JWT-based authentication with access and refresh tokens.

✅ Secure password handling using industry standards (bcrypt).

✅ OAuth2.0 Password Grant flow with FastAPI security utilities.

✅ Role-based access control (RBAC) ready.

✅ Extensible user model integrated with SQLAlchemy and async operations.

✅ Custom exception handling with consistent JSON responses.
</ol>
</div>

<h2 id="architecture" align="center">
🏗️ Architecture
</h2>

<p align="center">
  <img src="..\docs\diagrams\diagrams-svg-files\auth-service.svg" width="400"/>
</p>

<h2 id="endpoints" align="center">
⚡Endpoints
</h2>

`POST /auth/login`

Authenticate a user and return JWT tokens.

**Request**

```json
{
  "username": "example_user",
  "password": "example_password"
}
```
**Response**

```json
{
  "access_token": "jwt_token_here",
  "refresh_token": "refresh_token_here",
  "token_type": "bearer"
}
```

`POST /auth/refresh`

Refresh an expired access token using a refresh token.

`POST /auth/register`

Register a new user (can be disabled in production for security).

<h2 id="testing" align="center">
🧪Testing
</h2>

The service is fully testable using **pytest**.

Run all tests:

```bash
{
  pytest tests/ --disable-warnings
}
```

* **Unit tests ensure password hashing**, JWT creation/validation, and role enforcement work correctly.

* **Integration tests** verify interactions with the database and API endpoints.

* **Load testing** can be performed with `locust` or `k6` to measure performance under heavy authentication traffic.

<h2 id="security-considerations" align="center">
🔒Security Considerations
</h2>

* Passwords are **hashed** with `bcrypt` and never stored in plain text.

* Tokens are signed with strong secrets stored in `Vault/Kubernetes Secrets`.

* **CORS policies and rate limiting** should be configured depending on your environment.

* **RBAC** can be extended for fine-grained permissions.

<h2 id="configuration" align="center">
⚙️Configuration
</h2>

```ini
Environment variables (example `.env`):
DATABASE_URL=postgresql+asyncpg://user:password@db:5432/auth_db
JWT_SECRET_KEY=supersecretkey
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

<h2 id="deployment" align="center">
🚀Deployment
</h2>

This service runs as a **Dockerized microservice** and integrates into the template’s Kubernetes cluster.

```bash
docker build -t auth-service .
docker run -p 8000:8000 --env-file .env auth-service
```
When deployed in Kubernetes, secrets and configs should be injected via `ConfigMaps` and `Secrets`.

<h2 id="integrationwith-other-microservices" align="center">
📡Integration with Other Microservices
</h2>

* The **Auth Service** issues tokens that must be validated by other services (e.g., Order, Payment, Monitoring).

* Services only need to verify JWT tokens and check claims.

* Centralized authentication ensures consistency, security, and **scalability**.

<h2 id="future enhancements" align="center">
Future Enhancements</h2>

* 🔑Support for **third-party OAuth providers** (Google, GitHub, etc.).


* 📜Refresh token rotation with blacklist support.


* 🏛️Multi-tenancy and organization-based user management.


* 📊Audit logging for login attempts and suspicious activity.