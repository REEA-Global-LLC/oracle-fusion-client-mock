"""Tests for the mock Suppliers service."""

import pytest

from oracle_fusion_mock import OracleFusionMockClient
from oracle_fusion_mock.models import OracleCollectionResponse, Supplier


class TestMockSupplierService:
    """Tests for MockSupplierService."""

    @pytest.mark.asyncio
    async def test_list_suppliers(self):
        """Test listing suppliers."""
        async with OracleFusionMockClient() as client:
            result = await client.suppliers.list()

            assert isinstance(result, OracleCollectionResponse)
            assert len(result.items) > 0
            assert all(isinstance(s, Supplier) for s in result.items)

    @pytest.mark.asyncio
    async def test_get_by_id(self):
        """Test getting a single supplier."""
        async with OracleFusionMockClient() as client:
            supplier = await client.suppliers.get_by_id(1001)

            assert isinstance(supplier, Supplier)
            assert supplier.supplier_id == 1001
            assert supplier.supplier == "ABC Office Supplies Inc"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self):
        """Test getting a non-existent supplier raises error."""
        async with OracleFusionMockClient() as client:
            with pytest.raises(ValueError, match="not found"):
                await client.suppliers.get_by_id(99999)

    @pytest.mark.asyncio
    async def test_get_sites(self):
        """Test getting sites for a supplier."""
        async with OracleFusionMockClient() as client:
            sites = await client.suppliers.get_sites(1001)

            assert len(sites) >= 1
            assert sites[0].supplier_site == "MAIN"

    @pytest.mark.asyncio
    async def test_get_contacts(self):
        """Test getting contacts for a supplier."""
        async with OracleFusionMockClient() as client:
            contacts = await client.suppliers.get_contacts(1001)

            assert len(contacts) >= 1
            assert contacts[0].contact_name == "Robert Brown"

    @pytest.mark.asyncio
    async def test_search_by_name(self):
        """Test searching suppliers by name."""
        async with OracleFusionMockClient() as client:
            result = await client.suppliers.search_by_name("ABC")

            assert len(result.items) > 0
            assert "ABC" in result.items[0].supplier

    @pytest.mark.asyncio
    async def test_search_by_number(self):
        """Test searching supplier by number."""
        async with OracleFusionMockClient() as client:
            supplier = await client.suppliers.search_by_number("SUP-001")

            assert supplier is not None
            assert supplier.supplier_number == "SUP-001"

    @pytest.mark.asyncio
    async def test_get_active_suppliers(self):
        """Test getting active suppliers."""
        async with OracleFusionMockClient() as client:
            result = await client.suppliers.get_active_suppliers()

            assert all(s.status_code == "ACTIVE" for s in result.items)

    @pytest.mark.asyncio
    async def test_supplier_has_sites_and_contacts(self):
        """Test that suppliers include sites and contacts."""
        async with OracleFusionMockClient() as client:
            supplier = await client.suppliers.get_by_id(1001)

            assert len(supplier.sites) > 0
            assert len(supplier.contacts) > 0
