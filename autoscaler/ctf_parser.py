# autoscaler/ctf_parser.py

"""
Module: ctf_parser
Chức năng:
- Parse và validate file .ctf
- Kiểm tra định dạng, giá trị hợp lệ
- Phân loại rule còn hạn và hết hạn
"""

import datetime
from typing import List, Optional
from dataclasses import dataclass


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

    def is_expired(self, today: Optional[datetime.date] = None) -> bool:
        if today is None:
            today = datetime.date.today()
        try:
            exp = datetime.datetime.strptime(self.expire.strip(), "%d/%m/%Y").date()
            return today > exp
        except ValueError:
            return True  # Nếu định dạng ngày sai thì coi như expired luôn


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
                    days=parts[4],
                    hours=parts[5],
                    expire=parts[6],
                    purpose=parts[7]
                )
                rules.append(rule)
            except Exception as e:
                print(f"[CTF] ❌ Lỗi dòng {lineno}: {e}")
    return rules


def get_valid_rules(rules: List[CTFRule]) -> List[CTFRule]:
    return [r for r in rules if not r.is_expired()]


def get_expired_rules(rules: List[CTFRule]) -> List[CTFRule]:
    return [r for r in rules if r.is_expired()]
