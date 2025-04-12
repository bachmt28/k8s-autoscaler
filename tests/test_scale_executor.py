# tests/test_scale_executor.py

import os
import sys
from datetime import datetime

# Thêm path để import được module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autoscaler.scale_executor import scale_workload

def mock_scale(namespace, workload, replicas, dry_run=True):
    print(f"[Mock] Scale: {namespace}/{workload} to {replicas} (dry_run={dry_run})")

# Thay thế hàm scale thật bằng mock trong test
def test_scale_executor():
    workloads = [
        ("team1", "svc-a", 1),
        ("team1", "svc-b", 2),
        ("team2", "svc-x", 0),
    ]

    print("🔧 Test scale_executor.py với dry-run:")
    for ns, wl, rep in workloads:
        mock_scale(ns, wl, rep, dry_run=True)

if __name__ == "__main__":
    test_scale_executor()
