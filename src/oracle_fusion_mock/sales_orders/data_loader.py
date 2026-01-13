"""Data loader for Sales Orders mock data.

Loads and manages mock data from local JSON files, providing consistent
access to sales orders, customers, and products.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SalesOrderDataLoader:
    """Loads and manages mock Sales Order data from local JSON files.

    This class handles loading data from the sales_orders.json file and provides
    indexed access to all entities for efficient lookups.

    Attributes:
        data: Raw data dictionary loaded from JSON file.
        orders_by_id: Index of orders by HeaderId.
        customers_by_id: Index of customers by CustomerId.
        products_by_id: Index of products by InventoryItemId.
    """

    _instance: SalesOrderDataLoader | None = None
    _data: dict[str, Any] | None = None

    def __new__(cls, data_path: str | Path | None = None) -> SalesOrderDataLoader:
        """Singleton pattern - ensures consistent data across all services."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, data_path: str | Path | None = None) -> None:
        """Initialize the data loader.

        Args:
            data_path: Path to the sales_orders.json file. If None, uses the default
                       location relative to this package.
        """
        if getattr(self, "_initialized", False):
            return

        if data_path is None:
            # Default to the package's data directory
            default_path = Path(__file__).parent.parent / "data" / "sales_orders.json"
            data_path = default_path

        self._data_path = Path(data_path)
        self._load_data()
        self._build_indexes()
        self._initialized = True

    def _load_data(self) -> None:
        """Load data from the JSON file."""
        if not self._data_path.exists():
            raise FileNotFoundError(
                f"Sales order mock data file not found: {self._data_path}\n"
                f"Please ensure sales_orders.json exists at the expected location."
            )

        with open(self._data_path, encoding="utf-8") as f:
            SalesOrderDataLoader._data = json.load(f)

    def _build_indexes(self) -> None:
        """Build indexes for efficient lookups."""
        data = self.data

        # Orders index by HeaderId
        self.orders_by_id: dict[str, dict[str, Any]] = {}
        for order in data.get("salesOrders", []):
            if "HeaderId" in order:
                self.orders_by_id[order["HeaderId"]] = order

        # Customers index by CustomerId
        self.customers_by_id: dict[str, dict[str, Any]] = {}
        for customer in data.get("customers", []):
            if "CustomerId" in customer:
                self.customers_by_id[customer["CustomerId"]] = customer

        # Products index by InventoryItemId
        self.products_by_id: dict[str, dict[str, Any]] = {}
        for product in data.get("products", []):
            if "InventoryItemId" in product:
                self.products_by_id[product["InventoryItemId"]] = product

    @property
    def data(self) -> dict[str, Any]:
        """Get the raw data dictionary."""
        if SalesOrderDataLoader._data is None:
            raise RuntimeError("Data not loaded. Call _load_data() first.")
        return SalesOrderDataLoader._data

    @property
    def orders(self) -> list[dict[str, Any]]:
        """Get all sales orders."""
        return self.data.get("salesOrders", [])

    @property
    def customers(self) -> list[dict[str, Any]]:
        """Get all customers."""
        return self.data.get("customers", [])

    @property
    def products(self) -> list[dict[str, Any]]:
        """Get all products."""
        return self.data.get("products", [])

    def get_order(self, header_id: str) -> dict[str, Any] | None:
        """Get an order by HeaderId."""
        return self.orders_by_id.get(header_id)

    def get_customer(self, customer_id: str) -> dict[str, Any] | None:
        """Get a customer by CustomerId."""
        return self.customers_by_id.get(customer_id)

    def get_product(self, product_id: str) -> dict[str, Any] | None:
        """Get a product by InventoryItemId."""
        return self.products_by_id.get(product_id)

    def get_orders_by_customer(self, customer_id: str) -> list[dict[str, Any]]:
        """Get all orders for a customer."""
        return [o for o in self.orders if o.get("CustomerId") == customer_id]

    def get_order_lines_by_product(self, product_id: str) -> list[dict[str, Any]]:
        """Get all order lines that contain a specific product."""
        lines = []
        for order in self.orders:
            for line in order.get("lines", []):
                if line.get("InventoryItemId") == product_id:
                    lines.append(line)
        return lines

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance. Useful for testing."""
        cls._instance = None
        cls._data = None
