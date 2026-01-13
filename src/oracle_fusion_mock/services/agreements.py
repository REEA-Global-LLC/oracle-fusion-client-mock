"""Mock Purchase Agreements service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oracle_fusion_mock.models import (
    OracleCollectionResponse,
    PurchaseAgreement,
)
from oracle_fusion_mock.services.base import BaseMockService

if TYPE_CHECKING:
    from oracle_fusion_mock.data_loader import MockDataLoader


class MockAgreementService(BaseMockService):
    """Mock service for Purchase Agreement operations.

    Returns data from local JSON files instead of making API calls.

    Example:
        >>> service = MockAgreementService()
        >>> agreements = await service.list(limit=10)
        >>> agreement = await service.get_by_id(300100574820001)
    """

    def __init__(self, data_loader: MockDataLoader | None = None) -> None:
        super().__init__(data_loader)
        self._resource_name = "purchaseAgreements"

    async def list(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        query: str | None = None,
        expand: str | None = None,
    ) -> OracleCollectionResponse[PurchaseAgreement]:
        """List purchase agreements.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            query: Filter query (e.g., "StatusCode='ACTIVE'").
            expand: Expand child resources. Ignored in mock.

        Returns:
            Collection response with agreements.
        """
        # Get all agreements with valid data
        all_items = [
            agr for agr in self._data_loader.agreements
            if "AgreementHeaderId" in agr
        ]

        # Apply filtering
        filtered = self._apply_query_filter(all_items, query)

        # Apply pagination
        paginated, has_more = self._apply_pagination(filtered, limit, offset)

        # Convert to models
        items = [PurchaseAgreement.model_validate(item) for item in paginated]

        return OracleCollectionResponse[PurchaseAgreement](
            items=items,
            count=len(items),
            has_more=has_more,
            limit=limit,
            offset=offset,
            links=self._build_collection_links(self._resource_name),
        )

    async def get_by_id(
        self,
        agreement_id: int,
        *,
        expand: str | None = None,
    ) -> PurchaseAgreement:
        """Get an agreement by ID.

        Args:
            agreement_id: Agreement header ID.
            expand: Expand child resources. Ignored in mock.

        Returns:
            Purchase agreement instance.

        Raises:
            ValueError: If agreement not found.
        """
        agreement_data = self._data_loader.get_agreement(agreement_id)
        if agreement_data is None:
            raise ValueError(f"Agreement not found: {agreement_id}")

        return PurchaseAgreement.model_validate(agreement_data)

    async def get_by_agreement_number(self, agreement_number: str) -> PurchaseAgreement | None:
        """Get an agreement by agreement number.

        Args:
            agreement_number: The agreement number (e.g., "BPA-2024-001").

        Returns:
            Agreement if found, None otherwise.
        """
        result = await self.list(query=f"Agreement='{agreement_number}'", limit=1)
        return result.items[0] if result.items else None

    async def get_by_supplier(
        self,
        supplier_id: int,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseAgreement]:
        """Get agreements for a specific supplier.

        Args:
            supplier_id: Supplier ID.
            limit: Maximum number of records to return.

        Returns:
            Collection response with agreements.
        """
        return await self.list(query=f"SupplierId={supplier_id}", limit=limit)

    async def get_active_agreements(
        self,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[PurchaseAgreement]:
        """Get all active agreements.

        Args:
            limit: Maximum number of records to return.

        Returns:
            Collection response with active agreements.
        """
        return await self.list(query="StatusCode='ACTIVE'", limit=limit)
