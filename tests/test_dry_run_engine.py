
# tests/test_dry_run_engine.py

import os
import sys
from datetime import datetime

# Đảm bảo import được module autoscaler
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autoscaler.ctf_parser import parse_ctf_file, get_valid_rules
from autoscaler.dry_run_engine import generate_effective_rules, determine_workload_actions, print_dry_run_summary

def test_dry_run_summary():
    rules = parse_ctf_file("conf/example.ctf")
    valid_rules = get_valid_rules(rules)
    effective_rules = generate_effective_rules(valid_rules)

    all_workloads = set((r.namespace, r.workload) for r in valid_rules)
    all_workloads.add(("teamX", "unknown-wl"))  # workload không có rule để test fallback

    now = datetime.strptime("2025-08-01 10:00", "%Y-%m-%d %H:%M")
    keep, scale_to_zero = determine_workload_actions(effective_rules, list(all_workloads), now)

    print_dry_run_summary(keep, list(all_workloads))

    # Kiểm tra số lượng
    assert isinstance(keep, list)
    assert isinstance(scale_to_zero, list)

    # Có ít nhất một workload bị scale về 0
    assert any(isinstance(i, tuple) and len(i) == 2 for i in scale_to_zero)
