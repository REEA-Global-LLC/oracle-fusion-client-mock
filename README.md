# Oracle Fusion Client Mock

A Python mock client for Oracle Fusion Cloud APIs that returns data from local JSON files instead of making real API calls. Designed as a drop-in replacement for testing and development.

## Features

- **Drop-in replacement** for the real Oracle Fusion client
- **Two Oracle modules supported**:
  - **Procurement** (Purchase Orders, Suppliers, Requisitions, etc.)
  - **Sales Orders** (Order Hub) - Compatible with `client-valence-anomaly-detection`
- **Consistent mock data** from local JSON files
- **Full async/await support** with context managers
- **Same interface** as real clients for seamless swapping
- **Statistical calculations** for anomaly detection (CustomerOrderHistory, ProductOrderHistory)

## Installation

```bash
# Basic installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

## Quick Start

### Procurement Mock (Purchase Orders)

```python
import asyncio
from oracle_fusion_mock import OracleFusionMockClient

async def main():
    async with OracleFusionMockClient() as client:
        # List purchase orders
        orders = await client.purchase_orders.list(limit=10)
        for order in orders.items:
            print(f"{order.order_number}: {order.supplier} - ${order.total_amount}")

        # Get supplier with sites and contacts
        supplier = await client.suppliers.get_by_id(1001)
        print(f"Supplier: {supplier.supplier}")

        # Filter by status
        open_orders = await client.purchase_orders.list(query="StatusCode='OPEN'")
        print(f"Open orders: {len(open_orders.items)}")

asyncio.run(main())
```

### Sales Orders Mock (Anomaly Detection Compatible)

```python
import asyncio
from oracle_fusion_mock.sales_orders import (
    SalesOrderMockClient,
    SalesOrderMockOperations,
)

async def main():
    # Low-level client (drop-in for OracleFusionClient)
    async with SalesOrderMockClient() as client:
        orders = await client.get_orders({"q": "StatusCode=Booked"})
        order = await client.get_order("100100574829001", include_lines=True)
        print(f"Order: {order['OrderNumber']} - ${order['TotalAmount']}")

    # High-level operations with statistics
    async with SalesOrderMockOperations() as ops:
        # Get customer order history for anomaly detection
        history = await ops.get_customer_order_history("CUST-1001", months=12)
        print(f"Customer: {history.customer_name}")
        print(f"Average order: ${history.average_order_amount}")
        print(f"Std deviation: ${history.std_dev_amount}")

        # Get product statistics
        product = await ops.get_product_order_history("ITEM-5001", months=12)
        print(f"Product: {product.product_number}")
        print(f"Average quantity: {product.average_quantity}")

asyncio.run(main())
```

## Module: Procurement (Purchase Orders)

### Available Services

| Service | Access | Description |
|---------|--------|-------------|
| Purchase Orders | `client.purchase_orders` | Manage POs, lines, actions |
| Draft POs | `client.draft_purchase_orders` | Draft creation and submission |
| Suppliers | `client.suppliers` | Supplier info, sites, contacts |
| Requisitions | `client.requisitions` | Purchase requisitions |
| Agreements | `client.agreements` | Blanket and contract agreements |
| Acknowledgments | `client.acknowledgments` | Supplier acknowledgments |

### Purchase Orders

```python
# List with filtering and pagination
orders = await client.purchase_orders.list(
    limit=25,
    offset=0,
    query="StatusCode='OPEN'",
    order_by="CreationDate:desc"
)

# Get by ID with lines
po = await client.purchase_orders.get_by_id("300100574829561")
lines = await client.purchase_orders.get_lines("300100574829561")

# Actions (mock - return success responses)
await client.purchase_orders.cancel(po_id, reason="No longer needed")
await client.purchase_orders.close(po_id)
await client.purchase_orders.communicate(po_id, method="Email")

# Convenience methods
await client.purchase_orders.get_open_orders()
await client.purchase_orders.get_by_supplier(1001)
```

### Suppliers

```python
# List and search
suppliers = await client.suppliers.list()
results = await client.suppliers.search_by_name("ABC Corp")
supplier = await client.suppliers.search_by_number("SUP-001")

