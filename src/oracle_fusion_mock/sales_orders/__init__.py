"""Sales Orders mock module - Compatible with client-valence-anomaly-detection.

This module provides mock implementations that are compatible with the Oracle
client interface expected by the anomaly detection system.

Usage with original names:
    >>> from oracle_fusion_mock.sales_orders import (
    ...     SalesOrderMockClient,
    ...     SalesOrderMockOperations,
    ... )

Usage as drop-in replacement (same names as anomaly-detection):
    >>> from oracle_fusion_mock.sales_orders import (
    ...     OracleFusionClient,  # Alias for SalesOrderMockClient
    ...     OracleOperations,    # Alias for SalesOrderMockOperations
    ...     Order,
    ...     OrderLine,
    ...     Customer,
    ...     Product,
    ... )
    >>>
    >>> async with OracleFusionClient() as client:
    ...     orders = await client.get_orders()
    ...     order = await client.get_order("100100574829001")
    >>>
    >>> async with OracleOperations() as ops:
    ...     orders = await ops.get_recent_orders(days=7)
    ...     history = await ops.get_customer_order_history("CUST-1001")
"""

from oracle_fusion_mock.sales_orders.client import (
    SalesOrderMockClient,
    SalesOrderMockError,
    SalesOrderMockAuthError,
    SalesOrderMockNotFoundError,
)
from oracle_fusion_mock.sales_orders.models import (
    Customer,
    CustomerOrderHistory,
    Order,
    OrderLine,
    OrderSearchCriteria,
    OrderStatus,
    OrderUpdate,
    Product,
    ProductOrderHistory,
)
from oracle_fusion_mock.sales_orders.operations import SalesOrderMockOperations

# Aliases for compatibility with client-valence-anomaly-detection
OracleFusionClient = SalesOrderMockClient
OracleOperations = SalesOrderMockOperations
OracleFusionError = SalesOrderMockError
OracleFusionAuthError = SalesOrderMockAuthError
OracleFusionNotFoundError = SalesOrderMockNotFoundError

__all__ = [
    # Client (original names)
    "SalesOrderMockClient",
    "SalesOrderMockOperations",
    "SalesOrderMockError",
    "SalesOrderMockAuthError",
    "SalesOrderMockNotFoundError",
    # Client (compatible aliases - same names as anomaly-detection)
    "OracleFusionClient",
    "OracleOperations",
    "OracleFusionError",
    "OracleFusionAuthError",
    "OracleFusionNotFoundError",
    # Models (same names as anomaly-detection expects)
    "Order",
    "OrderLine",
    "OrderStatus",
    "OrderUpdate",
    "OrderSearchCriteria",
    "Customer",
    "Product",
    "CustomerOrderHistory",
    "ProductOrderHistory",
]
