# Raw Kubernetes manifests

These plain manifests are a lightweight alternative to the [Helm chart](../helm/api)
for quick `kubectl apply -f` demos (e.g. against a local `kind`/`minikube`
cluster). For anything beyond a demo, prefer the Helm chart — it is templated,
values-driven and produces the same resources plus HPA/ServiceMonitor.

```bash
kubectl apply -f deploy/k8s/
kubectl port-forward svc/api 8080:80
```