# Get with nested data
supplier = await client.suppliers.get_by_id(1001)
sites = await client.suppliers.get_sites(1001)
contacts = await client.suppliers.get_contacts(1001)
```

### Requisitions

```python
# List and filter
reqs = await client.requisitions.list()
approved = await client.requisitions.get_approved_requisitions()
pending = await client.requisitions.get_pending_requisitions()

# Actions
await client.requisitions.return_lines(req_id, line_ids=[1, 2], reason="Incorrect")
```

## Module: Sales Orders (Anomaly Detection)

This module provides 100% compatibility with `client-valence-anomaly-detection/src/oracle/`.

### Compatibility Mapping

| anomaly-detection | oracle-fusion-mock | Description |
|-------------------|-------------------|-------------|
| `OracleFusionClient` | `SalesOrderMockClient` | Low-level HTTP client |
| `OracleOperations` | `SalesOrderMockOperations` | High-level operations |
| `Order` | `Order` | Sales order model |
| `OrderLine` | `OrderLine` | Order line item |
| `Customer` | `Customer` | Customer entity |
| `Product` | `Product` | Product/inventory item |
| `CustomerOrderHistory` | `CustomerOrderHistory` | Customer statistics |
| `ProductOrderHistory` | `ProductOrderHistory` | Product statistics |

### SalesOrderMockClient

Drop-in replacement for `OracleFusionClient`:

```python
from oracle_fusion_mock.sales_orders import SalesOrderMockClient

async with SalesOrderMockClient() as client:
    # Get orders with filtering
    orders = await client.get_orders({"q": "CustomerId=CUST-1001"})
    orders = await client.get_orders({"q": "StatusCode=Booked", "limit": "10"})

    # Get single order with lines
    order = await client.get_order("100100574829001", include_lines=True)

    # Get customers and products
    customers = await client.get_customers()
    customer = await client.get_customer("CUST-1001")
    products = await client.get_products()
    product = await client.get_product("ITEM-5001")

    # Health check
    is_healthy = await client.health_check()  # Always True for mock
```

### SalesOrderMockOperations

Drop-in replacement for `OracleOperations` with statistical calculations:

```python
from oracle_fusion_mock.sales_orders import SalesOrderMockOperations, OrderSearchCriteria

async with SalesOrderMockOperations() as ops:
    # Get orders
    order = await ops.get_order("100100574829001")
    order = await ops.get_order_by_number("SO-2025-0001")

    # Search with criteria
    criteria = OrderSearchCriteria(
        customer_id="CUST-1001",
        status=OrderStatus.BOOKED,
        min_amount=Decimal("1000"),
    )
    orders = await ops.search_orders(criteria)

    # Recent orders
    recent = await ops.get_recent_orders(days=30, limit=50)

    # Customer history (for anomaly detection)
    history = await ops.get_customer_order_history("CUST-1001", months=12)
    # Returns: customer_name, total_orders, total_amount, average_order_amount,
    #          max_order_amount, min_order_amount, std_dev_amount, average_quantity,
    #          last_order_date, first_order_date, orders[]

    # Product history (for anomaly detection)
    product = await ops.get_product_order_history("ITEM-5001", months=12)
    # Returns: product_number, product_description, total_orders, total_quantity,
    #          average_quantity, max_quantity, min_quantity, std_dev_quantity,
    #          average_price, order_lines[]
```

### Anomaly Detection Example

```python
from oracle_fusion_mock.sales_orders import SalesOrderMockOperations

async def check_order_anomaly(order_id: str) -> bool:
    """Check if an order amount is anomalous."""
    async with SalesOrderMockOperations() as ops:
        order = await ops.get_order(order_id)
        history = await ops.get_customer_order_history(order.customer_id, months=12)

        if history.std_dev_amount == 0:
            return False  # Not enough data

        # Z-score calculation
        z_score = abs(
            float(order.total_amount - history.average_order_amount)
            / float(history.std_dev_amount)
        )

        return z_score > 2  # Flag if >2 standard deviations
