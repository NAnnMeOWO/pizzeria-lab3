from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List

from sqlmodel import SQLModel, Field, Relationship


# ============================================================
# БЛОК 1: СПРАВОЧНИКИ И МЕНЮ
# ============================================================

class Client(SQLModel, table=True):
    __tablename__ = "client"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=150)
    phone: str = Field(max_length=20)
    email: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=255)


class Employee(SQLModel, table=True):
    __tablename__ = "employee"

    id: Optional[int] = Field(default=None, primary_key=True)
    full_name: str = Field(max_length=150)
    position: str = Field(max_length=50)
    phone: str = Field(max_length=20)
    hire_date: date


class Courier(SQLModel, table=True):
    __tablename__ = "courier"

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id", unique=True)
    transport: str = Field(max_length=50)
    delivery_zone: str = Field(max_length=100)


class Shift(SQLModel, table=True):
    __tablename__ = "shift"

    id: Optional[int] = Field(default=None, primary_key=True)
    employee_id: int = Field(foreign_key="employee.id")
    shift_date: date
    start_time: datetime
    end_time: Optional[datetime] = None
    role_in_shift: str = Field(max_length=50)


class MenuCategory(SQLModel, table=True):
    __tablename__ = "menu_category"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, unique=True)


class Dish(SQLModel, table=True):
    __tablename__ = "dish"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="menu_category.id")
    name: str = Field(max_length=100)
    dish_type: str = Field(max_length=50)
    description: Optional[str] = Field(default=None, max_length=255)
    price: Decimal = Field(max_digits=10, decimal_places=2)
    size: Optional[str] = Field(default=None, max_length=20)
    is_available: bool = Field(default=True)


# ============================================================
# БЛОК 2: СКЛАД И РЕЦЕПТУРЫ
# ============================================================

class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredient"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100, unique=True)
    unit: str = Field(max_length=20)
    stock_qty: Decimal = Field(default=0, max_digits=12, decimal_places=3)
    purchase_price: Decimal = Field(max_digits=10, decimal_places=2)


class Recipe(SQLModel, table=True):
    """M:N Блюдо — Ингредиент (ассоциативная таблица)."""
    __tablename__ = "recipe"

    dish_id: int = Field(foreign_key="dish.id", primary_key=True)
    ingredient_id: int = Field(foreign_key="ingredient.id", primary_key=True)
    quantity: Decimal = Field(max_digits=12, decimal_places=3)


# ============================================================
# БЛОК 3: ЗАКАЗЫ И ОПЛАТА
# ============================================================

class Order(SQLModel, table=True):
    __tablename__ = "order"

    id: Optional[int] = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    employee_id: int = Field(foreign_key="employee.id")
    courier_id: Optional[int] = Field(default=None, foreign_key="courier.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    order_type: str = Field(max_length=20)
    status: str = Field(max_length=20)
    total_sum: Decimal = Field(default=0, max_digits=12, decimal_places=2)


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_item"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id")
    dish_id: int = Field(foreign_key="dish.id")
    quantity: int = Field(default=1)
    price_at_order: Decimal = Field(max_digits=10, decimal_places=2)
    wishes: Optional[str] = Field(default=None, max_length=255)


class PaymentSystem(SQLModel, table=True):
    __tablename__ = "payment_system"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50)
    external_payment_id: Optional[str] = Field(default=None, max_length=100)
    status: Optional[str] = Field(default=None, max_length=30)


class Payment(SQLModel, table=True):
    __tablename__ = "payment"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="order.id", unique=True)
    payment_system_id: Optional[int] = Field(default=None, foreign_key="payment_system.id")
    paid_at: datetime = Field(default_factory=datetime.utcnow)
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    method: str = Field(max_length=20)
    status: str = Field(max_length=20)


# ============================================================
# БЛОК 4: ПОСТАВКИ
# ============================================================

class Supplier(SQLModel, table=True):
    __tablename__ = "supplier"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=150)
    contact_person: Optional[str] = Field(default=None, max_length=150)
    phone: Optional[str] = Field(default=None, max_length=20)


class Supply(SQLModel, table=True):
    __tablename__ = "supply"

    id: Optional[int] = Field(default=None, primary_key=True)
    supplier_id: int = Field(foreign_key="supplier.id")
    supply_date: date
    total_sum: Decimal = Field(default=0, max_digits=12, decimal_places=2)


class SupplyLine(SQLModel, table=True):
    __tablename__ = "supply_line"

    id: Optional[int] = Field(default=None, primary_key=True)
    supply_id: int = Field(foreign_key="supply.id")
    ingredient_id: int = Field(foreign_key="ingredient.id")
    quantity: Decimal = Field(max_digits=12, decimal_places=3)
    price: Decimal = Field(max_digits=10, decimal_places=2)