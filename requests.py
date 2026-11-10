from datetime import datetime, date, timezone
from decimal import Decimal

from sqlmodel import Session, select, func

from database import engine
from models import (
    Client, Employee, Courier, Dish, Ingredient, Recipe,
    Order, OrderItem, Payment, Supplier, Supply, SupplyLine,
)


# ============================================================
# БЛОК 1: ЗАКАЗЫ
# ============================================================

def get_order_with_items(order_id: int):
    """Детали заказа: клиент, позиции, блюда, оплата."""
    with Session(engine) as s:
        order = s.get(Order, order_id)
        if not order:
            return None

        client = s.get(Client, order.client_id)

        items_stmt = select(OrderItem).where(OrderItem.order_id == order.id)
        items = []
        for it in s.exec(items_stmt).all():
            dish = s.get(Dish, it.dish_id)
            items.append({
                "dish": dish.name if dish else None,
                "qty": it.quantity,
                "price": float(it.price_at_order),
                "wishes": it.wishes,
            })

        payment = s.exec(select(Payment).where(Payment.order_id == order.id)).first()

        return {
            "order_id": order.id,
            "client": client.full_name if client else None,
            "type": order.order_type,
            "status": order.status,
            "total_sum": float(order.total_sum),
            "items": items,
            "payment": (
                {
                    "method": payment.method,
                    "status": payment.status,
                    "amount": float(payment.amount),
                }
                if payment else None
            ),
        }


def get_orders_by_status(status: str):
    """Все заказы в заданном статусе."""
    with Session(engine) as s:
        stmt = select(Order).where(Order.status == status).order_by(Order.created_at)
        return s.exec(stmt).all()


def get_orders_for_period(start: datetime, end: datetime):
    """Заказы за период."""
    with Session(engine) as s:
        stmt = (select(Order)
                .where(Order.created_at >= start)
                .where(Order.created_at <= end)
                .order_by(Order.created_at))
        return s.exec(stmt).all()


# ============================================================
# БЛОК 2: СКЛАД И РЕЦЕПТУРЫ
# ============================================================

def get_recipe_for_dish(dish_id: int):
    """Состав блюда: ингредиенты и количество."""
    with Session(engine) as s:
        stmt = (select(Recipe, Ingredient)
                .join(Ingredient, Recipe.ingredient_id == Ingredient.id)
                .where(Recipe.dish_id == dish_id))
        return [
            {"ingredient": ing.name, "qty": float(r.quantity), "unit": ing.unit}
            for r, ing in s.exec(stmt).all()
        ]


def get_low_stock(threshold: Decimal = Decimal("1000")):
    """Ингредиенты, которых на складе меньше порога."""
    with Session(engine) as s:
        stmt = select(Ingredient).where(Ingredient.stock_qty < threshold)
        return s.exec(stmt).all()


def calculate_ingredients_needed(dish_id: int, portions: int = 1):
    """Сколько ингредиентов нужно на N порций блюда."""
    with Session(engine) as s:
        stmt = (select(Ingredient.name, Ingredient.unit,
                       (Recipe.quantity * portions).label("need"))
                .join(Recipe, Recipe.ingredient_id == Ingredient.id)
                .where(Recipe.dish_id == dish_id))
        return [
            {"ingredient": name, "need": float(need), "unit": unit}
            for name, unit, need in s.exec(stmt).all()
        ]


# ============================================================
# БЛОК 3: ОТЧЁТНОСТЬ
# ============================================================

def revenue_for_period(start: datetime, end: datetime) -> float:
    """Выручка (сумма оплаченных заказов) за период."""
    with Session(engine) as s:
        stmt = (select(func.coalesce(func.sum(Payment.amount), 0))
                .join(Order, Payment.order_id == Order.id)
                .where(Order.created_at >= start)
                .where(Order.created_at <= end)
                .where(Payment.status == "paid"))
        return float(s.exec(stmt).one())


