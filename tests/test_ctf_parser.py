# tests/test_ctf_parser.py

from autoscaler.ctf_parser import parse_ctf_file, get_valid_rules, get_expired_rules

if __name__ == "__main__":
    rules = parse_ctf_file("conf/example.ctf")

    print("📄 Tổng số rule trong file:", len(rules))
    print()

    print("🟢 Rule còn hạn:")
    for r in get_valid_rules(rules):
        print(f"  - {r.namespace}/{r.workload} ({r.replica} replicas) [{r.days} {r.hours}] đến {r.expire}")

    print("\n🔴 Rule đã hết hạn:")
    for r in get_expired_rules(rules):
        print(f"  - {r.namespace}/{r.workload} hết hạn {r.expire}")
