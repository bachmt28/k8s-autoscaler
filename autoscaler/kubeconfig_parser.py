# autoscaler/kubeconfig_parser.py

"""
Module: kubeconfig_parser (v2.1)
Mục tiêu:
- Load kubeconfig để xác thực với Kubernetes API
- Dùng Kubernetes client truy vấn namespace & workload theo quyền user
- Trích xuất user từ file YAML kubeconfig
"""

from kubernetes import client, config
from kubernetes.client.rest import ApiException
import yaml


def load_kube_config(file_path: str = None):
    """
    Load kubeconfig từ file để authenticate API
    """
    config.load_kube_config(config_file=file_path)


def get_user_info_from_yaml(file_path: str) -> str:
    """
    Lấy tên user từ current-context trong kubeconfig YAML
    """
    with open(file_path, "r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    current_context = raw.get("current-context", "")
    for ctx in raw.get("contexts", []):
        if ctx["name"] == current_context:
            return ctx["context"].get("user", "unknown")
    return "unknown"


def list_namespaces() -> list:
    """
    Trả về danh sách namespace mà user có quyền truy cập
    """
    try:
        v1 = client.CoreV1Api()
        ns_list = v1.list_namespace()
        return [ns.metadata.name for ns in ns_list.items]
    except ApiException as e:
        print(f"❌ Không thể lấy namespace: {e}")
        return []


def list_workloads(namespace: str) -> dict:
    """
    Trả về workloads trong 1 namespace:
    - deployment
    - statefulset
    """
    apps_v1 = client.AppsV1Api()
    workloads = {
        "deployments": [],
        "statefulsets": []
    }

    try:
        deployments = apps_v1.list_namespaced_deployment(namespace)
        workloads["deployments"] = [d.metadata.name for d in deployments.items]
    except ApiException as e:
        print(f"⚠️ Không thể lấy deployment ở namespace '{namespace}': {e}")

    try:
        statefulsets = apps_v1.list_namespaced_stateful_set(namespace)
        workloads["statefulsets"] = [s.metadata.name for s in statefulsets.items]
    except ApiException as e:
        print(f"⚠️ Không thể lấy statefulset ở namespace '{namespace}': {e}")

    return workloads
