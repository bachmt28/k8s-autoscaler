# Scale execution module
import os
from typing import List, Tuple
from kubernetes import client, config
from autoscaler.ctf_parser import CTFRule
from autoscaler.config import ENABLE_NOTIFY, PROTECTED_NAMESPACES
from autoscaler.notifier import send_webex_message


def load_kube_config():
    if os.getenv("KUBERNETES_SERVICE_HOST"):
        config.load_incluster_config()
    else:
        config.load_kube_config()


def scale_workload(namespace: str, workload: str, target_replicas: int, dry_run: bool = True) -> str:
    api = client.AppsV1Api()
    try:
        dep = api.read_namespaced_deployment(workload, namespace)
        current = dep.spec.replicas
        if dry_run:
            return f"🌀 [DRY-RUN] Scale Deployment {namespace}/{workload} from {current} → {target_replicas}"
        else:
            dep.spec.replicas = target_replicas
            api.patch_namespaced_deployment(workload, namespace, dep)
            return f"✅ Scaled Deployment {namespace}/{workload} from {current} → {target_replicas}"
    except client.exceptions.ApiException:
        try:
            sts = api.read_namespaced_stateful_set(workload, namespace)
            current = sts.spec.replicas
            if dry_run:
                return f"🌀 [DRY-RUN] Scale StatefulSet {namespace}/{workload} from {current} → {target_replicas}"
            else:
                sts.spec.replicas = target_replicas
                api.patch_namespaced_stateful_set(workload, namespace, sts)
                return f"✅ Scaled StatefulSet {namespace}/{workload} from {current} → {target_replicas}"
        except client.exceptions.ApiException:
            return f"❌ Không tìm thấy workload {namespace}/{workload}"


def execute_scaling(keep_rules: List[CTFRule], scale_to_zero: List[Tuple[str, str]], dry_run: bool = True):
    load_kube_config()
    logs = []

    # ✅ Rule KEEP
    for rule in keep_rules:
        msg = scale_workload(rule.namespace, rule.workload, rule.replica, dry_run)
        logs.append(msg)

    # 🛑 SCALE TO 0 (nếu không nằm trong protected)
    for ns, wl in scale_to_zero:
        if ns in PROTECTED_NAMESPACES:
            logs.append(f"🚫 BỎ QUA {ns}/{wl} (namespace được bảo vệ)")
            continue
        msg = scale_workload(ns, wl, 0, dry_run)
        logs.append(msg)

    report = "\n".join(logs)
    print(report)

    if ENABLE_NOTIFY:
        send_webex_message(f"**[ScaleExecutor Report]**\n\n```\n{report}\n```")
