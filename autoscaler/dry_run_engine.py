# autoscaler/dry_run_engine.py

import datetime
from collections import defaultdict
from autoscaler.ctf_parser import CTFRule
from autoscaler.config import ENABLE_NOTIFY
from autoscaler.notifier import send_webex_message


def generate_effective_rules(valid_rules: list[CTFRule]) -> list[CTFRule]:
    grouped = defaultdict(list)
    for rule in valid_rules:
        key = (rule.namespace, rule.workload)
        grouped[key].append(rule)

    def score_rule(r: CTFRule):
        exp_date = r.expire_date()
        time_span_score = len(r.days) + len(r.hours)
        return (
            exp_date.year * 10000 + exp_date.month * 100 + exp_date.day,
            r.replica,
            time_span_score,
        )

    effective = []
    for group in grouped.values():
        group.sort(key=score_rule, reverse=True)
        effective.append(group[0])
    return effective


def determine_workload_actions(
    rules: list[CTFRule],
    all_workloads: list[tuple[str, str]],
    now: datetime.datetime | None = None,
) -> tuple[list[CTFRule], list[tuple[str, str]]]:
    if now is None:
        now = datetime.datetime.now()

    keep = []
    keep_map = {}

    for r in rules:
        if r.matches(now):
            keep.append(r)
            keep_map[(r.namespace, r.workload)] = r

    scale_to_zero = []
    for ns, wl in all_workloads:
        if (ns, wl) not in keep_map:
            scale_to_zero.append((ns, wl))

    return keep, scale_to_zero


def print_dry_run_summary(keep: list[CTFRule], scale_to_zero: list[tuple[str, str]]):
    print("📥 Tổng số rule được áp dụng:", len(keep))

    if keep:
        print("\n✅ Workload sẽ được KEEP:")
        for r in keep:
            print(f" • {r.namespace}/{r.workload} ({r.replica} replicas) — {r.days} {r.hours} đến {r.expire} — {r.purpose}")

    if scale_to_zero:
        print("\n🛑 Workload sẽ SCALE TO 0:")
        for ns, wl in scale_to_zero:
            print(f" • {ns}/{wl}")

    if ENABLE_NOTIFY:
        send_dry_run_webex(keep, scale_to_zero)


def send_dry_run_webex(keep: list[CTFRule], scale_to_zero: list[tuple[str, str]]):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    msg = f"**[Dry-Run Report] {now}**\n\n"

    if keep:
        msg += "✅ **Workload sẽ được KEEP:**\n"
        for r in keep:
            msg += f"• `{r.namespace}/{r.workload}` ({r.replica} replicas) — `{r.days} {r.hours}` đến `{r.expire}`\n  > *{r.purpose}*\n"

    if scale_to_zero:
        msg += "\n🛑 **Workload sẽ SCALE TO 0:**\n"
        for ns, wl in scale_to_zero:
            msg += f"• `{ns}/{wl}`\n"

    send_webex_message(msg)
