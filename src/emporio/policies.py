import re
from dataclasses import dataclass
from pathlib import Path

HEADING = re.compile(r"^#{2,3} (\d+(?:\.\d+)?)\.? ")


def within(section_id: str, wanted: str) -> bool:
    return section_id == wanted or section_id.startswith(wanted + ".")


@dataclass
class Section:
    id: str
    title: str
    text: str


class Policies:
    def __init__(self, sections: list[Section]):
        self.sections = sections

    @classmethod
    def load(cls, path: Path) -> "Policies":
        sections = []
        for line in path.read_text(encoding="utf-8").splitlines():
            match = HEADING.match(line)
            if match:
                sections.append(Section(match[1], line.lstrip("#").strip(), line))
            elif sections:
                sections[-1].text += "\n" + line
        return cls(sections)

    def read(self, section_ids: list[str]) -> str:
        wanted = [s.strip().rstrip(".") for s in section_ids]
        found = [s for s in self.sections if any(within(s.id, w) for w in wanted)]
        parts = [section.text.strip() for section in found]
        missing = [w for w in wanted if not any(within(s.id, w) for s in found)]
        if missing:
            parts.append(
                f"Seções inexistentes: {', '.join(missing)}. "
                f"Seções válidas: {', '.join(s.id for s in self.sections)}."
            )
        return "\n\n".join(parts)

    def table_of_contents(self) -> str:
        return "\n".join(section.title for section in self.sections)
