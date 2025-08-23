<h1 align ="center">

🐍 Auth Service - Source Code Overview

</h1>

This folder contains the source code for the authentication logic, including database access, user management, JWT handling, and utilities for password hashing and email sending.

<h2 align = "center">

`main.py`
Sequence Diagram

<p align="center">

  <img src="..\..\docs\diagrams\diagrams-svg-files\auth-src-sequenceDiagram.svg" width="1000"/>

</p>

</h2>


<h2>

`database.py`

</h2>

* Handles **asynchronous database connections using SQLAlchemy** `AsyncSession`.

* Retrieves the secret key from AWS Secrets Manager in production or from environment variables in development.

* **Functions:**

    * `get_user_by_username`: Fetches a user from the database.

    * `authenticate_user`: Validates username and password.

    * `create_access_token`: Generates JWT tokens.

    * `decode_token_return_username`: Decodes JWT to extract the username.

<h2>

`logger.py`

</h2>

* Configures structured logging with Loguru.

* Logs requests and responses, serializing output to stdout.

* Supports asynchronous logging contexts via `bind()`.


<h2>

`main.py`

</h2>

* Implements the FastAPI application.

* **Provides endpoints for:**

    * `POST /register` – user registration with hashed password and email verification.

    * `GET /verify-email` – email verification using a token.

    * `POST /token` – login endpoint returning JWT token.

    * `GET /users/me` – retrieve authenticated user info.

    * `GET /health` – health check.

* **Middleware:**

    * Request logging with UUID and client info.

    * Rate limiting using SlowAPI.

    * Prometheus instrumentation with Instrumentator.

<h2>

`models.py`

</h2>

* **Defines SQLAlchemy ORM models.**

* `User` table fields:

    * `username`, `email`, `full_name`, `hashed_password`, `verification_token`, `is_verified`.

<h2>

`schemas.py`

</h2>

* **Pydantic models for input validation and output serialization:**

    * `UserCreate` – user registration input with strong password validation.

    * `UserOut` – user info output.

* Ensures password policies: uppercase, lowercase, number, special character, and not same as username

<h2>

`utils.py`

</h2>

* **Utility functions:**

    * `get_password_hash` / `verify_password` – handle secure password hashing using bcrypt.

    * `send_email` – send email via SMTP (Gmail) with plain text content.

<h2 align = "center">

Main flow of `main.py`

</h2>

<p align="center">

  <img src="..\..\docs\diagrams\diagrams-svg-files\auth_service-src-diagram.svg" width="1000"/>

</p>


<h2 align = "center">

✅Key Notes

</h2>

* **Async DB access:** All database operations are asynchronous, which requires `AsyncSession` and careful handling in testing.

* **JWT handling:** Tokens are generated and verified securely using the configured secret key.

* **Email verification logic** is embedded in the registration flow.

* **Structured logging** allows easy tracing of requests.


