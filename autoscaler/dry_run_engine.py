# autoscaler/dry_run_engine.py

"""
Module: dry_run_engine
Chức năng:
- Nhận danh sách rule CTF (sau khi parse & validate)
- Áp dụng logic conflict: giữ rule mạnh nhất nếu bị trùng
- Trả ra danh sách workload cần KEEP hoặc SCALE TO 0 tại thời điểm hiện tại
"""

from collections import defaultdict
from datetime import datetime
from typing import List, Tuple, Dict
from autoscaler.ctf_parser import CTFRule


from datetime import datetime

def score_rule(rule: CTFRule) -> Tuple[int, int, int]:
    """Tính điểm cho rule để so sánh ưu tiên"""
    days_count = len(rule.days.split("-")) if "-" in rule.days else 1
    hours_range = rule.hours.replace("h", "").split("-")
    hours_span = int(hours_range[1]) - int(hours_range[0]) if len(hours_range) == 2 else 0

    # Ép expire về datetime nếu cần
    if isinstance(rule.expire, str):
        try:
            rule.expire = datetime.strptime(rule.expire.strip(), "%d/%m/%Y").date()
        except Exception:
            rule.expire = datetime(1970, 1, 1).date()

    return (
        rule.expire.year * 10000 + rule.expire.month * 100 + rule.expire.day,
        rule.replica,
        days_count * hours_span
    )



def generate_effective_rules(rules: List[CTFRule]) -> Dict[str, CTFRule]:
    """Tìm rule mạnh nhất cho mỗi namespace/workload"""
    grouped: Dict[str, List[CTFRule]] = defaultdict(list)

    for rule in rules:
        key = f"{rule.namespace}/{rule.workload}"
        grouped[key].append(rule)

    effective = {}

    for key, rule_list in grouped.items():
        rule_list.sort(key=score_rule, reverse=True)
        best_rule = rule_list[0]
        effective[key] = best_rule

    return effective


def determine_workload_actions(
    effective_rules: Dict[str, CTFRule],
    all_workloads: List[str],
    now: datetime,
    fallback_in_office_hour: bool = True,
    default_replica: int = 1,
) -> Tuple[List[CTFRule], List[Tuple[str, int]]]:
    """
    Trả ra danh sách workload cần KEEP (theo rule hoặc fallback giờ hành chính)
    và danh sách workload cần SCALE TO 0 (không có rule và ngoài giờ)
    """
    keep = []
    scale_down = []

    current_day = now.strftime("%a")  # Mon, Tue,...
    current_hour = now.hour

    # Tìm rule match giờ/ngày
    keep_keys = set()
    for key, rule in effective_rules.items():
        if current_day not in rule.days:
            continue
        hour_range = rule.hours.replace("h", "").split("-")
        if len(hour_range) != 2:
            continue
        start, end = int(hour_range[0]), int(hour_range[1])
        if start <= current_hour <= end:
            keep.append(rule)
            keep_keys.add(key)

    # Với workload không có rule → kiểm tra fallback giờ hành chính
    for w in all_workloads:
        if w in keep_keys:
            continue

        if fallback_in_office_hour:
            day_office = ["Mon", "Tue", "Wed", "Thu", "Fri"]
            if current_day in day_office and 8 <= current_hour <= 18:
                # Giữ lại với replica mặc định
                namespace, workload = w.split("/")
                keep.append(CTFRule(
                    requester="fallback",
                    namespace=namespace,
                    workload=workload,
                    replica=default_replica,
                    days=current_day,
                    hours=f"{current_hour}h-{current_hour+1}h",
                    expire=now.date(),
                    purpose="Default during office hours"
                ))
                continue

        scale_down.append((w, 0))

    return keep, scale_down
