<h1 align = "center">
🛰️Monitoring - Grafana/Loki/Prometheus (Monitorign/)
</h1>

This README explains how the monitoring stack in MicroForge is organized and how to deploy / customize it. It assumes you already run Kubernetes and (for Prometheus) the Prometheus Operator (kube-prometheus / prometheus-operator). The provided configuration uses Helm and includes a `values.yaml` fragment for Loki/Promtail (loki-stack style), plus RBAC/ServiceMonitor YAML snippets for Prometheus.

>**Goal**: lightweight, Kubernetes-native observability:
>* **Loki for log ingestion (Promtail → Loki)** <br>
>* **Grafana (Helm) for dashboards and as the Loki data source**<br>
>* **Prometheus (operator) scraping auth-service metrics via Service Monitor**

<h2 align = "center">

Files included / referenced

</h2>

* `values.yaml` — Loki/Promtail + Grafana values (you provided)

* `prometheus-rbac.yaml` — ClusterRole + ClusterRoleBinding for Prometheus scraping

* `service-monitor.yaml` — ServiceMonitor that tells Prometheus to scrape `auth-service` metrics

* Notes on required Service/Labels for `auth-service` (metrics port/path)


<h2 align = "center">

Deploying (recommended quick steps)

</h2>

1. **Add Grafana helm repo and update:**

```bash
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
```

2. **Install Loki stack (this chart can install Loki + Promtail + optional Grafana). Use your values.yaml (the fragment you supplied):**
```bash
#create monitoring namespace
kubectl create ns monitoring

#install or upgrade loki-stack (will install loki + promtail; also enables grafana if values set)
helm upgrade --install loki-stack grafana/loki-stack \
-n monitoring \
-f monitoring/values.yaml
```

> Your `values.yaml` enables `grafana` inside the stack (`grafana.enabled: true`).
> If you prefer to install Grafana separately (grafana/grafana chart), remove 
> `grafana.enabled` and install Grafana independently.

3. **Apply Prometheus RBAC and ServiceMonitor (Prometheus Operator must be installed and watching `monitoring` namespace):**

```bash
kubectl apply -f monitoring/prometheus-rbac.yaml
kubectl apply -f monitoring/service-monitor.yaml
```
<h2 align = "center">

What the provided `values.yaml`  does (summary)

</h2>

* **Grafana**

  * `enabled: true` → Helm will deploy Grafana with the stack.

  * `adminPassword: "admin"` → default admin password (replace with secret — see Security notes).

  * `sidecar.datasources.enabled: false` → the chart will not use the sidecar to auto-load datasource CRs; the values include a `datasources.yaml` that configures a Loki datasource pointing to `http://loki:3100`.

* **Promtail**

  * `enabled: true` → deploy Promtail.

  * `config.server` ports, `positions.filename` and `clients.url` point to Loki.

  * `scrape_configs` includes:

    * `job_name: auth-service` with `pipeline_stages.json` that extracts fields (level, request_id, client_ip, method, path, status_code) from JSON logs produced by your app.

    * `kubernetes_sd_configs` with `role: pod` and `relabel_configs` that keep pods labeled `app=auth-service` and add labels like `namespace`, `pod`, `container`.

    * A `kubernetes-pods` job that collects container logs from `/var/log/containers/*.log`(the chart normally mounts host paths for this).

This configuration expects application logs to be structured JSON (your `loguru` setup uses `serialize=True`) so Promtail can parse and index fields for Loki.

<h2 align = "center">

Prometheus RBAC & ServiceMonitor (summary)

</h2>

`prometheus-rbac.yaml` (ClusterRole + ClusterRoleBinding) grants Prometheus the required permissions to list/watch pods/services/endpoints and read ServiceMonitor resources in the cluster. The `roleRef` binds to the Prometheus service account `prometheus-kube-prometheus-prometheus` in the `monitoring` namespace (adjust if your operator uses a different account/namespace).

`service-monitor.yaml` configures a `ServiceMonitor` to scrape endpoints that match `app=auth-service` across `auth-dev` and `auth-prod` namespaces. It scrapes the `metrics` port at path `/metrics` every 20s.

> **Important:** `ServiceMonitor` resources are honored only if you run the Prometheus Operator / kube-prometheus stack.


<h2 align = "center">

How the pieces connect

</h2>

1. Auth Service exposes `/metrics` on port `metrics` (targetPort 8000 in the Service).

