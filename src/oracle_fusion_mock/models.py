"""Pydantic models for Oracle Fusion API responses.

These models mirror the oracle-fusion-client models to ensure
compatibility and consistent response formats.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


# =============================================================================
# Base Response Models
# =============================================================================

class OracleLink(BaseModel):
    """Link in Oracle REST API response."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    rel: str
    href: str
    name: str
    kind: str


class OracleCollectionResponse(BaseModel, Generic[T]):
    """Generic collection response from Oracle REST API."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    items: list[T]
    count: int
    has_more: bool = Field(default=False, alias="hasMore")
    limit: int = 25
    offset: int = 0
    links: list[OracleLink] = Field(default_factory=list)


class OracleActionResponse(BaseModel):
    """Response from Oracle action execution."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    result: str
    message: str
    action: str
    timestamp: datetime
    details: dict[str, Any] | None = None


# =============================================================================
# Purchase Order Models
# =============================================================================

class POSchedule(BaseModel):
    """Purchase Order schedule (shipment) model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    line_location_id: int = Field(alias="LineLocationId")
    schedule_number: int = Field(alias="ScheduleNumber")
    quantity: Decimal = Field(alias="Quantity")
    quantity_received: Decimal | None = Field(default=None, alias="QuantityReceived")
    quantity_billed: Decimal | None = Field(default=None, alias="QuantityBilled")
    ship_to_organization: str | None = Field(default=None, alias="ShipToOrganization")
    ship_to_organization_id: int | None = Field(default=None, alias="ShipToOrganizationId")
    ship_to_location: str | None = Field(default=None, alias="ShipToLocation")
    ship_to_location_id: int | None = Field(default=None, alias="ShipToLocationId")
    need_by_date: datetime | None = Field(default=None, alias="NeedByDate")
    promised_date: datetime | None = Field(default=None, alias="PromisedDate")


class POLine(BaseModel):
    """Purchase Order line model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    po_line_id: int = Field(alias="POLineId")
    line_number: int = Field(alias="LineNumber")
    line_status: str | None = Field(default=None, alias="LineStatus")
    line_status_code: str | None = Field(default=None, alias="LineStatusCode")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_number: str | None = Field(default=None, alias="ItemNumber")
    item_id: int | None = Field(default=None, alias="ItemId")
    category_name: str | None = Field(default=None, alias="CategoryName")
    category_id: int | None = Field(default=None, alias="CategoryId")
    quantity: Decimal = Field(alias="Quantity")
    uom: str | None = Field(default=None, alias="UOM")
    uom_code: str | None = Field(default=None, alias="UOMCode")
    unit_price: Decimal = Field(alias="UnitPrice")
    amount: Decimal | None = Field(default=None, alias="Amount")
    currency_amount: Decimal | None = Field(default=None, alias="CurrencyAmount")
    need_by_date: datetime | None = Field(default=None, alias="NeedByDate")
    promised_date: datetime | None = Field(default=None, alias="PromisedDate")
    source_agreement: str | None = Field(default=None, alias="SourceAgreement")
    source_agreement_id: int | None = Field(default=None, alias="SourceAgreementId")
    schedules: list[POSchedule] = Field(default_factory=list, alias="schedules")


