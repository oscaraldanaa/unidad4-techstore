"""Ejecuta los escenarios E01-E15 de datos/escenarios.csv sin modificar pedidos ni reglas.
Cada caso recarga load_fixture() para partir de un estado limpio.
Genera bitacora.csv y bitacora.md (caso, estado inicial, operación, resultado real, explicación).
"""
import csv
from decimal import Decimal
from cargar_csv import load_fixture
from app.domain import OrderItem, Money, DomainException
from app.specification import ten_percent, five_percent

NO_EVENTO = "sin evento"


def snap(o):
    return f"{o.status.value}, {o.units} uds, ${o.total.amount} MXN"


def describe_client(o):
    c = o.customer
    return (f"{c.id}: {'VIP' if c.is_vip else 'no VIP'}, "
            f"{'activo' if c.activate else 'inactivo'}, "
            f"{'con promo' if o.has_promotion else 'sin promo'}")


def ev(o, since=0):
    names = [e.name for e in o.events[since:]]
    return ", ".join(names) if names else NO_EVENTO


def try_op(label, fn, o):
    """Ejecuta fn; devuelve (ok, texto). Captura excepciones de dominio."""
    n = len(o.events)
    try:
        fn()
        return True, f"{label}: OK -> {o.status.value}, evento: {ev(o, n)}"
    except DomainException as exc:
        return False, (f"{label}: {type(exc).__name__}(\"{exc}\") -> "
                       f"estado sigue {o.status.value}, evento: {NO_EVENTO}")


def discount(o):
    t = o.total.amount
    r10, r5 = ten_percent.is_satisfied_by(o), five_percent.is_satisfied_by(o)
    pct = Decimal("10") if r10 else Decimal("5") if r5 else Decimal("0")
    desc = t * pct / 100
    return pct, desc, t - desc, r10, r5


def run_discount(cid, oid, why):
    o = load_fixture()[oid]
    inicial = f"{oid} {describe_client(o)}; {snap(o)}"
    pct, desc, final, r10, r5 = discount(o)
    real = (f"Regla 10%={r10}, regla 5%={r5} -> descuento {pct}% "
            f"(-${desc}); total final ${final}. Estado {o.status.value}, {NO_EVENTO} (no es transición)")
    return cid, inicial, "evaluar_descuento", real, why


