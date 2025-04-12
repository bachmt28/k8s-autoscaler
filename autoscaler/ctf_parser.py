# autoscaler/ctf_parser.py

import datetime
from typing import List
from dataclasses import dataclass

WEEKDAY_MAP = {
    "Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6
}

@dataclass
class CTFRule:
    requester: str
    namespace: str
    workload: str
    replica: int
    days: str
    hours: str
    expire: str
    purpose: str

    def expire_date(self) -> datetime.date:
        return datetime.datetime.strptime(self.expire.strip(), "%d/%m/%Y").date()

    def is_expired(self, today=None) -> bool:
        if today is None:
            today = datetime.date.today()
        return self.expire_date() < today

    def matches(self, check_time: datetime.datetime) -> bool:
        weekday = check_time.weekday()
        hour = check_time.hour

        valid_days = [WEEKDAY_MAP[d] for d in self.days.strip().split("-") if d in WEEKDAY_MAP]
        valid_hours = [tuple(map(int, self.hours.strip().replace("h", "").split("-")))]

        return (
            weekday in valid_days and
            any(start <= hour < end for start, end in valid_hours) and
            not self.is_expired(check_time.date())
        )


def parse_ctf_file(file_path: str) -> List[CTFRule]:
    rules = []
    with open(file_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = [p.strip() for p in line.split("|")]
            if len(parts) != 8:
                print(f"[CTF] ⚠️ Bỏ qua dòng {lineno}, không đủ trường")
                continue
            try:
                rules.append(CTFRule(*parts))
            except Exception as e:
                print(f"[CTF] ❌ Lỗi dòng {lineno}: {e}")
    return rules

def get_valid_rules(rules: List[CTFRule]) -> List[CTFRule]:
    return [r for r in rules if not r.is_expired()]
