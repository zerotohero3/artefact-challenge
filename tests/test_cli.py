import sys

import pytest
from pydantic_ai.exceptions import ModelHTTPError

from emporio.agent import Turn
from emporio.cli import main, run


class FakeConversation:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.received = []

    def send(self, message):
        self.received.append(message)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def typed(*lines):
    remaining = iter(lines)

    def read(prompt=""):
        try:
            return next(remaining)
        except StopIteration:
            raise EOFError from None

    return read


def test_model_error_warns_and_the_conversation_goes_on():
    conversation = FakeConversation(ModelHTTPError(503, "gemini"), Turn("Custa R$ 2.199,00", []))
    output = []
    run(conversation, read=typed("Oi", "Quanto custa o GD20?"), write=output.append)

    assert "Não consegui responder agora (ModelHTTPError). Tente de novo em instantes." in output
    assert any("Custa R$ 2.199,00" in line for line in output)
    assert conversation.received == ["Oi", "Quanto custa o GD20?"]


def test_tool_calls_only_with_the_option():
    call = "search_products(query='GD20')"
    shown, hidden = [], []
    run(FakeConversation(Turn("ok", [call])), read=typed("x"), write=shown.append, show_tools=True)
    run(FakeConversation(Turn("ok", [call])), read=typed("x"), write=hidden.append)

    assert any(call in line for line in shown)
    assert not any(call in line for line in hidden)


def test_sair_ends_the_conversation():
    conversation = FakeConversation(Turn("ok", []), Turn("ok", []))
    run(conversation, read=typed("Oi", "sair", "não devia chegar"), write=lambda text: None)
    assert conversation.received == ["Oi"]


def test_missing_key_explains_and_exits(monkeypatch, tmp_path, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("EMPORIO_MODEL", raising=False)
    monkeypatch.setattr(sys, "argv", ["emporio"])

    with pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code == 1
    assert "GOOGLE_API_KEY" in capsys.readouterr().err