def top_dishes(limit: int = 5):
    """Самые популярные блюда по количеству проданных порций."""
    with Session(engine) as s:
        stmt = (select(Dish.name, func.sum(OrderItem.quantity).label("sold"))
                .join(OrderItem, OrderItem.dish_id == Dish.id)
                .group_by(Dish.id, Dish.name)
                .order_by(func.sum(OrderItem.quantity).desc())
                .limit(limit))
        return [{"dish": name, "sold": int(sold)} for name, sold in s.exec(stmt).all()]


def orders_count_by_type():
    """Сколько заказов каждого типа."""
    with Session(engine) as s:
        stmt = (select(Order.order_type, func.count(Order.id))
                .group_by(Order.order_type))
        return {t: int(c) for t, c in s.exec(stmt).all()}


def courier_deliveries():
    """Сколько доставок у каждого курьера."""
    with Session(engine) as s:
        stmt = (select(Employee.full_name, func.count(Order.id))
                .join(Courier, Courier.employee_id == Employee.id)
                .join(Order, Order.courier_id == Courier.id)
                .where(Order.order_type == "delivery")
                .group_by(Employee.id, Employee.full_name))
        return {name: int(cnt) for name, cnt in s.exec(stmt).all()}


# ============================================================
# БЛОК 4: ПОСТАВКИ
# ============================================================

def supplies_for_period(start: date, end: date):
    """Поставки за период с поставщиками."""
    with Session(engine) as s:
        stmt = (select(Supply, Supplier)
                .join(Supplier, Supply.supplier_id == Supplier.id)
                .where(Supply.supply_date >= start)
                .where(Supply.supply_date <= end))
        return [
            {"date": supply.supply_date.isoformat(),
             "supplier": supplier.name,
             "sum": float(supply.total_sum)}
            for supply, supplier in s.exec(stmt).all()
        ]


def supply_details(supply_id: int):
    """Детализация одной поставки по ингредиентам."""
    with Session(engine) as s:
        stmt = (select(SupplyLine, Ingredient)
                .join(Ingredient, SupplyLine.ingredient_id == Ingredient.id)
                .where(SupplyLine.supply_id == supply_id))
        return [
            {"ingredient": ing.name, "qty": float(line.quantity),
             "price": float(line.price), "unit": ing.unit}
            for line, ing in s.exec(stmt).all()
        ]


# ============================================================
# ДЕМО-ЗАПУСК
# ============================================================

if __name__ == "__main__":
    print("=== 1. Детали заказа #1 ===")
    print(get_order_with_items(1))

    print("\n=== 2. Заказы со статусом 'closed' ===")
    for o in get_orders_by_status("closed"):
        print(f"  заказ #{o.id}, {o.order_type}, {o.total_sum}")

    print("\n=== 3. Заказы за май 2024 ===")
    for o in get_orders_for_period(datetime(2024, 5, 1, tzinfo=timezone.utc),
                                    datetime(2024, 5, 31, 23, 59, tzinfo=timezone.utc)):
        print(f"  #{o.id}, {o.created_at}, {o.status}")

    print("\n=== 4. Рецепт Маргариты (dish_id=1) ===")
    print(get_recipe_for_dish(1))

    print("\n=== 5. Ингредиенты с остатком < 1000 ===")
    for i in get_low_stock():
        print(f"  {i.name}: {i.stock_qty} {i.unit}")

    print("\n=== 6. Расход на 3 Маргариты ===")
    print(calculate_ingredients_needed(1, 3))

    print("\n=== 7. Выручка за май 2024 ===")
    print(revenue_for_period(datetime(2024, 5, 1, tzinfo=timezone.utc),
                              datetime(2024, 5, 31, 23, 59, tzinfo=timezone.utc)))

    print("\n=== 8. Топ-5 блюд ===")
    print(top_dishes())

    print("\n=== 9. Заказы по типам ===")
    print(orders_count_by_type())

    print("\n=== 10. Доставки курьеров ===")
    print(courier_deliveries())

    print("\n=== 11. Поставки за апрель 2024 ===")
    print(supplies_for_period(date(2024, 4, 1), date(2024, 4, 30)))

    print("\n=== 12. Детали поставки #1 ===")
    print(supply_details(1))