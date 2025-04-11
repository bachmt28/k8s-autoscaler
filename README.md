# 🚀 K8s Autoscaler Project

This project helps automatically scale workloads on Kubernetes based on working hours and exceptions declared through Web UI.

## Modules

- `autoscaler/ctf_parser.py` – Load and validate Compact Table Format input
- `api/` – FastAPI backend for UI interaction
- `cronjob/` – Scheduled scripts to scale workloads
