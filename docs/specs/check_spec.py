#!/usr/bin/env python3
"""Verificador mecânico de specs.

Confere o que é contável; não substitui a leitura crítica (references/revisao.md).

Uso:
  check_spec.py <pasta-da-spec> [<pasta> ...]
  check_spec.py --all <raiz-das-specs>        # todas as pastas NNN-* e o índice
  check_spec.py --all <raiz> --desde 014      # só as specs a partir da 014 (projeto com specs antigas)

Confere: arquivos por tamanho; identificadores duplicados; requisito sem critério; critério sem
tarefa; tarefa sem verificação; marcador [PREENCHER esquecido; questão bloqueante numa spec já
aprovada; mais de cinco questões; estado incoerente com as tarefas; STATUS com estados
empilhados ou longo demais; spec.md citando arquivo; decisão sem estado (vigente/substituída) ou
sem linha de confirmação; índice divergente do STATUS. Mostra o total de linhas de cada spec,
para a leitura de proporção.

Não confere o que é juízo: se o critério pode mesmo falhar, se há critério de continuidade que
faça sentido, se a premissa é razoável. Isso é a leitura crítica.

Saída 1 se houver ERRO, 0 caso contrário. Só usa a biblioteca padrão.
"""
import re
import sys
import unicodedata
from pathlib import Path

STATES = ["concluida com ressalvas", "substituida", "em execucao", "implementada",
          "concluida", "aprovada", "rascunho", "pausada", "descartada"]
RANK = {"rascunho": 0, "aprovada": 1, "em execucao": 2, "implementada": 3,
        "concluida": 4, "concluida com ressalvas": 4}
