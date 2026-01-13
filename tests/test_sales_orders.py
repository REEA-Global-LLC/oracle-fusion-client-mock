"""Tests for Sales Orders mock module - compatible with client-valence-anomaly-detection."""

import pytest
from decimal import Decimal

from oracle_fusion_mock.sales_orders import (
    SalesOrderMockClient,
    SalesOrderMockOperations,
    Order,
    OrderLine,
    Customer,
    Product,
    CustomerOrderHistory,
    ProductOrderHistory,
    OrderSearchCriteria,
    OrderStatus,
)
from oracle_fusion_mock.sales_orders.client import SalesOrderMockNotFoundError
from oracle_fusion_mock.sales_orders.data_loader import SalesOrderDataLoader


@pytest.fixture(autouse=True)
def reset_sales_order_data_loader():
    """Reset the sales order data loader singleton before each test."""
    SalesOrderDataLoader.reset()
    yield
    SalesOrderDataLoader.reset()


class TestSalesOrderMockClient:
    """Test SalesOrderMockClient - drop-in replacement for OracleFusionClient."""

    @pytest.mark.asyncio
    async def test_get_orders_returns_all_orders(self):
        """Should return all orders by default."""
        async with SalesOrderMockClient() as client:
            result = await client.get_orders()

        assert "items" in result
        assert "count" in result
        assert result["count"] == 6
        assert len(result["items"]) == 6

    @pytest.mark.asyncio
    async def test_get_orders_with_limit(self):
        """Should respect limit parameter."""
        async with SalesOrderMockClient() as client:
            result = await client.get_orders({"limit": "3"})

        assert len(result["items"]) == 3
        assert result["count"] == 6
        assert result["hasMore"] is True

    @pytest.mark.asyncio
    async def test_get_orders_with_pagination(self):
        """Should support offset pagination."""
        async with SalesOrderMockClient() as client:
            result = await client.get_orders({"limit": "2", "offset": "2"})

        assert len(result["items"]) == 2
        assert result["offset"] == 2

    @pytest.mark.asyncio
    async def test_get_orders_filter_by_customer(self):
        """Should filter orders by CustomerId."""
        async with SalesOrderMockClient() as client:
            result = await client.get_orders({"q": "CustomerId=CUST-1001"})

        assert len(result["items"]) == 2
        for item in result["items"]:
            assert item["CustomerId"] == "CUST-1001"

    @pytest.mark.asyncio
    async def test_get_orders_filter_by_status(self):
        """Should filter orders by StatusCode."""
        async with SalesOrderMockClient() as client:
            result = await client.get_orders({"q": "StatusCode=Booked"})

        assert len(result["items"]) == 3
        for item in result["items"]:
            assert item["StatusCode"] == "Booked"

    @pytest.mark.asyncio
    async def test_get_order_by_id(self):
        """Should return specific order by HeaderId."""
        async with SalesOrderMockClient() as client:
            order = await client.get_order("100100574829001")

        assert order["HeaderId"] == "100100574829001"
        assert order["OrderNumber"] == "SO-2025-0001"
        assert order["CustomerId"] == "CUST-1001"
        assert order["TotalAmount"] == 15750.00

    @pytest.mark.asyncio
    async def test_get_order_includes_lines(self):
        """Should include order lines by default."""
        async with SalesOrderMockClient() as client:
            order = await client.get_order("100100574829001", include_lines=True)

        assert "lines" in order
        assert "items" in order["lines"]
        assert len(order["lines"]["items"]) == 2
        assert order["lines"]["items"][0]["ProductNumber"] == "WIDGET-A100"

    @pytest.mark.asyncio
    async def test_get_order_not_found(self):
        """Should raise SalesOrderMockNotFoundError for invalid ID."""
        async with SalesOrderMockClient() as client:
            with pytest.raises(SalesOrderMockNotFoundError) as exc_info:
                await client.get_order("INVALID-ID")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_get_customers(self):
        """Should return all customers."""
        async with SalesOrderMockClient() as client:
            result = await client.get_customers()

        assert len(result["items"]) == 4
        assert result["count"] == 4

    @pytest.mark.asyncio
    async def test_get_customer_by_id(self):
        """Should return specific customer."""
        async with SalesOrderMockClient() as client:
            customer = await client.get_customer("CUST-1001")

        assert customer["CustomerName"] == "Acme Corporation"
        assert customer["CustomerNumber"] == "ACME-001"

    @pytest.mark.asyncio
    async def test_get_customer_not_found(self):
        """Should raise error for invalid customer ID."""
        async with SalesOrderMockClient() as client:
            with pytest.raises(SalesOrderMockNotFoundError):
                await client.get_customer("INVALID-CUSTOMER")

    @pytest.mark.asyncio
    async def test_get_products(self):
        """Should return all products."""
        async with SalesOrderMockClient() as client:
            result = await client.get_products()

        assert len(result["items"]) == 7
        assert result["count"] == 7

    @pytest.mark.asyncio
    async def test_get_product_by_id(self):
        """Should return specific product."""
        async with SalesOrderMockClient() as client:
            product = await client.get_product("ITEM-5001")

        assert product["ProductNumber"] == "WIDGET-A100"
        assert product["ProductDescription"] == "Premium Widget A100"

    @pytest.mark.asyncio
    async def test_health_check(self):
        """Health check should always return True for mock."""
        async with SalesOrderMockClient() as client:
            result = await client.health_check()

        assert result is True

    @pytest.mark.asyncio
    async def test_generic_get_method(self):
        """Should support generic get() for API compatibility."""
        async with SalesOrderMockClient() as client:
            result = await client.get("salesOrdersForOrderHub", {"limit": "2"})

        assert len(result["items"]) == 2

    @pytest.mark.asyncio
    async def test_generic_get_by_id_method(self):
        """Should support generic get_by_id() for API compatibility."""
        async with SalesOrderMockClient() as client:
            order = await client.get_by_id(
                "salesOrdersForOrderHub",
                "100100574829001",
                expand=["lines"]
            )

        assert order["OrderNumber"] == "SO-2025-0001"


