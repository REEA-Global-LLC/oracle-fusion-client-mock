"""Data loader for mock Oracle Fusion data.

Loads and manages mock data from local JSON files, providing consistent
access to purchase orders, suppliers, requisitions, and other entities.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class MockDataLoader:
    """Loads and manages mock data from local JSON files.

    This class handles loading data from the db.json file and provides
    indexed access to all entities for efficient lookups.

    Attributes:
        data: Raw data dictionary loaded from JSON file.
        purchase_orders_by_id: Index of purchase orders by POHeaderId.
        suppliers_by_id: Index of suppliers by SupplierId.
        requisitions_by_id: Index of requisitions by RequisitionHeaderId.
        draft_pos_by_id: Index of draft POs by POHeaderId.
        agreements_by_id: Index of agreements by AgreementHeaderId.
        acknowledgments_by_po_id: Index of acknowledgments by POHeaderId.
    """

    _instance: MockDataLoader | None = None
    _data: dict[str, Any] | None = None

    def __new__(cls, data_path: str | Path | None = None) -> MockDataLoader:
        """Singleton pattern - ensures consistent data across all services."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_path: str | Path | None = None) -> None:
        """Initialize the data loader.

        Args:
            data_path: Path to the db.json file. If None, uses the default
                       location relative to this package.
        """
        if getattr(self, "_initialized", False):
            return

        if data_path is None:
            # Default to the mock server's db.json
            default_path = (
                Path(__file__).parent.parent.parent.parent
                / "oracle-fusion-client"
                / "oracle-fusion-mock-server"
                / "db.json"
            )
            data_path = default_path

        self._data_path = Path(data_path)
        self._load_data()
        self._build_indexes()
        self._initialized = True

    def _load_data(self) -> None:
        """Load data from the JSON file."""
        if not self._data_path.exists():
            raise FileNotFoundError(
                f"Mock data file not found: {self._data_path}\n"
                f"Please ensure db.json exists at the expected location."
            )

        with open(self._data_path, encoding="utf-8") as f:
            MockDataLoader._data = json.load(f)

    def _build_indexes(self) -> None:
        """Build indexes for efficient lookups."""
        data = self.data

        # Purchase Orders index
        self.purchase_orders_by_id: dict[int, dict[str, Any]] = {}
        for po in data.get("purchaseOrders", []):
            if "POHeaderId" in po:
                self.purchase_orders_by_id[po["POHeaderId"]] = po

        # Suppliers index
        self.suppliers_by_id: dict[int, dict[str, Any]] = {}
        for supplier in data.get("suppliers", []):
            if "SupplierId" in supplier:
                self.suppliers_by_id[supplier["SupplierId"]] = supplier

        # Requisitions index
        self.requisitions_by_id: dict[int, dict[str, Any]] = {}
        for req in data.get("purchaseRequisitions", []):
            if "RequisitionHeaderId" in req:
                self.requisitions_by_id[req["RequisitionHeaderId"]] = req

        # Draft Purchase Orders index
        self.draft_pos_by_id: dict[int, dict[str, Any]] = {}
        for draft in data.get("draftPurchaseOrders", []):
            if "POHeaderId" in draft:
                self.draft_pos_by_id[draft["POHeaderId"]] = draft

        # Agreements index
        self.agreements_by_id: dict[int, dict[str, Any]] = {}
        for agreement in data.get("purchaseAgreements", []):
            if "AgreementHeaderId" in agreement:
                self.agreements_by_id[agreement["AgreementHeaderId"]] = agreement

        # Acknowledgments index (by PO Header ID)
        self.acknowledgments_by_po_id: dict[int, dict[str, Any]] = {}
        for ack in data.get("purchaseOrderAcknowledgments", []):
            if "POHeaderId" in ack:
                self.acknowledgments_by_po_id[ack["POHeaderId"]] = ack

    @property
    def data(self) -> dict[str, Any]:
        """Get the raw data dictionary."""
        if MockDataLoader._data is None:
            raise RuntimeError("Data not loaded. Call _load_data() first.")
        return MockDataLoader._data

    @property
    def purchase_orders(self) -> list[dict[str, Any]]:
        """Get all purchase orders."""
        return self.data.get("purchaseOrders", [])

    @property
    def suppliers(self) -> list[dict[str, Any]]:
        """Get all suppliers."""
        return self.data.get("suppliers", [])

    @property
    def requisitions(self) -> list[dict[str, Any]]:
        """Get all purchase requisitions."""
        return self.data.get("purchaseRequisitions", [])

    @property
    def draft_purchase_orders(self) -> list[dict[str, Any]]:
        """Get all draft purchase orders."""
        return self.data.get("draftPurchaseOrders", [])

    @property
    def agreements(self) -> list[dict[str, Any]]:
        """Get all purchase agreements."""
        return self.data.get("purchaseAgreements", [])

    @property
    def acknowledgments(self) -> list[dict[str, Any]]:
        """Get all purchase order acknowledgments."""
        return self.data.get("purchaseOrderAcknowledgments", [])

    def get_purchase_order(self, po_header_id: int) -> dict[str, Any] | None:
        """Get a purchase order by ID."""
        return self.purchase_orders_by_id.get(po_header_id)

    def get_supplier(self, supplier_id: int) -> dict[str, Any] | None:
        """Get a supplier by ID."""
        return self.suppliers_by_id.get(supplier_id)

    def get_requisition(self, requisition_id: int) -> dict[str, Any] | None:
        """Get a requisition by ID."""
        return self.requisitions_by_id.get(requisition_id)

    def get_draft_po(self, po_header_id: int) -> dict[str, Any] | None:
        """Get a draft purchase order by ID."""
        return self.draft_pos_by_id.get(po_header_id)

    def get_agreement(self, agreement_id: int) -> dict[str, Any] | None:
        """Get an agreement by ID."""
        return self.agreements_by_id.get(agreement_id)

    def get_acknowledgment(self, po_header_id: int) -> dict[str, Any] | None:
        """Get an acknowledgment by PO header ID."""
        return self.acknowledgments_by_po_id.get(po_header_id)

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance. Useful for testing."""
        cls._instance = None
        cls._data = None
