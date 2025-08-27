<h1 align="center">

🛠️ Alembic  
`env-template` Guide

</h1>

<h2 align="center">

 🎯 Purpose

</h2>

- Connect to your database (PostgreSQL) using **AWS Secrets Manager** or local environment variables.  
- Define the target metadata (`Base.metadata`) for auto-generating migrations.  
- Provide **offline and online migration functions** compatible with both sync and async contexts.

---

<h2 align="center">

 📝 Modifying `env-template`

</h2>

1. **Change database connection**  
   - Update `secret_name` and `region_name` for production secrets in AWS.  
   - For local development, set environment variables (`POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `POSTGRES_HOST`) or override `DATABASE_URL`.  

2. **Add models to migrations**  
   - Ensure all models are imported (`import src.models`) so Alembic can detect schema changes automatically.  

3. **Adjust logging**  
   - Modify `logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)` to change SQL log verbosity.  

4. **Custom migration behavior**  
   - Edit `run_migrations_offline()` or `run_migrations_online()` to add extra options or hooks if needed.  

---


<h2 align = "center">
🏗️ Local Testing and Alembic Usage
</h2>

### ⚡ Running Alembic migrations locally

```bash
# Show current revision
alembic current

# Create a new migration after changing models (autogenerate)
alembic revision --autogenerate -m "Add new tables or fields"

# Apply migrations to the database
alembic upgrade head
```

<h2 align = "center">
🐳 Kubernetes / Pods Notes (auth-dev)
</h2>

PostgreSQL pod (`postgres-0`) is in the same namespace (`auth-dev`) as the auth service pods.

Pods communicate via in-cluster DNS:

- `postgres-0.auth-dev.svc.cluster.local` (direct pod)  
- `postgres.auth-dev.svc.cluster.local` (preferred service)

**Implications:**

- Run Alembic from auth service pods; it will update `postgres-0`.  
- Test migrations on dev pods first.  
- Avoid running multiple migrations in parallel.

<h2 align = "center">
🐳 Notes for Kubernetes / Pods (auth-dev)
</h2>

* The PostgreSQL StatefulSet pod (postgres-0) usually lives in the same namespace auth-dev as your authentication service pods.

* Pods communicate using in-cluster DNS. Examples of names a pod can use:

  * postgres-0 (pod name, not recommended for stable access)

  * postgres-0.auth-dev.svc.cluster.local (pod DNS)

  * postgres.auth-dev.svc.cluster.local (service DNS — prefer service access)

* Prefer connecting via the DB Service (e.g. postgres.auth-dev.svc.cluster.local) rather than pod DNS. Services provide stable DNS and load balancing across replicas.

 Implications for migrations:

  * Running Alembic from the auth service pod will talk to the DB service and update the database in postgres-0 (or the primary).

  * Do not run multiple migrations in parallel against the same DB instance — this can cause locks or conflicting schema changes.

  * Ensure migrations are tested on dev/staging postgres-0 before applying to production.


<h2 align = "center">

🔧 Apply migrations in-cluster 

</h2>

```bash
kubectl exec -it path/deploy.yaml -n auth-dev -- /bin/bash
alembic upgrade head
alembic history --verbose
```

<h2 align = "center">
🌐 Outside the Cluster (Simpler and Safe)
</h2>

```bash
# Forward the pod port to localhost
kubectl port-forward pod/postgres-0 5432:5432 -n auth-dev

# Optionally, export environment variables needed by Alembic
export POSTGRES_USER=authuser
export POSTGRES_PASSWORD=testpass
export POSTGRES_DB=authdb
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

#If needed 
alembic revision --autogenerate -m "Add new tables or fields"

# Then apply migrations
alembic upgrade head
```

<h2 align = "center">
🐋 Local Docker Testing
</h2>

```bash
docker network create auth-network

docker run -d --name auth-db \
  --network auth-network \
  -e POSTGRES_USER=authuser \
  -e POSTGRES_PASSWORD=testpass \
  -e POSTGRES_DB=authdb \
  -p 5432:5432 \
  postgres:13

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

