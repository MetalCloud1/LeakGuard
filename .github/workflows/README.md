<h1 align="center">⚙️ Continuous Integration Pipeline</h1>

<p align="center">
  <a href="https://www.docker.com/"><img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker"></a>
  <a href="https://kubernetes.io/"><img src="https://img.shields.io/badge/Kubernetes-Ready-blue?logo=kubernetes"></a>
  <a href="https://creativecommons.org/licenses/by-nc-nd/4.0/"><img src="https://img.shields.io/badge/License-CC--BY--NC--ND-lightgrey.svg"></a>
</p>

---
<h1 align="center">
🔍 Overview
</h1>

This repository provides a **CI pipeline** for Python-based microservices:

- `auth_service`
- `password_checker_service`

The pipeline ensures **quality, consistency, and reproducibility** across all services.

---
<h1 align="center">

🚀 Workflow Triggers

</h1>

The CI pipeline runs automatically on:

- Push to `dev`, `main`, or `leakchecker`
- Pull requests into `dev` or `main`
- Manual runs via `workflow_dispatch`

---
<h1 align="center">

🛠️ Pipeline Stages

</h1>

1. **Checkout** repository  
2. **Setup Python 3.11**  
3. **Install dependencies** for all services  
4. **Linting** with `flake8`  
5. **Start PostgreSQL** service (used for testing)  
6. **Run tests** with `pytest`  
7. **List discovered test files**  
8. **Build local Docker images**  

---

<h1 align="center">

🐳 Local Usage

</h1>

---

To build Docker images locally:

```bash
# Build Docker images for all services
services=("auth_service" "password_checker_service")
for service in "${services[@]}"; do
  docker build -t gilbr/$service:latest $service/
done
```

<h1 align="center">

🗄️ Database Configuration

</h1>

---

**PostgreSQL service runs during the pipeline with:**

```ini
POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
POSTGRES_DB=testdb
```
**Database URL for tests:**

```bash
postgresql+asyncpg://testuser:testpass@localhost:5432/testdb

```

---

<h1 align="center">

✅ Code Quality

</h1>

---

* Linting: `flake8`

* Testing: `pytest`

* Both enforced during CI to maintain code quality and stability.

```yaml
```yaml
name: CI Pipeline

on:
  push:
    branches: [dev, main, leakchecker]
  pull_request:
    branches: [dev, main]
  workflow_dispatch:

jobs:
  ci:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_USER: testuser
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd="pg_isready -U testuser -d testdb"
          --health-interval=5s
          --health-timeout=5s
          --health-retries=20

    steps:
      - name: 📥 Checkout repository
        uses: actions/checkout@v3

      - name: 🐍 Setup Python 3.11
        uses: actions/setup-python@v4
        with:
          python-version: 3.11

      - name: 📦 Install dependencies
        run: |
          pip install --upgrade pip
          pip install -r auth_service/requirements-test.txt
          pip install -r auth_service/requirements.txt
          pip install -r password_checker_service/requirements.txt

      - name: 🔍 Lint services
        run: |
          flake8 auth_service/src
          flake8 password_checker_service/src_pcs

      - name: ⏳ Wait for PostgreSQL
        run: |
          echo "Waiting for Postgres to be ready..."
          for i in {1..20}; do
            pg_isready -h localhost -p 5432 -U testuser -d testdb && break
            echo "Postgres not ready yet..."
            sleep 3
          done
          pg_isready -h localhost -p 5432 -U testuser -d testdb || exit 1

      - name: 🧪 Run tests
        env:
          DATABASE_URL: postgresql+asyncpg://testuser:testpass@localhost:5432/testdb
          PYTHONPATH: ${{ github.workspace }}/auth_service/src:${{ github.workspace }}/password_checker_service/src_pcs
        run: |
          python -m pytest auth_service/tests -vv --disable-warnings
          python -m pytest password_checker_service/tests -vv --disable-warnings

      - name: 📂 List test files
        run: |
          echo "Discovered test files:"
          find auth_service/tests -name "*.py"
          find password_checker_service/tests -name "*.py"

      - name: 🐳 Build Docker images (local)
        run: |
          services=("auth_service" "password_checker_service")
          for service in "${services[@]}"; do
            docker build -t gilbr/$service:latest $service/
          done
```