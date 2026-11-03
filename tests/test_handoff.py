import json
import re
from datetime import datetime, timedelta, timezone

from emporio.handoff import HandoffLog

NOW = datetime(2026, 11, 2, 21, 53, tzinfo=timezone(timedelta(hours=-4)))


def test_handoff_is_recorded_and_returns_protocol(tmp_path):
    path = tmp_path / "var" / "handoffs.jsonl"
    result = HandoffLog(path).register(
        "complaint", "Violão chegou com o braço trincado", "(67) 98888-7777", 8, NOW
    )

    assert re.fullmatch(r"EM-[0-9A-F]{6}", result["protocol"])
    assert result["registered_at"] == "02/11/2026 21:53"
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 1
    assert json.loads(lines[0]) == {
        "protocol": result["protocol"],
        "created_at": "2026-11-02T21:53:00-04:00",
        "reason": "complaint",
        "summary": "Violão chegou com o braço trincado",
        "contact": "(67) 98888-7777",
        "order_id": 8,
    }


def test_handoff_appends(tmp_path):
    path = tmp_path / "handoffs.jsonl"
    log = HandoffLog(path)
    first = log.register("question", "Frete de R$ 500,00", "ana@exemplo.com", None, NOW)
    second = log.register("human_request", "Quer falar com alguém", "67988887777", None, NOW)

    assert first["protocol"] != second["protocol"]
    protocols = [json.loads(line)["protocol"] for line in path.read_text().splitlines()]
    assert protocols == [first["protocol"], second["protocol"]]


def test_handoff_without_contact_records_nothing(tmp_path):
    path = tmp_path / "handoffs.jsonl"
    result = HandoffLog(path).register("complaint", "Reclamação", "  ", None, NOW)

    assert result == {"error": "Informe um telefone ou e-mail para a equipe retornar."}
    assert not path.exists()