class PurchaseOrder(BaseModel):
    """Purchase Order header model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str | None = Field(default=None)
    po_header_id: int = Field(alias="POHeaderId")
    order_number: str = Field(alias="OrderNumber")
    status: str = Field(alias="Status")
    status_code: str = Field(alias="StatusCode")
    supplier: str = Field(alias="Supplier")
    supplier_id: int = Field(alias="SupplierId")
    supplier_site: str | None = Field(default=None, alias="SupplierSite")
    supplier_site_id: int | None = Field(default=None, alias="SupplierSiteId")
    procurement_bu: str = Field(alias="ProcurementBU")
    procurement_bu_id: int = Field(alias="ProcurementBUId")
    requisitioning_bu: str | None = Field(default=None, alias="RequisitioningBU")
    requisitioning_bu_id: int | None = Field(default=None, alias="RequisitioningBUId")
    sold_to_legal_entity: str | None = Field(default=None, alias="SoldToLegalEntity")
    sold_to_legal_entity_id: int | None = Field(default=None, alias="SoldToLegalEntityId")
    bill_to_location: str | None = Field(default=None, alias="BillToLocation")
    bill_to_location_id: int | None = Field(default=None, alias="BillToLocationId")
    buyer: str | None = Field(default=None, alias="Buyer")
    buyer_id: int | None = Field(default=None, alias="BuyerId")
    currency: str = Field(alias="Currency")
    total_amount: Decimal | None = Field(default=None, alias="TotalAmount")
    creation_date: datetime | None = Field(default=None, alias="CreationDate")
    last_update_date: datetime | None = Field(default=None, alias="LastUpdateDate")
    order_date: datetime | None = Field(default=None, alias="OrderDate")
    description: str | None = Field(default=None, alias="Description")
    payment_terms: str | None = Field(default=None, alias="PaymentTerms")
    payment_terms_id: int | None = Field(default=None, alias="PaymentTermsId")
    fob_point: str | None = Field(default=None, alias="FOBPoint")
    freight_terms: str | None = Field(default=None, alias="FreightTerms")
    shipping_method: str | None = Field(default=None, alias="ShippingMethod")
    acknowledgment_status: str | None = Field(default=None, alias="AcknowledgmentStatus")
    required_acknowledgment: str | None = Field(default=None, alias="RequiredAcknowledgment")
    required_acknowledgment_code: str | None = Field(
        default=None, alias="RequiredAcknowledgmentCode"
    )
    acknowledgment_due_date: datetime | None = Field(default=None, alias="AcknowledgmentDueDate")
    acknowledgment_within_days: int | None = Field(default=None, alias="AcknowledgmentWithinDays")
    communicated_date: datetime | None = Field(default=None, alias="CommunicatedDate")
    communicated_version: int | None = Field(default=None, alias="CommunicatedVersion")
    closed_date: datetime | None = Field(default=None, alias="ClosedDate")
    lines: list[POLine] = Field(default_factory=list, alias="lines")


# =============================================================================
# Draft Purchase Order Models
# =============================================================================

class DraftPOLine(BaseModel):
    """Draft Purchase Order line model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    po_line_id: int | None = Field(default=None, alias="POLineId")
    line_number: int = Field(alias="LineNumber")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_number: str | None = Field(default=None, alias="ItemNumber")
    category_name: str | None = Field(default=None, alias="CategoryName")
    quantity: Decimal = Field(alias="Quantity")
    uom: str | None = Field(default=None, alias="UOM")
    unit_price: Decimal = Field(alias="UnitPrice")
    amount: Decimal | None = Field(default=None, alias="Amount")
    need_by_date: datetime | None = Field(default=None, alias="NeedByDate")


class DraftPurchaseOrder(BaseModel):
    """Draft Purchase Order header model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: str | None = Field(default=None)
    po_header_id: int | None = Field(default=None, alias="POHeaderId")
    order_number: str | None = Field(default=None, alias="OrderNumber")
    status: str | None = Field(default=None, alias="Status")
    status_code: str | None = Field(default=None, alias="StatusCode")
    supplier: str | None = Field(default=None, alias="Supplier")
    supplier_id: int | None = Field(default=None, alias="SupplierId")
    supplier_site: str | None = Field(default=None, alias="SupplierSite")
    procurement_bu: str | None = Field(default=None, alias="ProcurementBU")
    procurement_bu_id: int | None = Field(default=None, alias="ProcurementBUId")
    sold_to_legal_entity: str | None = Field(default=None, alias="SoldToLegalEntity")
    sold_to_legal_entity_id: int | None = Field(default=None, alias="SoldToLegalEntityId")
    buyer: str | None = Field(default=None, alias="Buyer")
    buyer_id: int | None = Field(default=None, alias="BuyerId")
    currency: str | None = Field(default=None, alias="Currency")
    total_amount: Decimal | None = Field(default=None, alias="TotalAmount")
    creation_date: datetime | None = Field(default=None, alias="CreationDate")
    last_update_date: datetime | None = Field(default=None, alias="LastUpdateDate")
    description: str | None = Field(default=None, alias="Description")
    lines: list[DraftPOLine] = Field(default_factory=list, alias="lines")


# =============================================================================
# Supplier Models
# =============================================================================

class SupplierContact(BaseModel):
    """Supplier contact model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    contact_id: int = Field(alias="ContactId")
    contact_name: str | None = Field(default=None, alias="ContactName")
    first_name: str | None = Field(default=None, alias="FirstName")
    last_name: str | None = Field(default=None, alias="LastName")
    email: str | None = Field(default=None, alias="Email")
    phone: str | None = Field(default=None, alias="Phone")
    mobile: str | None = Field(default=None, alias="Mobile")
    fax: str | None = Field(default=None, alias="Fax")
    role: str | None = Field(default=None, alias="Role")
    primary_contact_flag: bool | None = Field(default=False, alias="PrimaryContactFlag")
    status: str | None = Field(default=None, alias="Status")


