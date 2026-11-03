import json
import re
import time

import pytest
from cases import CASES, Case, problems
from dotenv import load_dotenv
from pydantic_ai.exceptions import (
    ModelConnectionError,
    ModelRateLimitError,
    ModelServerError,
    ModelUnavailableError,
)
from pydantic_ai.messages import ToolCallPart

from emporio.agent import ROOT, Conversation, build_agent, load_deps

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

    assert problems(case, replies, calls) == []
    if case.handoff_recorded:
        protocol = re.search(r"EM-[0-9A-F]{6}", replies[-1].upper())[0]
        recorded = [json.loads(line)["protocol"] for line in handoffs.read_text().splitlines()]
        assert protocol in recorded
