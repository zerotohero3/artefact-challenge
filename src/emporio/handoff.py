import json
import re
import secrets
from datetime import datetime
from pathlib import Path


def is_contact(text: str) -> bool:
    is_email = re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", text) is not None
    return is_email or len(re.sub(r"\D", "", text)) >= 8


class HandoffLog:
    def __init__(self, path: Path):
        self.path = path

    def register(self, reason, summary, contact, order_id, now: datetime) -> dict:
        if not is_contact(contact.strip()):
            return {"error": "Informe um telefone ou e-mail para a equipe retornar."}
        protocol = f"EM-{secrets.token_hex(3).upper()}"
        record = {
            "protocol": protocol,
            "created_at": now.isoformat(timespec="seconds"),
            "reason": reason,
            "summary": summary,
            "contact": contact.strip(),
            "order_id": order_id,
        }
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("a", encoding="utf-8") as file:
            file.write(json.dumps(record, ensure_ascii=False) + "\n")
        return {"protocol": protocol, "registered_at": now.strftime("%d/%m/%Y %H:%M")}
