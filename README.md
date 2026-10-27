# TechStore - Sistema de Administración de Pedidos (U4)

Repositorio para la administración de pedidos de una tienda ficticia mediante un núcleo de negocio robusto, Patrón Specification, Máquina de Estados, Domain Events, API REST con FastAPI y pruebas automatizadas con pytest.

---

##  Estructura del Repositorio

unidad4-techstore/
│
├── app/
│   ├── init.py
│   ├── domain.py         # Entidades, Value Objects, Excepciones y Máquina de Estados
│   ├── specifications.py # Reglas de descuento (Patrón Specification y operadores &, |, ~)
│   └── api.py            # Endpoints de la API REST con FastAPI
│
├── tests/
│   └── test_domain.py    # Pruebas unitarias e integración con pytest
│
├── datos/                # Archivos CSV (clientes, productos, pedidos, detalle, escenarios)
├── cargar_csv.py         # Cargador de fixtures e inicializador de objetos
├── .gitignore            # Exclusión de .venv y pycache
└── README.md             # Documentación principal

## ⚙️ Pasos de Instalación y Ejecución

1. **Clonar el repositorio y abrir la terminal** en la carpeta del proyecto.
2. **Crear y activar el entorno virtual**:
   ```bash
   python -m venv .venv
   # Windows PowerShell:
   .venv\Scripts\Activate.ps1
   # macOS / Linux:
   source .venv/bin/activate

Instalar las dependencias:
python -m pip install fastapi uvicorn pytest httpx

Cargar y verificar los datos (16 pedidos):
python cargar_csv.py

Ejecutar la API REST con FastAPI:
uvicorn app.api:app --reload

Ejecutar las pruebas automatizadas (pytest):
python -m pytest -q

## Reglas de Negocio Principales

1. **Monto y Divisa (`Money`)**: Inmutable, almacena montos en `Decimal` (MXN). Rechaza montos negativos y divisas distintas en sumas.
2. **Límite de Artículos (`OrderItem`)**: Un pedido admite un **máximo de 20 unidades** en total (suma de cantidades, no de renglones). Si se supera, lanza `OrderItemLimitExceeded`.
3. **Reglas de Descuento (Specification Pattern)**:
   * **Descuento del 10%**: Requiere cliente VIP (`is_vip=True`), cliente activo, total mayor a $500 MXN (`> 500`), al menos 4 unidades (`>= 4`) y sin promoción activa (`~ActivePromotionSpec`).
   * **Descuento del 5%**: Total mayor a $5000 MXN (`> 5000`) y sin promoción activa, combinados mediante operador `OR`.
4. **Máquina de Estados y Ciclo de Vida**:
   * **Estados**: `DRAFT` ➔ `CONFIRMED` ➔ `SHIPPED` ➔ `DELIVERED` o `RETURNED` (también admite `CANCELLED` desde `CONFIRMED`).
   * Cada transición válida registra su respectivo **Domain Event** (`OrderConfirmed`, `OrderShipped`, `OrderCancelled`, `OrderDelivered`, `OrderReturned`). Las operaciones inválidas no alteran el estado ni generan eventos.

---

## Endpoints de la API REST

* `GET /orders/{order_id}` - Consulta el estado, unidades y total de un pedido.
* `POST /orders/{order_id}/confirm` - Confirma un pedido en estado `DRAFT`.
* `POST /orders/{order_id}/ship` - Envía un pedido confirmado requiriendo un número de guía (`tracking_number`).
* `POST /orders/{order_id}/cancel` - Cancela un pedido confirmado indicando un motivo.