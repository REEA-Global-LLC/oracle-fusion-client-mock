"""Tests for the main mock client."""

import pytest

from oracle_fusion_mock import OracleFusionMockClient


class TestOracleFusionMockClient:
    """Tests for OracleFusionMockClient."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test that client works as async context manager."""
        async with OracleFusionMockClient() as client:
            assert client is not None
            assert hasattr(client, "purchase_orders")
            assert hasattr(client, "suppliers")

    @pytest.mark.asyncio
    async def test_purchase_orders_service_available(self):
        """Test that purchase orders service is available."""
        async with OracleFusionMockClient() as client:
            service = client.purchase_orders
            assert service is not None

    @pytest.mark.asyncio
    async def test_suppliers_service_available(self):
        """Test that suppliers service is available."""
        async with OracleFusionMockClient() as client:
            service = client.suppliers
            assert service is not None

    @pytest.mark.asyncio
    async def test_requisitions_service_available(self):
        """Test that requisitions service is available."""
        async with OracleFusionMockClient() as client:
            service = client.requisitions
            assert service is not None

    @pytest.mark.asyncio
    async def test_draft_pos_service_available(self):
        """Test that draft purchase orders service is available."""
        async with OracleFusionMockClient() as client:
            service = client.draft_purchase_orders
            assert service is not None

    @pytest.mark.asyncio
    async def test_agreements_service_available(self):
        """Test that agreements service is available."""
        async with OracleFusionMockClient() as client:
            service = client.agreements
            assert service is not None

    @pytest.mark.asyncio
    async def test_acknowledgments_service_available(self):
        """Test that acknowledgments service is available."""
        async with OracleFusionMockClient() as client:
            service = client.acknowledgments
            assert service is not None

    @pytest.mark.asyncio
    async def test_services_share_data_loader(self):
        """Test that all services share the same data loader."""
        async with OracleFusionMockClient() as client:
            dl1 = client.purchase_orders._data_loader
            dl2 = client.suppliers._data_loader
            dl3 = client.requisitions._data_loader
            # They should all be the same singleton instance
            assert dl1 is dl2
            assert dl2 is dl3
