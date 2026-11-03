from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from emporio.store import Store, installments

DATA = Path(__file__).parents[1] / "data"
TODAY = date(2026, 11, 2)


@pytest.fixture(scope="module")
def store():
    return Store.load(DATA)


def ids(result):
    return [p["id"] for p in result["products"]]


def test_inactive_promotion_is_never_offered(store):
    result = store.search_products(query="Takamine GD20")
    assert ids(result) == [95]
    gd20 = result["products"][0]
    assert gd20["promotion"] is None
    assert gd20["final_price"] == "R$ 2.199,00"
    assert gd20["pix_price"] == "R$ 2.089,05"
    assert "1.935" not in str(result)


def test_active_promotion_shows_original_price_and_percent(store):
    result = store.search_products(query="Ohana CK-20")
    assert ids(result) == [121]
    ohana = result["products"][0]
    assert ohana["price"] == "R$ 549,00"
    assert ohana["promotion"] == {"name": "Desconto Exclusivo", "percent": 20}
    assert ohana["final_price"] == "R$ 439,20"
    assert ohana["pix_price"] is None
    assert ohana["installments"] == "5x de R$ 87,84 sem juros"


def test_pix_rounds_half_up(store):
    assert store.search_products(query="Yamaha C40")["products"][0]["pix_price"] == "R$ 569,91"


@pytest.mark.parametrize(
    ("price", "expected"),
    [
        ("349.90", "4x de R$ 87,48 sem juros"),
        ("599.00", "6x de R$ 99,83 sem juros"),
        ("2199.00", "12x de R$ 183,25 sem juros"),
        ("159.90", "3x de R$ 53,30 sem juros"),
        ("99.90", "1x de R$ 99,90 sem juros"),
    ],
)
def test_max_installments(price, expected):
    assert installments(Decimal(price)) == expected


@pytest.mark.parametrize(
    ("query", "product_id", "availability"),
    [
        ("Giannini GF-3D", 96, "esgotado"),
        ("Shelby SN-7C", 113, "descontinuado"),
        ("Kala KA-ABP-CTG", 130, "em breve"),
        ("Ibanez Bass 2X", 136, "descontinuado"),
        ("Yamaha C40", 81, "disponível"),
    ],
)
def test_status_prevails_over_stock(store, query, product_id, availability):
    result = store.search_products(query=query)
    assert ids(result) == [product_id]
    assert result["products"][0]["availability"] == availability


def test_available_guitars_up_to_1000(store):
    result = store.search_products(category="violoes", max_price=1000, only_available=True)
    assert ids(result) == [83, 85, 89, 88, 81, 84, 87, 86, 107, 82, 91, 112]
    assert result["total"] == 12
    assert result["products"][0]["final_price"] == "R$ 429,90"
    assert result["products"][-1]["final_price"] == "R$ 999,00"


def test_price_range_uses_final_price(store):
    result = store.search_products(category="Violões", min_price=1900, max_price=2000)
    assert ids(result) == [90]


@pytest.mark.parametrize(
    ("query", "product_id"),
    [
        ("Takamine GD20", 95),
        ("takamine gd-20", 95),
        ("TAKAMINE GD 20", 95),
        ("violão Giannini GF-3D", 96),
        ("ukulele Ohana CK-20", 121),
        ("Shelby SN-7C", 113),
        ("violão, Giannini GF-3D?", 96),
    ],
)
def test_search_by_name(store, query, product_id):
    assert ids(store.search_products(query=query)) == [product_id]


def test_results_are_capped_with_the_full_total(store):
    result = store.search_products()
    assert result["total"] == 65
    assert len(result["products"]) == 20


def test_unknown_category_lists_valid_ones(store):
    result = store.search_products(category="Pedais")
    assert "Pedais" in result["error"]
    assert "Violões" in result["error"]


def test_wrong_contact_looks_like_missing_order(store):
    assert store.get_order(10, "bruno.martins@jmail.com", TODAY)["found"] is True

    missing = store.get_order(999, "joao@exemplo.com", TODAY)
    for contact in ["joao@exemplo.com", "anacarol.ferreira@coldmail.com", "(67) 99654-7821"]:
        wrong = store.get_order(10, contact, TODAY)
        assert wrong == missing
        for leaked in ["Bruno", "bruno.martins", "98543", "Music Man", "8.732", "8732"]:
            assert leaked not in str(wrong)


@pytest.mark.parametrize(
    "contact",
    [
        "Bruno.Martins@jmail.com ",
        "(67) 98543-2109",
        "67985432109",
        "+55 67 98543-2109",
        "98543-2109",
    ],
)
def test_holder_contact_formats(store, contact):
    order = store.get_order(10, contact, TODAY)
    assert order["found"] is True
    assert order["customer_first_name"] == "Bruno"
    assert "bruno.martins" not in str(order)
    assert "98543" not in str(order)


def test_phone_suffix_needs_eight_digits(store):
    assert store.get_order(10, "8543-2109", TODAY)["found"] is True
    assert store.get_order(10, "543-2109", TODAY)["found"] is False


def test_order_total_is_the_recorded_one(store):
    order = store.get_order(3, "isabela.moreira@jmail.com", TODAY)
    assert order["found"] is True
    assert order["total"] == "R$ 3.450,00"
    assert order["items"] == [{"product": "Kala KA-ABP-CTG Barítono Cedar", "quantity": 2}]
    assert order["payment"] == "cartão de crédito em 12x"


def test_shipped_order_past_estimate_is_late(store):
    order = store.get_order(8, "anacarol.ferreira@coldmail.com", TODAY)
    assert order["found"] is True
    assert order["status"] == "enviado"
    assert order["late"] is True
    assert order["tracking_code"] == "BRJL5544332BR"
    assert order["estimated_delivery"] == "28/02/2026"
    assert order["days_since_estimated_delivery"] == 247
    assert order["days_since_order"] == 260
    assert order["cancellation_reason"] is None


def test_delivered_order_is_never_late(store):
    order = store.get_order(7, "leticia.rocha@jmail.com", TODAY)
    assert order["found"] is True
    assert order["status"] == "entregue"
    assert order["days_since_estimated_delivery"] == 258
    assert order["late"] is False


def test_cancelled_order_brings_the_reason(store):
    order = store.get_order(20, "(67) 98321-6543", TODAY)
    assert order["found"] is True
    assert order["status"] == "cancelado"
    assert order["cancellation_reason"] == "Endereço de entrega inválido informado pelo cliente"
    assert order["late"] is False


def test_description_with_another_brand_is_hidden(store):
    products = {
        p["id"]: p
        for category in ["Baixos", "Baterias e Percussão", "Teclados e Pianos"]
        for p in store.search_products(category=category)["products"]
    }
    assert {135, 137, 138, 139, 140, 141, 142, 143, 144} <= products.keys()
    for hidden in [135, 137, 139, 140, 142, 144]:
        assert products[hidden]["description"] is None
    for shown in [138, 141, 143]:
        assert products[shown]["description"]
