from fastapi import APIRouter, UploadFile, HTTPException
from kubernetes import client, config
from autoscaler.config import PROTECTED_NAMESPACES

import yaml

router = APIRouter()

def get_workloads_from_kubeconfig(kubeconfig_bytes: bytes):
    try:
        kube_dict = yaml.safe_load(kubeconfig_bytes)
        config.load_kube_config_from_dict(kube_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Lỗi kubeconfig: {e}")

    v1 = client.AppsV1Api()
    core = client.CoreV1Api()
    workloads = []

    namespaces = [ns.metadata.name for ns in core.list_namespace().items if ns.metadata.name not in PROTECTED_NAMESPACES]

    for ns in namespaces:
        try:
            for deploy in v1.list_namespaced_deployment(ns).items:
                workloads.append((ns, deploy.metadata.name))
            for sts in v1.list_namespaced_stateful_set(ns).items:
                workloads.append((ns, sts.metadata.name))
        except Exception:
            continue

    return workloads

@router.post("/upload-kubeconfig")
async def upload_kubeconfig(file: UploadFile):
    contents = await file.read()
    workloads = get_workloads_from_kubeconfig(contents)
    return {"total": len(workloads), "workloads": workloads}
