"""Mock client for Oracle Fusion Sales Orders API.

This client provides the same interface as OracleFusionClient in
client-valence-anomaly-detection/src/oracle/client.py, but returns
data from local JSON files instead of making real API calls.

It can be used as a drop-in replacement for testing and development.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from oracle_fusion_mock.sales_orders.data_loader import SalesOrderDataLoader


class SalesOrderMockError(Exception):
    """Base exception for Sales Order mock errors."""

    def __init__(self, message: str, status_code: int | None = None, response: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class SalesOrderMockAuthError(SalesOrderMockError):
    """Mock authentication error (for API compatibility)."""

    pass


class SalesOrderMockNotFoundError(SalesOrderMockError):
    """Resource not found error."""

    pass


class SalesOrderMockClient:
    """Mock client for Oracle Fusion Sales Orders API.

    Provides the same interface as OracleFusionClient but returns
    data from local JSON files.

    This client is designed to be a drop-in replacement for testing.

    Example:
        >>> # Replace OracleFusionClient with SalesOrderMockClient
        >>> # Before: from src.oracle import OracleFusionClient
        >>> from oracle_fusion_mock.sales_orders import SalesOrderMockClient
        >>>
        >>> async with SalesOrderMockClient() as client:
        ...     orders = await client.get_orders()
        ...     order = await client.get_order("100100574829001")
    """

    def __init__(
        self,
        base_url: str | None = None,
        username: str | None = None,
        password: str | None = None,
        timeout: float = 30.0,
        data_path: str | Path | None = None,
    ):
        """Initialize the mock client.

        Args:
            base_url: Ignored (for API compatibility).
            username: Ignored (for API compatibility).
            password: Ignored (for API compatibility).
            timeout: Ignored (for API compatibility).
            data_path: Path to custom sales_orders.json file.
        """
        # These are kept for API compatibility but not used
        self.base_url = base_url or "https://mock.oraclecloud.com"
        self.username = username or "mock_user"
        self.api_version = "11.13.18.05"
        self.timeout = timeout

        # Reset singleton if custom path provided
        if data_path is not None:
            SalesOrderDataLoader.reset()

        self._data_loader = SalesOrderDataLoader(data_path)

    async def close(self) -> None:
        """Close the client (no-op for mock)."""
        pass

    async def __aenter__(self) -> SalesOrderMockClient:
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()

    def _build_url(self, resource: str) -> str:
        """Build full API URL for a resource (for compatibility)."""
        return f"/fscmRestApi/resources/{self.api_version}/{resource}"

    def _apply_query_filter(
        self,
        items: list[dict[str, Any]],
        query: str | None,
    ) -> list[dict[str, Any]]:
        """Apply query filter to items.

        Supports Oracle Fusion query format like:
        - "CustomerId=CUST-1001"
        - "StatusCode=Booked"
        - "OrderNumber=SO-2024-0001"
        - Combined: "CustomerId=CUST-1001;StatusCode=Booked"
        """
        if not query:
            return items

        filtered = items

        # Split on semicolon for multiple conditions
        for condition in query.split(";"):
            condition = condition.strip()
            if not condition:
                continue

            # Handle comparison operators
            # Format: Field>=Value, Field<=Value, Field=Value
            match = re.match(r"(\w+)(>=|<=|=)(.+)", condition)
            if not match:
                continue

            field, op, value = match.groups()

            # Convert numeric values
            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass  # Keep as string

            if op == "=":
                filtered = [item for item in filtered if item.get(field) == value]
            elif op == ">=":
                filtered = [
                    item for item in filtered
                    if item.get(field) is not None and item.get(field) >= value
                ]
            elif op == "<=":
                filtered = [
                    item for item in filtered
                    if item.get(field) is not None and item.get(field) <= value
                ]

        return filtered

    def _apply_pagination(
        self,
        items: list[dict[str, Any]],
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], int]:
        """Apply pagination and return (items, total_count)."""
        total = len(items)
        paginated = items[offset : offset + limit]
        return paginated, total

    # =========================================================================
    # Generic HTTP-like methods (for compatibility)
    # =========================================================================

    async def get(
        self,
        resource: str,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Make GET request (mock implementation).

        Args:
            resource: Resource path (e.g., 'salesOrdersForOrderHub')
            params: Query parameters

        Returns:
            Mock response with items array
        """
        params = params or {}

        if resource == "salesOrdersForOrderHub":
            return await self.get_orders(params)
        elif resource == "accounts":
            return await self.get_customers(params)
        elif resource == "inventoryItems":
            return await self.get_products(params)

        return {"items": [], "count": 0}

    async def get_by_id(
        self,
        resource: str,
        resource_id: str,
        expand: list[str] | None = None,
    ) -> dict[str, Any]:
        """Get a specific resource by ID.

        Args:
            resource: Resource path
            resource_id: Resource identifier
            expand: Child resources to expand

        Returns:
            Resource data
        """
        if resource == "salesOrdersForOrderHub":
            return await self.get_order(resource_id, include_lines=bool(expand))
        elif resource == "accounts":
            return await self.get_customer(resource_id)
        elif resource == "inventoryItems":
            return await self.get_product(resource_id)

        raise SalesOrderMockNotFoundError(f"Resource not found: {resource}/{resource_id}")

    async def post(
        self,
        resource: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Make POST request (mock - returns success)."""
        return {"status": "success", "message": "Mock POST successful"}

    async def patch(
        self,
        resource: str,
        resource_id: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Make PATCH request (mock - returns updated resource).

        Handles two calling conventions:
        1. patch("salesOrdersForOrderHub", "12345", {...})
        2. patch("", "salesOrdersForOrderHub/12345/child/lines/67890", {...})
        """
        # Handle case where full path is in resource_id
        if not resource and "/" in resource_id:
            # Parse path like "salesOrdersForOrderHub/12345/child/lines/67890"
            parts = resource_id.split("/")
            if parts[0] == "salesOrdersForOrderHub":
                order_id = parts[1]
                return await self.get_order(order_id)

        # Standard case
        return await self.get_by_id(resource, resource_id)

    async def delete(
        self,
        resource: str,
        resource_id: str,
    ) -> dict[str, Any]:
        """Make DELETE request (mock - returns success)."""
        return {"status": "success", "message": "Mock DELETE successful"}

    # =========================================================================
    # Sales Orders methods
    # =========================================================================

    async def get_orders(
        self,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Get sales orders.

        Args:
            params: Query parameters (limit, offset, q, etc.)

        Returns:
            Orders response with items array
        """
        params = params or {}

        limit = int(params.get("limit", "100"))
        offset = int(params.get("offset", "0"))
        query = params.get("q")

        # Get all orders
        items = self._data_loader.orders.copy()

        # Apply filters
        items = self._apply_query_filter(items, query)

        # Apply pagination
        paginated, total = self._apply_pagination(items, limit, offset)

        return {
            "items": paginated,
            "count": total,
            "limit": limit,
            "offset": offset,
            "hasMore": (offset + limit) < total,
        }

    async def get_order(
        self,
        order_id: str,
        include_lines: bool = True,
    ) -> dict[str, Any]:
        """Get a specific order by ID.

        Args:
            order_id: Order header ID
            include_lines: Whether to include order lines

        Returns:
            Order details

        Raises:
            SalesOrderMockNotFoundError: If order not found
        """
        order = self._data_loader.get_order(order_id)

        if order is None:
            raise SalesOrderMockNotFoundError(
                f"Order not found: {order_id}",
                status_code=404,
            )

        result = order.copy()

        # Format lines as Oracle returns them
        if include_lines and "lines" in result:
            result["lines"] = {"items": result["lines"]}
        elif not include_lines:
            result.pop("lines", None)

        return result

    async def update_order(
        self,
        order_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any]:
        """Update an order (mock - returns current order).

        Args:
            order_id: Order header ID
            updates: Fields to update (ignored in mock)

        Returns:
            Order details (unchanged in mock)
        """
        # Verify order exists
        return await self.get_order(order_id)

    # =========================================================================
    # Customers methods
    # =========================================================================

    async def get_customers(
        self,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Get customers.

        Args:
            params: Query parameters

        Returns:
            Customers response with items array
        """
        params = params or {}

        limit = int(params.get("limit", "100"))
        offset = int(params.get("offset", "0"))
        query = params.get("q")

        items = self._data_loader.customers.copy()
        items = self._apply_query_filter(items, query)
        paginated, total = self._apply_pagination(items, limit, offset)

        return {
            "items": paginated,
            "count": total,
            "limit": limit,
            "offset": offset,
        }

    async def get_customer(self, customer_id: str) -> dict[str, Any]:
        """Get a specific customer.

        Args:
            customer_id: Customer ID

        Returns:
            Customer details
        """
        customer = self._data_loader.get_customer(customer_id)

        if customer is None:
            raise SalesOrderMockNotFoundError(
                f"Customer not found: {customer_id}",
                status_code=404,
            )

        return customer

    # =========================================================================
    # Products methods
    # =========================================================================

    async def get_products(
        self,
        params: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Get products/items.

        Args:
            params: Query parameters

        Returns:
            Products response with items array
        """
        params = params or {}

        limit = int(params.get("limit", "100"))
        offset = int(params.get("offset", "0"))
        query = params.get("q")

        items = self._data_loader.products.copy()
        items = self._apply_query_filter(items, query)
        paginated, total = self._apply_pagination(items, limit, offset)

        return {
            "items": paginated,
            "count": total,
            "limit": limit,
            "offset": offset,
        }

    async def get_product(self, product_id: str) -> dict[str, Any]:
        """Get a specific product.

        Args:
            product_id: Product/item ID

        Returns:
            Product details
        """
        product = self._data_loader.get_product(product_id)

        if product is None:
            raise SalesOrderMockNotFoundError(
                f"Product not found: {product_id}",
                status_code=404,
            )

        return product

    async def health_check(self) -> bool:
        """Check if the mock API is accessible (always returns True)."""
        return True
