# CI Pipeline

[![CI](https://github.com/MetalCloud1/microservices-workflow/actions/workflows/ci.yaml/badge.svg)](https://github.com/MetalCloud1/microservices-workflow/actions/workflows/ci-cd-dev.yaml)  
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](https://www.docker.com/)  
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue?logo=kubernetes)](https://kubernetes.io/)  
[![License: CC BY-NC-ND](https://img.shields.io/badge/License-CC--BY--NC--ND-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-nd/4.0/)

## Overview

This repository contains a **CI pipeline** for multiple Python microservices:

- `auth_service`
- `users-api`
- `password_checker_service`

* **The workflow automatically runs on:**

- Push to `dev`, `main`, or `leakchecker` branches
- Pull requests to `dev` or `main`
- Manual trigger via `workflow_dispatch`

* **The CI pipeline includes:**

1. Checking out the repository
2. Setting up Python 3.11
3. Installing dependencies for all services
4. Linting all services with Flake8
5. Starting a PostgreSQL service for testing
6. Running all tests with `pytest`
7. Listing all test files
8. Building Docker images locally

## Usage

To run the workflow locally:

```bash
# Build Docker images for all services
services=("auth_service" "users-api" "password_checker_service")
for service in "${services[@]}"; do
  docker build -t gilbr/$service:latest $service/
done
```
## Badges

* CI Status: Shows the current status of the GitHub Actions workflow.

  * Python Version: Indicates the Python version used.

  * Docker: Confirms Docker setup for local builds.

  * License: Repository license.

## Notes

  * The PostgreSQL service is configured with:

```ini
POSTGRES_USER=testuser
POSTGRES_PASSWORD=testpass
POSTGRES_DB=testdb
```

## Database URL for tests:

```ini
postgresql+asyncpg://testuser:testpass@localhost:5432/testdb
```

Flake8 and pytest are used to maintain code quality and run unit tests.