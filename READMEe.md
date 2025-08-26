<div id="leakguard" align="center">
  <h1>🛡️ LeakGuard 🔐</h1>
  <p><em>Quickly detect if your information (passwords, emails, etc.) has been compromised before it's too late.</em></p>

  <p style="display:flex; justify-content:center; gap:10px; flex-wrap:wrap;">
    <a href="https://github.com/MetalCloud1/leakguard/actions/workflows/tests.yaml">
      <img src="https://github.com/MetalCloud1/leakguard/actions/workflows/tests.yaml/badge.svg" alt="Tests">
    </a>
    <img src="https://img.shields.io/badge/python-3.11+-blue" alt="Python">
    <img src="https://img.shields.io/badge/docker-ready-blue" alt="Docker">
    <img src="https://img.shields.io/badge/status-demo-orange" alt="Demo">
    <img src="https://img.shields.io/badge/template--based--on-MicroForge-green" alt="Template">
  </p>

  <p><strong>Version 1.0 — demo release</strong><br>❗ Local demo: ready for testing. No production deployment by default.</p>
</div>

<hr/>

<h2>🔍 Project Overview</h2>
<p>
LeakGuard is a collection of microservices focused on <strong>early leak detection</strong>. Users can check if passwords or sensitive data appear in leaked datasets and receive timely alerts. This demo is built using a <strong>custom template</strong> (MicroForge) to accelerate development and integration.
</p>

<ul>
  <li><strong>Password Checker Service</strong> (<code>password_checker_service</code>): FastAPI app that checks a local JSON dataset of leaked passwords and returns whether a password has been found and how many times.</li>
  <li><strong>Auth Service</strong> (<code>auth_service</code>): full user management, registration, email verification, JWT login, protected endpoints, rate-limiting.</li>
  <li><strong>PostgreSQL</strong>: Docker container for user persistence (used by <code>auth_service</code>).</li>
  <li><strong>Monitoring</strong>: Prometheus + Loki + Grafana instrumented for metrics, logs, and dashboards.</li>
  <li><strong>Testing & CI</strong>: unit & integration tests with <code>pytest</code>, extensive mocking to validate behavior without external services.</li>
</ul>

<hr/>

<h2>🏗️ Architecture (placeholder)</h2>
<p>Insert architecture diagrams here.<br><em>[Architecture diagram placeholder]</em></p>

<hr/>

<h2>📂 Repository Structure</h2>
<pre>
leakguard/
├─ auth_service/
│  ├─ src/                # auth service code
│  ├─ requirements.txt
├─ password_checker_service/
│  ├─ src_pcs/            # app.py, checker logic, leaked JSON reference
│  ├─ requirements.txt
├─ infra/
│  ├─ json/
│     └─ leaked_passwords.json
├─ docker/
│  └─ docker-compose.demo.yml
├─ tests/
│  ├─ test_auth.py
│  └─ test_password_checker.py
└─ .github/
   └─ workflows/
      └─ tests.yaml       # CI workflow (tests, lint)
</pre>

<hr/>

<h2>⚡ Quick Start (local / demo)</h2>
<h3>Requirements</h3>
<ul>
  <li>Docker & Docker Compose (recommended for demo)</li>
  <li>Python 3.11+</li>
  <li>(Optional) <code>uvicorn</code> to run services individually</li>
</ul>

<h3>Start with Docker Compose</h3>
<pre>
git clone https://github.com/MetalCloud1/leakguard.git
cd leakguard
docker-compose -f docker/docker-compose.demo.yml up --build -d
</pre>
<p>This will start: Postgres (optional), auth_service, password_checker_service, Prometheus, Loki, and Grafana in demo mode.</p>

<h3>Run a single service locally</h3>
<pre>
cd password_checker_service
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt -r requirements-test.txt
uvicorn src_pcs.app:app --reload --port 8001
</pre>
<p>Endpoints available:</p>
<ul>
  <li><code>http://localhost:8001/health</code></li>
  <li><code>POST http://localhost:8001/check-password</code></li>
</ul>

<hr/>

<h2>🧪 Tests & Professional Mocking</h2>
<p>
Uses <code>pytest</code> and <code>unittest.mock</code> to simulate external dependencies (e.g., auth_service validation, email sending). Tests are <strong>deterministic and fast</strong>.
</p>

```bash

# Run all tests

pytest -q

# Coverage

pytest --cov=src --cov-report=term-missing

# Lint / static analysis

ruff check .
black --check .
mypy src
```

<p><em>Professional note:</em> Tests demonstrate advanced mocking skills to verify authentication, timeouts, and service responses without external resources.</p>

<hr/>

<h2>🛰️ Observability & Monitoring</h2>
<ul>
  <li><strong>Prometheus:</strong> instrumented FastAPI metrics (latency, counters, errors).</li>
  <li><strong>Loki:</strong> structured JSON logs for advanced querying.</li>
  <li><strong>Grafana:</strong> preconfigured dashboards for latency, throughput, and errors.</li>
</ul>

<hr/>

<h2>📍 Roadmap</h2>
<ul>
  <li><strong>Short term:</strong> Improve detection, expand datasets, increase test coverage.</li>
  <li><strong>Medium term:</strong> Gmail notification system: check user data every <strong>6 hours</strong> and alert if compromised.</li>
  <li><strong>Long term (with user consent):</strong> Optional automatic non-critical actions to protect sensitive information, demo deployment on Kubernetes.</li>
</ul>

<hr/>

<h2>⚙️ Security & Data Notes</h2>
<ul>
  <li>Demo uses a local JSON dataset (<code>infra/json/leaked_passwords.json</code>) for reproducible testing.</li>
  <li>Do not store real credentials in the repo; use <code>.env</code> or GitHub Secrets for CI/deployment.</li>
  <li>Real-account actions require explicit consent and strict security measures.</li>
</ul>

<hr/>

<h2>🤝 Contribution & License</h2>
<p>
Based on <strong>MicroForge</strong> template by Gilbert Ramírez (GitHub: <code>MetalCloud1</code>).  
Contribution guidelines:
</p>
<ul>
  <li>Open an issue describing the change.</li>
  <li>Send a PR to <code>dev</code> branch.</li>
  <li>Maintain proper attribution when using the original template.</li>
</ul>
<p><strong>License:</strong> CC BY-NC-ND (see <code>LICENSE.md</code>).</p>

<hr/>

<h2>📝 Final Notes</h2>
<ul>
  <li>Custom template + integration: this demo was developed and tested in a few hours thanks to the MicroForge template, highlighting how a well-designed template accelerates real development.</li>
  <li>Repo is focused on local demos and testing; production deployment pipeline is disabled by default.</li>
</ul>
