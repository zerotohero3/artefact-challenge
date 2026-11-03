import csv
import json
import re
import unicodedata
from dataclasses import dataclass
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

# Manual §6.2: PIX discount only applies to products without a promotion.
PIX_DISCOUNT = Decimal("0.05")
# Manual §3.1: (max installments, minimum installment value), the specific rule wins over the
# payment table (P-01).
INSTALLMENT_TIERS = [(3, Decimal("50")), (6, Decimal("80")), (12, Decimal("100"))]
# Brands found in product names and descriptions; a description citing a brand that is not in
# the product name belongs to another product.
BRANDS = [
    "Crafter", "Fender", "Giannini", "Gibson", "Ibanez", "Kala", "Kalani", "Korg", "Martin",
    "Music Man", "Nord", "Ohana", "Pearl", "PRS", "Roland", "Rozini", "Shelby", "Tagima",
    "Takamine", "Tama", "Taylor", "Yamaha",
]  # fmt: skip
MAX_RESULTS = 20

AVAILABILITY = {"discontinued": "descontinuado", "coming_soon": "em breve"}
ORDER_STATUS = {
    "pending": "pendente (aguardando confirmação do pagamento)",
    "confirmed": "confirmado (pagamento aprovado, em preparação)",
    "shipped": "enviado",
    "delivered": "entregue",
    "cancelled": "cancelado",
}
PAYMENT = {"pix": "PIX", "debit": "cartão de débito", "boleto": "boleto"}
NOT_FOUND = {"found": False, "message": "Nenhum pedido encontrado com esse número e esse contato."}


def brl(value: Decimal) -> str:
    text = f"{value.quantize(Decimal('0.01'), ROUND_HALF_UP):,.2f}"
    return "R$ " + text.replace(",", "_").replace(".", ",").replace("_", ".")


def installments(price: Decimal) -> str:
    count = 1
    for n in range(2, 13):
        minimum = next(value for limit, value in INSTALLMENT_TIERS if n <= limit)
        if price / n >= minimum:
            count = n
    return f"{count}x de {brl(price / count)} sem juros"


def normalize(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).lower()


def compact(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", normalize(text))


def singular(word: str) -> str:
    for plural, single in [("oes", "ao"), ("aes", "ao"), ("ais", "al"), ("eis", "el")]:
        if word.endswith(plural):
            return word[: -len(plural)] + single
    return word.removesuffix("s")


def mentions(text: str, brand: str) -> bool:
    return re.search(rf"\b{re.escape(brand.lower())}\b", text.lower()) is not None


def br_date(value: date) -> str:
    return value.strftime("%d/%m/%Y")


@dataclass
class Product:
    id: int
    name: str
    category: str
    price: Decimal
    promotion: dict | None
    final_price: Decimal
    availability: str
    description: str | None
    specs: dict

    def matches(self, terms: list[str]) -> bool:
        name = compact(self.name)
        category_words = {singular(w) for w in re.findall(r"[a-z0-9]+", normalize(self.category))}
        return all(
            compact(term) in name or singular(normalize(term)) in category_words for term in terms
        )

    def as_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "price": brl(self.price),
            "promotion": self.promotion,
            "final_price": brl(self.final_price),
            "pix_price": None if self.promotion else brl(self.price * (1 - PIX_DISCOUNT)),
            "installments": installments(self.final_price),
            "availability": self.availability,
            "description": self.description,
            "specs": self.specs,
        }


