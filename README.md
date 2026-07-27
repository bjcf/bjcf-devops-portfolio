# bjcf-devops-portfolio

> A compact but **end-to-end cloud-native delivery pipeline** — from a
> containerized service all the way to Infrastructure as Code, Kubernetes
> deployment, CI/CD and observability. The application is deliberately tiny;
> the point of this repo is to show *how software is built, shipped, run and
> observed* in a production-minded way.

[![CI](https://github.com/bjcf/bjcf-devops-portfolio/actions/workflows/ci.yml/badge.svg)](https://github.com/bjcf/bjcf-devops-portfolio/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-blue)
![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC)
![Kubernetes](https://img.shields.io/badge/deploy-Helm%2FK8s-326CE5)

## What this demonstrates

| Area | Tech | Where |
|------|------|-------|
| **App / containerization** | FastAPI, multi-stage Docker, non-root, healthcheck | [`app/`](app/) |
| **Kubernetes** | Helm chart (HPA, probes, ServiceMonitor, hardened securityContext) + raw manifests | [`deploy/`](deploy/) |
| **Infrastructure as Code** | Terraform → AWS VPC + EKS via official modules | [`infra/terraform/`](infra/terraform/) |
| **CI/CD** | GitHub Actions: lint, test, image build + Trivy scan, `helm lint`, `terraform validate`, GHCR release | [`.github/workflows/`](.github/workflows/) |
| **Observability** | Prometheus metrics + Grafana dashboard, provisioned via Docker Compose | [`observability/`](observability/) |

## Architecture

```
                                   ┌─────────────────────────────────────────┐
   git push / PR                   │           GitHub Actions (CI)           │
  ───────────────▶  repo  ───────▶ │  ruff · pytest · docker build + Trivy   │
                                   │  helm lint · terraform validate         │
                                   └───────────────┬─────────────────────────┘
                                                   │ on main / tag
                                                   ▼
                                        ghcr.io/bjcf/…  (container image)
                                                   │
                          terraform apply          │ helm upgrade --install
                     ┌───────────────────┐         ▼
                     │   AWS (Terraform) │   ┌──────────────────────────┐
                     │  VPC · 3 AZs      │   │  EKS cluster             │
                     │  EKS control plane│──▶│   Deployment (2..6 pods) │
                     │  managed nodes    │   │   Service · Ingress · HPA│
                     └───────────────────┘   │   /metrics ─▶ Prometheus │
                                             └──────────────────────────┘
                                                        │
                                                        ▼   Grafana dashboard
```

See [`docs/architecture.md`](docs/architecture.md) for the detailed walkthrough.

## Quickstart

### 1. Run the app locally
```bash
make install
make test          # unit tests
make run           # http://127.0.0.1:8000/docs
```

### 2. Full local stack (API + Prometheus + Grafana)
```bash
make compose-up
# API        http://localhost:8000/docs
# Prometheus http://localhost:9090
# Grafana    http://localhost:3000   (admin / admin) → "API Overview" dashboard
```

### 3. Deploy to Kubernetes
```bash
helm upgrade --install api deploy/helm/api \
  --set image.repository=ghcr.io/bjcf/bjcf-devops-portfolio \
  --set image.tag=0.1.0
kubectl port-forward svc/api-api 8080:80    # http://127.0.0.1:8080/docs
```

### 4. Provision the platform (AWS EKS)
```bash
cd infra/terraform
terraform init && terraform validate && terraform plan
# terraform apply  → creates real, billable AWS resources (see infra/terraform/README.md)
```

## Repository layout

```
.
├── app/                    FastAPI service, tests, multi-stage Dockerfile
├── deploy/
│   ├── helm/api/           Helm chart (deployment, service, ingress, hpa, servicemonitor)
│   └── k8s/                Raw manifests for quick kubectl demos
├── infra/terraform/        AWS VPC + EKS (Infrastructure as Code)
├── observability/          Prometheus config + Grafana provisioning & dashboard
├── .github/workflows/      CI (lint/test/scan/validate) and Release (GHCR)
├── docker-compose.yml      Local API + observability stack
└── Makefile                Common developer tasks
```

## Design choices worth noting

- **Security-first containers:** non-root user, read-only root filesystem, all
  Linux capabilities dropped, `seccomp: RuntimeDefault`, image vulnerability
  scanning in CI.
- **Production-shaped Kubernetes:** liveness/readiness probes, resource
  requests/limits, HorizontalPodAutoscaler, and a `ServiceMonitor` for the
  Prometheus Operator.
- **Reproducible infra:** Terraform pinned to official AWS modules with a remote
  state stub ready to enable.
- **Fast feedback:** every PR runs the full quality gate; nothing ships without
  passing lint, tests, chart rendering and Terraform validation.

## License

[MIT](LICENSE)
