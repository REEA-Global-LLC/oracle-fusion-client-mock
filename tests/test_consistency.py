"""Tests for data consistency across services."""

import pytest

from oracle_fusion_mock import OracleFusionMockClient


class TestDataConsistency:
    """Tests to verify data consistency across different services."""

    @pytest.mark.asyncio
    async def test_po_supplier_consistency(self):
        """Test that PO supplier IDs match actual suppliers."""
        async with OracleFusionMockClient() as client:
            pos = await client.purchase_orders.list()
            suppliers = await client.suppliers.list()

            supplier_ids = {s.supplier_id for s in suppliers.items}

            for po in pos.items:
                assert po.supplier_id in supplier_ids, (
                    f"PO {po.order_number} references non-existent supplier {po.supplier_id}"
                )

    @pytest.mark.asyncio
    async def test_po_supplier_name_consistency(self):
        """Test that PO supplier names match the actual supplier data."""
        async with OracleFusionMockClient() as client:
            pos = await client.purchase_orders.list()

            for po in pos.items:
                supplier = await client.suppliers.get_by_id(po.supplier_id)
                assert po.supplier == supplier.supplier, (
                    f"PO {po.order_number} supplier name '{po.supplier}' "
                    f"doesn't match supplier record '{supplier.supplier}'"
                )

    @pytest.mark.asyncio
    async def test_acknowledgment_po_consistency(self):
        """Test that acknowledgments reference valid POs."""
        async with OracleFusionMockClient() as client:
            acks = await client.acknowledgments.list()
            pos = await client.purchase_orders.list()

            po_ids = {po.po_header_id for po in pos.items}

            for ack in acks.items:
                assert ack.po_header_id in po_ids, (
                    f"Acknowledgment references non-existent PO {ack.po_header_id}"
                )

    @pytest.mark.asyncio
    async def test_agreement_supplier_consistency(self):
        """Test that agreements reference valid suppliers."""
        async with OracleFusionMockClient() as client:
            agreements = await client.agreements.list()
            suppliers = await client.suppliers.list()

            supplier_ids = {s.supplier_id for s in suppliers.items}

            for agreement in agreements.items:
                assert agreement.supplier_id in supplier_ids, (
                    f"Agreement {agreement.agreement} references "
                    f"non-existent supplier {agreement.supplier_id}"
                )

    @pytest.mark.asyncio
    async def test_draft_po_supplier_consistency(self):
        """Test that draft POs reference valid suppliers."""
        async with OracleFusionMockClient() as client:
            drafts = await client.draft_purchase_orders.list()
            suppliers = await client.suppliers.list()

            supplier_ids = {s.supplier_id for s in suppliers.items}

            for draft in drafts.items:
                if draft.supplier_id:
                    assert draft.supplier_id in supplier_ids, (
                        f"Draft PO {draft.order_number} references "
                        f"non-existent supplier {draft.supplier_id}"
                    )

    @pytest.mark.asyncio
    async def test_collection_response_format(self):
        """Test that all collection responses have consistent format."""
        async with OracleFusionMockClient() as client:
            # Test all list endpoints
            pos = await client.purchase_orders.list()
            suppliers = await client.suppliers.list()
            reqs = await client.requisitions.list()
            drafts = await client.draft_purchase_orders.list()
            agreements = await client.agreements.list()
            acks = await client.acknowledgments.list()

            for response in [pos, suppliers, reqs, drafts, agreements, acks]:
                assert hasattr(response, "items")
                assert hasattr(response, "count")
                assert hasattr(response, "has_more")
                assert hasattr(response, "limit")
                assert hasattr(response, "offset")
                assert hasattr(response, "links")

    @pytest.mark.asyncio
    async def test_service_id_types_consistency(self):
        """Test that ID fields have consistent types."""
        async with OracleFusionMockClient() as client:
            # PO IDs should be integers
            po = await client.purchase_orders.get_by_id("300100574829561")
            assert isinstance(po.po_header_id, int)

            # Supplier IDs should be integers
            supplier = await client.suppliers.get_by_id(1001)
            assert isinstance(supplier.supplier_id, int)

            # Requisition IDs should be integers
            req = await client.requisitions.get_by_id(300100574825001)
            assert isinstance(req.requisition_header_id, int)

    @pytest.mark.asyncio
    async def test_po_lines_belong_to_correct_po(self):
        """Test that PO lines are correctly associated with their parent PO."""
        async with OracleFusionMockClient() as client:
            pos = await client.purchase_orders.list()

            for po in pos.items:
                if po.lines:
                    # Line numbers should be sequential starting from 1
                    line_numbers = [line.line_number for line in po.lines]
                    expected_numbers = list(range(1, len(po.lines) + 1))
                    assert line_numbers == expected_numbers, (
                        f"PO {po.order_number} has non-sequential line numbers"
                    )
