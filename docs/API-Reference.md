# Oracle Fusion Client Mock - API Reference

Complete API reference for the Oracle Fusion Mock Client library.

## Table of Contents

- [Module: Procurement](#module-procurement)
  - [OracleFusionMockClient](#oraclefusionmockclient)
  - [PurchaseOrderService](#purchaseorderservice)
  - [SupplierService](#supplierservice)
  - [RequisitionService](#requisitionservice)
  - [DraftPurchaseOrderService](#draftpurchaseorderservice)
  - [AgreementService](#agreementservice)
  - [AcknowledgmentService](#acknowledgmentservice)
- [Module: Sales Orders](#module-sales-orders)
  - [SalesOrderMockClient](#salesordermockclient)
  - [SalesOrderMockOperations](#salesordermockoperations)
  - [Models](#sales-order-models)
- [Common Types](#common-types)

---

## Module: Procurement

### OracleFusionMockClient

Main facade class providing access to all Procurement services.

```python
from oracle_fusion_mock import OracleFusionMockClient
```

#### Constructor

```python
OracleFusionMockClient(data_path: str | Path | None = None)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `data_path` | `str \| Path \| None` | `None` | Path to custom db.json file. If None, uses default location. |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `purchase_orders` | `PurchaseOrderService` | Access to Purchase Orders service |
| `draft_purchase_orders` | `DraftPurchaseOrderService` | Access to Draft POs service |
| `suppliers` | `SupplierService` | Access to Suppliers service |
| `requisitions` | `RequisitionService` | Access to Requisitions service |
| `agreements` | `AgreementService` | Access to Agreements service |
| `acknowledgments` | `AcknowledgmentService` | Access to Acknowledgments service |

#### Context Manager

```python
async with OracleFusionMockClient() as client:
    # Use client
    pass
```

---

### PurchaseOrderService

Access via `client.purchase_orders`

#### Methods

##### `list()`

List purchase orders with optional filtering and pagination.

```python
async def list(
    limit: int = 25,
    offset: int = 0,
    query: str | None = None,
    expand: list[str] | None = None,
    order_by: str | None = None
) -> OracleCollectionResponse[PurchaseOrder]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | `int` | `25` | Maximum items per page (1-500) |
| `offset` | `int` | `0` | Number of items to skip |
| `query` | `str \| None` | `None` | Filter query (e.g., `"StatusCode='OPEN'"`) |
| `expand` | `list[str] \| None` | `None` | Child resources to include |
| `order_by` | `str \| None` | `None` | Sort order (e.g., `"CreationDate:desc"`) |

**Returns:** `OracleCollectionResponse[PurchaseOrder]`

**Example:**
```python
orders = await client.purchase_orders.list(
    limit=10,
    query="StatusCode='OPEN'",
    order_by="CreationDate:desc"
)
for order in orders.items:
    print(f"{order.order_number}: ${order.total_amount}")
```

##### `get_by_id()`

Get a specific purchase order by ID.

```python
async def get_by_id(
    po_id: str,
    expand: list[str] | None = None
) -> PurchaseOrder
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `po_id` | `str` | Purchase Order header ID |
| `expand` | `list[str] \| None` | Child resources to include |

**Returns:** `PurchaseOrder`

**Raises:** `MockNotFoundError` if not found

##### `get_lines()`

Get all lines for a purchase order.

```python
async def get_lines(po_id: str) -> list[POLine]
```

**Returns:** `list[POLine]`

##### `cancel()`

Cancel a purchase order (mock action).

```python
async def cancel(
    po_id: str,
    reason: str | None = None
) -> OracleActionResponse
```

**Returns:** `OracleActionResponse` with `success=True`

##### `close()`

Close a purchase order (mock action).

```python
async def close(po_id: str) -> OracleActionResponse
```

##### `communicate()`

Send communication for a purchase order (mock action).

```python
async def communicate(
    po_id: str,
    method: str | None = None
) -> OracleActionResponse
```

##### `acknowledge()`

Record acknowledgment for a purchase order (mock action).

```python
async def acknowledge(po_id: str) -> OracleActionResponse
```

##### `get_open_orders()`

Get all orders with status OPEN.

```python
async def get_open_orders(limit: int = 100) -> OracleCollectionResponse[PurchaseOrder]
```

##### `get_by_supplier()`

Get orders for a specific supplier.

```python
async def get_by_supplier(
    supplier_id: int,
    limit: int = 100
) -> OracleCollectionResponse[PurchaseOrder]
```

##### `get_by_order_number()`

Find order by order number.

```python
async def get_by_order_number(order_number: str) -> PurchaseOrder | None
```

---

### SupplierService

Access via `client.suppliers`

#### Methods

##### `list()`

```python
async def list(
    limit: int = 25,
    offset: int = 0,
    query: str | None = None,
    expand: list[str] | None = None
) -> OracleCollectionResponse[Supplier]
```

##### `get_by_id()`

```python
async def get_by_id(
    supplier_id: int,
    expand: list[str] | None = None
) -> Supplier
```

##### `get_sites()`

Get all sites for a supplier.

```python
async def get_sites(supplier_id: int) -> list[SupplierSite]
```

##### `get_contacts()`

Get all contacts for a supplier.

```python
async def get_contacts(supplier_id: int) -> list[SupplierContact]
```

##### `search_by_name()`

Search suppliers by name (partial match).

```python
async def search_by_name(
    name: str,
    limit: int = 25
) -> OracleCollectionResponse[Supplier]
```

##### `search_by_number()`

Find supplier by exact supplier number.

```python
async def search_by_number(supplier_number: str) -> Supplier | None
```

##### `get_active_suppliers()`

Get all active suppliers.

```python
async def get_active_suppliers(limit: int = 100) -> OracleCollectionResponse[Supplier]
```

---

### RequisitionService

Access via `client.requisitions`

#### Methods

##### `list()`

```python
async def list(
    limit: int = 25,
    offset: int = 0,
    query: str | None = None
) -> OracleCollectionResponse[PurchaseRequisition]
```

##### `get_by_id()`

```python
async def get_by_id(requisition_id: int) -> PurchaseRequisition
```

##### `get_lines()`

```python
async def get_lines(requisition_id: int) -> list[RequisitionLine]
```

##### `get_approved_requisitions()`

```python
async def get_approved_requisitions(limit: int = 100) -> OracleCollectionResponse[PurchaseRequisition]
```

##### `get_pending_requisitions()`

```python
async def get_pending_requisitions(limit: int = 100) -> OracleCollectionResponse[PurchaseRequisition]
```

##### `return_lines()`

Return lines to preparer (mock action).

```python
async def return_lines(
    requisition_id: int,
    line_ids: list[int],
    reason: str | None = None
) -> OracleActionResponse
```

##### `reassign_buyer()`

Reassign buyer (mock action).

```python
async def reassign_buyer(
    requisition_id: int,
    new_buyer_id: int
) -> OracleActionResponse
```

---

### DraftPurchaseOrderService

Access via `client.draft_purchase_orders`

#### Methods

##### `list()`

```python
async def list(
    limit: int = 25,
    offset: int = 0,
    query: str | None = None
) -> OracleCollectionResponse[DraftPurchaseOrder]
```

##### `get_by_id()`

```python
async def get_by_id(po_id: str) -> DraftPurchaseOrder
```

##### `submit()`

Submit draft for processing (mock action).

```python
async def submit(po_id: str) -> OracleActionResponse
```

##### `calculate_tax()`

Calculate tax (mock action).

```python
async def calculate_tax(po_id: str) -> OracleActionResponse
```

##### `check_funds()`

Check funds availability (mock action).

```python
async def check_funds(po_id: str) -> OracleActionResponse
```

---

### AgreementService

Access via `client.agreements`

#### Methods

##### `list()`

```python
async def list(
    limit: int = 25,
    offset: int = 0,
    query: str | None = None
) -> OracleCollectionResponse[PurchaseAgreement]
```

##### `get_by_id()`

```python
async def get_by_id(agreement_id: int) -> PurchaseAgreement
```

##### `get_by_supplier()`

```python
async def get_by_supplier(supplier_id: int) -> OracleCollectionResponse[PurchaseAgreement]
```

##### `get_active_agreements()`

```python
async def get_active_agreements(limit: int = 100) -> OracleCollectionResponse[PurchaseAgreement]
```

---

### AcknowledgmentService

Access via `client.acknowledgments`

#### Methods

##### `list()`

```python
async def list(
    limit: int = 25,
    offset: int = 0
) -> OracleCollectionResponse[POAcknowledgment]
```

##### `get_by_po_id()`

```python
async def get_by_po_id(po_header_id: int) -> POAcknowledgment
```

##### `get_schedules()`

```python
async def get_schedules(po_header_id: int) -> list[AckSchedule]
```

##### `accept()`

Accept order (mock action).

```python
async def accept(
    po_id: int,
    supplier_order: str | None = None,
    note: str | None = None
) -> OracleActionResponse
```

##### `reject()`

Reject order (mock action).

```python
async def reject(
    po_id: int,
    reason: str | None = None,
    note: str | None = None
) -> OracleActionResponse
```

##### `get_pending_acknowledgments()`

```python
async def get_pending_acknowledgments() -> OracleCollectionResponse[POAcknowledgment]
```

---

## Module: Sales Orders

Compatible with `client-valence-anomaly-detection/src/oracle/`

### SalesOrderMockClient

Drop-in replacement for `OracleFusionClient` from anomaly-detection.

```python
from oracle_fusion_mock.sales_orders import SalesOrderMockClient
```

#### Constructor

```python
SalesOrderMockClient(
    base_url: str | None = None,      # Ignored (compatibility)
    username: str | None = None,       # Ignored (compatibility)
    password: str | None = None,       # Ignored (compatibility)
    timeout: float = 30.0,             # Ignored (compatibility)
    data_path: str | Path | None = None
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `data_path` | `str \| Path \| None` | Custom sales_orders.json path |

#### Methods

##### `get_orders()`

Get sales orders with optional filtering.

```python
async def get_orders(
    params: dict[str, str] | None = None
) -> dict[str, Any]
```

| Parameter | Description |
|-----------|-------------|
| `params["limit"]` | Max items (default: "100") |
| `params["offset"]` | Pagination offset (default: "0") |
| `params["q"]` | Query filter (e.g., `"CustomerId=CUST-1001"`) |

**Returns:**
```python
{
    "items": [...],
    "count": 6,
    "limit": 100,
    "offset": 0,
    "hasMore": False
}
```

**Example:**
```python
result = await client.get_orders({"q": "StatusCode=Booked", "limit": "10"})
```

##### `get_order()`

Get a single order by ID.

```python
async def get_order(
    order_id: str,
    include_lines: bool = True
) -> dict[str, Any]
```

**Returns:** Order dict with `lines.items` if `include_lines=True`

**Raises:** `SalesOrderMockNotFoundError` if not found

##### `get_customers()`

Get all customers.

```python
async def get_customers(
    params: dict[str, str] | None = None
) -> dict[str, Any]
```

##### `get_customer()`

Get a customer by ID.

```python
async def get_customer(customer_id: str) -> dict[str, Any]
```

**Raises:** `SalesOrderMockNotFoundError` if not found

##### `get_products()`

Get all products.

```python
async def get_products(
    params: dict[str, str] | None = None
) -> dict[str, Any]
```

##### `get_product()`

Get a product by ID.

```python
async def get_product(product_id: str) -> dict[str, Any]
```

**Raises:** `SalesOrderMockNotFoundError` if not found

##### `update_order()`

Update an order (mock - returns unchanged order).

```python
async def update_order(
    order_id: str,
    updates: dict[str, Any]
) -> dict[str, Any]
```

##### `health_check()`

Check API health (always returns True for mock).

```python
async def health_check() -> bool
```

##### Generic Methods (API Compatibility)

```python
async def get(resource: str, params: dict | None = None) -> dict
async def get_by_id(resource: str, resource_id: str, expand: list | None = None) -> dict
async def post(resource: str, data: dict) -> dict
async def patch(resource: str, resource_id: str, data: dict) -> dict
async def delete(resource: str, resource_id: str) -> dict
```

---

### SalesOrderMockOperations

Drop-in replacement for `OracleOperations` with statistical calculations.

```python
from oracle_fusion_mock.sales_orders import SalesOrderMockOperations
```

#### Constructor

```python
SalesOrderMockOperations(client: SalesOrderMockClient | None = None)
```

#### Methods

##### `get_order()`

Get a single order as a parsed model.

```python
async def get_order(order_id: str) -> Order
```

**Returns:** `Order` model object

##### `get_order_by_number()`

Find order by order number.

```python
async def get_order_by_number(order_number: str) -> Order | None
```

##### `search_orders()`

Search orders with criteria.

```python
async def search_orders(criteria: OrderSearchCriteria) -> list[Order]
```

**Example:**
```python
from oracle_fusion_mock.sales_orders import OrderSearchCriteria, OrderStatus

criteria = OrderSearchCriteria(
    customer_id="CUST-1001",
    status=OrderStatus.BOOKED,
    from_date=datetime(2025, 1, 1),
    min_amount=Decimal("1000"),
    limit=50
)
orders = await ops.search_orders(criteria)
```

##### `get_recent_orders()`

Get orders from the last N days.

```python
async def get_recent_orders(
    days: int = 1,
    limit: int = 100
) -> list[Order]
```

##### `get_customer_order_history()`

Get customer order statistics for anomaly detection.

```python
async def get_customer_order_history(
    customer_id: str,
    months: int = 12
) -> CustomerOrderHistory
```

**Returns:** `CustomerOrderHistory` with fields:

| Field | Type | Description |
|-------|------|-------------|
| `customer_id` | `str` | Customer ID |
| `customer_name` | `str` | Customer name |
| `total_orders` | `int` | Number of orders |
| `total_amount` | `Decimal` | Sum of all order amounts |
| `average_order_amount` | `Decimal` | Mean order amount |
| `max_order_amount` | `Decimal` | Maximum order amount |
| `min_order_amount` | `Decimal` | Minimum order amount |
| `std_dev_amount` | `Decimal` | Standard deviation of amounts |
| `average_quantity` | `Decimal` | Mean quantity per order |
| `last_order_date` | `datetime \| None` | Most recent order date |
| `first_order_date` | `datetime \| None` | Earliest order date |
| `orders` | `list[Order]` | List of orders in period |

##### `get_product_order_history()`

Get product order statistics for anomaly detection.

```python
async def get_product_order_history(
    product_id: str,
    months: int = 12
) -> ProductOrderHistory
```

**Returns:** `ProductOrderHistory` with fields:

| Field | Type | Description |
|-------|------|-------------|
| `product_id` | `str` | Product ID |
| `product_number` | `str` | Product number |
| `product_description` | `str \| None` | Product description |
| `total_orders` | `int` | Number of order lines |
| `total_quantity` | `Decimal` | Sum of quantities |
| `average_quantity` | `Decimal` | Mean quantity per order |
| `max_quantity` | `Decimal` | Maximum quantity |
| `min_quantity` | `Decimal` | Minimum quantity |
| `std_dev_quantity` | `Decimal` | Standard deviation of quantities |
| `average_price` | `Decimal` | Mean selling price |
| `order_lines` | `list[OrderLine]` | Order lines in period |

##### `update_order()`

Update an order (mock).

```python
async def update_order(
    order_id: str,
    update: OrderUpdate
) -> Order
```

##### `update_order_field()`

Update a specific field (mock).

```python
async def update_order_field(
    order_id: str,
    field: str,
    value: Any,
    reason: str | None = None
) -> Order
```

##### `update_order_line_quantity()`

Update line quantity (mock).

```python
async def update_order_line_quantity(
    order_id: str,
    line_id: str,
    new_quantity: Decimal,
    reason: str | None = None
) -> Order
```

##### `get_customer()`

Get customer as a model.

```python
async def get_customer(customer_id: str) -> Customer
```

##### `get_product()`

Get product as a model.

```python
async def get_product(product_id: str) -> Product
```

---

### Sales Order Models

#### OrderStatus

```python
class OrderStatus(str, Enum):
    ENTERED = "Entered"
    BOOKED = "Booked"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"
    AWAITING_SHIPPING = "Awaiting Shipping"
    AWAITING_BILLING = "Awaiting Billing"
    PENDING_APPROVAL = "Pending Approval"
```

#### Order

```python
class Order(BaseModel):
    order_id: str                    # alias: HeaderId
    order_number: str                # alias: OrderNumber
    order_type: str | None           # alias: OrderTypeCode
    status: OrderStatus | str        # alias: StatusCode

    customer_id: str                 # alias: CustomerId
    customer_name: str | None        # alias: CustomerName
    customer_number: str | None      # alias: CustomerNumber
    bill_to_site_id: str | None      # alias: BillToSiteId
    ship_to_site_id: str | None      # alias: ShipToSiteId

    total_amount: Decimal            # alias: TotalAmount
    currency_code: str               # alias: CurrencyCode (default: "USD")

    order_date: datetime             # alias: OrderedDate
    requested_ship_date: datetime | None  # alias: RequestedShipDate
    creation_date: datetime | None   # alias: CreationDate
    last_update_date: datetime | None # alias: LastUpdateDate

    salesperson_id: str | None       # alias: SalespersonId
    salesperson_name: str | None     # alias: SalespersonName
    business_unit: str | None        # alias: BusinessUnitName

    lines: list[OrderLine]           # Order line items
    raw_data: dict | None            # Raw API response (excluded)

    # Properties
    @property
    def total_quantity(self) -> Decimal: ...  # Sum of line quantities

    @property
    def line_count(self) -> int: ...  # Number of lines

    def get_line_by_product(self, product_id: str) -> OrderLine | None: ...
```

#### OrderLine

```python
class OrderLine(BaseModel):
    line_id: str                     # alias: OrderLineId
    line_number: int                 # alias: LineNumber
    product_id: str                  # alias: InventoryItemId
    product_number: str | None       # alias: ProductNumber
    product_description: str | None  # alias: ProductDescription
    ordered_quantity: Decimal        # alias: OrderedQuantity
    ordered_uom: str | None          # alias: OrderedUOMCode
    unit_selling_price: Decimal | None  # alias: UnitSellingPrice
    extended_amount: Decimal | None  # alias: ExtendedAmount
    status: str | None               # alias: StatusCode

    @property
    def line_total(self) -> Decimal: ...  # Extended amount or calculated
```

#### Customer

```python
class Customer(BaseModel):
    customer_id: str                 # alias: CustomerId
    customer_number: str | None      # alias: CustomerNumber
    customer_name: str               # alias: CustomerName
    account_number: str | None       # alias: AccountNumber
    site_id: str | None              # alias: BillToSiteId
```

#### Product

```python
class Product(BaseModel):
    product_id: str                  # alias: InventoryItemId
    product_number: str              # alias: ProductNumber
    product_description: str | None  # alias: ProductDescription
    uom: str | None                  # alias: UOMCode
    unit_price: Decimal | None       # alias: UnitSellingPrice
```

#### OrderSearchCriteria

```python
class OrderSearchCriteria(BaseModel):
    customer_id: str | None = None
    customer_name: str | None = None
    order_number: str | None = None
    status: OrderStatus | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    business_unit: str | None = None
    limit: int = 100                 # Range: 1-500
    offset: int = 0

    def to_query_params(self) -> dict[str, str]: ...
```

#### OrderUpdate

```python
class OrderUpdate(BaseModel):
    status: OrderStatus | None = None
    requested_ship_date: datetime | None = None
    line_updates: dict[str, dict[str, Any]] | None = None

    def to_oracle_payload(self) -> dict[str, Any]: ...
```

---

## Common Types

### OracleCollectionResponse

Generic response for collection endpoints.

```python
class OracleCollectionResponse(Generic[T]):
    items: list[T]
    count: int
    has_more: bool
    limit: int
    offset: int
    links: list[OracleLink]
```

### OracleActionResponse

Response for action endpoints (cancel, close, submit, etc.)

```python
class OracleActionResponse:
    success: bool
    message: str
    result: dict | None
```

### Exceptions

```python
class MockNotFoundError(Exception):
    """Resource not found."""
    status_code: int = 404
    response: Any

class SalesOrderMockError(Exception):
    """Base exception for Sales Order mock."""
    status_code: int | None
    response: Any

class SalesOrderMockNotFoundError(SalesOrderMockError):
    """Sales order resource not found."""
    pass

class SalesOrderMockAuthError(SalesOrderMockError):
    """Mock authentication error (for compatibility)."""
    pass
```

---

## Query Filter Syntax

Both modules support Oracle Fusion query syntax:

```python
# Single condition
"StatusCode=OPEN"
"CustomerId=CUST-1001"

# Numeric comparison
"TotalAmount>=1000"
"OrderedQuantity<=100"

# Multiple conditions (semicolon-separated)
"CustomerId=CUST-1001;StatusCode=Booked"

# Like patterns (Procurement only)
"Supplier like 'ABC*'"
```

---

## Field Alias Mapping

All models use Pydantic field aliases to map Python snake_case to Oracle PascalCase:

| Python Field | Oracle API Field |
|--------------|------------------|
| `order_id` | `HeaderId` |
| `order_number` | `OrderNumber` |
| `customer_id` | `CustomerId` |
| `customer_name` | `CustomerName` |
| `total_amount` | `TotalAmount` |
| `order_date` | `OrderedDate` |
| `product_id` | `InventoryItemId` |
| `line_id` | `OrderLineId` |

Access either way with `model_config = {"populate_by_name": True}`:

```python
order.order_id       # Python style
order.HeaderId       # Oracle style (via alias)
```
