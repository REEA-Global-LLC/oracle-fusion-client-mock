"""Tests for the mock Purchase Orders service."""

import pytest

from oracle_fusion_mock import OracleFusionMockClient
from oracle_fusion_mock.models import OracleCollectionResponse, PurchaseOrder


class TestMockPurchaseOrderService:
    """Tests for MockPurchaseOrderService."""

    @pytest.mark.asyncio
    async def test_list_purchase_orders(self):
        """Test listing purchase orders."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.list()

            assert isinstance(result, OracleCollectionResponse)
            assert len(result.items) > 0
            assert all(isinstance(po, PurchaseOrder) for po in result.items)

    @pytest.mark.asyncio
    async def test_list_with_limit(self):
        """Test listing with limit."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.list(limit=2)

            assert len(result.items) <= 2
            assert result.limit == 2

    @pytest.mark.asyncio
    async def test_list_with_pagination(self):
        """Test pagination works correctly."""
        async with OracleFusionMockClient() as client:
            # Get first page
            page1 = await client.purchase_orders.list(limit=2, offset=0)
            # Get second page
            page2 = await client.purchase_orders.list(limit=2, offset=2)

            # Items should be different
            if page1.items and page2.items:
                assert page1.items[0].po_header_id != page2.items[0].po_header_id

    @pytest.mark.asyncio
    async def test_list_with_query_filter(self):
        """Test filtering by query."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.list(query="StatusCode='OPEN'")

            assert all(po.status_code == "OPEN" for po in result.items)

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        """Test getting a single purchase order."""
        async with OracleFusionMockClient() as client:
            po = await client.purchase_orders.get_by_id("300100574829561")

            assert isinstance(po, PurchaseOrder)
            assert po.po_header_id == 300100574829561
            assert po.order_number == "PO-2024-0001"
            assert po.supplier == "ABC Office Supplies Inc"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test getting a non-existent PO raises error."""
        async with OracleFusionMockClient() as client:
            with pytest.raises(ValueError, match="not found"):
                await client.purchase_orders.get_by_id("999999999")

    @pytest.mark.asyncio
    async def test_get_lines(self):
        """Test getting lines for a purchase order."""
        async with OracleFusionMockClient() as client:
            lines = await client.purchase_orders.get_lines("300100574829561")

            assert len(lines) == 2
            assert lines[0].line_number == 1
            assert lines[0].item_description == "Premium Copy Paper A4"

    @pytest.mark.asyncio
    async def test_cancel_action(self):
        """Test cancel action returns success response."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.cancel(
                "300100574829561", reason="Testing"
            )

            assert result.result == "SUCCESS"
            assert result.action == "cancel"

    @pytest.mark.asyncio
    async def test_close_action(self):
        """Test close action returns success response."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.close("300100574829561")

            assert result.result == "SUCCESS"
            assert result.action == "close"

    @pytest.mark.asyncio
    async def test_communicate_action(self):
        """Test communicate action returns success response."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.communicate(
                "300100574829561", method="Email"
            )

            assert result.result == "SUCCESS"
            assert result.action == "communicate"

    @pytest.mark.asyncio
    async def test_get_open_orders(self):
        """Test getting open orders helper."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.get_open_orders()

            assert all(po.status_code == "OPEN" for po in result.items)

    @pytest.mark.asyncio
    async def test_get_by_supplier(self):
        """Test getting orders by supplier."""
        async with OracleFusionMockClient() as client:
            result = await client.purchase_orders.get_by_supplier(1001)

            assert all(po.supplier_id == 1001 for po in result.items)

    @pytest.mark.asyncio
    async def test_po_has_lines_with_schedules(self):
        """Test that PO lines include schedules."""
        async with OracleFusionMockClient() as client:
            po = await client.purchase_orders.get_by_id("300100574829561")

            assert len(po.lines) > 0
            # First line should have schedules
            assert len(po.lines[0].schedules) > 0
            assert po.lines[0].schedules[0].schedule_number == 1
