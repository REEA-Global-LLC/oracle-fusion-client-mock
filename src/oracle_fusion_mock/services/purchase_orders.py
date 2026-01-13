"""Mock Purchase Orders service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oracle_fusion_mock.models import (
    OracleActionResponse,
    OracleCollectionResponse,
    POLine,
    PurchaseOrder,
)
from oracle_fusion_mock.services.base import BaseMockService

if TYPE_CHECKING:
    from oracle_fusion_mock.data_loader import MockDataLoader


class MockPurchaseOrderService(BaseMockService):
    """Mock service for Purchase Order operations.

    Returns data from local JSON files instead of making API calls.

    Example:
        >>> service = MockPurchaseOrderService()
        >>> orders = await service.list(limit=10)
        >>> po = await service.get_by_id("300100574829561")
    """

    def __init__(self, data_loader: MockDataLoader | None = None) -> None:
        super().__init__(data_loader)
        self._resource_name = "purchaseOrders"

    async def list(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        query: str | None = None,
        expand: str | None = None,
        order_by: str | None = None,
    ) -> OracleCollectionResponse[PurchaseOrder]:
        """List purchase orders.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            query: Filter query (e.g., "StatusCode='OPEN'").
            expand: Expand child resources (e.g., "lines"). Ignored in mock.
            order_by: Sort order (e.g., "CreationDate:desc").

        Returns:
            Collection response with purchase orders.
        """
        # Get all POs with valid data (skip empty items)
        all_items = [
            po for po in self._data_loader.purchase_orders if "POHeaderId" in po
        ]

        # Apply filtering
        filtered = self._apply_query_filter(all_items, query)

        # Apply sorting
        sorted_items = self._apply_order_by(filtered, order_by)

        # Apply pagination
        paginated, has_more = self._apply_pagination(sorted_items, limit, offset)

        # Convert to models
        items = [PurchaseOrder.model_validate(item) for item in paginated]

        return OracleCollectionResponse[PurchaseOrder](
            items=items,
            count=len(items),
            has_more=has_more,
            limit=limit,
            offset=offset,
            links=self._build_collection_links(self._resource_name),
        )

    async def get_by_id(
        self,
        po_id: str,
        *,
        expand: str | None = None,
    ) -> PurchaseOrder:
        """Get a purchase order by ID.

        Args:
            po_id: Purchase order ID (can be POHeaderId or the compound id).
            expand: Expand child resources. Ignored in mock.

        Returns:
            Purchase order instance.

        Raises:
            ValueError: If purchase order not found.
        """
        # Try to parse as integer first
        try:
            header_id = int(po_id)
        except ValueError:
            # If it's a compound ID, extract the numeric part
            header_id = int(po_id.replace("AABORAQLEABORAQLE", ""))

        po_data = self._data_loader.get_purchase_order(header_id)
        if po_data is None:
            raise ValueError(f"Purchase order not found: {po_id}")

        return PurchaseOrder.model_validate(po_data)

    async def get_lines(self, po_id: str) -> list[POLine]:
        """Get lines for a purchase order.

        Args:
            po_id: Purchase order ID.

        Returns:
            List of purchase order lines.
        """
        po = await self.get_by_id(po_id)
        return po.lines

    async def cancel(
        self,
        po_id: str,
        *,
        reason: str | None = None,
    ) -> OracleActionResponse:
        """Cancel a purchase order (mock).

        In mock mode, this simulates a successful cancellation.

        Args:
            po_id: Purchase order ID.
            reason: Cancellation reason.

        Returns:
            Action response.
        """
        # Verify PO exists
        po = await self.get_by_id(po_id)

        return self._create_action_response(
            action="cancel",
            result="SUCCESS",
            message=f"Purchase order {po.order_number} cancelled successfully.",
            details={"reason": reason} if reason else None,
        )

    async def close(self, po_id: str) -> OracleActionResponse:
        """Close a purchase order (mock).

        Args:
            po_id: Purchase order ID.

        Returns:
            Action response.
        """
        po = await self.get_by_id(po_id)

        return self._create_action_response(
            action="close",
            result="SUCCESS",
            message=f"Purchase order {po.order_number} closed successfully.",
        )

    async def communicate(
        self,
        po_id: str,
        *,
        method: str | None = None,
    ) -> OracleActionResponse:
        """Communicate a purchase order to the supplier (mock).

        Args:
            po_id: Purchase order ID.
            method: Communication method (e.g., "Email", "EDI").

        Returns:
            Action response.
        """
        po = await self.get_by_id(po_id)

        return self._create_action_response(
            action="communicate",
            result="SUCCESS",
            message=f"Purchase order {po.order_number} communicated to {po.supplier}.",
            details={"method": method or "Email"},
        )

    async def acknowledge(self, po_id: str) -> OracleActionResponse:
        """Request acknowledgment for a purchase order (mock).

        Args:
            po_id: Purchase order ID.

        Returns:
            Action response.
        """
        po = await self.get_by_id(po_id)

        return self._create_action_response(
            action="acknowledge",
            result="SUCCESS",
            message=f"Acknowledgment requested for purchase order {po.order_number}.",
        )

    async def get_by_order_number(self, order_number: str) -> PurchaseOrder | None:
        """Get a purchase order by order number.

        Args:
            order_number: The order number (e.g., "PO-2024-0001").

        Returns:
            Purchase order if found, None otherwise.
        """
        result = await self.list(query=f"OrderNumber='{order_number}'", limit=1)
        return result.items[0] if result.items else None

    async def get_by_supplier(
        self,
        supplier_id: int,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseOrder]:
        """Get purchase orders for a specific supplier.

        Args:
            supplier_id: Supplier ID.
            limit: Maximum number of records to return.

        Returns:
            Collection response with purchase orders.
        """
        return await self.list(query=f"SupplierId={supplier_id}", limit=limit)

    async def get_open_orders(
        self,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseOrder]:
        """Get all open purchase orders.

        Args:
            limit: Maximum number of records to return.

        Returns:
            Collection response with open purchase orders.
        """
        return await self.list(query="StatusCode='OPEN'", limit=limit)