FULL_REQUIRED = ["spec.md", "design.md", "tasks.md", "STATUS.md"]


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", text.replace("*", "").replace("`", "")).strip().lower()


def canonical_state(raw: str):
    value = norm(raw)
    for state in STATES:  # mais longos primeiro
        if value.startswith(state):
            return state
    return None


def find_state(text: str):
    m = re.search(r"\*\*(?:Estado|Status):\*\*\s*([^·|\n]+)", text)
    return (canonical_state(m.group(1)), m.group(1).strip()) if m else (None, None)


def strip_code(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.S)


def strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.S)


def definitions(text: str, kind: str):
    patterns = {
        "R": [r"^\s*\*\*R-(\d+)\b", r"^\|\s*\**R-(\d+)\**\s*\|"],
        "CA": [r"^\|\s*\**CA-(\d+)\**\s*\|", r"^\s*\*\*CA-(\d+)\b"],
        "Q": [r"^\|\s*\**Q-(\d+)\**\s*\|"],
        "P": [r"^\s*-\s*\*\*P-(\d+)\b", r"^\|\s*\**P-(\d+)\**\s*\|"],
        "D": [r"^#{2,4}\s*D-(\d+)\b"],
        "RS": [r"^\|\s*\**RS-(\d+)\**\s*\|"],
    }[kind]
    found = []
    for line in text.splitlines():
        for pattern in patterns:
            m = re.match(pattern, line)
            if m:
                found.append((int(m.group(1)), line))
                break
    return found


def task_blocks(text: str):
    blocks, current = [], None
    for line in text.splitlines():
        m = re.match(r"^\s*-\s*\[(.)\]\s*\**\s*T-?(\d+)\b", line)
        if m:
            current = {"mark": m.group(1), "id": int(m.group(2)), "lines": [line]}
            blocks.append(current)
        elif re.match(r"^\s*(#|-\s*\[)", line):
            current = None
        elif current is not None:
            current["lines"].append(line)
    return blocks


class Report:
    def __init__(self, name: str):
        self.name, self.items, self.lines = name, [], None

    def error(self, where, msg):
        self.items.append(("ERRO ", where, msg))

    def warn(self, where, msg):
        self.items.append(("AVISO", where, msg))

    @property
    def errors(self):
        return sum(1 for level, _, _ in self.items if level.startswith("ERRO"))


def sections_with(text: str, keyword: str) -> str:
    """Conteúdo das seções '## …' cujo título contém a palavra; o texto todo se não houver."""
    parts = re.split(r"^(?=##\s)", text, flags=re.M)
    found = [p for p in parts if p.startswith("##") and keyword in norm(p.splitlines()[0])]
    return "\n".join(found) if found else text


def strip_inline_code(text: str) -> str:
    return re.sub(r"`[^`\n]*`", "", text)


def section(text: str, title_regex: str) -> str:
    m = re.search(rf"^##\s*{title_regex}.*?$(.*?)(?=^##\s|\Z)", text, flags=re.M | re.S | re.I)
    return m.group(1) if m else ""


def check_folder(folder: Path) -> tuple:
    rep = Report(folder.name)
    rep.lines = sum(len(p.read_text(encoding="utf-8").splitlines())
                    for p in folder.glob("*.md"))
    spec_path = folder / "spec.md"
    if not spec_path.exists():
        rep.error("pasta", "sem spec.md")
        return rep, None
    spec = spec_path.read_text(encoding="utf-8")
    size_m = re.search(r"\*\*Tamanho:\*\*\s*([SML])\b", spec)
    present = {p.name for p in folder.iterdir() if p.is_file()}
    size = size_m.group(1) if size_m else ("S" if present <= {"spec.md"} else "M")

    # arquivos
    if size in {"M", "L"}:
        for name in FULL_REQUIRED:
            if name not in present:
                rep.error("pasta", f"tamanho {size} exige {name}")
        if "LOG.md" not in present:
            rep.warn("pasta", "sem LOG.md: a história da spec acaba empilhada no STATUS")
    files = {name: (folder / name).read_text(encoding="utf-8")
             for name in ["spec.md", "design.md", "tasks.md", "STATUS.md", "LOG.md"]
             if (folder / name).exists()}

    # estado
    status_text = files.get("STATUS.md", "")
    state, raw_state = find_state(status_text if size in {"M", "L"} and status_text else spec)
    where_state = "STATUS.md" if size in {"M", "L"} else "spec.md"
    if raw_state is None:
        rep.error(where_state, "sem linha '**Estado:** …'")
    elif state is None:
        rep.warn(where_state, f"estado desconhecido: '{raw_state}' (use os estados da convenção)")
    rank = RANK.get(state, -1)

    # identificadores
    spec_body = strip_comments(strip_code(spec))
    design = strip_comments(strip_code(files.get("design.md", "")))
    tasks_text = strip_comments(files.get("tasks.md", "")) if size in {"M", "L"} else section(spec, r"Tarefas")
    defs = {
        "R": definitions(sections_with(spec_body, "requisito"), "R"),
        "CA": definitions(sections_with(spec_body, "criterio"), "CA"),
        "Q": definitions(sections_with(spec_body, "quest"), "Q"),
        "P": definitions(sections_with(spec_body, "premissa"), "P"),
        "D": definitions(design, "D"),
        "RS": definitions(design, "RS"),
    }
    for kind, items in defs.items():
        seen = set()
        for number, _ in items:
            if number in seen:
                rep.error("spec.md" if kind in {"R", "CA", "Q", "P"} else "design.md",
                          f"{kind}-{number:02d} definido mais de uma vez")
            seen.add(number)

    # R -> CA
    ca_rows = [l for l in sections_with(spec_body, "criterio").splitlines()
               if re.match(r"^\|\s*\**CA-\d+", l)]
    covered = {int(n) for row in ca_rows for n in re.findall(r"\bR-(\d+)\b", row)}
    for number, line in defs["R"]:
        if number not in covered and "removid" not in norm(line):
            rep.warn("spec.md", f"R-{number:02d} não aparece na coluna 'Cobre' de nenhum critério")
    ca_header = next((l for l in spec_body.splitlines()
                      if l.startswith("|") and "criterio" in norm(l) and "como" in norm(l)), "")
    if ca_rows and "tipo" not in norm(ca_header):
        rep.warn("spec.md", "tabela de critérios sem a coluna 'Tipo' (auto · comando · manual · real)")
    elif ca_rows and not any(re.search(r"\bauto\b", norm(r)) for r in ca_rows):
        rep.warn("spec.md", "nenhum critério de aceite do tipo 'auto'")

    # tarefas
    blocks = task_blocks(tasks_text)
    if not blocks:
        rep.warn("tasks.md" if size != "S" else "spec.md", "nenhuma tarefa no formato '- [ ] **T-01 · …**'")
    task_refs = {int(n) for n in re.findall(r"\bCA-(\d+)\b", tasks_text)}
    for number, _ in defs["CA"]:
        if blocks and number not in task_refs:
            rep.warn("tasks.md" if size != "S" else "spec.md",
                     f"CA-{number:02d} não é citado por nenhuma tarefa")
    seen_tasks = set()
    for block in blocks:
        tid = f"T-{block['id']:02d}"
        if block["id"] in seen_tasks:
            rep.error("tasks.md", f"{tid} aparece mais de uma vez")
        seen_tasks.add(block["id"])
        body = "\n".join(block["lines"])
        if not re.search(r"verifica|verification|→", norm(body) + body):
            rep.warn("tasks.md", f"{tid} sem verificação")
        if block["mark"] not in {" ", "x", "X", "~", "-", "!"}:
            rep.warn("tasks.md", f"{tid} com marca desconhecida '[{block['mark']}]'")
    marks = [b["mark"].lower() for b in blocks]
    if state in {"concluida", "concluida com ressalvas"}:
        pending = [f"T-{b['id']:02d}" for b in blocks if b["mark"] in {" ", "!"}]
        if pending:
            rep.error("tasks.md", f"spec {raw_state} com tarefas abertas: {', '.join(pending[:8])}"
                                  " (feche, descarte com [-] ou mova para fora com dono)")
        if state == "concluida" and "~" in marks:
            rep.warn("tasks.md", "tarefas com ressalva [~] numa spec 'concluída': use 'concluída com ressalvas'")
    if state == "rascunho" and "x" in marks and size != "S":
        rep.warn(where_state, "tarefas feitas numa spec ainda em 'rascunho'")
    if size == "S" and rep.lines and rep.lines > 150:
        rep.warn("spec.md", f"spec S com {rep.lines} linhas: está repetindo, ou é M")

    # marcadores e questões
    for name, text in files.items():
        count = strip_inline_code(strip_code(strip_comments(text))).count("[PREENCHER")
        if count:
            if rank >= 1:
                rep.error(name, f"{count} marcador(es) [PREENCHER numa spec {raw_state}")
            else:
                rep.warn(name, f"{count} marcador(es) [PREENCHER a completar")
    for number, line in defs["Q"]:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and norm(cells[-1]).startswith("sim") and rank >= 1:
            rep.error("spec.md", f"Q-{number:02d} bloqueia e a spec já está {raw_state}")
    if len(defs["Q"]) > 5:
        rep.warn("spec.md", f"{len(defs['Q'])} questões em aberto: as que têm resposta padrão"
                            " razoável deviam ser premissas assumidas")

    # STATUS
    status_file = "STATUS.md" if size in {"M", "L"} else "spec.md"
    status_body = strip_code(status_text) if size in {"M", "L"} else section(spec, r"Estado atual")
    if size in {"M", "L"} and status_text:
        h1 = [l for l in strip_code(status_text).splitlines() if re.match(r"^#\s", l)]
        if len(h1) > 1:
            rep.error("STATUS.md", f"{len(h1)} títulos de nível 1: estados empilhados. Reescreva o"
                                   " STATUS no lugar e mova a história para o LOG.md")
        lines = len(status_text.splitlines())
        if lines > 150:
            rep.warn("STATUS.md", f"{lines} linhas: o STATUS é o estado atual; história vai para o LOG.md")
        for field in ["Atualizado em", "Próximo passo"]:
            if field.lower() not in status_text.lower():
                rep.warn("STATUS.md", f"sem o campo '{field}'")
    if size == "S" and not status_body.strip():
        rep.warn(status_file, "sem a seção 'Estado atual'")

    # spec.md sem implementação
    if size in {"M", "L"}:
        prose = "\n".join(l for l in strip_comments(spec).splitlines() if not re.match(r"^\|\s*\**CA-\d+", l))
        leaks = re.findall(r"`([^`\n]*\.(?:jsx?|tsx?|py|rb|go|java|kt|swift|cs|php|sql|css|scss|html|vue)\b[^`\n]*)`",
                           prose)
        if leaks:
            rep.warn("spec.md", f"parece citar implementação ({', '.join(leaks[:3])}): isso é design.md")

    # decisões com estado
    decision_blocks = re.split(r"^(?=#{2,4}\s*D-\d+)", design, flags=re.M)
    for number, line in defs["D"]:
        low = norm(line)
        if not any(w in low for w in ["vigente", "substituida", "removida", "revogada"]):
            rep.warn("design.md", f"D-{number:02d} sem estado no título (vigente / substituída por …)")
        elif "vigente" in low:
            block = next((b for b in decision_blocks if re.match(rf"#{{2,4}}\s*D-0*{number}\b", b)), "")
            if "confirma" not in norm(block):
                rep.warn("design.md", f"D-{number:02d} vigente sem linha de 'Confirmação'")

    # fases em L
    if size == "L" and "design.md" in files and not re.search(r"^##.*Fases", files["design.md"], flags=re.M):
        rep.warn("design.md", "tamanho L sem seção de fases")

    return rep, state


def check_index(root: Path, states: dict) -> Report:
    rep = Report("índice")
    readme = root / "README.md"
    if not readme.exists():
        rep.warn("README.md", "sem README.md (convenção e índice) na raiz das specs")
        return rep
    text = readme.read_text(encoding="utf-8")
    pending = strip_inline_code(strip_code(strip_comments(text))).count("[PREENCHER")
    if pending:
        rep.warn("README.md", f"{pending} marcador(es) [PREENCHER na convenção instalada")
    checklist = root.parent / "DOC-CHECKLIST.md"
    if checklist.exists():
        pending = strip_inline_code(strip_code(strip_comments(checklist.read_text(encoding="utf-8")))).count("[PREENCHER")
        if pending:
            rep.warn(str(checklist), f"{pending} marcador(es) [PREENCHER: checklist ainda não adaptado ao projeto")
    index = re.split(r"^##\s*(?:Índice|Indice|Index)\s*$", text, maxsplit=1, flags=re.M)
    if len(index) < 2:
        rep.warn("README.md", "sem seção '## Índice'")
        return rep
    lines = index[1].splitlines()
    header = next((l for l in lines if l.startswith("|") and "estado" in norm(l)), None)
    if header is None:
        return rep
    cols = [norm(c) for c in header.strip().strip("|").split("|")]
    idx = next(i for i, c in enumerate(cols) if "estado" in c)
    for line in lines:
        m = re.match(r"^\|\s*\[(\d{3,})\]", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if idx >= len(cells):
            continue
        listed = canonical_state(cells[idx])
        actual = states.get(m.group(1))
        if actual and listed and listed != actual:
            rep.warn("README.md", f"índice diz '{cells[idx]}' para {m.group(1)}, o STATUS diz '{actual}'")
    return rep


def main(argv) -> int:
    if not argv or argv[0] in {"-h", "--help"}:
        print(__doc__)
        return 0
    reports, states = [], {}
    since = 0
    if "--desde" in argv:
        pos = argv.index("--desde")
        since = int(argv[pos + 1])
        argv = argv[:pos] + argv[pos + 2:]
    if argv[0] == "--all":
        root = Path(argv[1] if len(argv) > 1 else "docs/specs")
        folders = sorted(d for d in root.iterdir() if d.is_dir() and re.match(r"^\d{3,}-", d.name)
                         and int(d.name.split("-")[0]) >= since)
        for folder in folders:
            rep, state = check_folder(folder)
            reports.append(rep)
            states[folder.name.split("-")[0]] = state
        reports.append(check_index(root, states))
    else:
        for arg in argv:
            reports.append(check_folder(Path(arg))[0])
    total_err = total_warn = 0
    for rep in reports:
        size = f" ({rep.lines} linhas de markdown)" if rep.lines else ""
        if not rep.items:
            print(f"✔ {rep.name}{size}")
            continue
        print(f"== {rep.name}{size}")
        for level, where, msg in rep.items:
            print(f"  {level}  {where}: {msg}")
        total_err += rep.errors
        total_warn += len(rep.items) - rep.errors
    print(f"\nResumo: {total_err} erro(s), {total_warn} aviso(s)")
    return 1 if total_err else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
