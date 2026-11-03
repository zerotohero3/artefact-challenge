from pathlib import Path

import pytest

from emporio.policies import Policies

MANUAL = Path(__file__).parents[1] / "data" / "politicas_da_loja.md"


@pytest.fixture(scope="module")
def policies():
    return Policies.load(MANUAL)


def test_table_of_contents_lists_the_28_sections(policies):
    lines = policies.table_of_contents().splitlines()
    assert len(lines) == 28
    assert lines[0] == "1. Sobre a Empório da Música"
    assert "4.1 Direito de Arrependimento (Compras Online)" in lines
    assert lines[-1] == "10. Disposições Finais"


def test_subsection_text(policies):
    text = policies.read(["4.1"])
    assert "4.1 Direito de Arrependimento" in text
    assert "7 (sete) dias corridos após o recebimento" in text
    assert "4.2 Trocas por Defeito" not in text


def test_section_brings_its_subsections(policies):
    text = policies.read(["4"])
    for title in ["4.1 Direito", "4.2 Trocas por Defeito", "4.3 Trocas", "4.4 Itens"]:
        assert title in text
    assert "5. Política de Frete" not in text


def test_section_1_does_not_bring_section_10(policies):
    text = policies.read(["1"])
    assert "1.1 Missão" in text
    assert "1.2 Dados da Empresa" in text
    assert "Disposições Finais" not in text


def test_unknown_section_lists_valid_ones(policies):
    text = policies.read(["4.9"])
    assert "Seções inexistentes: 4.9." in text
    assert "Seções válidas: 1, 1.1, 1.2, 2, 3, 3.1, 4," in text


def test_curated_contacts_and_installment_rule(policies):
    everything = policies.read([str(n) for n in range(1, 11)])
    assert "3321-4500" not in everything
    assert "empóriodamusica" not in everything
    assert "Conversão do" not in everything
    assert "| Cartão de Crédito | Até 12x sem juros | Parcela mínima conforme a seção 3.1 |" in (
        policies.read(["3"])
    )
    three_times = "Parcelamento em até 3x: sem juros, parcela mínima de R$ 50,00."
    assert three_times in policies.read(["3.1"])
