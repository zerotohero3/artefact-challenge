import argparse
import os
import sys

import pydantic_ai
from dotenv import load_dotenv
from pydantic_ai.exceptions import AgentRunError

from emporio.agent import ROOT, Conversation, build_agent, load_deps, model_name_from_env


def run(conversation, read=input, write=print, show_tools=False) -> None:
    write("Assistente virtual da Empório da Música. Digite 'sair' para encerrar.")
    while True:
        try:
            message = read("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            write("")
            return
        if message.lower() == "sair":
            return
        if not message:
            continue
        try:
            turn = conversation.send(message)
        except KeyboardInterrupt:
            write("")
            return
        except AgentRunError as error:
            reason = type(error).__name__
            write(f"Não consegui responder agora ({reason}). Tente de novo em instantes.")
            continue
        if show_tools:
            for call in turn.tool_calls:
                write(f"  [consulta] {call}")
        write(f"\nAssistente: {turn.reply}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="emporio", description="Converse com a assistente virtual da Empório da Música."
    )
    parser.add_argument(
        "--show-tools", action="store_true", help="mostra as consultas feitas a cada resposta"
    )
    args = parser.parse_args()
    load_dotenv(ROOT / ".env")
    model = model_name_from_env()
    if model.startswith("google") and not os.environ.get("GOOGLE_API_KEY"):
        print(
            "Falta a chave do Google AI Studio: copie .env.example para .env e preencha "
            "GOOGLE_API_KEY (https://aistudio.google.com/apikey).",
            file=sys.stderr,
        )
        sys.exit(1)
    pydantic_ai.BANNER_ENABLED = False
    run(Conversation(build_agent(model), load_deps()), show_tools=args.show_tools)
