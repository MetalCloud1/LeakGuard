
<h1 align="center">🔐 Password Leak Checker Service</h1>

<p align="center">
Microservice for verifying if a password has appeared in known data breaches using <b>Have I Been Pwned</b> (HIBP) API.
</p>

---
<h1 align="center"> 
🚀 Overview 
</h1>

---

- Built with **FastAPI**.  
- Validates user identity via **Auth Service** (OAuth2).  
- Optionally checks password leaks via **HIBP API**.  
- Deployed inside **Kubernetes (`auth-dev` namespace)**.  
- Three pods communicate:
  1. `password-checker` (this service)
  2. `auth-service` (token verification)
  3. `postgres-0` (credentials & tokens storage)

<h1 align="center"> 
📡 Communication inside cluster:
</h1>

<p align="center">
  <img src="../docs/diagrams/diagrams-svg-files/process-flowchart.svg" width="900" alt="Project Architecture"/>
</p>

<h1 align="center"> 
 🚀  Build & Run
</h1>


<h2 align = "center">

📦 Docker:

</h2>


```bash
Build and run locally:

```bash
docker build -t password-checker:local .
docker run -d --name password-checker \
  -p 8000:8000 \
  -e AUTH_SERVICE_URL=http://localhost:8001 \
  -e USE_HIBP=true \
  password-checker:local
```
<h2 align = "center">
️☸ In Cluster with Kubernetes
</h2>

1. **Apply manifests**
Make sure you are connected to your Kubernetes cluster (e.g., Minikube, EKS, or other).  
Apply the manifests for each microservice and dependencies:

```bash
# Just with de namespace auth-dev: 
# kubectl apply -f auth_service/infra/k8s/dev/namespace-dev.yaml
kubectl apply -f auth_service/infra/k8s/dev-db/stattefulSet-db-dev.yaml
kubectl apply -f auth_service/infra/k8s/dev/deployment-dev.yaml
kubectl apply -f auth_service/infra/k8s/dev/service-dev.yaml
kubectl apply -f password_checker_service/infra/k8s/service.yaml
kubectl apply -f password_checker_service/infra/k8s/deployment.yaml
# Add other microservices here
```

2. **Check pods:**

```bash
kubectl get pods
```

3. **Port-forward services:**

Expose the pods locally using kubectl `port-forward`. Example:

```bash
# PostgreSQL
kubectl port-forward svc/postgres-0 5432:5432

# Auth Service
kubectl port-forward svc/<"podname"> 8000:8000

# Password Checker Service
kubectl port-forward svc/<"podname"> 8001:8000
```

4. **Access services:**

* Auth API: http://localhost:8000/docs

* Password Checker API: http://localhost:8001/docs

* Database: postgresql://testuser:testpass@localhost:5432/testdb

<h1 align="center"> 
☸️ Kubernetes Deployment
</h1>

---

1. Deployment manifest (infra/k8s/deployment.yaml):
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: password-checker-deployment
  namespace: auth-dev
spec:
  replicas: 1
  selector:
    matchLabels:
      app: password-checker
  template:
    metadata:
      labels:
        app: password-checker
    spec:
      containers:
        - name: password-checker-container
          image: gilbr/password-checker:latest
          ports:
            - containerPort: 8000
          env:
            - name: AUTH_SERVICE_URL
              value: "http://auth-service"
            - name: USE_HIBP
              value: "true"
```
2. Service manifest (infra/k8s/service.yaml)

```yaml
apiVersion: v1
kind: Service
metadata:
  name: password-checker
  namespace: auth-dev
spec:
  selector:
    app: password-checker
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

<h1 align="center">
🔑 Authentication Flow
</h1>

---

1. User requests token from auth-service.

2. password-checker receives password + token.

3. Token is validated with auth-service.

4. If valid, password is checked against HIBP API.

5. Response is returned:

```json
{
  "leaked": true,
  "times": 1000000
}
```
<h1 align = "center">
🧪 Example Usage
</h1>

---

1. **Get token from Auth Service:**
```bash
curl -X POST http://auth-service/token \
  -d "username=testuser&password=testpass"
```
Response:
```json
{ "access_token": "eyJhbGciOi..." }
```
2. **Call Password Checker:**

```bash

curl -X POST http://localhost:8000/check-password \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -H "Content-Type: application/json" \
  -d '{"password": "123456"}'

```
<h1 align = "center">
⚙️ Environment Variables
</h1>

---

| Variable           | Default               | Description                          |
| ------------------ | --------------------- | ------------------------------------ |
| `AUTH_SERVICE_URL` | `http://auth-service` | Auth service base URL inside cluster |
| `USE_HIBP`         | `true`                | Enable/disable HIBP check            |

<h1 align = "center">
🧑‍🔬 Testing
</h1>

---

Run unit tests with pytest:

```bash
pytest -v tests/
```

**Tests include:**

* Service health check

* Valid password leak detection (mocked HIBP)

* Invalid token rejection

* Local fallback when HIBP is disabled

<h1 align="center">
💡 Tips
</h1>

---

* Always test inside the dev namespace (auth-dev) before production.

* Ensure auth-service and postgres-0 are running before deploying.

* Monitor via logs (kubectl logs -f <pod> -n auth-dev).

* Never expose real secrets — use Kubernetes Secrets or .env.example.