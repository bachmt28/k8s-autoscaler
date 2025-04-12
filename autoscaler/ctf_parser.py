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
    expire: str  # giữ nguyên string để dễ debug/log
    purpose: str

    def expire_date(self) -> Optional[datetime.date]:
        """Trả về đối tượng datetime.date nếu hợp lệ, None nếu lỗi"""
        try:
            return datetime.datetime.strptime(self.expire.strip(), "%d/%m/%Y").date()
        except ValueError:
            return None

    def is_expired(self, today: Optional[datetime.date] = None) -> bool:
        """Kiểm tra rule đã hết hạn chưa"""
        if today is None:
            today = datetime.date.today()
        exp = self.expire_date()
        return exp is None or today > exp


def parse_ctf_file(file_path: str) -> List[CTFRule]:
    rules: List[CTFRule] = []
    with open(file_path, "r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
