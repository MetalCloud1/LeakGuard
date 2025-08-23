<h1 align="center">
 <b>CI/CD Pipeline - MicroForge🗡️</b>
</h1>

This workflow provides automated **Continuous Integration (CI) and Continuous Deployment (CD)** for the MicroForge template, covering the core microservices: `auth_service` and `users-api`. It is designed to ensure that any changes pushed to `dev` or pull requests targeting `main` or `dev` are automatically tested, linted, and optionally deployed to AWS with Docker images and Terraform-managed infrastructure.<br><br>

> 💡 **Note:** This workflow is modular and configurable. It can be extended to additional services or environments without breaking the existing pipeline.

<h2 id="table-of-content" align="center">
📋Table Of Content
</h2>
<div style="font-size:20px;">
<ol>

1. [Workflow Triggers](#workflow-triggers)

2. [Environment Variables](#environment-variables)

3. [CI Job](#ci-job)

4. [CD Job](#cd-job)

5. [Usage and Adaptation](#usage-and-adaptation)

</ol>
</div>

<h2 id="workflow-triggers" align="center">
▶️Workflow Triggers
</h2>

This workflow runs on:
* `push` events to the `dev` branch (CI)
* `pull_request` events targeting `dev` or `main` (CI)
* Manual triggers via `workflow_dispatch` (CD deployment)

> 💡 **Technical Note**: CI and CD are separated. CI runs automatically to validate code quality and test coverage. CD is manual to prevent automatic deployment to production without approval.

<h2 id="environment-variables" align="center">
🛠️Environment Variables
</h2>

```bash
env:
  AWS_REGION: us-west-2
```

* `AWS_REGION`: Default AWS region for deployments.


* Additional secrets are loaded during CD using GitHub Secrets:

  * `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

  * `DOCKER_USERNAME`, `DOCKER_PASSWORD`

* Database connection string and other service-specific configuration are injected via   environment variables for flexibility.

<h2 id="ci-job" align="center">
🧪CI Job
</h2>

**Purpose:** Test and validate code before merging to main branches.

**Key Steps:**

1. Checkout repository using `actions/checkout@v3`.

2. Setup Python 3.11 environment.

3. Install dependencies for all services.

4. Run linter (`flake8`) on all source code.

5. Launch temporary PostgreSQL container for tests.

6. Wait until PostgreSQL is ready.

7. Run unit tests with `pytest` and list test files for logging.

8. Build Docker images locally for all services (`auth_service` and `users-api`).


<h2 id="cd-job" align="center">
☁️CD Job
</h2>

**Purpose:** Deploy tested services to AWS and update Docker images in the registry. Triggered manually.

**Key Steps:**

1. Checkout repository.

2. Configure AWS credentials using `aws-actions/configure-aws-credentials@v2`.

3. Authenticate with Docker Hub (`docker/login-action@v2`).

4. Build and push Docker images for all services.

5. Navigate to Terraform configuration and run `terraform init` and `terraform apply`.

<h2 id="usage-and-adaptation" align="center">
🌍 Usage and Adaptation
</h2>

* Adding new microservices: Add them to the `services` array in both CI and CD steps. Ensure dependencies and test scripts exist.

* Switching databases or environments: Adjust `DATABASE_URL` or other service-specific environment variables.

* Secrets management: Always use GitHub Secrets for sensitive information. Avoid hardcoding credentials or keys in YAML.

* Image tagging: Replace `latest` with versioned tags for reproducible deployments.

## License

This project is licensed under **CC BY-NC-ND (custom)**.  
See [LICENSE.md](./LICENSE.md) for full details.

> ⚠️ Please respect the author's attribution and license when using this template.