2. ServiceMonitor selects the `auth-service` Service and configures Prometheus to scrape `/metrics`.

3. Promtail runs as a DaemonSet (from the chart), watches pods, filters for `app=auth-service`, parses JSON logs and pushes to `Loki` at `/loki/api/v1/push`.

4. **Loki** stores logs; **Grafana** uses the configured Loki datasource to visualize logs and dashboards.

5. Prometheus scrapes metrics and stores time-series for Grafana dashboards/alerts.

<h2 align = "center">

Customization & recommendations

</h2>

<h3>

 **Grafana:**

</h3>

* Do not store `adminPassword` plaintext in `values.yaml` for production. Use a Kubernetes Secret and reference it, or supply via Helm `--set using` CI/CD secrets.

* Enable TLS and an ingress for Grafana; configure OAuth or a reverse-proxy for authentication in production.

* Use `sidecar.datasources.enabled: true` if you want to manage datasources via ConfigMaps/CRDs.

<h3>

 **Loki / Promtail:**
 
</h3>

* Keep logs structured JSON (you already do). This makes queries and labels powerful. Promtail pipeline_stages.json must match your log fields exactly (level, request_id, client_ip, method, path, status_code).

* Tune Loki retention, chunk sizes, and index settings for production. Loki defaults are not necessarily production-ready for large volumes.

* Ensure Promtail DaemonSet mounts host paths (`/var/log/containers`) — the chart usually does this automatically for container log collection.

<h3>

 **Prometheus:**
 
</h3>


* `ServiceMonitor.namespaceSelector.matchNames` is helpful to include only the namespaces you want; you already list `auth-dev` and `auth-prod`.

* If you have multiple Prometheus instances, ensure `release:` labels match the right Prometheus in your cluster.


<h2 align = "center">

Security & secrets

</h2>

* Replace `grafana.adminPassword` with a Kubernetes Secret. Example:

```bash
kubectl create secret generic grafana-admin --from-literal=admin-password='<strong-password>' -n monitoring
```

Then supply secret via Helm (chart-specific method) or patch the Deployment to read the secret. Avoid committing credentials to repo.

* Configure network policies if you want to restrict Promtail/Loki/Grafana access inside the cluster.

* Secure Grafana with OAuth or LDAP for production.
<h2 align = "center">

Troubleshooting

</h2>

* **Grafana not showing Loki datasource / empty logs**

  * `kubectl -n monitoring get pods` → check `promtail`, `loki`, `grafana` pod status.

  * `kubectl logs <promtail-pod>` → look for errors in pushing logs to Loki.

  * Test Loki endpoint: `kubectl port-forward svc/loki 3100:3100 -n monitoring` then curl `http://localhost:3100/ready`.

* **Prometheus not scraping targets**

  * Check ServiceMonitor existence: `kubectl get servicemonitor -n monitoring`.

  * In Prometheus UI → `Targets`, search for `auth-service`. If absent, make sure `prometheus-operator` watches ServiceMonitor resources in that namespace and that `release` label matches.

* **No JSON fields extracted**

  * Ensure your app emits JSON logs (you use `loguru` with `serialize=True`).

  * Confirm Promtail `pipeline_stages.json` expressions match field names exactly.

<h2 align = "center">
Scaling & production notes
</h2>

* **Promtail:** run as DaemonSet; scale depends on node count and log volume.

* **Loki:** consider HA mode or sharding if you expect high ingestion.

* **Grafana:** run with replicas behind an ingress and load balancer; enable persistence for dashboards.

* **Prometheus:** run with Thanos or Cortex for long-term storage & horizontal scaling if needed.

<h2 align = "center">
Example: Add another service to log scraping
</h2>

* To collect logs from another service (e.g., `users-api`), add a `scrape_config` in Promtail values similar to auth-service but matching `app: users-api`. Or label pods accordingly and reuse the `kubernetes-pods` job with proper relabel rules.

<h2 align ="center">
Final checklist before production
</h2>

* [ ] Move secrets out of plain `values.yaml` into Kubernetes Secrets.

 * [ ] Secure Grafana (TLS / auth).

 * [ ] Tune Loki retention, index and chunk settings.
 
 * [ ] Validate Prometheus target discovery in Prometheus UI.

 * [ ] Create Grafana dashboards and export them as JSON for repo-managed dashboards.