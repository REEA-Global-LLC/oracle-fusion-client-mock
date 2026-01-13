"""Base service class for mock services."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, TypeVar

from oracle_fusion_mock.data_loader import MockDataLoader
from oracle_fusion_mock.models import OracleActionResponse, OracleCollectionResponse, OracleLink

T = TypeVar("T")


class BaseMockService:
    """Base class for all mock services.

    Provides common functionality for filtering, pagination, and response building.
    """

    def __init__(self, data_loader: MockDataLoader | None = None) -> None:
        """Initialize the service.

        Args:
            data_loader: Optional data loader instance. If None, creates a new one.
        """
        self._data_loader = data_loader or MockDataLoader()

    def _apply_pagination(
        self,
        items: list[dict[str, Any]],
        limit: int,
        offset: int,
    ) -> tuple[list[dict[str, Any]], bool]:
        """Apply pagination to a list of items.

        Args:
            items: List of items to paginate.
            limit: Maximum number of items to return.
            offset: Number of items to skip.

        Returns:
            Tuple of (paginated items, has_more flag).
        """
        total = len(items)
        paginated = items[offset : offset + limit]
        has_more = (offset + limit) < total
        return paginated, has_more

    def _apply_query_filter(
        self,
        items: list[dict[str, Any]],
        query: str | None,
    ) -> list[dict[str, Any]]:
        """Apply a simple query filter to items.

        Supports basic Oracle-style queries like:
        - "StatusCode='OPEN'"
        - "Supplier like 'ABC*'"
        - "SupplierId=1001"

        Args:
            items: List of items to filter.
            query: Query string in Oracle format.

        Returns:
            Filtered list of items.
        """
        if not query:
            return items

        # Parse simple equality: Field='Value' or Field=Value
        eq_match = re.match(r"(\w+)='?([^']+)'?", query)
        if eq_match:
            field, value = eq_match.groups()
            # Try numeric conversion
            try:
                value = int(value)  # type: ignore[assignment]
            except ValueError:
                pass
            return [item for item in items if item.get(field) == value]

        # Parse LIKE query: Field like 'Value*'
        like_match = re.match(r"(\w+)\s+like\s+'([^']+)'", query, re.IGNORECASE)
        if like_match:
            field, pattern = like_match.groups()
            # Convert Oracle LIKE pattern to regex
            regex_pattern = pattern.replace("*", ".*").replace("%", ".*")
            regex = re.compile(regex_pattern, re.IGNORECASE)
            return [
                item for item in items if item.get(field) and regex.match(str(item.get(field)))
            ]

        return items

    def _apply_order_by(
        self,
        items: list[dict[str, Any]],
        order_by: str | None,
    ) -> list[dict[str, Any]]:
        """Apply sorting to items.

        Args:
            items: List of items to sort.
            order_by: Sort expression like "CreationDate:desc" or "OrderNumber:asc".

        Returns:
            Sorted list of items.
        """
        if not order_by:
            return items

        parts = order_by.split(":")
        field = parts[0]
        descending = len(parts) > 1 and parts[1].lower() == "desc"

        return sorted(
            items,
            key=lambda x: x.get(field) or "",
            reverse=descending,
        )

    def _build_collection_links(self, resource_name: str) -> list[OracleLink]:
        """Build standard collection links.

        Args:
            resource_name: Name of the resource (e.g., "purchaseOrders").

        Returns:
            List of OracleLink objects.
        """
        return [
            OracleLink(
                rel="self",
                href=f"/{resource_name}",
                name=resource_name,
                kind="collection",
            )
        ]

    def _build_item_links(self, resource_name: str, item_id: str | int) -> list[OracleLink]:
        """Build standard item links.

        Args:
            resource_name: Name of the resource (e.g., "purchaseOrders").
            item_id: ID of the item.

        Returns:
            List of OracleLink objects.
        """
        return [
            OracleLink(
                rel="self",
                href=f"/{resource_name}/{item_id}",
                name=resource_name,
                kind="item",
            ),
            OracleLink(
                rel="canonical",
                href=f"/{resource_name}/{item_id}",
                name=resource_name,
                kind="item",
            ),
        ]

    def _create_action_response(
        self,
        action: str,
        result: str = "SUCCESS",
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> OracleActionResponse:
        """Create a standard action response.

        Args:
            action: Name of the action.
            result: Result status (SUCCESS or FAILURE).
            message: Optional message. If None, generates a default message.
            details: Optional details dictionary.

        Returns:
            OracleActionResponse object.
        """
        if message is None:
            message = f"Action '{action}' completed successfully."
            if result == "FAILURE":
                message = f"Action '{action}' failed."

        return OracleActionResponse(
            result=result,
            message=message,
            action=action,
            timestamp=datetime.now(),
            details=details,
        )