docker exec -it auth-service alembic upgrade head
```

<h2 align ="center">
🏗️ Forcing Table Creation in PostgreSQL
</h2>

If you need to create tables manually or ensure that Alembic applies them even if the database is empty, you can define the schema directly in a migration file:

```python

"""Initial schema

Revision ID: 32cceb7bc6db
Revises: 
Create Date: 2025-08-03 23:23:47.473871
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '32cceb7bc6db'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.create_table(
        'users',
        sa.Column('username', sa.String(), primary_key=True),
        sa.Column('email', sa.String(), unique=True),
        sa.Column('full_name', sa.String()),
        sa.Column('hashed_password', sa.String()),
        sa.Column('verification_token', sa.String(), nullable=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false')
    )

def downgrade():
    op.drop_table('users')
```

<h3 align = "center">
⚡ Applying the migration
</h3>

```bash
#Make sure your environment variables are set (especially if running outside the cluster):
export POSTGRES_USER=authuser
export POSTGRES_PASSWORD=testpass
export POSTGRES_DB=authdb
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432

alembic upgrade head
```

**Notes:**

* This approach guarantees that the table is created exactly as defined.

* Always review the migration file before running upgrade head in production.

* Use this method in dev or staging environments first to verify correctness.

* If the table already exists, Alembic will skip creation unless you modify the migration to handle conflicts (e.g., using if_not_exists patterns or manual checks).

<h2 align = "center">
🧩 How postgres-0, Service and Auth Pods communicate (practical notes)
</h2>

```yaml
env:
  - name: POSTGRES_HOST
    value: "postgres"
  - name: POSTGRES_PORT
    value: "5432"
  - name: POSTGRES_DB
    value: "authdb"
  - name: POSTGRES_USER
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: username
  - name: POSTGRES_PASSWORD
    valueFrom:
      secretKeyRef:
        name: db-credentials
        key: password
```

* Why service vs pod DNS matters:

  * Services maintain consistent endpoints and can route to the current primary.
  * Directly addressing postgres-0 may break after restarts or scaling.


<h2 align = "center">
🛡️ Best practices when creating/updating tables with Alembic (focus on postgres-0)
</h2>

1. Always autogenerate + review

  * Use alembic revision --autogenerate then manually inspect the migration file in alembic/versions/.

  * Ensure column types, defaults, nullability, and indexes are correct.

2. Perform migrations on a dev cluster first

  * Apply to a dev postgres-0 replica and run integration tests.

3. Avoid destructive changes without backups

  * Big destructive operations (DROP column, DROP table) should be planned and possibly performed in multiple steps (create replacement columns, migrate data, then drop).

4. Mind locks and long-running transactions

  * Schema changes can lock tables. Run during maintenance windows if needed.

  * For large tables, prefer non-blocking patterns (e.g., create new table, copy data in batches, swap).

5. Single source of truth

  * Keep migrations in VCS and apply them from your deployment pipeline (CI/CD) or via a controlled kubectl exec into a maintenance job.

6. Use DB Services & primary awareness

  * Ensure your Alembic run targets the primary writable node behind the DB Service.

<h2 align = "center">
  ⚠️ Async considerations (service code & tests)
</h2>

* The microservice uses async SQLAlchemy (AsyncSession) and asyncpg.

* Migrations are synchronous, but your application code must use async sessions.

* Tests should use pytest-asyncio or similar to await DB calls.

Example async endpoint using AsyncSession:

```python
# example: async endpoint using AsyncSession
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import Depends, HTTPException, status

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
```


<h2 align = "center">
💡 Tips
</h2>

* Keep ports as integers in secrets and env variables.

* Always test migrations on a development DB/Pod before applying to production.

* Do not commit sensitive keys; use environment variables or a secrets store (AWS Secrets Manager / Kubernetes Secrets).

* Use a Kubernetes Service for DB access (postgres.auth-dev.svc.cluster.local) rather than direct pod access.

* Ensure only one migration runs at a time to avoid conflicts.

* Monitor migrations via alembic history, DB logs, and Kubernetes pod logs.

<h2 align = "center">
📄 License
</h2>

This project is licensed under CC BY-NC-ND (custom).
See LICENSE.md
 for full details.

> ⚠️ Please respect the author's attribution and license when using this template.