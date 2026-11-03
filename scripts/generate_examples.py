"""Run the example conversations against the configured model and save them as Markdown.

Usage: uv run python scripts/generate_examples.py [number ...]
"""

import sys
import tempfile
import time
from pathlib import Path

import pydantic_ai
from dotenv import load_dotenv
from pydantic_ai.exceptions import ModelRateLimitError, ModelUnavailableError

from emporio.agent import ROOT, Conversation, build_agent, load_deps, model_name_from_env

EXAMPLES = [
    (
        "catalogo",
        "Catálogo",
        [
            "Quais violões vocês têm até R$ 1.000?",
            "Qual desses é melhor para quem está começando?",
        ],
    ),
    (
        "preco",
        "Preço, PIX e parcelamento",
        ["Quanto custa o Takamine GD20?", "E no PIX?", "Dá para parcelar em 12x?"],
    ),
    (
        "devolucao",
        "Devolução de um pedido",
        [
            "Me arrependi da minha compra, posso devolver?",
            "É o pedido 7, meu e-mail é leticia.rocha@jmail.com",
            "E se ele tiver defeito?",
        ],
    ),
    (
        "pedido-atrasado",
        "Pedido atrasado e encaminhamento",
        [
            "Cadê meu pedido 8?",
            "Meu e-mail é anacarol.ferreira@coldmail.com",
            "Quero falar com alguém",
        ],
    ),
    (
        "escopo",
        "Fora do escopo",
        ["Vocês vendem cabo e pedal?", "Qual o endereço da loja?", "Me indica um filme?"],
    ),
]


def send(conversation: Conversation, message: str):
    for wait in [15, 30, 60, None]:
        try:
            return conversation.send(message)
        except (ModelRateLimitError, ModelUnavailableError):
            if wait is None:
                raise
            time.sleep(wait)


def main() -> None:
    load_dotenv(ROOT / ".env")
    pydantic_ai.BANNER_ENABLED = False
    chosen = {int(n) for n in sys.argv[1:]} or set(range(1, len(EXAMPLES) + 1))
    model = model_name_from_env()
    with tempfile.TemporaryDirectory() as handoffs_dir:
        for number, (slug, title, messages) in enumerate(EXAMPLES, start=1):
            if number not in chosen:
                continue
            deps = load_deps(handoff_path=Path(handoffs_dir) / "handoffs.jsonl")
            conversation = Conversation(build_agent(model), deps)
            lines = [
                f"# Exemplo {number} — {title}",
                "",
                f"Modelo `{model}`, executado em {deps.now():%d/%m/%Y %H:%M} "
                "(horário de Campo Grande).",
            ]
            for message in messages:
                turn = send(conversation, message)
                lines += ["", f"**Cliente:** {message}", ""]
                calls = [f"> consulta: `{call}`" for call in turn.tool_calls]
                lines += calls or ["> (sem consulta)"]
                lines += ["", f"**Assistente:** {turn.reply.strip()}"]
            path = ROOT / "examples" / f"{number:02d}-{slug}.md"
            path.parent.mkdir(exist_ok=True)
            path.write_text("\n".join(lines) + "\n", encoding="utf-8")
            print(f"gravado {path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