class TestSalesOrderMockOperations:
    """Test SalesOrderMockOperations - high-level operations with statistics."""

    @pytest.mark.asyncio
    async def test_get_order(self):
        """Should return parsed Order model."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order("100100574829001")

        assert isinstance(order, Order)
        assert order.order_id == "100100574829001"
        assert order.order_number == "SO-2025-0001"
        assert order.customer_id == "CUST-1001"
        assert order.total_amount == Decimal("15750")

    @pytest.mark.asyncio
    async def test_get_order_with_lines(self):
        """Should parse order lines as OrderLine models."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order("100100574829001")

        assert len(order.lines) == 2
        assert isinstance(order.lines[0], OrderLine)
        assert order.lines[0].product_number == "WIDGET-A100"
        assert order.lines[0].ordered_quantity == Decimal("500")

    @pytest.mark.asyncio
    async def test_get_order_by_number(self):
        """Should find order by order number."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order_by_number("SO-2025-0001")

        assert order is not None
        assert order.order_id == "100100574829001"

    @pytest.mark.asyncio
    async def test_get_order_by_number_not_found(self):
        """Should return None for non-existent order number."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order_by_number("INVALID-ORDER")

        assert order is None

    @pytest.mark.asyncio
    async def test_search_orders(self):
        """Should search orders with criteria."""
        criteria = OrderSearchCriteria(
            customer_id="CUST-1001",
            limit=10,
        )

        async with SalesOrderMockOperations() as ops:
            orders = await ops.search_orders(criteria)

        assert len(orders) == 2
        assert all(o.customer_id == "CUST-1001" for o in orders)

    @pytest.mark.asyncio
    async def test_get_recent_orders(self):
        """Should get orders from recent days."""
        async with SalesOrderMockOperations() as ops:
            orders = await ops.get_recent_orders(days=365, limit=10)

        # Should return orders from the last year
        assert len(orders) > 0
        assert all(isinstance(o, Order) for o in orders)

    @pytest.mark.asyncio
    async def test_get_customer(self):
        """Should return parsed Customer model."""
        async with SalesOrderMockOperations() as ops:
            customer = await ops.get_customer("CUST-1001")

        assert isinstance(customer, Customer)
        assert customer.customer_id == "CUST-1001"
        assert customer.customer_name == "Acme Corporation"

    @pytest.mark.asyncio
    async def test_get_product(self):
        """Should return parsed Product model."""
        async with SalesOrderMockOperations() as ops:
            product = await ops.get_product("ITEM-5001")

        assert isinstance(product, Product)
        assert product.product_id == "ITEM-5001"
        assert product.product_number == "WIDGET-A100"

    @pytest.mark.asyncio
    async def test_order_total_quantity_property(self):
        """Order should calculate total quantity across lines."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order("100100574829001")

        # Line 1: 500, Line 2: 100
        assert order.total_quantity == Decimal("600")

    @pytest.mark.asyncio
    async def test_order_line_count_property(self):
        """Order should report correct line count."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order("100100574829001")

        assert order.line_count == 2


