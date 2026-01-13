"""Main mock client facade for Oracle Fusion API."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from oracle_fusion_mock.data_loader import MockDataLoader

if TYPE_CHECKING:
    from oracle_fusion_mock.services.acknowledgments import MockAcknowledgmentService
    from oracle_fusion_mock.services.agreements import MockAgreementService
    from oracle_fusion_mock.services.draft_purchase_orders import MockDraftPurchaseOrderService
    from oracle_fusion_mock.services.purchase_orders import MockPurchaseOrderService
    from oracle_fusion_mock.services.requisitions import MockRequisitionService
    from oracle_fusion_mock.services.suppliers import MockSupplierService


class OracleFusionMockClient:
    """Mock client for Oracle Fusion Cloud Procurement API.

    This client returns data from local JSON files instead of making real API calls.
    It provides the same interface as the real OracleFusionClient for seamless testing.

    All data is loaded from a single db.json file and shared across all services
    to ensure consistency.

    Args:
        data_path: Path to the db.json file. If None, uses the default location.

    Example:
        >>> from oracle_fusion_mock import OracleFusionMockClient
        >>>
        >>> # Using default data (from oracle-fusion-mock-server/db.json)
        >>> async with OracleFusionMockClient() as client:
        ...     orders = await client.purchase_orders.list(limit=10)
        ...     for order in orders.items:
        ...         print(f"{order.order_number}: {order.supplier}")
        >>>
        >>> # Using custom data file
        >>> async with OracleFusionMockClient("/path/to/custom-db.json") as client:
        ...     suppliers = await client.suppliers.list()

    Supported Operations:
        Purchase Orders:
            - list, get_by_id, get_lines
            - cancel, close, communicate, acknowledge (mock actions)
            - get_by_order_number, get_by_supplier, get_open_orders

        Draft Purchase Orders:
            - list, get_by_id, get_lines
            - submit, calculate_tax, check_funds (mock actions)

        Suppliers:
            - list, get_by_id, get_sites, get_contacts
            - search_by_name, search_by_number
            - get_active_suppliers

        Requisitions:
            - list, get_by_id, get_lines
            - list_by_status, return_lines, reassign_buyer (mock actions)
            - get_approved_requisitions, get_pending_requisitions

        Agreements:
            - list, get_by_id
            - get_by_agreement_number, get_by_supplier
            - get_active_agreements

        Acknowledgments:
            - list, get_by_po_id, get_schedules
            - accept, reject, accept_with_changes (mock actions)
            - get_pending_acknowledgments
    """

    def __init__(self, data_path: str | Path | None = None) -> None:
        """Initialize the mock client.

        Args:
            data_path: Path to the db.json file. If None, uses the default location.
        """
        # Reset singleton if a custom path is provided
        if data_path is not None:
            MockDataLoader.reset()

        self._data_loader = MockDataLoader(data_path)

        # Lazy-loaded services
        self._purchase_orders: MockPurchaseOrderService | None = None
        self._draft_purchase_orders: MockDraftPurchaseOrderService | None = None
        self._suppliers: MockSupplierService | None = None
        self._requisitions: MockRequisitionService | None = None
        self._agreements: MockAgreementService | None = None
        self._acknowledgments: MockAcknowledgmentService | None = None

    @property
    def purchase_orders(self) -> MockPurchaseOrderService:
        """Access the Purchase Orders service."""
        if self._purchase_orders is None:
            from oracle_fusion_mock.services.purchase_orders import MockPurchaseOrderService

            self._purchase_orders = MockPurchaseOrderService(self._data_loader)
        return self._purchase_orders

    @property
    def draft_purchase_orders(self) -> MockDraftPurchaseOrderService:
        """Access the Draft Purchase Orders service."""
        if self._draft_purchase_orders is None:
            from oracle_fusion_mock.services.draft_purchase_orders import (
                MockDraftPurchaseOrderService,
            )

            self._draft_purchase_orders = MockDraftPurchaseOrderService(self._data_loader)
        return self._draft_purchase_orders

    @property
    def suppliers(self) -> MockSupplierService:
        """Access the Suppliers service."""
        if self._suppliers is None:
            from oracle_fusion_mock.services.suppliers import MockSupplierService

            self._suppliers = MockSupplierService(self._data_loader)
        return self._suppliers

    @property
    def requisitions(self) -> MockRequisitionService:
        """Access the Requisitions service."""
        if self._requisitions is None:
            from oracle_fusion_mock.services.requisitions import MockRequisitionService

            self._requisitions = MockRequisitionService(self._data_loader)
        return self._requisitions

    @property
    def agreements(self) -> MockAgreementService:
        """Access the Agreements service."""
        if self._agreements is None:
            from oracle_fusion_mock.services.agreements import MockAgreementService

            self._agreements = MockAgreementService(self._data_loader)
        return self._agreements

    @property
    def acknowledgments(self) -> MockAcknowledgmentService:
        """Access the Acknowledgments service."""
        if self._acknowledgments is None:
            from oracle_fusion_mock.services.acknowledgments import MockAcknowledgmentService

            self._acknowledgments = MockAcknowledgmentService(self._data_loader)
        return self._acknowledgments

    @property
    def data_loader(self) -> MockDataLoader:
        """Access the underlying data loader for advanced usage."""
        return self._data_loader

    async def close(self) -> None:
        """Close the client (no-op for mock client)."""
        pass

    async def __aenter__(self) -> OracleFusionMockClient:
        """Enter async context manager."""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Exit async context manager."""
        await self.close()

    @classmethod
    def reset_data(cls) -> None:
        """Reset the data loader singleton.

        Useful for testing when you need to reload data or switch to a different file.
        """
        MockDataLoader.reset()
