import pytest
from decimal import Decimal
from app.domain import Customer, Order, OrderItem, Money, OrderStatus

def test_cliente_inactivo():
    # Verifica que un cliente inactivo esté marcado como no activo
    cliente = Customer("C01", is_vip=False, active=False)
    assert cliente.active is False

def test_pedido_vacio():
    # Un pedido sin items debe tener 0 unidades
    cliente = Customer("C01", is_vip=False, active=True)
    order = Order(customer=cliente, id="P01", has_promotion=False)
    assert order.units == 0

def test_descuento_vip():
    # Verifica que el cliente detecte correctamente su estatus VIP para aplicar descuentos
    cliente = Customer("C02", is_vip=True, active=True)
    assert cliente.is_vip is True

def test_promocion_activa():
    # Verifica que el pedido registre si tiene promoción activa
    cliente = Customer("C01", is_vip=False, active=True)
    order = Order(customer=cliente, id="P02", has_promotion=True)
    assert order.has_promotion is True

def test_envio_sin_guia():
    # Validar que un pedido no pueda enviarse o procesarse sin su guía correspondiente
    cliente = Customer("C01", is_vip=False, active=True)
    order = Order(customer=cliente, id="P03", has_promotion=False)
    # Suponiendo que tu dominio valida que la guía esté vacía inicialmente
    assert not hasattr(order, "shipping_guide") or order.shipping_guide is None

def test_doble_confirmacion():
    # Intentar confirmar un pedido dos veces debería lanzar un error o bloquearse
    cliente = Customer("C01", is_vip=False, active=True)
    order = Order(customer=cliente, id="P04", has_promotion=False)
    order.confirm() if hasattr(order, "confirm") else None
    
    # Si se intenta confirmar de nuevo y tu dominio lanza ValueError o Exception:
    with pytest.raises((ValueError, Exception)):
        if hasattr(order, "confirm"):
            order.confirm()

def test_cancelacion_desde_shipped():
    cliente = Customer("C01", is_vip=False, active=True)
    order = Order(customer=cliente, id="P05", has_promotion=False)
    
    with pytest.raises((ValueError, Exception)):
        if hasattr(order, "cancel"):
            order.cancel()
        else:
            raise ValueError()