class TestCustomerOrderHistory:
    """Test CustomerOrderHistory statistics calculation."""

    @pytest.mark.asyncio
    async def test_get_customer_order_history(self):
        """Should calculate customer order statistics."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_customer_order_history("CUST-1001", months=12)

        assert isinstance(history, CustomerOrderHistory)
        assert history.customer_id == "CUST-1001"
        assert history.customer_name == "Acme Corporation"
        assert history.total_orders == 2  # CUST-1001 has 2 orders

    @pytest.mark.asyncio
    async def test_customer_history_amounts(self):
        """Should calculate correct amount statistics."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_customer_order_history("CUST-1001", months=12)

        # Orders: 15750 + 8500 = 24250
        assert history.total_amount == Decimal("24250")
        assert history.average_order_amount == Decimal("12125")
        assert history.max_order_amount == Decimal("15750")
        assert history.min_order_amount == Decimal("8500")

    @pytest.mark.asyncio
    async def test_customer_history_standard_deviation(self):
        """Should calculate standard deviation for anomaly detection."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_customer_order_history("CUST-1001", months=12)

        # With only 2 orders, stdev should be calculated
        assert history.std_dev_amount > Decimal("0")

    @pytest.mark.asyncio
    async def test_customer_history_empty(self):
        """Should return empty history for unknown customer."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_customer_order_history("UNKNOWN-CUSTOMER", months=12)

        assert history.total_orders == 0
        assert history.total_amount == Decimal("0")
        assert history.average_order_amount == Decimal("0")
        assert history.orders == []


