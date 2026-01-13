"""Pydantic models for Sales Orders - Compatible with client-valence-anomaly-detection.

These models are designed to be 100% compatible with the models expected by
the anomaly detection system in client-valence-anomaly-detection/src/oracle/models.py.

The field aliases match exactly what Oracle Fusion Sales Orders API returns.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Order status values in Oracle Fusion."""

    ENTERED = "Entered"
    BOOKED = "Booked"
    CLOSED = "Closed"
    CANCELLED = "Cancelled"
    AWAITING_SHIPPING = "Awaiting Shipping"
    AWAITING_BILLING = "Awaiting Billing"
    PENDING_APPROVAL = "Pending Approval"


class Product(BaseModel):
    """Product information."""

    product_id: str = Field(..., alias="InventoryItemId")
    product_number: str = Field(..., alias="ProductNumber")
    product_description: str | None = Field(None, alias="ProductDescription")
    uom: str | None = Field(None, alias="UOMCode")
    unit_price: Decimal | None = Field(None, alias="UnitSellingPrice")

    model_config = {"populate_by_name": True}


class Customer(BaseModel):
    """Customer information."""

    customer_id: str = Field(..., alias="CustomerId")
    customer_number: str | None = Field(None, alias="CustomerNumber")
    customer_name: str = Field(..., alias="CustomerName")
    account_number: str | None = Field(None, alias="AccountNumber")
    site_id: str | None = Field(None, alias="BillToSiteId")

    model_config = {"populate_by_name": True}


class OrderLine(BaseModel):
    """Individual line item in an order."""

    line_id: str = Field(..., alias="OrderLineId")
    line_number: int = Field(..., alias="LineNumber")
    product_id: str = Field(..., alias="InventoryItemId")
    product_number: str | None = Field(None, alias="ProductNumber")
    product_description: str | None = Field(None, alias="ProductDescription")
    ordered_quantity: Decimal = Field(..., alias="OrderedQuantity")
    ordered_uom: str | None = Field(None, alias="OrderedUOMCode")
    unit_selling_price: Decimal | None = Field(None, alias="UnitSellingPrice")
    extended_amount: Decimal | None = Field(None, alias="ExtendedAmount")
    status: str | None = Field(None, alias="StatusCode")

    model_config = {"populate_by_name": True}

    @property
    def line_total(self) -> Decimal:
        """Calculate line total."""
        if self.extended_amount is not None:
            return self.extended_amount
        if self.unit_selling_price is not None:
            return self.ordered_quantity * self.unit_selling_price
        return Decimal("0")


class Order(BaseModel):
    """Sales order from Oracle Fusion."""

    order_id: str = Field(..., alias="HeaderId")
    order_number: str = Field(..., alias="OrderNumber")
    order_type: str | None = Field(None, alias="OrderTypeCode")
    status: OrderStatus | str = Field(..., alias="StatusCode")

    # Customer information
    customer_id: str = Field(..., alias="CustomerId")
    customer_name: str | None = Field(None, alias="CustomerName")
    customer_number: str | None = Field(None, alias="CustomerNumber")
    bill_to_site_id: str | None = Field(None, alias="BillToSiteId")
    ship_to_site_id: str | None = Field(None, alias="ShipToSiteId")

    # Amounts
    total_amount: Decimal = Field(..., alias="TotalAmount")
    currency_code: str = Field(default="USD", alias="CurrencyCode")

    # Dates
    order_date: datetime = Field(..., alias="OrderedDate")
    requested_ship_date: datetime | None = Field(None, alias="RequestedShipDate")
    creation_date: datetime | None = Field(None, alias="CreationDate")
    last_update_date: datetime | None = Field(None, alias="LastUpdateDate")

    # Sales info
    salesperson_id: str | None = Field(None, alias="SalespersonId")
    salesperson_name: str | None = Field(None, alias="SalespersonName")
    business_unit: str | None = Field(None, alias="BusinessUnitName")

    # Order lines
    lines: list[OrderLine] = Field(default_factory=list, alias="lines")

    # Additional data (raw response for reference)
    raw_data: dict[str, Any] | None = Field(default=None, exclude=True)

    model_config = {"populate_by_name": True}

    @property
    def total_quantity(self) -> Decimal:
        """Get total quantity across all lines."""
        return sum((line.ordered_quantity for line in self.lines), Decimal("0"))

    @property
    def line_count(self) -> int:
        """Get number of order lines."""
        return len(self.lines)

    def get_line_by_product(self, product_id: str) -> OrderLine | None:
        """Find order line by product ID."""
        for line in self.lines:
            if line.product_id == product_id:
                return line
        return None


class OrderUpdate(BaseModel):
    """Model for updating an order in Oracle Fusion."""

    # Fields that can be updated
    status: OrderStatus | None = None
    requested_ship_date: datetime | None = None

    # Line updates (by line_id)
    line_updates: dict[str, dict[str, Any]] | None = None

    def to_oracle_payload(self) -> dict[str, Any]:
        """Convert to Oracle Fusion PATCH payload."""
        payload: dict[str, Any] = {}

        if self.status:
            payload["StatusCode"] = self.status.value

        if self.requested_ship_date:
            payload["RequestedShipDate"] = self.requested_ship_date.isoformat()

        return payload


class OrderSearchCriteria(BaseModel):
    """Search criteria for querying orders."""

    customer_id: str | None = None
    customer_name: str | None = None
    order_number: str | None = None
    status: OrderStatus | None = None
    from_date: datetime | None = None
    to_date: datetime | None = None
    min_amount: Decimal | None = None
    max_amount: Decimal | None = None
    business_unit: str | None = None
    limit: int = Field(default=100, ge=1, le=500)
    offset: int = Field(default=0, ge=0)

    def to_query_params(self) -> dict[str, str]:
        """Convert to Oracle Fusion query parameters."""
        params: dict[str, str] = {
            "limit": str(self.limit),
            "offset": str(self.offset),
        }

        # Build finder query
        finder_parts: list[str] = []

        if self.customer_id:
            finder_parts.append(f"CustomerId={self.customer_id}")

        if self.order_number:
            finder_parts.append(f"OrderNumber={self.order_number}")

        if self.status:
            finder_parts.append(f"StatusCode={self.status.value}")

        if self.from_date:
            finder_parts.append(f"OrderedDate>={self.from_date.strftime('%Y-%m-%d')}")

        if self.to_date:
            finder_parts.append(f"OrderedDate<={self.to_date.strftime('%Y-%m-%d')}")

        if self.min_amount is not None:
            finder_parts.append(f"TotalAmount>={self.min_amount}")

        if self.max_amount is not None:
            finder_parts.append(f"TotalAmount<={self.max_amount}")

        if finder_parts:
            params["q"] = ";".join(finder_parts)

        return params


class CustomerOrderHistory(BaseModel):
    """Customer's historical order patterns."""

    customer_id: str
    customer_name: str
    total_orders: int
    total_amount: Decimal
    average_order_amount: Decimal
    max_order_amount: Decimal
    min_order_amount: Decimal
    std_dev_amount: Decimal
    average_quantity: Decimal
    last_order_date: datetime | None
    first_order_date: datetime | None
    orders: list[Order] = Field(default_factory=list)


class ProductOrderHistory(BaseModel):
    """Product's historical order patterns."""

    product_id: str
    product_number: str
    product_description: str | None
    total_orders: int
    total_quantity: Decimal
    average_quantity: Decimal
    max_quantity: Decimal
    min_quantity: Decimal
    std_dev_quantity: Decimal
    average_price: Decimal
    order_lines: list[OrderLine] = Field(default_factory=list)
