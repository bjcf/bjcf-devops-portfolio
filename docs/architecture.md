# Architecture & design walkthrough

This document explains the *why* behind each part of the repository.

## 1. Application layer (`app/`)

A small [FastAPI](https://fastapi.tiangolo.com/) service. It exposes:

| Endpoint | Purpose |
|----------|---------|
| `GET /` | Service metadata |
| `GET /api/v1/hello` | Example business endpoint |
| `GET /health/live` | Liveness probe |
| `GET /health/ready` | Readiness probe |
| `GET /metrics` | Prometheus metrics (via `prometheus-fastapi-instrumentator`) |

Health endpoints are split (liveness vs readiness) because Kubernetes treats
them differently: a failed *liveness* check restarts the pod, while a failed
*readiness* check only removes it from the Service endpoints.

### Container image
Multi-stage build: dependencies are compiled in a `builder` stage and copied
into a minimal `python:3.12-slim` runtime. The runtime runs as an unprivileged
user (`uid 10001`) and ships a `HEALTHCHECK`. Combined with the Kubernetes
`securityContext`, the container runs non-root with a read-only root filesystem
and no Linux capabilities.

## 2. Delivery — CI/CD (`.github/workflows/`)

**`ci.yml`** runs on every push and PR as a quality gate:
1. `ruff` lint + `pytest`
2. Docker image build + [Trivy](https://github.com/aquasecurity/trivy) vulnerability scan
3. `helm lint` + `helm template`
4. `terraform fmt -check` + `terraform validate`

**`release.yml`** builds and pushes a multi-tagged image to GHCR on pushes to
`main` and on `v*` tags, using build cache and `docker/metadata-action` for
semver/sha tagging.

## 3. Runtime — Kubernetes (`deploy/`)

The Helm chart (`deploy/helm/api`) renders:
- **Deployment** with probes, resource requests/limits and hardened security context
- **Service** (ClusterIP)
- **Ingress** (optional, `nginx` class)
- **HorizontalPodAutoscaler** (CPU-based, 2→6 replicas)
- **ServiceMonitor** (optional; for kube-prometheus-stack)
- **ServiceAccount**

Raw manifests in `deploy/k8s/` provide a zero-dependency `kubectl apply` path
for local clusters (`kind`/`minikube`).

## 4. Platform — Infrastructure as Code (`infra/terraform/`)

Terraform provisions the cluster the app runs on, using the official
community modules:
- `terraform-aws-modules/vpc` — a 3-AZ VPC with public/private subnets and a
  single NAT gateway (cost-optimized for a demo). Subnets are tagged for the
  AWS Load Balancer Controller.
- `terraform-aws-modules/eks` — managed control plane + a managed node group in
  the private subnets.

Remote state (S3 + DynamoDB lock) is stubbed and ready to enable for team use.

## 5. Observability (`observability/`)

`docker-compose.yml` brings up the API together with Prometheus and Grafana.
Prometheus scrapes the app's `/metrics`; Grafana is auto-provisioned with the
Prometheus datasource and an "API Overview" dashboard (request rate, p95
latency, 5xx rate). In-cluster, the same signals are collected via the
`ServiceMonitor`.

## Possible next steps

- GitOps delivery with Argo CD / Flux
- Progressive delivery (canary) with Argo Rollouts
- Policy enforcement (OPA/Gatekeeper or Kyverno)
- SLO-based alerting rules and Alertmanager routing