class TestProductOrderHistory:
    """Test ProductOrderHistory statistics calculation."""

    @pytest.mark.asyncio
    async def test_get_product_order_history(self):
        """Should calculate product order statistics."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_product_order_history("ITEM-5001", months=12)

        assert isinstance(history, ProductOrderHistory)
        assert history.product_id == "ITEM-5001"
        assert history.product_number == "WIDGET-A100"
        # WIDGET-A100 appears in 3 orders: 500 + 128 + 30 = 658
        assert history.total_orders == 3

    @pytest.mark.asyncio
    async def test_product_history_quantities(self):
        """Should calculate correct quantity statistics."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_product_order_history("ITEM-5001", months=12)

        # Quantities: 500 + 128 + 30 = 658
        assert history.total_quantity == Decimal("658")
        assert history.max_quantity == Decimal("500")
        assert history.min_quantity == Decimal("30")

    @pytest.mark.asyncio
    async def test_product_history_average_price(self):
        """Should calculate average selling price."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_product_order_history("ITEM-5001", months=12)

        # All WIDGET-A100 orders at $25
        assert history.average_price == Decimal("25")

    @pytest.mark.asyncio
    async def test_product_history_empty(self):
        """Should return empty history for unknown product."""
        async with SalesOrderMockOperations() as ops:
            history = await ops.get_product_order_history("UNKNOWN-PRODUCT", months=12)

        assert history.total_orders == 0
        assert history.total_quantity == Decimal("0")


class TestDataConsistency:
    """Test referential integrity and data consistency."""

    @pytest.mark.asyncio
    async def test_orders_reference_valid_customers(self):
        """All orders should reference existing customers."""
        async with SalesOrderMockClient() as client:
            orders = await client.get_orders()
            customers = await client.get_customers()

        customer_ids = {c["CustomerId"] for c in customers["items"]}

        for order in orders["items"]:
            assert order["CustomerId"] in customer_ids, (
                f"Order {order['OrderNumber']} references invalid customer "
                f"{order['CustomerId']}"
            )

    @pytest.mark.asyncio
    async def test_order_lines_reference_valid_products(self):
        """All order lines should reference existing products."""
        async with SalesOrderMockClient() as client:
            orders = await client.get_orders()
            products = await client.get_products()

        product_ids = {p["InventoryItemId"] for p in products["items"]}

        for order_data in orders["items"]:
            order = await client.get_order(order_data["HeaderId"])
            for line in order["lines"]["items"]:
                assert line["InventoryItemId"] in product_ids, (
                    f"Order line {line['OrderLineId']} references invalid product "
                    f"{line['InventoryItemId']}"
                )

    @pytest.mark.asyncio
    async def test_singleton_data_consistency(self):
        """Multiple clients should share the same data."""
        client1 = SalesOrderMockClient()
        client2 = SalesOrderMockClient()

        async with client1:
            orders1 = await client1.get_orders()

        async with client2:
            orders2 = await client2.get_orders()

        assert orders1["count"] == orders2["count"]
        assert orders1["items"][0]["HeaderId"] == orders2["items"][0]["HeaderId"]


class TestOrderSearchCriteria:
    """Test OrderSearchCriteria query generation."""

    def test_to_query_params_basic(self):
        """Should generate basic query params."""
        criteria = OrderSearchCriteria(limit=50, offset=10)
        params = criteria.to_query_params()

        assert params["limit"] == "50"
        assert params["offset"] == "10"

    def test_to_query_params_with_customer(self):
        """Should include CustomerId in query."""
        criteria = OrderSearchCriteria(customer_id="CUST-1001")
        params = criteria.to_query_params()

        assert "q" in params
        assert "CustomerId=CUST-1001" in params["q"]

    def test_to_query_params_with_status(self):
        """Should include StatusCode in query."""
        criteria = OrderSearchCriteria(status=OrderStatus.BOOKED)
        params = criteria.to_query_params()

        assert "StatusCode=Booked" in params["q"]

    def test_to_query_params_combined(self):
        """Should combine multiple criteria."""
        criteria = OrderSearchCriteria(
            customer_id="CUST-1001",
            status=OrderStatus.BOOKED,
            min_amount=Decimal("1000"),
        )
        params = criteria.to_query_params()

        assert "CustomerId=CUST-1001" in params["q"]
        assert "StatusCode=Booked" in params["q"]
        assert "TotalAmount>=1000" in params["q"]


class TestModelAliases:
    """Test that model aliases match Oracle Fusion API field names."""

    @pytest.mark.asyncio
    async def test_order_aliases(self):
        """Order model aliases should match Oracle API."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order("100100574829001")

        # Test snake_case properties map to PascalCase API fields
        assert order.order_id == "100100574829001"  # HeaderId
        assert order.order_number == "SO-2025-0001"  # OrderNumber
        assert order.customer_id == "CUST-1001"  # CustomerId

    @pytest.mark.asyncio
    async def test_order_line_aliases(self):
        """OrderLine model aliases should match Oracle API."""
        async with SalesOrderMockOperations() as ops:
            order = await ops.get_order("100100574829001")
            line = order.lines[0]

        assert line.line_id == "100100574829002"  # OrderLineId
        assert line.product_id == "ITEM-5001"  # InventoryItemId
        assert line.product_number == "WIDGET-A100"  # ProductNumber

    @pytest.mark.asyncio
    async def test_customer_aliases(self):
        """Customer model aliases should match Oracle API."""
        async with SalesOrderMockOperations() as ops:
            customer = await ops.get_customer("CUST-1001")

        assert customer.customer_id == "CUST-1001"  # CustomerId
        assert customer.customer_name == "Acme Corporation"  # CustomerName

    @pytest.mark.asyncio
    async def test_product_aliases(self):
        """Product model aliases should match Oracle API."""
        async with SalesOrderMockOperations() as ops:
            product = await ops.get_product("ITEM-5001")

        assert product.product_id == "ITEM-5001"  # InventoryItemId
        assert product.product_number == "WIDGET-A100"  # ProductNumber
