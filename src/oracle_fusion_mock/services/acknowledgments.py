"""Mock Purchase Order Acknowledgments service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oracle_fusion_mock.models import (
    AcknowledgmentSchedule,
    OracleActionResponse,
    OracleCollectionResponse,
    PurchaseOrderAcknowledgment,
)
from oracle_fusion_mock.services.base import BaseMockService

if TYPE_CHECKING:
    from oracle_fusion_mock.data_loader import MockDataLoader


class MockAcknowledgmentService(BaseMockService):
    """Mock service for Purchase Order Acknowledgment operations.

    Returns data from local JSON files instead of making API calls.

    Example:
        >>> service = MockAcknowledgmentService()
        >>> acks = await service.list(limit=10)
        >>> ack = await service.get_by_po_id(300100574829580)
    """

    def __init__(self, data_loader: MockDataLoader | None = None) -> None:
        super().__init__(data_loader)
        self._resource_name = "purchaseOrderAcknowledgments"

    async def list(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        query: str | None = None,
    ) -> OracleCollectionResponse[PurchaseOrderAcknowledgment]:
        """List purchase order acknowledgments.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            query: Filter query.

        Returns:
            Collection response with acknowledgments.
        """
        # Get all acknowledgments with valid data
        all_items = [
            ack for ack in self._data_loader.acknowledgments
            if "POHeaderId" in ack
        ]

        # Apply filtering
        filtered = self._apply_query_filter(all_items, query)

        # Apply pagination
        paginated, has_more = self._apply_pagination(filtered, limit, offset)

        # Convert to models
        items = [PurchaseOrderAcknowledgment.model_validate(item) for item in paginated]

        return OracleCollectionResponse[PurchaseOrderAcknowledgment](
            items=items,
            count=len(items),
            has_more=has_more,
            limit=limit,
            offset=offset,
            links=self._build_collection_links(self._resource_name),
        )

    async def get_by_po_id(self, po_header_id: int) -> PurchaseOrderAcknowledgment:
        """Get an acknowledgment by PO header ID.

        Args:
            po_header_id: Purchase order header ID.

        Returns:
            Purchase order acknowledgment instance.

        Raises:
            ValueError: If acknowledgment not found.
        """
        ack_data = self._data_loader.get_acknowledgment(po_header_id)
        if ack_data is None:
            raise ValueError(f"Acknowledgment not found for PO: {po_header_id}")

        return PurchaseOrderAcknowledgment.model_validate(ack_data)

    async def get_schedules(self, po_header_id: int) -> list[AcknowledgmentSchedule]:
        """Get schedules for an acknowledgment.

        Args:
            po_header_id: Purchase order header ID.

        Returns:
            List of acknowledgment schedules.
        """
        ack = await self.get_by_po_id(po_header_id)
        return ack.schedules

    async def accept(
        self,
        po_header_id: int,
        *,
        supplier_order: str | None = None,
        note: str | None = None,
    ) -> OracleActionResponse:
        """Accept a purchase order acknowledgment (mock).

        Args:
            po_header_id: Purchase order header ID.
            supplier_order: Optional supplier order reference.
            note: Optional acknowledgment note.

        Returns:
            Action response.
        """
        ack = await self.get_by_po_id(po_header_id)

        return self._create_action_response(
            action="accept",
            result="SUCCESS",
            message=f"Acknowledgment accepted for PO {ack.order_number}.",
            details={
                "supplier_order": supplier_order,
                "note": note,
                "response": "ACCEPT",
            },
        )

    async def reject(
        self,
        po_header_id: int,
        *,
        reason: str,
        note: str | None = None,
    ) -> OracleActionResponse:
        """Reject a purchase order acknowledgment (mock).

        Args:
            po_header_id: Purchase order header ID.
            reason: Rejection reason.
            note: Optional acknowledgment note.

        Returns:
            Action response.
        """
        ack = await self.get_by_po_id(po_header_id)

        return self._create_action_response(
            action="reject",
            result="SUCCESS",
            message=f"Acknowledgment rejected for PO {ack.order_number}.",
            details={
                "reason": reason,
                "note": note,
                "response": "REJECT",
            },
        )

    async def accept_with_changes(
        self,
        po_header_id: int,
        *,
        supplier_order: str | None = None,
        note: str | None = None,
        schedule_changes: list[dict] | None = None,
    ) -> OracleActionResponse:
        """Accept with changes a purchase order acknowledgment (mock).

        Args:
            po_header_id: Purchase order header ID.
            supplier_order: Optional supplier order reference.
            note: Optional acknowledgment note.
            schedule_changes: Optional list of schedule modifications.

        Returns:
            Action response.
        """
        ack = await self.get_by_po_id(po_header_id)

        return self._create_action_response(
            action="acceptWithChanges",
            result="SUCCESS",
            message=f"Acknowledgment accepted with changes for PO {ack.order_number}.",
            details={
                "supplier_order": supplier_order,
                "note": note,
                "response": "ACCEPT_WITH_CHANGES",
                "schedule_changes": schedule_changes,
            },
        )

    async def get_pending_acknowledgments(
        self,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseOrderAcknowledgment]:
        """Get all pending acknowledgments (where response is null).

        Args:
            limit: Maximum number of records to return.

        Returns:
            Collection response with pending acknowledgments.
        """
        # Filter for acknowledgments without a response
        all_items = [
            ack for ack in self._data_loader.acknowledgments
            if "POHeaderId" in ack and ack.get("AcknowledgmentResponse") is None
        ]

        paginated, has_more = self._apply_pagination(all_items, limit, 0)
        items = [PurchaseOrderAcknowledgment.model_validate(item) for item in paginated]

        return OracleCollectionResponse[PurchaseOrderAcknowledgment](
            items=items,
            count=len(items),
            has_more=has_more,
            limit=limit,
            offset=0,
            links=self._build_collection_links(self._resource_name),
        )
