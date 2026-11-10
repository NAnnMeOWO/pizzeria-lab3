from datetime import date, datetime, timezone
from decimal import Decimal

from sqlmodel import Session

from database import engine, create_db_and_tables
from models import (
    Client, Employee, Courier, Shift, MenuCategory, Dish,
    Ingredient, Recipe, Order, OrderItem, PaymentSystem, Payment,
    Supplier, Supply, SupplyLine,
)


def seed():
    create_db_and_tables()

    with Session(engine) as s:
        # ---------- Клиенты ----------
        c1 = Client(full_name="Иван Иванов", phone="+79001112233",
                    email="ivan@mail.ru", address="ул. Ленина, 1")
        c2 = Client(full_name="Мария Петрова", phone="+79004445566",
                    address="ул. Пушкина, 10")
        s.add_all([c1, c2])

        # ---------- Сотрудники ----------
        e1 = Employee(full_name="Пётр Поваров", position="повар",
                      phone="+79007778899", hire_date=date(2023, 1, 15))
        e2 = Employee(full_name="Ольга Официантова", position="официант",
                      phone="+79001231234", hire_date=date(2023, 5, 1))
        e3 = Employee(full_name="Сергей Курьеров", position="курьер",
                      phone="+79005556677", hire_date=date(2023, 6, 10))
        s.add_all([e1, e2, e3])
        s.commit()

        # ---------- Курьер ----------
        courier = Courier(employee_id=e3.id, transport="авто",
                          delivery_zone="Центральный")
        s.add(courier)

        # ---------- Смены ----------
        s.add_all([
            Shift(employee_id=e2.id, shift_date=date(2024, 5, 1),
                  start_time=datetime(2024, 5, 1, 9, 0, tzinfo=timezone.utc),
                  end_time=datetime(2024, 5, 1, 18, 0, tzinfo=timezone.utc),
                  role_in_shift="официант"),
            Shift(employee_id=e1.id, shift_date=date(2024, 5, 1),
                  start_time=datetime(2024, 5, 1, 10, 0, tzinfo=timezone.utc),
                  end_time=datetime(2024, 5, 1, 20, 0, tzinfo=timezone.utc),
                  role_in_shift="повар"),
        ])

        # ---------- Категории и блюда ----------
        cat_pizza = MenuCategory(name="Пицца")
        cat_drink = MenuCategory(name="Напитки")
        s.add_all([cat_pizza, cat_drink])
        s.commit()

        d1 = Dish(category_id=cat_pizza.id, name="Маргарита", dish_type="пицца",
                  description="Томат, моцарелла, базилик", price=Decimal("450.00"),
                  size="30 см", is_available=True)
        d2 = Dish(category_id=cat_pizza.id, name="Пепперони", dish_type="пицца",
                  description="Пепперони, моцарелла", price=Decimal("550.00"),
                  size="30 см", is_available=True)
        d3 = Dish(category_id=cat_drink.id, name="Кола", dish_type="напиток",
                  description="0.5 л", price=Decimal("120.00"), is_available=True)
        s.add_all([d1, d2, d3])
        s.commit()

        # ---------- Ингредиенты ----------
        ing1 = Ingredient(name="Моцарелла", unit="г",
                          stock_qty=Decimal("5000"), purchase_price=Decimal("0.8"))
        ing2 = Ingredient(name="Томатный соус", unit="г",
                          stock_qty=Decimal("3000"), purchase_price=Decimal("0.4"))
        ing3 = Ingredient(name="Пепперони", unit="г",
                          stock_qty=Decimal("2000"), purchase_price=Decimal("1.2"))
        s.add_all([ing1, ing2, ing3])
        s.commit()

        # ---------- Рецептуры ----------
        s.add_all([
            Recipe(dish_id=d1.id, ingredient_id=ing1.id, quantity=Decimal("150")),
            Recipe(dish_id=d1.id, ingredient_id=ing2.id, quantity=Decimal("100")),
            Recipe(dish_id=d2.id, ingredient_id=ing1.id, quantity=Decimal("150")),
            Recipe(dish_id=d2.id, ingredient_id=ing3.id, quantity=Decimal("80")),
        ])

        # ---------- Заказ 1: в зале, оплата картой ----------
        o1 = Order(client_id=c1.id, employee_id=e2.id, order_type="in_hall",
                   status="closed", total_sum=Decimal("1020.00"),
                   created_at=datetime(2024, 5, 1, 12, 30, tzinfo=timezone.utc))
        s.add(o1)
        s.commit()
        s.add_all([
            OrderItem(order_id=o1.id, dish_id=d1.id, quantity=1,
                      price_at_order=Decimal("450.00")),
            OrderItem(order_id=o1.id, dish_id=d2.id, quantity=1,
                      price_at_order=Decimal("550.00")),
            OrderItem(order_id=o1.id, dish_id=d3.id, quantity=1,
                      price_at_order=Decimal("120.00"), wishes="без льда"),
        ])
        s.add(Payment(order_id=o1.id, amount=Decimal("1020.00"),
                      method="card", status="paid",
                      paid_at=datetime(2024, 5, 1, 13, 0, tzinfo=timezone.utc)))

        # ---------- Заказ 2: доставка, онлайн ----------
        o2 = Order(client_id=c2.id, employee_id=e2.id, courier_id=courier.id,
                   order_type="delivery", status="delivered",
                   total_sum=Decimal("550.00"),
                   created_at=datetime(2024, 5, 2, 18, 0, tzinfo=timezone.utc))
        s.add(o2)
        s.commit()
        s.add(OrderItem(order_id=o2.id, dish_id=d2.id, quantity=1,
                        price_at_order=Decimal("550.00")))

        ps = PaymentSystem(name="ЮKassa", external_payment_id="ext-123",
                           status="success")
        s.add(ps)
        s.commit()
        s.add(Payment(order_id=o2.id, payment_system_id=ps.id,
                      amount=Decimal("550.00"), method="online",
                      status="paid",
                      paid_at=datetime(2024, 5, 2, 18, 5, tzinfo=timezone.utc)))

        # ---------- Поставка ----------
        sup = Supplier(name="ООО Молоко", contact_person="Анна",
                       phone="+79009990000")
        s.add(sup)
        s.commit()
        supply = Supply(supplier_id=sup.id, supply_date=date(2024, 4, 30),
                        total_sum=Decimal("7000.00"))
        s.add(supply)
        s.commit()
        s.add_all([
            SupplyLine(supply_id=supply.id, ingredient_id=ing1.id,
                       quantity=Decimal("5000"), price=Decimal("0.8")),
            SupplyLine(supply_id=supply.id, ingredient_id=ing2.id,
                       quantity=Decimal("3000"), price=Decimal("0.4")),
        ])

        s.commit()
        print("Seed data inserted.")


if __name__ == "__main__":
    seed()