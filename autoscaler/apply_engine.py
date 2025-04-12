import os
from autoscaler.config import ENABLE_NOTIFY, PROTECTED_NAMESPACES
from autoscaler.ctf_parser import parse_ctf_file, get_valid_rules
from autoscaler.dry_run_engine import generate_effective_rules, determine_workload_actions
from autoscaler.scale_executor import scale_workload
from autoscaler.notifier import send_webex_message


def run_apply_engine(ctf_path: str, dry_run: bool = False):
    print("🚀 Đang chạy apply engine...")

    rules = parse_ctf_file(ctf_path)
    valid_rules = get_valid_rules(rules)
    effective = generate_effective_rules(valid_rules)

    all_workloads = [(r.namespace, r.workload) for r in effective]
    keep, scale_to_zero = determine_workload_actions(effective, all_workloads)

    # Lọc các workload thuộc namespace được bảo vệ
    keep = [r for r in keep if r.namespace not in PROTECTED_NAMESPACES]
    scale_to_zero = [wl for wl in scale_to_zero if wl[0] not in PROTECTED_NAMESPACES]

    for r in keep:
        scale_workload(r.namespace, r.workload, r.replica, dry_run=dry_run)

    for ns, wl in scale_to_zero:
        scale_workload(ns, wl, 0, dry_run=dry_run)

    if ENABLE_NOTIFY:
        msg = "**[Apply Result]**\n"
        if keep:
            msg += "✅ **Workload được giữ nguyên:**\n"
            for r in keep:
                msg += f"• `{r.namespace}/{r.workload}` → {r.replica}\n"
        if scale_to_zero:
            msg += "\n🛑 **Workload scale về 0:**\n"
            for ns, wl in scale_to_zero:
                msg += f"• `{ns}/{wl}`\n"
        send_webex_message(msg)
