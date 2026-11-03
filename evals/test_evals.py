import json
import re
import time

import pytest
from cases import CASES, Case
from dotenv import load_dotenv
from pydantic_ai.exceptions import (
    ModelConnectionError,
    ModelRateLimitError,
    ModelServerError,
    ModelUnavailableError,
)
from pydantic_ai.messages import ToolCallPart

from emporio.agent import ROOT, Conversation, build_agent, load_deps
from emporio.store import normalize

load_dotenv(ROOT / ".env")

TRANSIENT = (ModelConnectionError, ModelRateLimitError, ModelServerError, ModelUnavailableError)
WAITS = [15, 30, 60]


def send(conversation: Conversation, message: str) -> str:
    for wait in [*WAITS, None]:
        try:
            return conversation.send(message).reply
        except TRANSIENT as error:
            if wait is None:
                raise
            print(f"[falha de ambiente: {type(error).__name__}; nova tentativa em {wait}s]")
            print(f"[detalhe: {str(error)[:600]}]")
            time.sleep(wait)


@pytest.mark.parametrize("case", CASES, ids=lambda case: f"{case.group}-{case.name}")
def test_case(case: Case, tmp_path):
    handoffs = tmp_path / "handoffs.jsonl"
    conversation = Conversation(build_agent(), load_deps(lambda: case.now, handoffs))
    replies = []
    for message in case.messages:
        print(f"\nCliente: {message}")
        replies.append(send(conversation, message))
        print(f"Assistente: {replies[-1]}")
    calls = [
        (part.tool_name, part.args_as_dict())
        for message in conversation.history
        for part in message.parts
        if isinstance(part, ToolCallPart)
    ]
    print(f"Consultas: {calls}")

    texts = [normalize(reply) for reply in replies]
    for tool, minimum in case.calls.items():
        assert sum(name == tool for name, _ in calls) >= minimum, f"{tool} ×{minimum}"
    if case.no_calls:
        assert calls == []
    if case.args:
        assert case.args(calls), case.args.__name__
    for pattern in case.contains:
        assert re.search(pattern, texts[-1]), f"falta: {pattern}"
    for pattern in case.absent:
        assert not re.search(pattern, texts[-1]), f"não podia ter: {pattern}"
    for pattern in case.first:
        assert re.search(pattern, texts[0]), f"falta na 1ª: {pattern}"
    for pattern in case.never:
        for text in texts:
            assert not re.search(pattern, text), f"não podia ter: {pattern}"
    if case.handoff_recorded:
        protocol = re.search(r"em-[0-9a-f]{6}", texts[-1])[0].upper()
        recorded = [json.loads(line)["protocol"] for line in handoffs.read_text().splitlines()]
        assert protocol in recorded
