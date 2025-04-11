# tests/test_kubeconfig_parser.py

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autoscaler.kubeconfig_parser import (
    load_kube_config, get_user_info_from_yaml,
    list_namespaces, list_workloads
)

if __name__ == "__main__":
    kubeconfig_path = "conf/example.kubeconfig"

    # Load cấu hình kubeconfig
    load_kube_config(kubeconfig_path)

    # In thông tin người dùng từ YAML
    print("👤 Current user:", get_user_info_from_yaml(kubeconfig_path))

    # Lấy danh sách namespace
    print("📦 Available namespaces:")
    for ns in list_namespaces():
        print(f" - {ns}")

    # Test query workload từ namespace mặc định
    print("\n📌 Workload trong namespace 'default':")
    workloads = list_workloads("default")
    print("  Deployments:", workloads["deployments"])
    print("  StatefulSets:", workloads["statefulsets"])
