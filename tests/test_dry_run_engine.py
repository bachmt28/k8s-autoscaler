# tests/test_dry_run_engine.py

from autoscaler.ctf_parser import parse_ctf_file, get_valid_rules
from autoscaler.dry_run_engine import (
    generate_effective_rules,
    determine_workload_actions,
    print_dry_run_summary,
)

if __name__ == "__main__":
    print("🔍 Đang chạy dry-run test...")

    # Bước 1: Load rule từ file
    rules = parse_ctf_file("conf/example.ctf")
    valid_rules = get_valid_rules(rules)

    # Bước 2: Tạo rule hiệu lực
    effective = generate_effective_rules(valid_rules)

    # Bước 3: Tập hợp toàn bộ workload từ file + 1 workload giả định không có rule
    all_workloads = list({(r.namespace, r.workload) for r in rules}) + [("teamX", "unknown-wl")]

    # Bước 4: Xác định action theo thời điểm hiện tại
    keep, scale_to_zero = determine_workload_actions(effective, all_workloads)

    # Bước 5: In kết quả ra terminal (và gửi Webex nếu cấu hình bật)
    print_dry_run_summary(keep, all_workloads)
