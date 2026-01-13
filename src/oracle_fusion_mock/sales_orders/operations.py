"""High-level operations for Sales Orders mock data.

This module provides the same interface as OracleOperations in
client-valence-anomaly-detection/src/oracle/operations.py.

It includes statistical calculations for CustomerOrderHistory and
ProductOrderHistory that are used by the anomaly detection system.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta
from decimal import Decimal
from statistics import mean, stdev
from typing import Any

from oracle_fusion_mock.sales_orders.client import SalesOrderMockClient
from oracle_fusion_mock.sales_orders.models import (
    Customer,
    CustomerOrderHistory,
    Order,
    OrderLine,
    OrderSearchCriteria,
    OrderUpdate,
    Product,
    ProductOrderHistory,
)

logger = logging.getLogger(__name__)


class SalesOrderMockOperations:
    """High-level operations for Sales Orders mock data.

    Provides the same interface as OracleOperations from the
    anomaly detection project.

    Example:
        >>> async with SalesOrderMockOperations() as ops:
        ...     orders = await ops.get_recent_orders(days=7)
        ...     history = await ops.get_customer_order_history("CUST-1001")
        ...     print(f"Customer avg: ${history.average_order_amount}")
    """

    def __init__(self, client: SalesOrderMockClient | None = None):
        """Initialize operations with a mock client.

        Args:
            client: Mock client (creates new if not provided)
        """
        self.client = client or SalesOrderMockClient()

    async def __aenter__(self) -> SalesOrderMockOperations:
        """Async context manager entry."""
        await self.client.__aenter__()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.client.__aexit__(exc_type, exc_val, exc_tb)

    def _parse_order(self, data: dict[str, Any]) -> Order:
        """Parse raw order data into Order model.

        Args:
            data: Raw order data from API

        Returns:
            Parsed Order object
        """
        # Parse order lines if present
        lines: list[OrderLine] = []
        lines_data = data.get("lines", {})

        # Handle both formats: {"items": [...]} or [...]
        if isinstance(lines_data, dict):
            line_items = lines_data.get("items", [])
        else:
            line_items = lines_data

        for line_data in line_items:
            lines.append(OrderLine.model_validate(line_data))

        # Create a copy of data without lines to avoid validation error
        # (lines field expects list, but API returns {"items": [...]})
        order_data = {k: v for k, v in data.items() if k != "lines"}
        order_data["lines"] = []  # Empty list for initial validation

        order = Order.model_validate(order_data)
        order.lines = lines
        order.raw_data = data
        return order

    async def get_order(self, order_id: str) -> Order:
        """Get a single order by ID.

        Args:
            order_id: Oracle order header ID

        Returns:
            Order object
        """
        data = await self.client.get_order(order_id, include_lines=True)
        return self._parse_order(data)

    async def get_order_by_number(self, order_number: str) -> Order | None:
        """Get an order by order number.

        Args:
            order_number: Order number (e.g., "SO-2024-0001")

        Returns:
            Order object or None if not found
        """
        params = {"q": f"OrderNumber={order_number}", "limit": "1"}
        response = await self.client.get_orders(params)

        items = response.get("items", [])
        if not items:
            return None

        # Get full order with lines
        order_id = items[0]["HeaderId"]
        return await self.get_order(order_id)

    async def search_orders(self, criteria: OrderSearchCriteria) -> list[Order]:
        """Search orders with criteria.

        Args:
            criteria: Search criteria

        Returns:
            List of matching orders
        """
        params = criteria.to_query_params()
        response = await self.client.get_orders(params)

        orders: list[Order] = []
        for item in response.get("items", []):
            try:
                order = await self.get_order(item["HeaderId"])
                orders.append(order)
            except Exception as e:
                logger.warning(f"Failed to fetch order {item['HeaderId']}: {e}")

        return orders

    async def get_recent_orders(
        self,
        days: int = 1,
        limit: int = 100,
    ) -> list[Order]:
        """Get orders from the last N days.

        Args:
            days: Number of days to look back
            limit: Maximum orders to return

        Returns:
            List of recent orders
        """
        from_date = datetime.now() - timedelta(days=days)
        criteria = OrderSearchCriteria(
            from_date=from_date,
            limit=limit,
        )
        return await self.search_orders(criteria)

    async def update_order(
        self,
        order_id: str,
        update: OrderUpdate,
    ) -> Order:
        """Update an order (mock - returns current order).

        Args:
            order_id: Order header ID
            update: Update payload

        Returns:
            Order object (unchanged in mock)
        """
        payload = update.to_oracle_payload()

        if payload:
            logger.info(f"Mock update order {order_id}: {payload}")
            await self.client.update_order(order_id, payload)

        return await self.get_order(order_id)

    async def update_order_field(
        self,
        order_id: str,
        field: str,
        value: Any,
        reason: str | None = None,
    ) -> Order:
        """Update a specific field on an order (mock).

        Args:
            order_id: Order header ID
            field: Field name to update
            value: New value
            reason: Reason for update

        Returns:
            Order object (unchanged in mock)
        """
        logger.info(f"Mock update order {order_id} field {field}={value} reason={reason}")
        return await self.get_order(order_id)

    async def update_order_line_quantity(
        self,
        order_id: str,
        line_id: str,
        new_quantity: Decimal,
        reason: str | None = None,
    ) -> Order:
        """Update the quantity of an order line (mock).

        Args:
            order_id: Order header ID
            line_id: Order line ID
            new_quantity: New quantity value
            reason: Reason for update

        Returns:
            Order object (unchanged in mock)
        """
        logger.info(
            f"Mock update order {order_id} line {line_id} quantity to {new_quantity}"
        )
        return await self.get_order(order_id)

    async def get_customer_order_history(
        self,
        customer_id: str,
        months: int = 12,
    ) -> CustomerOrderHistory:
        """Get historical order patterns for a customer.

        This method calculates statistics that are used by the
        anomaly detection system to identify unusual orders.

        Args:
            customer_id: Customer ID
            months: Number of months to analyze

        Returns:
            Customer order history with statistics
        """
        from_date = datetime.now() - timedelta(days=months * 30)
        criteria = OrderSearchCriteria(
            customer_id=customer_id,
            from_date=from_date,
            limit=500,
        )

        orders = await self.search_orders(criteria)

        if not orders:
            # Return empty history if no orders found
            return CustomerOrderHistory(
                customer_id=customer_id,
                customer_name="Unknown",
                total_orders=0,
                total_amount=Decimal("0"),
                average_order_amount=Decimal("0"),
                max_order_amount=Decimal("0"),
                min_order_amount=Decimal("0"),
                std_dev_amount=Decimal("0"),
                average_quantity=Decimal("0"),
                last_order_date=None,
                first_order_date=None,
                orders=[],
            )

        # Calculate statistics
        amounts = [float(o.total_amount) for o in orders]
        quantities = [float(o.total_quantity) for o in orders]

        return CustomerOrderHistory(
            customer_id=customer_id,
            customer_name=orders[0].customer_name or "Unknown",
            total_orders=len(orders),
            total_amount=Decimal(str(sum(amounts))),
            average_order_amount=Decimal(str(mean(amounts))),
            max_order_amount=Decimal(str(max(amounts))),
            min_order_amount=Decimal(str(min(amounts))),
            std_dev_amount=Decimal(str(stdev(amounts))) if len(amounts) > 1 else Decimal("0"),
            average_quantity=Decimal(str(mean(quantities))) if quantities else Decimal("0"),
            last_order_date=max(o.order_date for o in orders),
            first_order_date=min(o.order_date for o in orders),
            orders=orders,
        )

    async def get_product_order_history(
        self,
        product_id: str,
        months: int = 12,
    ) -> ProductOrderHistory:
        """Get historical order patterns for a product.

        Args:
            product_id: Product/item ID
            months: Number of months to analyze

        Returns:
            Product order history with statistics
        """
        # Get all orders and extract lines for this product
        response = await self.client.get_orders({"limit": "500"})

        lines: list[OrderLine] = []
        product_number = ""
        product_description = None

        for item in response.get("items", []):
            try:
                order = await self.get_order(item["HeaderId"])
                for line in order.lines:
                    if line.product_id == product_id:
                        lines.append(line)
                        product_number = line.product_number or product_number
                        product_description = line.product_description or product_description
            except Exception as e:
                logger.warning(f"Failed to process order {item.get('HeaderId')}: {e}")

        if not lines:
            return ProductOrderHistory(
                product_id=product_id,
                product_number="Unknown",
                product_description=None,
                total_orders=0,
                total_quantity=Decimal("0"),
                average_quantity=Decimal("0"),
                max_quantity=Decimal("0"),
                min_quantity=Decimal("0"),
                std_dev_quantity=Decimal("0"),
                average_price=Decimal("0"),
                order_lines=[],
            )

        quantities = [float(line.ordered_quantity) for line in lines]
        prices = [float(line.unit_selling_price) for line in lines if line.unit_selling_price]

        return ProductOrderHistory(
            product_id=product_id,
            product_number=product_number,
            product_description=product_description,
            total_orders=len(lines),
            total_quantity=Decimal(str(sum(quantities))),
            average_quantity=Decimal(str(mean(quantities))),
            max_quantity=Decimal(str(max(quantities))),
            min_quantity=Decimal(str(min(quantities))),
            std_dev_quantity=Decimal(str(stdev(quantities))) if len(quantities) > 1 else Decimal("0"),
            average_price=Decimal(str(mean(prices))) if prices else Decimal("0"),
            order_lines=lines,
        )

    async def get_customer(self, customer_id: str) -> Customer:
        """Get customer details.

        Args:
            customer_id: Customer ID

        Returns:
            Customer object
        """
        data = await self.client.get_customer(customer_id)
        return Customer.model_validate(data)

    async def get_product(self, product_id: str) -> Product:
        """Get product details.

        Args:
            product_id: Product/item ID

        Returns:
            Product object
        """
        data = await self.client.get_product(product_id)
        return Product.model_validate(data)
