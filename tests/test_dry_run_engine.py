# tests/test_dry_run_engine.py

import os
import sys
from datetime import datetime

# Thêm path để import được module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from autoscaler.ctf_parser import parse_ctf_file, get_valid_rules
from autoscaler.dry_run_engine import generate_effective_rules, determine_workload_actions

if __name__ == "__main__":
    # Bước 1: Load rule từ file .ctf
    rules = parse_ctf_file("conf/example.ctf")
    valid_rules = get_valid_rules(rules)

    print(f"📥 Số rule hợp lệ: {len(valid_rules)}")

    # Bước 2: Generate rule hiệu lực (sau khi resolve conflict)
    effective = generate_effective_rules(valid_rules)
    print(f"✅ Rule hiệu lực sau xử lý conflict: {len(effective)}")

    # Bước 3: Giả lập danh sách workload thực tế toàn cluster
    all_workloads = list(effective.keys()) + ["teamX/unknown-wl"]  # thêm 1 workload không có rule

    # Bước 4: Dry-run tại thời điểm hiện tại
    now = datetime.now()
    keep, scale_down = determine_workload_actions(effective, all_workloads, now)

    print("\n📌 KEEP các workload (theo rule tại thời điểm này):")
    for r in keep:
        print(f" - {r.namespace}/{r.workload} ({r.replica} replicas)")

    print("\n🛑 SCALE TO 0 các workload không match:")
    for w in scale_down:
        print(f" - {w}")