def main():
    log = []

    # E01-E05 descuentos
    log.append(run_discount("E01", "O001",
        "VIP, total 2100>500, 4 uds>=4 y sin promo: cumple las 4 condiciones del AND -> 10%."))
    log.append(run_discount("E02", "O002",
        "No VIP falla el AND del 10%; total 1050 no supera 5000 -> 0%."))
    # E03 confirmar O003
    o = load_fixture()["O003"]
    ini = f"O003 {describe_client(o)}; {snap(o)}"
    ok, txt = try_op("confirm()", o.confirm, o)
    log.append(("E03", ini, "confirm()", txt,
        "El cliente es VIP pero está inactivo: confirm() exige cliente activo -> InvalidOrderData; no hay transición ni evento."))
    log.append(run_discount("E04", "O005",
        "Promoción activa: ~ActivePromotion falla en ambas reglas -> 0% aunque sea VIP con 4 uds y total 2100."))
    log.append(run_discount("E05", "O006",
        "No VIP y 1 unidad (falla el AND del 10%) pero total 18000>5000 y sin promo -> regla 5% (OR)."))

    # E06 confirmar vacío
    o = load_fixture()["O007"]
    ini = f"O007 {describe_client(o)}; {snap(o)}"
    ok, txt = try_op("confirm()", o.confirm, o)
    log.append(("E06", ini, "confirm()", txt,
        "Pedido sin artículos: confirm() exige al menos un artículo -> InvalidOrderData; sin evento."))

    # E07 confirmar 20 unidades
    o = load_fixture()["O008"]
    ini = f"O008 {describe_client(o)}; {snap(o)}"
    ok, txt = try_op("confirm()", o.confirm, o)
    log.append(("E07", ini, "confirm()", txt,
        "20 unidades es el máximo permitido (límite es >20); cliente activo y con artículos -> DRAFT->CONFIRMED y se emite OrderConfirmed."))

    # E08 agregar SKU003 x2 a O009
    o = load_fixture()["O009"]
    ini = f"O009 {describe_client(o)}; {snap(o)}"
    price = Money(Decimal("120.00"))
    ok, txt = try_op("add_item(SKU003 x2)", lambda: o.add_item(OrderItem("SKU003", 2, price)), o)
    txt += f"; después: {snap(o)}"
    log.append(("E08", ini, "add_item(SKU003 x2)", txt,
        "19+2=21 unidades > 20 -> OrderItemLimitExceeded; el pedido queda sin cambios y no se emite evento."))

    log.append(run_discount("E09", "O010",
        "Total exacto 500.00 (SKU003 120 + SKU009 380): la regla usa '>' estricto, 500 no es >500 -> 0%."))
    log.append(run_discount("E10", "O011",
        "VIP y total 1500>500 pero solo 3 uds (<4): falla MinimumUnits; tampoco supera 5000 -> 0%."))

    # E11 confirmar y enviar sin guía
    o = load_fixture()["O012"]
    ini = f"O012 {describe_client(o)}; {snap(o)}"
    ok1, t1 = try_op("confirm()", o.confirm, o)
    ok2, t2 = try_op("ship('')", lambda: o.ship(""), o)
    log.append(("E11", ini, "confirm(); ship('') sin guía", f"{t1} | {t2}",
        "La confirmación es válida (OrderConfirmed). ship() exige tracking_number -> InvalidOrderData; sigue CONFIRMED y no hay OrderShipped."))

    # E12 confirmar dos veces
    o = load_fixture()["O013"]
    ini = f"O013 {describe_client(o)}; {snap(o)}"
    ok1, t1 = try_op("confirm() #1", o.confirm, o)
    ok2, t2 = try_op("confirm() #2", o.confirm, o)
    log.append(("E12", ini, "confirm(); confirm()", f"{t1} | {t2}",
        "La 2.ª llamada parte de CONFIRMED y confirm() solo admite DRAFT -> InvalidOrderTransition; solo hay un OrderConfirmed."))

    # E13 confirmar, enviar, cancelar
    o = load_fixture()["O014"]
    ini = f"O014 {describe_client(o)}; {snap(o)}"
    _, t1 = try_op("confirm()", o.confirm, o)
    _, t2 = try_op("ship('TRK-014')", lambda: o.ship("TRK-014"), o)
    _, t3 = try_op("cancel('cambio de opinión')", lambda: o.cancel("cambio de opinión"), o)
    log.append(("E13", ini, "confirm(); ship(guía); cancel(motivo)", f"{t1} | {t2} | {t3}",
        "cancel() solo admite CONFIRMED; desde SHIPPED -> InvalidOrderTransition. Eventos finales: OrderConfirmed, OrderShipped (sin OrderCancelled)."))

    # E14 devolución
    o = load_fixture()["O015"]
    ini = f"O015 {describe_client(o)}; {snap(o)}"
    _, t1 = try_op("confirm()", o.confirm, o)
    _, t2 = try_op("ship('TRK-015')", lambda: o.ship("TRK-015"), o)
    _, t3 = try_op("return_order()", o.return_order, o)
    log.append(("E14", ini, "confirm(); ship(guía); return_order()", f"{t1} | {t2} | {t3}",
        "Secuencia válida DRAFT->CONFIRMED->SHIPPED->RETURNED; return_order() sí admite SHIPPED. Estado final RETURNED."))

    # E15 entrega
    o = load_fixture()["O016"]
    ini = f"O016 {describe_client(o)}; {snap(o)}"
    _, t1 = try_op("confirm()", o.confirm, o)
    _, t2 = try_op("ship('TRK-016')", lambda: o.ship("TRK-016"), o)
    _, t3 = try_op("deliver()", o.deliver, o)
    log.append(("E15", ini, "confirm(); ship(guía); deliver()", f"{t1} | {t2} | {t3}",
        "Secuencia válida DRAFT->CONFIRMED->SHIPPED->DELIVERED. Estado final DELIVERED."))

    cols = ["Caso", "Estado inicial", "Operación", "Resultado real", "Explicación"]
    with open("bitacora.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(log)
    with open("bitacora.md", "w", encoding="utf-8") as f:
        f.write("| " + " | ".join(cols) + " |\n|" + "---|" * len(cols) + "\n")
        for r in log:
            f.write("| " + " | ".join(str(x).replace("|", "/") for x in r) + " |\n")
    for r in log:
        print("\n".join(f"{c}: {v}" for c, v in zip(cols, r)))
        print("-" * 70)


if __name__ == "__main__":
    main()
