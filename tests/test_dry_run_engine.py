# tests/test_dry_run_engine.py

from autoscaler.ctf_parser import parse_ctf_file, get_valid_rules
from autoscaler.dry_run_engine import generate_effective_rules, determine_workload_actions, print_dry_run_summary

print("🔍 Đang chạy dry-run test...")

rules = parse_ctf_file("conf/example.ctf")
valid_rules = get_valid_rules(rules)
effective = generate_effective_rules(valid_rules)

# Workload thực tế bao gồm workload có rule + workload không có rule
all_workloads = list({(r.namespace, r.workload) for r in rules}) + [("teamX", "unknown-wl")]

keep, scale_to_zero = determine_workload_actions(effective, all_workloads)
print_dry_run_summary(keep, scale_to_zero)
