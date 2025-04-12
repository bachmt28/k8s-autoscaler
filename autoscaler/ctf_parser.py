# autoscaler/ctf_parser.py

"""
Module: ctf_parser
Chức năng:
- Parse và validate file .ctf
- Kiểm tra định dạng, giá trị hợp lệ
- Phân loại rule còn hạn và hết hạn
- Cung cấp các hàm kiểm tra rule có hiệu lực theo thời điểm
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime, date


@dataclass
class CTFRule:
    requester: str
    namespace: str
    workload: str
    replica: int
    days: List[str]    # Ex: ["Mon", "Tue"]
    hours: List[str]   # Ex: ["08-18"]
    expire: str        # Ex: "15/08/2025"
    purpose: str

    def expire_date(self) -> date:
        return datetime.strptime(self.expire.strip(), "%d/%m/%Y").date()

    def is_expired(self, today: Optional[date] = None) -> bool:
        if today is None:
            today = date.today()
        return self.expire_date() < today

    def matches(self, now: datetime) -> bool:
        """Check xem rule có hiệu lực tại thời điểm hiện tại"""
        now_day = now.strftime("%a")  # e.g. "Mon"
        now_hour = now.hour
        if now_day not in self.days:
            return False
        for h in self.hours:
            if self._hour_in_range(h, now_hour):
                return True
        return False

    def _hour_in_range(self, hour_range: str, current_hour: int) -> bool:
        try:
            clean = hour_range.replace("h", "")
            start_str, end_str = clean.split("-")
            start = int(start_str)
            end = int(end_str)
            return start <= current_hour < end
        except Exception:
            return False


def parse_ctf_file(file_path: str) -> List[CTFRule]:
    rules: List[CTFRule] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            parts = [p.strip() for p in line.split("|")]
            if len(parts) < 8:
                print(f"[CTF] ⚠️  Bỏ qua dòng {lineno}: thiếu trường ({len(parts)}/8)")
                continue

            try:
                rule = CTFRule(
                    requester=parts[0],
                    namespace=parts[1],
                    workload=parts[2],
                    replica=int(parts[3]),
                    days=_normalize_days(parts[4]),
                    hours=_normalize_hours(parts[5]),
                    expire=parts[6],
                    purpose=parts[7]
                )
                rules.append(rule)
            except Exception as e:
                print(f"[CTF] ❌ Lỗi dòng {lineno}: {e}")
    return rules


def _normalize_days(day_str: str) -> List[str]:
    """
    Convert: "Mon-Fri" -> ["Mon", "Tue", "Wed", "Thu", "Fri"]
             "Sat-Sun" -> ["Sat", "Sun"]
             "Mon,Wed,Fri" -> ["Mon", "Wed", "Fri"]
    """
    day_map = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    result = []
    if "-" in day_str:
        start, end = day_str.split("-")
        if start not in day_map or end not in day_map:
            return []
        start_idx = day_map.index(start)
        end_idx = day_map.index(end)
        if start_idx <= end_idx:
            result = day_map[start_idx:end_idx + 1]
        else:
            result = day_map[start_idx:] + day_map[:end_idx + 1]
    elif "," in day_str:
        result = [d for d in day_str.split(",") if d in day_map]
    else:
        result = [day_str] if day_str in day_map else []
    return result


def _normalize_hours(hour_str: str) -> List[str]:
    """
    Convert: "8h-18h" or "08h-17h" -> ["08-18"]
             "8-18" -> ["08-18"]
             "08h-12h,13h-18h" -> ["08-12", "13-18"]
    """
    result = []
    for h in hour_str.split(","):
        h = h.strip().replace("h", "")
        if "-" in h:
            parts = h.split("-")
            if len(parts) == 2:
                start = parts[0].zfill(2)
                end = parts[1].zfill(2)
                result.append(f"{start}-{end}")
    return result


def get_valid_rules(rules: List[CTFRule]) -> List[CTFRule]:
    return [r for r in rules if not r.is_expired()]


def get_expired_rules(rules: List[CTFRule]) -> List[CTFRule]:
    return [r for r in rules if r.is_expired()]