class SupplierSite(BaseModel):
    """Supplier site model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    supplier_site_id: int = Field(alias="SupplierSiteId")
    supplier_site: str = Field(alias="SupplierSite")
    address: str | None = Field(default=None, alias="Address")
    city: str | None = Field(default=None, alias="City")
    state: str | None = Field(default=None, alias="State")
    postal_code: str | None = Field(default=None, alias="PostalCode")
    country: str | None = Field(default=None, alias="Country")
    country_code: str | None = Field(default=None, alias="CountryCode")
    status: str | None = Field(default=None, alias="Status")
    status_code: str | None = Field(default=None, alias="StatusCode")
    payment_terms: str | None = Field(default=None, alias="PaymentTerms")
    payment_terms_id: int | None = Field(default=None, alias="PaymentTermsId")
    pay_site_flag: bool | None = Field(default=False, alias="PaySiteFlag")
    purchasing_site_flag: bool | None = Field(default=False, alias="PurchasingSiteFlag")
    rfq_site_flag: bool | None = Field(default=False, alias="RFQSiteFlag")
    email: str | None = Field(default=None, alias="Email")
    phone: str | None = Field(default=None, alias="Phone")
    fax: str | None = Field(default=None, alias="Fax")


class Supplier(BaseModel):
    """Supplier header model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int | None = Field(default=None)
    supplier_id: int = Field(alias="SupplierId")
    supplier: str = Field(alias="Supplier")
    supplier_number: str | None = Field(default=None, alias="SupplierNumber")
    status: str | None = Field(default=None, alias="Status")
    status_code: str | None = Field(default=None, alias="StatusCode")
    tax_registration_number: str | None = Field(default=None, alias="TaxRegistrationNumber")
    tax_registration_country: str | None = Field(default=None, alias="TaxRegistrationCountry")
    duns_number: str | None = Field(default=None, alias="DUNSNumber")
    supplier_type: str | None = Field(default=None, alias="SupplierType")
    supplier_type_code: str | None = Field(default=None, alias="SupplierTypeCode")
    business_relationship: str | None = Field(default=None, alias="BusinessRelationship")
    business_relationship_code: str | None = Field(
        default=None, alias="BusinessRelationshipCode"
    )
    one_time_supplier_flag: bool | None = Field(default=False, alias="OneTimeSupplierFlag")
    creation_date: datetime | None = Field(default=None, alias="CreationDate")
    last_update_date: datetime | None = Field(default=None, alias="LastUpdateDate")
    sites: list[SupplierSite] = Field(default_factory=list, alias="sites")
    contacts: list[SupplierContact] = Field(default_factory=list, alias="contacts")


# =============================================================================
# Requisition Models
# =============================================================================

class RequisitionLine(BaseModel):
    """Requisition line model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    requisition_line_id: int = Field(alias="RequisitionLineId")
    line_number: int = Field(alias="LineNumber")
    line_status: str | None = Field(default=None, alias="LineStatus")
    item_description: str | None = Field(default=None, alias="ItemDescription")
    item_number: str | None = Field(default=None, alias="ItemNumber")
    category_name: str | None = Field(default=None, alias="CategoryName")
    quantity: Decimal = Field(alias="Quantity")
    uom: str | None = Field(default=None, alias="UOM")
    unit_price: Decimal | None = Field(default=None, alias="UnitPrice")
    amount: Decimal | None = Field(default=None, alias="Amount")
    need_by_date: datetime | None = Field(default=None, alias="NeedByDate")
    suggested_supplier: str | None = Field(default=None, alias="SuggestedSupplier")
    suggested_supplier_id: int | None = Field(default=None, alias="SuggestedSupplierId")
    deliver_to_location: str | None = Field(default=None, alias="DeliverToLocation")
    deliver_to_location_id: int | None = Field(default=None, alias="DeliverToLocationId")
    urgent_flag: bool = Field(default=False, alias="UrgentFlag")


class PurchaseRequisition(BaseModel):
    """Purchase Requisition header model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int | None = Field(default=None)
    requisition_header_id: int = Field(alias="RequisitionHeaderId")
    requisition: str = Field(alias="Requisition")
    description: str | None = Field(default=None, alias="Description")
    status: str = Field(alias="Status")
    status_code: str = Field(alias="StatusCode")
    preparer_name: str | None = Field(default=None, alias="PreparerName")
    preparer_id: int | None = Field(default=None, alias="PreparerId")
    requisitioning_bu: str = Field(alias="RequisitioningBU")
    requisitioning_bu_id: int = Field(alias="RequisitioningBUId")
    currency: str = Field(alias="Currency")
    total_amount: Decimal | None = Field(default=None, alias="TotalAmount")
    creation_date: datetime | None = Field(default=None, alias="CreationDate")
    submitted_date: datetime | None = Field(default=None, alias="SubmittedDate")
    approval_date: datetime | None = Field(default=None, alias="ApprovalDate")
    lines: list[RequisitionLine] = Field(default_factory=list, alias="lines")


