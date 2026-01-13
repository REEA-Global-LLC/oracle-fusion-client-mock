"""Mock Draft Purchase Orders service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oracle_fusion_mock.models import (
    DraftPOLine,
    DraftPurchaseOrder,
    OracleActionResponse,
    OracleCollectionResponse,
)
from oracle_fusion_mock.services.base import BaseMockService

if TYPE_CHECKING:
    from oracle_fusion_mock.data_loader import MockDataLoader


class MockDraftPurchaseOrderService(BaseMockService):
    """Mock service for Draft Purchase Order operations.

    Returns data from local JSON files instead of making API calls.

    Example:
        >>> service = MockDraftPurchaseOrderService()
        >>> drafts = await service.list(limit=10)
        >>> draft = await service.get_by_id("300100574830001")
    """

    def __init__(self, data_loader: MockDataLoader | None = None) -> None:
        super().__init__(data_loader)
        self._resource_name = "draftPurchaseOrders"

    async def list(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        query: str | None = None,
        expand: str | None = None,
        order_by: str | None = None,
    ) -> OracleCollectionResponse[DraftPurchaseOrder]:
        """List draft purchase orders.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            query: Filter query (e.g., "StatusCode='INCOMPLETE'").
            expand: Expand child resources. Ignored in mock.
            order_by: Sort order (e.g., "CreationDate:desc").

        Returns:
            Collection response with draft purchase orders.
        """
        # Get all drafts with valid data (skip stub items with only id)
        all_items = [
            draft for draft in self._data_loader.draft_purchase_orders
            if "POHeaderId" in draft
        ]

        # Apply filtering
        filtered = self._apply_query_filter(all_items, query)

        # Apply sorting
        sorted_items = self._apply_order_by(filtered, order_by)

        # Apply pagination
        paginated, has_more = self._apply_pagination(sorted_items, limit, offset)

        # Convert to models
        items = [DraftPurchaseOrder.model_validate(item) for item in paginated]

        return OracleCollectionResponse[DraftPurchaseOrder](
            items=items,
            count=len(items),
            has_more=has_more,
            limit=limit,
            offset=offset,
            links=self._build_collection_links(self._resource_name),
        )

    async def get_by_id(
        self,
        draft_id: str,
        *,
        expand: str | None = None,
    ) -> DraftPurchaseOrder:
        """Get a draft purchase order by ID.

        Args:
            draft_id: Draft PO ID (can be POHeaderId or the compound id).
            expand: Expand child resources. Ignored in mock.

        Returns:
            Draft purchase order instance.

        Raises:
            ValueError: If draft not found.
        """
        # Try to parse as integer first
        try:
            header_id = int(draft_id)
        except ValueError:
            # If it's a compound ID, extract the numeric part
            header_id = int(draft_id.replace("AABORAQLEABORAQLE", ""))

        draft_data = self._data_loader.get_draft_po(header_id)
        if draft_data is None:
            raise ValueError(f"Draft purchase order not found: {draft_id}")

        return DraftPurchaseOrder.model_validate(draft_data)

    async def get_lines(self, draft_id: str) -> list[DraftPOLine]:
        """Get lines for a draft purchase order.

        Args:
            draft_id: Draft PO ID.

        Returns:
            List of draft purchase order lines.
        """
        draft = await self.get_by_id(draft_id)
        return draft.lines

    async def submit(self, draft_id: str) -> OracleActionResponse:
        """Submit a draft purchase order (mock).

        Args:
            draft_id: Draft PO ID.

        Returns:
            Action response.
        """
        draft = await self.get_by_id(draft_id)

        return self._create_action_response(
            action="submit",
            result="SUCCESS",
            message=f"Draft purchase order {draft.order_number} submitted successfully.",
        )

    async def calculate_tax(self, draft_id: str) -> OracleActionResponse:
        """Calculate tax for a draft purchase order (mock).

        Args:
            draft_id: Draft PO ID.

        Returns:
            Action response.
        """
        draft = await self.get_by_id(draft_id)

        return self._create_action_response(
            action="calculateTaxAndAccounting",
            result="SUCCESS",
            message=f"Tax calculated for draft {draft.order_number}.",
            details={"tax_amount": 0.0, "currency": draft.currency},
        )

    async def check_funds(self, draft_id: str) -> OracleActionResponse:
        """Check funds availability for a draft purchase order (mock).

        Args:
            draft_id: Draft PO ID.

        Returns:
            Action response.
        """
        draft = await self.get_by_id(draft_id)

        return self._create_action_response(
            action="checkFunds",
            result="SUCCESS",
            message=f"Funds available for draft {draft.order_number}.",
            details={"funds_available": True},
        )

    async def cancel_change_order(self, draft_id: str) -> OracleActionResponse:
        """Cancel a change order on a draft (mock).

        Args:
            draft_id: Draft PO ID.

        Returns:
            Action response.
        """
        await self.get_by_id(draft_id)

        return self._create_action_response(
            action="cancelChangeOrder",
            result="SUCCESS",
            message="Change order cancelled.",
        )

    async def delete_change_order(self, draft_id: str) -> OracleActionResponse:
        """Delete a change order on a draft (mock).

        Args:
            draft_id: Draft PO ID.

        Returns:
            Action response.
        """
        await self.get_by_id(draft_id)

        return self._create_action_response(
            action="deleteChangeOrder",
            result="SUCCESS",
            message="Change order deleted.",
        )
