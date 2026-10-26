from domain import Order
from decimal import Decimal
class Specification:
    def is_satisfied_by(self, order):
        raise NotImplementedError

    def __and__(self, other):
        return AndSpec(self, other)
    def __or__(self, other):
        return OrSpec(self, other)
    def __invert__(self):
        return NotSpec(self)

# And
class AndSpec(Specification):
    def __init__(self, left, right):
        self.left, self.right = left, right
    def is_satisfied_by(self, order):
        return (self.left.is_satisfied_by(order)
                and self.right.is_satisfied_by(order))

class OrSpec(Specification): 
    def __init__(self, left, right): 
        self.left, self.right = left, right
    def is_satisfied_by(self, order): 
        return (self.left.is_satisfied_by(order) 
                or self.right.is_satisfied_by(order))

class NotSpec(Specification): 
    def __init__(self, left): 
        self.left = left
    def is_satisfied_by(self, order): 
        return (not self.left.is_satisfied_by(order))


## Minima cantidad
class MinimumAmountSpec(Specification): 
    def __init__(self, min_amount): 
        self.min_amount = min_amount  # Guardamos el umbral (ej. Decimal("500"))

    def is_satisfied_by(self, order): 
        # Comparamos el total de la orden usando estrictamente mayor (>)
        return order.total.amount > self.min_amount

## Verifica si el cliente asociado al pedido es VIP
class VIPCustomerSpec(Specification): 
    def is_satisfied_by(self, order): 
        return order.customer.is_vip

## Recibe un número de unidades (en este caso, la regla pide exigir al menos 4 unidades).   
## Verifica que order.units sea mayor o igual a ese número (>= 4).

class MinimumUnitsSpec(Specification): 
    def __init__(self, min_units=4): 
        self.min_units = min_units

    def is_satisfied_by(self, order): 
        return order.units >= self.min_units

## Verifica si la orden cuenta con una promoción activa 
class ActivePromotionSpec(Specification):
    def is_satisfied_by(self, order): 
        return order.has_promotion

# Regla de descuento de 10 %:
ten_percent = (
    MinimumAmountSpec(Decimal("500"))
    & VIPCustomerSpec()
    & MinimumUnitsSpec(4)
    & ~ActivePromotionSpec()
)

# Regla de 5 %: total > 5000 y SIN promoción.
five_percent = (
    MinimumAmountSpec(Decimal("5000"))
    & ~ActivePromotionSpec()
)

# Combina ambas reglas con OR (si ambas se cumplen, 
# se prioriza la del 10% según el orden de evaluación o la lógica que definas)
discount_rule = ten_percent | five_percent
