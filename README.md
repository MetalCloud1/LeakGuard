<h1 align="center" style="font-size:40px;">
 <b>⚒️MicroForge🗡️</b>
 <p align="center"style="font-size:12px;"><em>
<br> Kickstart your microservices projects with secure authentication,
  <br>scalable services, automated CI/CD pipelines, and built-in monitoring.</em></p>
</h1>


**MicroForge** is a cloud-native microservices template designed to provide developers with a fully functional, scalable, and organized infrastructure foundation. It includes key components like monitoring, Terraform-based IaC, environment management, CI/CD, and essential microservices. The goal is to allow developers to focus on creating, updating, and extending services without the complexity of setting up the underlying infrastructure.
<p align="center">

❗ Version: **_initial/primitive_** (may contain minor issues).</p>

<h2 id="table-of-content" align="center">
📋Table Of Content
</h2>
<div align="center" style="font-size:17px;">
<ol>

1.[🔍Project Overview](#project-overview)

2.[🏗️Architecture](#architecture)

3.[📂Folder Structure](#folder-structure)

4.[🔄CI/CD Pipeline](#ci-cd-pipeline)

5.[📦Microservices](#microservices)

6.[🛰️Observability](#observability)

7.[📍Roadmap](#roadmap)

8.[⚡Quick Start](#quick-start)

9.[📝Notes](#notes)

</ol>
</div>

<h2 id="project-overview" align="center">🔍Project Overview</h2>

MicroForge provides a professional template with:

* **Infrastructure as Code**: Terraform manages PostgreSQL RDS, AWS Secrets Manager, and    Kubernetes resources.

* **Kubernetes Deployments**: Deployments, Services, Namespaces, ServiceAccounts, OIDC/IAM roles (IRSA).

* **CI/CD**: GitHub Actions workflows for automated testing, linting, building Docker images, and manual deployment to AWS.

* **Security**: Environment-specific secrets, AWS Secrets Manager integration, and secure password hashing.

* **Observability**: Prometheus metrics, Loki JSON logs, Grafana dashboards ready for use.

* **Microservices**: `auth_service` with full authentication flow, and `users-api` as a minimal, reusable scaffold service.

<h1 id="architecture" align="center">
🏗️Architecture
</h1>
<p align="center">
  <img src="\docs\diagrams\diagrams-svg-files\ProjectArchitecture.svg" width="600"/>
</p>

<h1 id="folder-structure" align="center">
📂Project Structure
</h1>

<h2 align="center">Project Overview</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\Project-Overview.svg" width="600"/>
</p>

<h2 align="center">Repository Workflows</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\repository-workflows.svg" width="600"/>
</p>

<h2 align="center">Auth_Service</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\auth-service.svg" width="600"/>
</p>

<h2 align="center">Monitoring</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\monitoring.svg" width="600"/>
</p>

<h2 align="center">Terraform</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\terraform.svg" width="600"/>
</p>

<h2 align="center">Template Service</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\demo-service.svg" width="600"/>
</p>

<h1 id= "ci-cd-pipeline" align = "center">
🔄CI/CD Pipeline
</h1>

<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\PipelineCI-CD.svg" width="600"/>
</p>

<h1 id="microservices" align = "center">
📦Microservices
</h1>

* **Auth Service** (`auth_service`)
Provides full authentication functionality including user registration, email verification, JWT-based login, and secure password handling.

* **Users API** (`users-api`)
Minimal, fully functional scaffold service that can be copied and extended. Demonstrates microservice structure, Kubernetes deployment, and basic endpoint (`/health`).

<h1 id="observability" align = "center">
🛰️Observability
</h1>

***Prometheus**: Metrics from FastAPI endpoints (`/metrics`) via `prometheus_fastapi_instrumentator`.

***Grafana**: Dashboards for latency, throughput, errors, ready to deploy via Helm.

***Loki**: JSON structured logs via Loguru for advanced querying.

<h2 align="center">RoadMap</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\roadmap.svg" width="600"/>
</p>

* **Prometheus**: Metrics from FastAPI endpoints (`/metrics`) via `prometheus_fastapi_instrumentator`.

* **Grafana**: Dashboards for latency, throughput, errors, ready to deploy via Helm.

* **Loki**: JSON structured logs via Loguru for advanced querying.

<h1 id="roadmap" align="center">
Roadmap📍
</h1>

<h2 align="center">RoadMap</h2>
<p align="center">
  <img src="docs\diagrams\diagrams-svg-files\roadmap.svg" width="600"/>
</p>


<h1 id="quick-start" align = "center">
⚡Quick Start
</h1>

```bash
git clone <repo_url>
cd MicroForge/auth_service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt

export POSTGRES_USER=authuser
export POSTGRES_PASSWORD=authpass
export POSTGRES_DB=authdb
export POSTGRES_HOST=localhost
export SECRET_KEY=dev_secret
export SENDER_EMAIL=<your_email>
export SENDER_PASSWORD=<your_email_password>
```

```python
uvicorn src.main:app --reload --port 8000
```

Test endpoints using cURL or Postman (/register, /verify-email, /token, /users/me).

<h2 id="notes" align = "center">
📝Notes
</h2>

***📌Version**: Initial, may contain minor issues. The focus is on providing a robust template for microservices, infrastructure, and observability, not a polished production-ready system yet.

*📌**MicroForge** is designed to be extensible, scalable, and professional, allowing developers to focus on creating new services without worrying about infrastructure complexity.