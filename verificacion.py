from decimal import Decimal
from cargar_csv import load_fixture
from app.specification import (
    MinimumAmountSpec,
    VIPCustomerSpec,
    MinimumUnitsSpec,
    ActivePromotionSpec
)

def ejecutar_verificacion():
    orders = load_fixture()

    # Definición de reglas
    ten_percent = (
        MinimumAmountSpec(Decimal("500"))
        & VIPCustomerSpec()
        & MinimumUnitsSpec(4)
        & ~ActivePromotionSpec()
    )

    five_percent = (
        MinimumAmountSpec(Decimal("5000"))
        & ~ActivePromotionSpec()
    )

    # Casos orientativos a verificar
    casos = ["O001", "O006", "O005", "O010"]

    print("=== VERIFICACIÓN DE REGLAS DE DESCUENTO ===")
    for order_id in casos:
        order = orders.get(order_id)
        if not order:
            continue
        
        aplica_10 = ten_percent.is_satisfied_by(order)
        aplica_5 = five_percent.is_satisfied_by(order)

        print(f"\nPedido: {order.id}")
        print(f"  - Total: {order.total.amount} MXN | Unidades: {order.units}")
        print(f"  - Cliente VIP: {order.customer.is_vip} | Promo activa: {order.has_promotion}")
        print(f"  - ¿Aplica 10%?: {aplica_10}")
        print(f"  - ¿Aplica 5%?: {aplica_5}")

        if aplica_10:
            print("  -> Resultado: Descuento del 10% aplicado.")
        elif aplica_5:
            print("  -> Resultado: Descuento alternativo del 5% aplicado.")
        else:
            print("  -> Resultado: Sin descuento (excluido o no cumple umbrales).")

if __name__ == "__main__":
    ejecutar_verificacion()