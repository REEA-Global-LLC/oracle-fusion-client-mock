"""Oracle Fusion Mock Client - Returns data from local JSON files.

This package provides a mock implementation of the Oracle Fusion Cloud API
client that returns data from local JSON files instead of making real API calls.

Supports two Oracle Fusion modules:

1. **Procurement (Purchase Orders)** - Original mock client:
    >>> from oracle_fusion_mock import OracleFusionMockClient
    >>>
    >>> async with OracleFusionMockClient() as client:
    ...     orders = await client.purchase_orders.list(limit=10)
    ...     for order in orders.items:
    ...         print(f"{order.order_number}: {order.supplier}")

2. **Sales Orders (Order Hub)** - Compatible with client-valence-anomaly-detection:
    >>> from oracle_fusion_mock.sales_orders import (
    ...     SalesOrderMockClient,
    ...     SalesOrderMockOperations,
    ... )
    >>>
    >>> async with SalesOrderMockOperations() as ops:
    ...     orders = await ops.get_recent_orders(days=7)
    ...     history = await ops.get_customer_order_history("CUST-1001")
"""

from oracle_fusion_mock.client import OracleFusionMockClient
from oracle_fusion_mock.data_loader import MockDataLoader

# Sales Orders module - compatible with client-valence-anomaly-detection
from oracle_fusion_mock.sales_orders import (
    SalesOrderMockClient,
    SalesOrderMockOperations,
)

__all__ = [
    # Procurement mock client
    "OracleFusionMockClient",
    "MockDataLoader",
    # Sales Orders mock client (anomaly-detection compatible)
    "SalesOrderMockClient",
    "SalesOrderMockOperations",
]

__version__ = "0.1.0"
