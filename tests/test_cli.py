import sys

import pytest
from pydantic_ai.exceptions import (
    ModelConnectionError,
    ModelHTTPError,
    ModelRateLimitError,
    ModelUnavailableError,
)

from emporio import cli
from emporio.agent import Turn
from emporio.cli import main, run


class FakeConversation:
    def __init__(self, *outcomes):
        self.outcomes = list(outcomes)
        self.received = []

    def send(self, message):
        self.received.append(message)
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, BaseException):
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


@pytest.mark.parametrize(
    "error",
    [
        ModelHTTPError(500, "gemini"),
        ModelUnavailableError("gemini", "high demand"),
        ModelRateLimitError("gemini", "quota"),
        ModelConnectionError("gemini", "offline"),
    ],
    ids=lambda error: type(error).__name__,
)
def test_model_error_warns_and_the_conversation_goes_on(error):
    conversation = FakeConversation(error, Turn("Custa R$ 2.199,00", []))
    output = []
    run(conversation, read=typed("Oi", "Quanto custa o GD20?"), write=output.append)

    reason = type(error).__name__
    assert f"Não consegui responder agora ({reason}). Tente de novo em instantes." in output
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


def test_ctrl_c_while_answering_ends_the_conversation():
    conversation = FakeConversation(KeyboardInterrupt(), Turn("ok", []))
    run(conversation, read=typed("Oi", "não devia chegar"), write=lambda text: None)
    assert conversation.received == ["Oi"]


def test_model_comes_from_the_environment(monkeypatch, tmp_path):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.setenv("GOOGLE_API_KEY", "fake")
    monkeypatch.setenv("EMPORIO_MODEL", "google:gemini-3.1-flash-lite")
    monkeypatch.setattr(sys, "argv", ["emporio"])
    started = []
    monkeypatch.setattr(cli, "run", lambda conversation, show_tools: started.append(conversation))

    main()
    assert started and started[0].agent.model == "google:gemini-3.1-flash-lite"


def test_missing_key_explains_and_exits(monkeypatch, tmp_path, capsys):
    monkeypatch.setattr(cli, "ROOT", tmp_path)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("EMPORIO_MODEL", raising=False)
    monkeypatch.setattr(sys, "argv", ["emporio"])

    with pytest.raises(SystemExit) as exit_info:
        main()
    assert exit_info.value.code == 1
    assert "GOOGLE_API_KEY" in capsys.readouterr().err
