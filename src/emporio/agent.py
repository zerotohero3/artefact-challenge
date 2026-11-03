import os
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import ModelMessage, ToolCallPart
from pydantic_ai.models import Model

from emporio.handoff import HandoffLog
from emporio.policies import Policies
from emporio.store import Store

ROOT = Path(__file__).parents[2]
# Mato Grosso do Sul has had no daylight saving time since 2019.
CAMPO_GRANDE = timezone(timedelta(hours=-4))
DEFAULT_MODEL = "google:gemini-3.1-flash-lite"
PERSONA = Path(__file__).with_name("persona.md").read_text(encoding="utf-8")
WEEKDAYS = ["segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira",
            "sábado", "domingo"]  # fmt: skip


@dataclass
class Deps:
    store: Store
    policies: Policies
    handoffs: HandoffLog
    now: Callable[[], datetime]


@dataclass
class Turn:
    reply: str
    tool_calls: list[str]


def model_name_from_env() -> str:
    return os.environ.get("EMPORIO_MODEL", "").strip() or DEFAULT_MODEL


def clock_from_env() -> Callable[[], datetime]:
    fixed = os.environ.get("EMPORIO_NOW", "").strip()
    if fixed:
        moment = datetime.fromisoformat(fixed).replace(tzinfo=CAMPO_GRANDE)
        return lambda: moment
    return lambda: datetime.now(CAMPO_GRANDE)


def load_deps(now=None, handoff_path: Path = ROOT / "var" / "handoffs.jsonl") -> Deps:
    return Deps(
        store=Store.load(ROOT / "data"),
        policies=Policies.load(ROOT / "data" / "politicas_da_loja.md"),
        handoffs=HandoffLog(handoff_path),
        now=now or clock_from_env(),
    )


def build_agent(model: str | Model | None = None) -> Agent[Deps, str]:
    agent = Agent(
        model or model_name_from_env(),
        deps_type=Deps,
        instructions=PERSONA,
        defer_model_check=True,
    )

    @agent.instructions
    def moment(ctx: RunContext[Deps]) -> str:
        now = ctx.deps.now()
        return (
            "## Contexto do momento\n\n"
            f"Agora: {WEEKDAYS[now.weekday()]}, {now:%d/%m/%Y}, {now:%H:%M} "
            "(horário de Campo Grande/MS).\n\n"
            f"Categorias do catálogo: {', '.join(ctx.deps.store.category_names)}.\n\n"
            f"Sumário do manual:\n{ctx.deps.policies.table_of_contents()}"
        )

    @agent.tool
    def search_products(
        ctx: RunContext[Deps],
        query: str | None = None,
        category: str | None = None,
        min_price: float | None = None,
        max_price: float | None = None,
        only_available: bool = False,
    ) -> dict:
        """Busca produtos no catálogo da loja, ordenados pelo preço final.

        Args:
            query: termos de nome, marca, modelo ou categoria, por exemplo "Takamine GD20" ou
                "violão Yamaha". Todos os termos precisam casar.
            category: nome exato de uma categoria do catálogo, por exemplo "Violões".
            min_price: preço final mínimo, em reais.
            max_price: preço final máximo, em reais.
            only_available: verdadeiro para trazer só produtos disponíveis para compra. Não use
                ao procurar um produto específico: ele some do resultado se estiver esgotado,
                descontinuado ou em breve.
        """
        return ctx.deps.store.search_products(query, category, min_price, max_price, only_available)

    @agent.tool
    def get_order(ctx: RunContext[Deps], order_id: int, contact: str) -> dict:
        """Consulta um pedido. Só devolve o pedido se o contato for do titular.

        Args:
            order_id: número do pedido.
            contact: e-mail ou telefone que o cliente informou na conversa.
        """
        return ctx.deps.store.get_order(order_id, contact, ctx.deps.now().date())

    @agent.tool
    def read_policy(ctx: RunContext[Deps], sections: list[str]) -> str:
        """Lê seções do manual de políticas da loja. Pedir "4" traz também 4.1 a 4.4.

        Args:
            sections: números das seções do sumário, por exemplo ["2"] ou ["4.1", "8.1"].
        """
        return ctx.deps.policies.read(sections)

    @agent.tool
    def handoff_to_staff(
        ctx: RunContext[Deps],
        reason: Literal["complaint", "return_or_exchange", "question", "human_request"],
        summary: str,
        contact: str,
        order_id: int | None = None,
    ) -> dict:
        """Registra um encaminhamento para a equipe da loja e devolve o protocolo.

        Args:
            reason: complaint (reclamação), return_or_exchange (troca, devolução ou garantia),
                question (dúvida que o manual não cobre) ou human_request (cliente quer falar
                com uma pessoa).
            summary: resumo do caso para a equipe.
            contact: telefone ou e-mail que o cliente informou para retorno.
            order_id: número do pedido, se houver.
        """
        return ctx.deps.handoffs.register(reason, summary, contact, order_id, ctx.deps.now())

    return agent


def describe(call: ToolCallPart) -> str:
    args = ", ".join(f"{name}={value!r}" for name, value in call.args_as_dict().items())
    return f"{call.tool_name}({args})"


class Conversation:
    def __init__(self, agent: Agent[Deps, str], deps: Deps):
        self.agent = agent
        self.deps = deps
        self.history: list[ModelMessage] = []

    def send(self, message: str) -> Turn:
        result = self.agent.run_sync(message, deps=self.deps, message_history=self.history)
        self.history = result.all_messages()
        calls = [
            describe(part)
            for response in result.new_messages()
            for part in response.parts
            if isinstance(part, ToolCallPart)
        ]
        return Turn(result.output, calls)
