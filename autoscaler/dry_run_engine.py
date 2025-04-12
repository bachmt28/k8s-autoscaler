from datetime import datetime
from autoscaler.ctf_parser import CTFRule
from autoscaler.config import ENABLE_NOTIFY
from autoscaler.notifier import send_webex_message

def generate_effective_rules(rules: list[CTFRule]) -> list[CTFRule]:
    """
    Resolve conflict rules và chỉ giữ lại rule hiệu lực nhất cho mỗi workload.
    Ưu tiên rule có expire xa hơn, replica cao hơn, thời gian dài hơn.
    """
    grouped = {}
    for r in rules:
        key = (r.namespace, r.workload)
        if key not in grouped:
            grouped[key] = []
        grouped[key].append(r)

    def score_rule(r: CTFRule):
        exp_date = r.expire_date()
        return (
            exp_date.year * 10000 + exp_date.month * 100 + exp_date.day,
            r.replica,
            len(r.days.split("-")) + len(r.hours.split("-"))
        )

    result = []
    for rule_list in grouped.values():
        rule_list.sort(key=score_rule, reverse=True)
        result.append(rule_list[0])
    return result

def determine_workload_actions(
    effective_rules: list[CTFRule],
    all_workloads: list[str],
    current_time: datetime = None
):
    if current_time is None:
        current_time = datetime.now()

    keep = []
    keep_map = {}
    for r in effective_rules:
        if r.matches(current_time):
            key = f"{r.namespace}/{r.workload}"
            keep.append(r)
            keep_map[key] = r

    scale_to_zero = [w for w in all_workloads if w not in keep_map]
    return keep, scale_to_zero

def print_dry_run_summary(keep_rules: list[CTFRule], scale_to_zero: list[str]):
    print("📥 Tổng số rule được áp dụng:", len(keep_rules))
    print()

    if keep_rules:
        print("✅ Workload sẽ được KEEP:")
        for r in keep_rules:
            print(f" • {r.namespace}/{r.workload} ({r.replica} replicas) — {r.days} {r.hours} đến {r.expire} — {r.purpose}")
        print()

    if scale_to_zero:
        print("🛑 Workload sẽ SCALE TO 0:")
        for w in scale_to_zero:
            print(f" • {w}")
        print()

    # Gửi Webex nếu bật
    if ENABLE_NOTIFY:
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        message = f"**[Dry-Run Report] {now}**\n\n"

        if keep_rules:
            message += "✅ **Workload sẽ được KEEP:**\n"
            for r in keep_rules:
                message += f"• `{r.namespace}/{r.workload}` ({r.replica} replicas) — {r.days} {r.hours} đến {r.expire} — {r.purpose}\n"
            message += "\n"

        if scale_to_zero:
            message += "🛑 **Workload sẽ SCALE TO 0:**\n"
            for w in scale_to_zero:
                message += f"• `{w}`\n"

        send_webex_message(message)
