# autoscaler/dry_run_engine.py

from collections import defaultdict
from datetime import datetime
from typing import List, Tuple
from autoscaler.config import ENABLE_NOTIFY, PROTECTED_NAMESPACES
from autoscaler.notifier import send_webex_message
from autoscaler.ctf_parser import CTFRule


def generate_effective_rules(valid_rules: List[CTFRule]) -> List[CTFRule]:
    grouped = defaultdict(list)
    for r in valid_rules:
        key = (r.namespace, r.workload)
        grouped[key].append(r)

    def score_rule(r: CTFRule):
        exp_date = r.expire_date()
        exp_score = (
            exp_date.year * 10000 + exp_date.month * 100 + exp_date.day
            if exp_date else 0
        )
        return (
            exp_score,              # Ưu tiên rule có expire xa hơn
            r.replica,              # Ưu tiên replica lớn hơn
            len(r.days) + len(r.hours)  # Ưu tiên khung thời gian dài hơn
        )

    effective_rules = []
    for rule_list in grouped.values():
        rule_list.sort(key=score_rule, reverse=True)
        best = rule_list[0]
        effective_rules.append(best)

    return effective_rules


def determine_workload_actions(
    effective_rules: List[CTFRule],
    all_workloads: List[str],
    now: datetime = None
) -> Tuple[List[CTFRule], List[str], List[str]]:
    if now is None:
        now = datetime.now()

    keep = []
    scale_to_zero = []
    skipped = []

    now_day = now.strftime("%a")  # Mon, Tue, ...
    now_hour = now.hour

    keep_map = {}

    for rule in effective_rules:
        workload_key = f"{rule.namespace}/{rule.workload}"
        if rule.namespace in PROTECTED_NAMESPACES:
            skipped.append(workload_key)
            continue

        if now_day in rule.days:
            hour_range = rule.hours.replace("h", "").split("-")
            try:
                h_start = int(hour_range[0])
                h_end = int(hour_range[1])
                if h_start <= now_hour < h_end:
                    keep.append(rule)
                    keep_map[workload_key] = rule
            except:
                continue

    for w in all_workloads:
        if w in keep_map:
            continue
        ns = w.split("/")[0]
        if ns in PROTECTED_NAMESPACES:
            skipped.append(w)
        else:
            scale_to_zero.append(w)

    return keep, scale_to_zero, skipped


def print_dry_run_summary(
    keep_rules: List[CTFRule],
    scale_to_zero: List[str],
    skipped: List[str]
):
    print(f"\n📌 KEEP các workload (theo rule tại thời điểm này):")
    for r in keep_rules:
        print(f" • {r.namespace}/{r.workload} ({r.replica} replicas) — {r.days} {r.hours} đến {r.expire} — {r.purpose}")

    print(f"\n🛑 SCALE TO 0 các workload không match:")
    for w in scale_to_zero:
        print(f" • {w}")

    if skipped:
        print(f"\n❗ SKIPPED (Protected Namespaces):")
        for w in skipped:
            print(f" • {w}")

    # Gửi Webex nếu bật
    if ENABLE_NOTIFY:
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        msg = f"**[Dry-Run Report] {now_str}**\n\n"

        if keep_rules:
            msg += "✅ **KEEP:**\n"
            for r in keep_rules:
                msg += f"• `{r.namespace}/{r.workload}` ({r.replica} replicas) — `{r.days} {r.hours}` đến `{r.expire}`\n> _{r.purpose}_\n"
        if scale_to_zero:
            msg += "\n🛑 **SCALE TO 0:**\n"
            for w in scale_to_zero:
                msg += f"• `{w}`\n"
        if skipped:
            msg += "\n❗ **SKIPPED (Protected Namespaces):**\n"
            for w in skipped:
                msg += f"• `{w}`\n"

        send_webex_message(msg)