def read_csv(path: Path) -> list[dict]:
    with path.open(encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def is_holder(customer: dict, contact: str) -> bool:
    contact = contact.strip()
    if "@" in contact:
        return contact.lower() == customer["email"].lower()
    digits = re.sub(r"\D", "", contact)
    if digits.startswith("55") and len(digits) > 11:
        digits = digits[2:]
    registered = re.sub(r"\D", "", customer["phone"])
    return len(digits) >= 8 and registered.endswith(digits)


class Store:
    def __init__(self, products, categories, customers, orders, items):
        self.products = products
        self.category_names = categories
        self.customers = customers
        self.orders = orders
        self.items = items

    @classmethod
    def load(cls, data_dir: Path) -> "Store":
        categories = {
            row["category_id"]: row["name"] for row in read_csv(data_dir / "categories.csv")
        }
        promotions = {}
        for row in read_csv(data_dir / "promotions.csv"):
            current = promotions.get(row["product_id"])
            if row["is_active"] == "1" and (
                current is None or int(row["discount_percent"]) > current["percent"]
            ):
                promotions[row["product_id"]] = {
                    "name": row["description"],
                    "percent": int(row["discount_percent"]),
                }
        products = {}
        for row in read_csv(data_dir / "products.csv"):
            price = Decimal(row["price_brl"])
            promotion = promotions.get(row["product_id"])
            final_price = price * (100 - promotion["percent"]) / 100 if promotion else price
            availability = AVAILABILITY.get(row["status"]) or (
                "disponível" if int(row["stock_quantity"]) > 0 else "esgotado"
            )
            description = row["description"]
            if any(mentions(description, b) and not mentions(row["name"], b) for b in BRANDS):
                description = None
            products[int(row["product_id"])] = Product(
                id=int(row["product_id"]),
                name=row["name"],
                category=categories[row["category_id"]],
                price=price,
                promotion=promotion,
                final_price=final_price.quantize(Decimal("0.01"), ROUND_HALF_UP),
                availability=availability,
                description=description,
                specs=json.loads(row["specs"]),
            )
        items = {}
        for row in read_csv(data_dir / "order_items.csv"):
            items.setdefault(int(row["order_id"]), []).append(
                {"product": products[int(row["product_id"])].name, "quantity": int(row["quantity"])}
            )
        return cls(
            products=products,
            categories=list(categories.values()),
            customers={row["customer_id"]: row for row in read_csv(data_dir / "customers.csv")},
            orders={int(row["order_id"]): row for row in read_csv(data_dir / "orders.csv")},
            items=items,
        )

    def search_products(
        self, query=None, category=None, min_price=None, max_price=None, only_available=False
    ) -> dict:
        found = list(self.products.values())
        if category:
            names = {normalize(name): name for name in self.category_names}
            if normalize(category) not in names:
                return {
                    "error": f"Categoria desconhecida: {category}. "
                    f"Categorias: {', '.join(self.category_names)}."
                }
            found = [p for p in found if p.category == names[normalize(category)]]
        if query:
            terms = query.split()
            found = [p for p in found if p.matches(terms)]
        if min_price is not None:
            found = [p for p in found if p.final_price >= Decimal(str(min_price))]
        if max_price is not None:
            found = [p for p in found if p.final_price <= Decimal(str(max_price))]
        if only_available:
            found = [p for p in found if p.availability == "disponível"]
        found.sort(key=lambda p: (p.final_price, p.id))
        return {"total": len(found), "products": [p.as_dict() for p in found[:MAX_RESULTS]]}

    def get_order(self, order_id: int, contact: str, today: date) -> dict:
        order = self.orders.get(order_id)
        if order is None:
            return dict(NOT_FOUND)
        customer = self.customers[order["customer_id"]]
        if not is_holder(customer, contact):
            return dict(NOT_FOUND)
        ordered_on = date.fromisoformat(order["order_date"])
        estimate = (
            date.fromisoformat(order["estimated_delivery"]) if order["estimated_delivery"] else None
        )
        payment = order["payment_method"]
        return {
            "found": True,
            "order_id": order_id,
            "customer_first_name": customer["name"].split()[0],
            "status": ORDER_STATUS[order["status"]],
            "order_date": br_date(ordered_on),
            "items": self.items.get(order_id, []),
            "total": brl(Decimal(order["total_brl"])),
            "payment": PAYMENT.get(payment)
            or f"cartão de crédito em {payment.removeprefix('credit_')}",
            "tracking_code": order["tracking_code"] or None,
            "estimated_delivery": br_date(estimate) if estimate else None,
            "days_since_order": (today - ordered_on).days,
            "days_since_estimated_delivery": (today - estimate).days if estimate else None,
            "late": order["status"] == "shipped" and estimate is not None and estimate < today,
            "cancellation_reason": order["notes"] if order["status"] == "cancelled" else None,
        }
