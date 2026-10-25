from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum
from datetime import datetime, timezone

class DomainException(Exception): pass
class InvalidOrderData(DomainException): pass
class InvalidOrderTransition(DomainException): pass
class OrderItemLimitExceeded(DomainException): pass

## Money: representar dinero correctamente
### Value Object
@dataclass(frozen=True)
class Money: 
    amount: Decimal
    currency: str = "MXN"

    def __post_init__(self): 
        if not self.amount.is_finite() or self.amount < 0: 
            raise InvalidOrderData("Monto inválido")

    def add(self, other): 
        if self.currency != other.currency: 
            raise InvalidOrderData("Monedas distintas")
        return Money(self.amount + other.amount, self.currency)

## Customer y OrderItem
@dataclass(frozen=True)
class Customer: 
    id: str
    is_vip: bool = False
    activate: bool = True

@dataclass(frozen=True)
class OrderItem: 
    sku: str
    quantity: int
    unit_price: Money

    def __post_init__(self): 
        if not self.sku.strip() or self.quantity <= 0: 
            raise InvalidOrderData("Articulo Inválido")

    @property # Hace que se trate como un atributo el subtotal
    def subtotal(self): 
        return Money(self.unit_price.amount * self.quantity)

## Order como Aggregate Root
class OrderStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    RETURNED = "RETURNED"

@dataclass
class Order: 
    customer: Customer
    id: str
    has_promotion: bool = False
    status: OrderStatus = OrderStatus.DRAFT
    items: list[OrderItem] = field(default_factory=list)
    events: list = field(default_factory=list)

    @property
    def total(self): 
        amount = sum((x.subtotal.amount for x in self.items), Decimal("0"))
        return Money(amount)

    @property
    def units(self):
        return sum(item.quantity for item in self.items)

    def add_item(self, item): 
        if self.status != OrderStatus.DRAFT:
            raise InvalidOrderTransition("Solo DRAFT admite artículos")
        if self.units + item.quantity > 20:
            raise OrderItemLimitExceeded("Máximo 20 unidades")
        if item.unit_price.currency != "MXN":
            raise InvalidOrderData("Solo MXN")
        self.items.append(item)
