<h1 align ="center">

🐳 Users API — Minimal Dockerized Microservice Template

</h1>

A lightweight starter microservice intended to be copied and used as a base when creating new services.
Goal: provide a minimal, working **Docker image + Kubernetes manifests + basic test** so you can fork this repository and start a new microservice in minutes.

> Very small, focused template — keep logic inside `src/`, build an image, run locally or deploy to Kubernetes using the provided manifests.

<h2 align="center">

🗂️Template content:

</h2>

* `src/` — tiny FastAPI app with two endpoints:

    * `GET /users` → simple users list (example)

    * `GET /health` → health check

* `tests/` — one basic pytest test asserting `/health`

* `Dockerfile` — lightweight production image (Python slim + Uvicorn)

* `requirements.txt` — runtime + test deps

* `k8s/` — Kubernetes manifests (each YAML in its own file):

* `users-api-secrets.yaml` — Secret template (stringData placeholders)

* `deployment.yaml` — Deployment using image: `"${DOCKER_USER}/users-api:${IMAGE_TAG}"`

* `service.yaml` — NodePort service exposing the app on `nodePort: 30001`

<h2 align="center">

▶️Quick start — build & run locally

</h2>

Build the Docker image:

```bash
# from repo root
docker build -t youruser/users-api:dev .
```
Run it locally (map port 80 inside container to 8000 on host):

```bash
docker run --rm -e SECRET_KEY=devsecret -e DATABASE_URL="sqlite:///:memory:" -p 8000:80 youruser/users-api:dev
#http://localhost:8000/health
```
Run tests:

```bash
pip install -r requirements.txt
pytest -q
```
<h2 align="center">

🐳Docker image notes (important)

</h2>

* The image is based on `python:3.10-slim` and runs Uvicorn:

```dockerfile
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]
```

**Important:** Ensure your package layout matches this CMD. If your app is under `src/main.py` change the CMD to:

```text
["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]
```

* Use semantic tags for the image (avoid latest in production). Example:

```bash
docker tag youruser/users-api:dev youruser/users-api:v0.1.0
docker push youruser/users-api:v0.1.0
```
* Keep the image minimal and cache-friendly (install only runtime deps in `requirements.txt`).

<h2 align="center">

☁️Kubernetes manifests

</h2>

**Secret template** (users-api-secrets.yaml)

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: users-api-secrets
type: Opaque
stringData:
  DATABASE_URL: ""
  SECRET_KEY: ""
  DOCKER_USER: ""
  IMAGE_TAG: ""
```
* Intentionally empty — users fill values for their environment. Do not commit production secrets.

**Deployment** (`deployment.yaml`)

* Image: `image: "${DOCKER_USER}/users-api:${IMAGE_TAG}"`

* `imagePullPolicy: IfNotPresent` — prefer local images when available, pull otherwise.

* Environment variables injected via `envFrom: secretRef: name: users-api-secrets`.

* Provisions requests/limits (small defaults) to be a friendly starter config.

**Service** (`service.yaml`)

* `type: NodePort` with `nodePort: 30001` so the service is reachable externally on node IP:30001. Good for quick testing.

* In production, replace with `ClusterIP`+ Ingress or LoadBalancer.

<h2 align="center">

✨How to deploy on Kubernetes (example)

</h2>

1. Edit `k8s/users-api-secrets.yaml` and fill real values (or create secret via CLI):

```bash
kubectl create secret generic users-api-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/db" \
  --from-literal=SECRET_KEY="supersecret" \
  --from-literal=DOCKER_USER="youruser" \
  --from-literal=IMAGE_TAG="v0.1.0" \
  -n your-namespace
```
or edit the `stringData` values and apply:

```bash
kubectl apply -f k8s/users-api-secrets.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

2. Verify pods and service:

```bash
kubectl get pods -l app=users-api -n your-namespace
kubectl get svc users-api-service -n your-namespace
#http://<node-ip>:30001/health
```

<h2 align="center">

⚙️How to customize (copy & start a new microservice)

</h2>

1. Copy the repo or folder and rename `users-api` to your service name in:

    * `k8s/*.yaml` (namespace, labels, resource names)

    * `Dockerfile` and `image` name usage

2. Update `src/` with your service logic.

3. Update `requirements.txt` with only the packages your service needs.

4. Build/tag/push a new image and adjust `DOCKER_USER` / `IMAGE_TAG` in the Secret.

5. Apply the Kubernetes manifests (or adapt them to your desired infra).

<h2 align="center">

🔍Basic CI suggestion

</h2>

* Run `pytest` in CI.

* Build and tag the Docker image only on `main` or release tags (avoid pushing images on every feature branch).

* Use `--no-cache` builds sparingly to keep CI fast.

<h2 align="center">

🔒Security & best-practices

</h2>

* Never commit secrets. Use `kubectl create secret` or a CI secret store.

* Use image tags (e.g., `v0.1.0`) and avoid `latest` for reproducible deploys.

* Use `ClusterIP` + Ingress / LoadBalancer for production instead of `NodePort`.

* Set appropriate resource requests/limits and add readiness/liveness probes when adding real business logic.

* Consider vulnerability scanning for images (CI step).

<h2 align="center">

✅Summary:

</h2>

This microservice template is intentionally tiny and practical:

* **Purpose:** quick-start scaffold for new microservices (image + k8s manifests + test).

* **Focus:** ease-of-copy & modify; minimal opinionated infra.

* **Next steps:** replace `src/` with your logic, update manifests, build image, deploy.
