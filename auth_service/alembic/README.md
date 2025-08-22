<h1 align="center">
 <b> Alembic `env-template` Guide </b>
</h1>


<h2 id="features" align="center">

**Purpose**

</h2>

* Connect to your database (PostgreSQL) using **AWS Secrets Manager** or local secrets.

* Define the target metadata (`Base.metadata`) for auto-generating migrations.

* Provide **offline and online migration functions**.

<h2 id="modifying-env-template" align="center">

**Modifying** `env-template`

</h2>

1. **Change database connection**

   * Update `secret_name` and `region_name` for production secrets in AWS.

   * For local development, modify `local_secret_file` or environment variables (`DB_USERNAME`, `DB_PASSWORD`, etc.).

2. **Add models to migrations**
   
   * Ensure all models are imported (`import src.models`) so Alembic can detect schema changes.

3. **Adjust logging**

   * Modify `logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)` to change SQL log verbosity.

4. **Custom migration behavior**

   * Edit `run_migrations_offline()` or `run_migrations_online()` to add extra options or hooks.

<h2 id="local-testing-with-docker" align="center">

**Asynchronous Database Considerations**

</h2>

* This **microservice uses async database functions** via SQLAlchemy’s `AsyncSession` and `asyncpg`.

* **Impact on tests:**

  * You must use async test clients (`httpx.AsyncClient`) and async fixtures (`pytest-asyncio`).

  * Tests must `await` database operations, making them more complex than synchronous tests.

* **Impact on Alembic:**

  * Migrations themselves run synchronously, but `env-template` must account for async engine configuration in the app.

  * The template ensures compatibility by separating **offline** and **online** modes, and by converting secrets to usable formats for both sync and async contexts.
**Impact on Endpoint Code:**

* **All endpoints interacting with the database must be async** and use await for queries and commits.

* **Example:**

```python
async def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    username = decode_token_return_username(token)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user
```
* **Important implications:**

  * Every DB operation must be `awaited`; synchronous calls will fail.

  * Dependency injection (`Depends(get_db)`) must provide an **async session**.

  * Any utility function accessing the DB must also support async, or be called inside an async context.

<h2 id="local-testing-with-docker" align="center">

**Local Testing with Docker**

</h2>

You can test migrations locally using Docker containers for the database and the authentication service:

```bash
# Create a custom network
docker network create auth-network

# Run PostgreSQL container
docker run -d --name auth-db \
  --network auth-network \
  -e POSTGRES_USER=authuser \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=authdb \
  -p 5432:5432 \
  postgres:13

# Build and run authentication service container
docker build -t auth-service:local ./auth_service
docker run -d --name auth-service \
  --network auth-network \
  -e POSTGRES_USER=authuser \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=authdb \
  -e POSTGRES_HOST=auth-db \
  -e SECRET_KEY=dummy_dev_key \
  -p 8000:8000 \
  auth-service:local
```

* Both containers share the same `auth-network`, allowing the service to communicate with the database.

* You can now run Alembic migrations pointing to `postgresql+asyncpg://authuser:testpass@auth-db:5432/authdb`.

<h2 id="tips" align="center">

**Tips**

</h2>

* Keep port as integer in secrets.
 
* Always test migrations on a dev database before applying to production.

* Avoid committing sensitive keys; use environment variables or AWS Secrets Manager.