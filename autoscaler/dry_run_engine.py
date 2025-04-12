# autoscaler/dry_run_engine.py

from collections import defaultdict
from datetime import datetime
from autoscaler.config import ENABLE_NOTIFY
from autoscaler.notifier import send_webex_message

def generate_effective_rules(valid_rules):
    grouped = defaultdict(list)
    for r in valid_rules:
        grouped[(r.namespace, r.workload)].append(r)

    def score(r):
        return (
            r.expire_date().toordinal(),
            r.replica,
            len(r.days) + len(r.hours)
        )

    effective = []
    for rule_list in grouped.values():
        rule_list.sort(key=score, reverse=True)
        effective.append(rule_list[0])
    return effective

def determine_workload_actions(effective_rules, all_workloads, check_time=None):
    if check_time is None:
        check_time = datetime.now()

    keep_rules = []
    keep_map = {}
    for r in effective_rules:
        if r.matches(check_time):
            key = (r.namespace, r.workload)
            keep_map[key] = r
            keep_rules.append(r)

    scale_to_zero = [wl for wl in all_workloads if wl not in keep_map]
    return keep_rules, scale_to_zero

def print_dry_run_summary(keep, scale_down):
    print(f"📥 Tổng số rule được áp dụng: {len(keep)}\n")
    if keep:
        print("✅ Workload sẽ được KEEP:")
        for r in keep:
            print(f" • {r.namespace}/{r.workload} ({r.replica} replicas) — {r.days} {r.hours} đến {r.expire} — {r.purpose}")
        print()
    if scale_down:
        print("🛑 Workload sẽ SCALE TO 0:")
        for ns, wl in scale_down:
            print(f" • {ns}/{wl}")
    if ENABLE_NOTIFY:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"**[Dry-Run Report] {now}**\n\n"
        if keep:
            msg += "✅ **KEEP:**\n"
            for r in keep:
                msg += f"• `{r.namespace}/{r.workload}` ({r.replica}) — `{r.days} {r.hours}` đến `{r.expire}`\n"
        if scale_down:
            msg += "\n🛑 **SCALE TO 0:**\n"
            for ns, wl in scale_down:
                msg += f"• `{ns}/{wl}`\n"
        send_webex_message(msg)