```

## Mock Data

### Procurement Data

By default loads from `oracle-fusion-mock-server/db.json`:

```json
{
  "purchaseOrders": [...],
  "draftPurchaseOrders": [...],
  "purchaseRequisitions": [...],
  "suppliers": [...],
  "purchaseAgreements": [...],
  "purchaseOrderAcknowledgments": [...]
}
```

### Sales Orders Data

Located at `src/oracle_fusion_mock/data/sales_orders.json`:

```json
{
  "salesOrders": [
    {
      "HeaderId": "100100574829001",
      "OrderNumber": "SO-2025-0001",
      "StatusCode": "Booked",
      "CustomerId": "CUST-1001",
      "CustomerName": "Acme Corporation",
      "TotalAmount": 15750.00,
      "OrderedDate": "2025-12-01T10:30:00Z",
      "lines": [...]
    }
  ],
  "customers": [...],
  "products": [...]
}
```

### Using Custom Data

```python
# Procurement - custom db.json path
async with OracleFusionMockClient("/path/to/custom-db.json") as client:
    orders = await client.purchase_orders.list()

# Sales Orders - custom sales_orders.json path
from oracle_fusion_mock.sales_orders import SalesOrderMockClient
async with SalesOrderMockClient(data_path="/path/to/sales_orders.json") as client:
    orders = await client.get_orders()
```

## Response Formats

### Collection Response (Oracle Standard)

```python
{
    "items": [...],      # List of items
    "count": 10,         # Total count
    "hasMore": False,    # Pagination indicator
    "limit": 25,         # Items per page
    "offset": 0,         # Current offset
    "links": [...]       # Navigation links
}
```

### Model Objects

All models use Pydantic with Oracle field aliases:

```python
# Python snake_case -> Oracle PascalCase
order.order_id      # <- HeaderId
order.order_number  # <- OrderNumber
order.customer_id   # <- CustomerId
order.total_amount  # <- TotalAmount
```

## Testing

```bash
# Run all tests
pytest tests/ -v

# Run only Procurement tests
pytest tests/test_client.py tests/test_purchase_orders.py -v

# Run only Sales Orders tests
pytest tests/test_sales_orders.py -v

# Run with coverage
pytest tests/ --cov=oracle_fusion_mock --cov-report=term-missing
```

**Test Results:** 83 tests (38 Procurement + 45 Sales Orders)

## Project Structure

```
oracle-fusion-client-mock/
├── src/oracle_fusion_mock/
│   ├── __init__.py              # Main exports
│   ├── client.py                # OracleFusionMockClient
│   ├── data_loader.py           # MockDataLoader singleton
│   ├── models.py                # Procurement models
│   ├── services/                # Procurement services
│   │   ├── purchase_orders.py
│   │   ├── suppliers.py
│   │   ├── requisitions.py
│   │   └── ...
│   ├── data/
│   │   └── sales_orders.json    # Sales Orders mock data
│   └── sales_orders/            # Sales Orders module
│       ├── __init__.py
│       ├── client.py            # SalesOrderMockClient
│       ├── operations.py        # SalesOrderMockOperations
│       ├── models.py            # Order, Customer, Product models
│       └── data_loader.py       # SalesOrderDataLoader
├── tests/
│   ├── test_client.py
│   ├── test_purchase_orders.py
│   ├── test_sales_orders.py     # 45 compatibility tests
│   └── ...
├── example.py                   # Procurement example
├── example_sales_orders.py      # Sales Orders example
└── pyproject.toml
```

## Related Projects

| Project | Description |
|---------|-------------|
| `oracle-fusion-client` | Real Oracle Fusion Procurement client |
| `oracle-fusion-mock-server` | Node.js JSON server for HTTP mocking |
| `client-valence-anomaly-detection` | Anomaly detection system using Sales Orders |

## License

MIT
