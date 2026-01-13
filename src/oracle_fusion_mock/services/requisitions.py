"""Mock Requisitions service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oracle_fusion_mock.models import (
    OracleActionResponse,
    OracleCollectionResponse,
    PurchaseRequisition,
    RequisitionLine,
)
from oracle_fusion_mock.services.base import BaseMockService

if TYPE_CHECKING:
    from oracle_fusion_mock.data_loader import MockDataLoader


class MockRequisitionService(BaseMockService):
    """Mock service for Purchase Requisition operations.

    Returns data from local JSON files instead of making API calls.

    Example:
        >>> service = MockRequisitionService()
        >>> reqs = await service.list(limit=10)
        >>> req = await service.get_by_id(300100574825001)
    """

    def __init__(self, data_loader: MockDataLoader | None = None) -> None:
        super().__init__(data_loader)
        self._resource_name = "purchaseRequisitions"

    async def list(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        query: str | None = None,
        expand: str | None = None,
        order_by: str | None = None,
    ) -> OracleCollectionResponse[PurchaseRequisition]:
        """List purchase requisitions.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            query: Filter query (e.g., "StatusCode='APPROVED'").
            expand: Expand child resources. Ignored in mock.
            order_by: Sort order (e.g., "CreationDate:desc").

        Returns:
            Collection response with requisitions.
        """
        # Get all requisitions with valid data
        all_items = [
            req for req in self._data_loader.requisitions
            if "RequisitionHeaderId" in req
        ]

        # Apply filtering
        filtered = self._apply_query_filter(all_items, query)

        # Apply sorting
        sorted_items = self._apply_order_by(filtered, order_by)

        # Apply pagination
        paginated, has_more = self._apply_pagination(sorted_items, limit, offset)

        # Convert to models
        items = [PurchaseRequisition.model_validate(item) for item in paginated]

        return OracleCollectionResponse[PurchaseRequisition](
            items=items,
            count=len(items),
            has_more=has_more,
            limit=limit,
            offset=offset,
            links=self._build_collection_links(self._resource_name),
        )

    async def get_by_id(
        self,
        requisition_id: int,
        *,
        expand: str | None = None,
    ) -> PurchaseRequisition:
        """Get a requisition by ID.

        Args:
            requisition_id: Requisition header ID.
            expand: Expand child resources. Ignored in mock.

        Returns:
            Purchase requisition instance.

        Raises:
            ValueError: If requisition not found.
        """
        req_data = self._data_loader.get_requisition(requisition_id)
        if req_data is None:
            raise ValueError(f"Requisition not found: {requisition_id}")

        return PurchaseRequisition.model_validate(req_data)

    async def get_lines(self, requisition_id: int) -> list[RequisitionLine]:
        """Get lines for a requisition.

        Args:
            requisition_id: Requisition header ID.

        Returns:
            List of requisition lines.
        """
        req = await self.get_by_id(requisition_id)
        return req.lines

    async def list_by_status(
        self,
        status_code: str,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseRequisition]:
        """List requisitions by status.

        Args:
            status_code: Status code (e.g., "APPROVED", "PENDING_APPROVAL").
            limit: Maximum number of records to return.

        Returns:
            Collection response with requisitions.
        """
        return await self.list(query=f"StatusCode='{status_code}'", limit=limit)

    async def return_lines(
        self,
        requisition_id: int,
        *,
        line_ids: list[int] | None = None,
        reason: str | None = None,
    ) -> OracleActionResponse:
        """Return requisition lines (mock).

        Args:
            requisition_id: Requisition header ID.
            line_ids: Optional list of specific line IDs to return.
            reason: Reason for return.

        Returns:
            Action response.
        """
        req = await self.get_by_id(requisition_id)

        return self._create_action_response(
            action="returnLines",
            result="SUCCESS",
            message=f"Lines returned for requisition {req.requisition}.",
            details={"line_ids": line_ids, "reason": reason},
        )

    async def reassign_buyer(
        self,
        requisition_id: int,
        *,
        new_buyer_id: int,
        line_ids: list[int] | None = None,
    ) -> OracleActionResponse:
        """Reassign buyer for requisition lines (mock).

        Args:
            requisition_id: Requisition header ID.
            new_buyer_id: New buyer ID.
            line_ids: Optional list of specific line IDs to reassign.

        Returns:
            Action response.
        """
        req = await self.get_by_id(requisition_id)

        return self._create_action_response(
            action="reassignBuyer",
            result="SUCCESS",
            message=f"Buyer reassigned for requisition {req.requisition}.",
            details={"new_buyer_id": new_buyer_id, "line_ids": line_ids},
        )

    async def split_line(
        self,
        requisition_id: int,
        *,
        line_id: int,
        split_quantities: list[int],
    ) -> OracleActionResponse:
        """Split a requisition line (mock).

        Args:
            requisition_id: Requisition header ID.
            line_id: Line ID to split.
            split_quantities: List of quantities for the split lines.

        Returns:
            Action response.
        """
        req = await self.get_by_id(requisition_id)

        return self._create_action_response(
            action="splitLine",
            result="SUCCESS",
            message=f"Line split for requisition {req.requisition}.",
            details={"line_id": line_id, "split_quantities": split_quantities},
        )

    async def get_approved_requisitions(
        self,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseRequisition]:
        """Get all approved requisitions.

        Args:
            limit: Maximum number of records to return.

        Returns:
            Collection response with approved requisitions.
        """
        return await self.list_by_status("APPROVED", limit=limit)

    async def get_pending_requisitions(
        self,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseRequisition]:
        """Get all pending approval requisitions.

        Args:
            limit: Maximum number of records to return.

        Returns:
            Collection response with pending requisitions.
        """
        return await self.list_by_status("PENDING_APPROVAL", limit=limit)
