import json
from datetime import datetime

import pytest
from pydantic_ai.exceptions import ModelHTTPError
from pydantic_ai.messages import (
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.function import FunctionModel

from emporio.agent import (
    CAMPO_GRANDE,
    Conversation,
    build_agent,
    clock_from_env,
    load_deps,
    model_name_from_env,
)

SUNDAY_NIGHT = datetime(2026, 11, 8, 20, 0, tzinfo=CAMPO_GRANDE)


@pytest.fixture
def deps(tmp_path):
    return load_deps(now=lambda: SUNDAY_NIGHT, handoff_path=tmp_path / "handoffs.jsonl")


def calling(tool, args):
    """A fake model that calls one tool, then answers with what the tool returned."""
    returned = []

    def respond(messages, info):
        last = messages[-1].parts[-1]
        if isinstance(last, ToolReturnPart):
            returned.append(last.content)
            return ModelResponse(parts=[TextPart("pronto")])
        return ModelResponse(parts=[ToolCallPart(tool, args)])

    return FunctionModel(respond), returned


def test_exactly_the_four_tools(deps):
    seen = {"tools": None}

    def respond(messages, info):
        seen["tools"] = sorted(tool.name for tool in info.function_tools)
        return ModelResponse(parts=[TextPart("Oi!")])

    Conversation(build_agent(FunctionModel(respond)), deps).send("Oi")
    assert seen["tools"] == ["get_order", "handoff_to_staff", "read_policy", "search_products"]


def test_instructions_bring_persona_and_moment(deps):
    seen = {"instructions": ""}

    def respond(messages, info):
        seen["instructions"] = info.instructions or ""
        return ModelResponse(parts=[TextPart("Oi!")])

    Conversation(build_agent(FunctionModel(respond)), deps).send("Oi")
    instructions = seen["instructions"]
    assert "Fontes da verdade" in instructions
    assert "domingo, 08/11/2026, 20:00" in instructions
    for category in deps.store.category_names:
        assert category in instructions
    assert "4.1 Direito de Arrependimento (Compras Online)" in instructions


def test_turn_reports_the_tool_calls(deps):
    model, returned = calling("search_products", {"query": "Takamine GD20"})
    turn = Conversation(build_agent(model), deps).send("Quanto custa o Takamine GD20?")

    assert turn.tool_calls == ["search_products(query='Takamine GD20')"]
    assert turn.reply == "pronto"
    assert returned and returned[0]["products"][0]["final_price"] == "R$ 2.199,00"


def test_order_lookup_uses_the_conversation_clock(deps):
    model, returned = calling(
        "get_order", {"order_id": 8, "contact": "anacarol.ferreira@coldmail.com"}
    )
    Conversation(build_agent(model), deps).send("Cadê meu pedido 8?")

    assert returned and returned[0]["days_since_order"] == 266
    assert returned[0]["late"] is True


def test_handoff_goes_to_the_conversation_log(deps, tmp_path):
    model, returned = calling(
        "handoff_to_staff",
        {"reason": "human_request", "summary": "Quer falar com alguém", "contact": "67988887777"},
    )
    Conversation(build_agent(model), deps).send("Quero falar com um atendente")

    assert returned and returned[0]["registered_at"] == "08/11/2026 20:00"
    record = json.loads((tmp_path / "handoffs.jsonl").read_text(encoding="utf-8"))
    assert record["protocol"] == returned[0]["protocol"]
    assert record["created_at"] == "2026-11-08T20:00:00-04:00"


def test_model_failure_keeps_the_history(deps):
    received = []

    def respond(messages, info):
        received.append(messages)
        if len(received) == 2:
            raise ModelHTTPError(503, "gemini")
        return ModelResponse(parts=[TextPart(f"resposta {len(received)}")])

    conversation = Conversation(build_agent(FunctionModel(respond)), deps)
    assert conversation.send("Primeira").reply == "resposta 1"
    with pytest.raises(ModelHTTPError):
        conversation.send("Segunda")
    assert conversation.send("Terceira").reply == "resposta 3"

    assert len(received) == 3
    third = received[2]
    prompts = [p.content for m in third for p in m.parts if isinstance(p, UserPromptPart)]
    replies = [p.content for m in third for p in m.parts if isinstance(p, TextPart)]
    assert prompts == ["Primeira", "Terceira"]
    assert replies == ["resposta 1"]


def test_model_comes_from_the_environment(monkeypatch):
    monkeypatch.delenv("EMPORIO_MODEL", raising=False)
    assert model_name_from_env() == "google:gemini-3.1-flash-lite"
    assert build_agent().model == "google:gemini-3.1-flash-lite"

    monkeypatch.setenv("EMPORIO_MODEL", "google:gemini-3.5-flash-lite")
    assert model_name_from_env() == "google:gemini-3.5-flash-lite"
    assert build_agent().model == "google:gemini-3.5-flash-lite"


def test_clock_can_be_fixed_by_the_environment(monkeypatch):
    monkeypatch.setenv("EMPORIO_NOW", "2026-11-03T10:00")
    assert clock_from_env()() == datetime(2026, 11, 3, 10, 0, tzinfo=CAMPO_GRANDE)

    monkeypatch.delenv("EMPORIO_NOW")
    assert clock_from_env()().utcoffset() == CAMPO_GRANDE.utcoffset(None)
