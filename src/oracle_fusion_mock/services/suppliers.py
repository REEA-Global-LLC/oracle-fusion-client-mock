"""Mock Suppliers service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from oracle_fusion_mock.models import (
    OracleCollectionResponse,
    Supplier,
    SupplierContact,
    SupplierSite,
)
from oracle_fusion_mock.services.base import BaseMockService

if TYPE_CHECKING:
    from oracle_fusion_mock.data_loader import MockDataLoader


class MockSupplierService(BaseMockService):
    """Mock service for Supplier operations.

    Returns data from local JSON files instead of making API calls.

    Example:
        >>> service = MockSupplierService()
        >>> suppliers = await service.list(limit=10)
        >>> supplier = await service.get_by_id(1001)
        >>> sites = await service.get_sites(1001)
    """

    def __init__(self, data_loader: MockDataLoader | None = None) -> None:
        super().__init__(data_loader)
        self._resource_name = "suppliers"

    async def list(
        self,
        *,
        limit: int = 25,
        offset: int = 0,
        query: str | None = None,
        expand: str | None = None,
    ) -> OracleCollectionResponse[Supplier]:
        """List suppliers.

        Args:
            limit: Maximum number of records to return.
            offset: Number of records to skip.
            query: Filter query (e.g., "StatusCode='ACTIVE'").
            expand: Expand child resources (e.g., "sites,contacts"). Ignored in mock.

        Returns:
            Collection response with suppliers.
        """
        # Get all suppliers with valid data
        all_items = [
            s for s in self._data_loader.suppliers if "SupplierId" in s
        ]

        # Apply filtering
        filtered = self._apply_query_filter(all_items, query)

        # Apply pagination
        paginated, has_more = self._apply_pagination(filtered, limit, offset)

        # Convert to models
        items = [Supplier.model_validate(item) for item in paginated]

        return OracleCollectionResponse[Supplier](
            items=items,
            count=len(items),
            has_more=has_more,
            limit=limit,
            offset=offset,
            links=self._build_collection_links(self._resource_name),
        )

    async def get_by_id(
        self,
        supplier_id: int,
        *,
        expand: str | None = None,
    ) -> Supplier:
        """Get a supplier by ID.

        Args:
            supplier_id: Supplier ID.
            expand: Expand child resources. Ignored in mock.

        Returns:
            Supplier instance.

        Raises:
            ValueError: If supplier not found.
        """
        supplier_data = self._data_loader.get_supplier(supplier_id)
        if supplier_data is None:
            raise ValueError(f"Supplier not found: {supplier_id}")

        return Supplier.model_validate(supplier_data)

    async def get_sites(self, supplier_id: int) -> list[SupplierSite]:
        """Get sites for a supplier.

        Args:
            supplier_id: Supplier ID.

        Returns:
            List of supplier sites.
        """
        supplier = await self.get_by_id(supplier_id)
        return supplier.sites

    async def get_contacts(self, supplier_id: int) -> list[SupplierContact]:
        """Get contacts for a supplier.

        Args:
            supplier_id: Supplier ID.

        Returns:
            List of supplier contacts.
        """
        supplier = await self.get_by_id(supplier_id)
        return supplier.contacts

    async def search_by_name(
        self,
        name: str,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[Supplier]:
        """Search suppliers by name.

        Args:
            name: Supplier name to search for (supports wildcards with *).
            limit: Maximum number of records to return.

        Returns:
            Collection response with matching suppliers.
        """
        query = f"Supplier like '{name}*'"
        return await self.list(limit=limit, query=query)

    async def search_by_number(self, supplier_number: str) -> Supplier | None:
        """Search for a supplier by supplier number.

        Args:
            supplier_number: Supplier number to search for.

        Returns:
            Supplier if found, None otherwise.
        """
        query = f"SupplierNumber='{supplier_number}'"
        result = await self.list(limit=1, query=query)
        return result.items[0] if result.items else None

    async def get_active_suppliers(
        self,
        *,
        limit: int = 25,
    ) -> OracleCollectionResponse[Supplier]:
        """Get all active suppliers.

        Args:
            limit: Maximum number of records to return.

        Returns:
            Collection response with active suppliers.
        """
        return await self.list(query="StatusCode='ACTIVE'", limit=limit)

    async def get_supplier_by_site(self, site_name: str) -> Supplier | None:
        """Find a supplier by one of their site names.

        Args:
            site_name: The site name to search for.

        Returns:
            Supplier if found, None otherwise.
        """
        for supplier_data in self._data_loader.suppliers:
            sites = supplier_data.get("sites", [])
            for site in sites:
                if site.get("SupplierSite") == site_name:
                    return Supplier.model_validate(supplier_data)
        return None
