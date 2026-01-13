"""Sales Orders mock module - Compatible with client-valence-anomaly-detection.

This module provides mock implementations that are compatible with the Oracle
client interface expected by the anomaly detection system.

Usage:
    >>> from oracle_fusion_mock.sales_orders import (
    ...     SalesOrderMockClient,
    ...     SalesOrderMockOperations,
    ...     Order,
    ...     OrderLine,
    ...     Customer,
    ...     Product,
    ... )
    >>>
    >>> # Use as drop-in replacement for OracleFusionClient
    >>> async with SalesOrderMockClient() as client:
    ...     orders = await client.get_orders()
    ...     order = await client.get_order("100100574829001")
    >>>
    >>> # Or use high-level operations
    >>> async with SalesOrderMockOperations() as ops:
    ...     orders = await ops.get_recent_orders(days=7)
    ...     history = await ops.get_customer_order_history("CUST-1001")
"""

from oracle_fusion_mock.sales_orders.client import SalesOrderMockClient
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

__all__ = [
    # Client
    "SalesOrderMockClient",
    "SalesOrderMockOperations",
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