# =============================================================================
# Agreement Models
# =============================================================================

class PurchaseAgreement(BaseModel):
    """Purchase Agreement model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int | None = Field(default=None)
    agreement_header_id: int = Field(alias="AgreementHeaderId")
    agreement: str = Field(alias="Agreement")
    description: str | None = Field(default=None, alias="Description")
    type: str | None = Field(default=None, alias="Type")
    type_code: str | None = Field(default=None, alias="TypeCode")
    status: str = Field(alias="Status")
    status_code: str = Field(alias="StatusCode")
    supplier: str = Field(alias="Supplier")
    supplier_id: int = Field(alias="SupplierId")
    supplier_site: str | None = Field(default=None, alias="SupplierSite")
    supplier_site_id: int | None = Field(default=None, alias="SupplierSiteId")
    procurement_bu: str = Field(alias="ProcurementBU")
    procurement_bu_id: int = Field(alias="ProcurementBUId")
    currency: str = Field(alias="Currency")
    agreed_amount: Decimal | None = Field(default=None, alias="AgreedAmount")
    amount_released: Decimal | None = Field(default=None, alias="AmountReleased")
    amount_remaining: Decimal | None = Field(default=None, alias="AmountRemaining")
    effective_date: datetime | None = Field(default=None, alias="EffectiveDate")
    expiration_date: datetime | None = Field(default=None, alias="ExpirationDate")
    buyer: str | None = Field(default=None, alias="Buyer")
    buyer_id: int | None = Field(default=None, alias="BuyerId")
    payment_terms: str | None = Field(default=None, alias="PaymentTerms")
    automatically_generate_orders_flag: bool = Field(
        default=False, alias="AutomaticallyGenerateOrdersFlag"
    )
    creation_date: datetime | None = Field(default=None, alias="CreationDate")
    last_update_date: datetime | None = Field(default=None, alias="LastUpdateDate")


# =============================================================================
# Acknowledgment Models
# =============================================================================

class AcknowledgmentSchedule(BaseModel):
    """Acknowledgment schedule model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    line_location_id: int = Field(alias="LineLocationId")
    po_header_id: int = Field(alias="POHeaderId")
    po_line_id: int = Field(alias="POLineId")
    line_number: int = Field(alias="LineNumber")
    schedule_number: int = Field(alias="ScheduleNumber")
    response: str | None = Field(default=None, alias="Response")
    rejection_reason: str | None = Field(default=None, alias="RejectionReason")
    supplier_order_line_number: str | None = Field(default=None, alias="SupplierOrderLineNumber")


class PurchaseOrderAcknowledgment(BaseModel):
    """Purchase Order Acknowledgment model."""

    model_config = ConfigDict(populate_by_name=True, extra="ignore")

    id: int | None = Field(default=None)
    po_header_id: int = Field(alias="POHeaderId")
    order_number: str = Field(alias="OrderNumber")
    sold_to_legal_entity: str | None = Field(default=None, alias="SoldToLegalEntity")
    sold_to_legal_entity_id: int | None = Field(default=None, alias="SoldToLegalEntityId")
    required_acknowledgment: str | None = Field(default=None, alias="RequiredAcknowledgment")
    required_acknowledgment_code: str | None = Field(
        default=None, alias="RequiredAcknowledgmentCode"
    )
    acknowledgment_due_date: datetime | None = Field(default=None, alias="AcknowledgmentDueDate")
    acknowledgment_within_days: int | None = Field(default=None, alias="AcknowledgmentWithinDays")
    acknowledgment_response: str | None = Field(default=None, alias="AcknowledgmentResponse")
    acknowledgment_note: str | None = Field(default=None, alias="AcknowledgmentNote")
    supplier_order: str | None = Field(default=None, alias="SupplierOrder")
    change_order_number: str | None = Field(default=None, alias="ChangeOrderNumber")
    schedules: list[AcknowledgmentSchedule] = Field(default_factory=list, alias="schedules")
