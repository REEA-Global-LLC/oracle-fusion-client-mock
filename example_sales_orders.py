#!/usr/bin/env python3
"""Example script demonstrating the Sales Orders mock module.

This module is compatible with client-valence-anomaly-detection and can be
used as a drop-in replacement for the real OracleFusionClient.

Run with: python example_sales_orders.py
"""

import asyncio
from decimal import Decimal

from oracle_fusion_mock.sales_orders import (
    SalesOrderMockClient,
    SalesOrderMockOperations,
    OrderSearchCriteria,
    OrderStatus,
)


async def demo_client():
    """Demonstrate SalesOrderMockClient - low-level API access."""
    print("=" * 60)
    print("SalesOrderMockClient Demo (Drop-in for OracleFusionClient)")
    print("=" * 60)

    async with SalesOrderMockClient() as client:
        # List all orders
        print("\n1. List all orders:")
        result = await client.get_orders()
        print(f"   Total orders: {result['count']}")
        for order in result["items"][:3]:
            print(f"   - {order['OrderNumber']}: ${order['TotalAmount']:,.2f} ({order['StatusCode']})")

        # Get specific order with lines
        print("\n2. Get order details with lines:")
        order = await client.get_order("100100574829001", include_lines=True)
        print(f"   Order: {order['OrderNumber']}")
        print(f"   Customer: {order['CustomerName']}")
        print(f"   Total: ${order['TotalAmount']:,.2f}")
        print(f"   Lines:")
        for line in order["lines"]["items"]:
            print(f"     - {line['ProductNumber']}: {line['OrderedQuantity']} x ${line['UnitSellingPrice']}")

        # Filter orders by status
        print("\n3. Filter by status (Booked):")
        result = await client.get_orders({"q": "StatusCode=Booked"})
        print(f"   Found {len(result['items'])} booked orders:")
        for order in result["items"]:
            print(f"   - {order['OrderNumber']}: {order['CustomerName']}")

        # Get customer
        print("\n4. Get customer details:")
        customer = await client.get_customer("CUST-1001")
        print(f"   Customer: {customer['CustomerName']}")
        print(f"   Account: {customer['AccountNumber']}")


async def demo_operations():
    """Demonstrate SalesOrderMockOperations - high-level with statistics."""
    print("\n" + "=" * 60)
    print("SalesOrderMockOperations Demo (Compatible with OracleOperations)")
    print("=" * 60)

    async with SalesOrderMockOperations() as ops:
        # Get recent orders
        print("\n1. Get recent orders (last 365 days):")
        orders = await ops.get_recent_orders(days=365, limit=5)
        print(f"   Found {len(orders)} recent orders:")
        for order in orders[:3]:
            print(f"   - {order.order_number}: ${order.total_amount:,.2f}")
            print(f"     Lines: {order.line_count}, Total qty: {order.total_quantity}")

        # Search with criteria
        print("\n2. Search orders with criteria:")
        criteria = OrderSearchCriteria(
            customer_id="CUST-1001",
            status=OrderStatus.BOOKED,
        )
        orders = await ops.search_orders(criteria)
        print(f"   Found {len(orders)} orders for CUST-1001 with status Booked")

        # Customer order history (for anomaly detection)
        print("\n3. Customer Order History (for anomaly detection):")
        history = await ops.get_customer_order_history("CUST-1001", months=12)
        print(f"   Customer: {history.customer_name}")
        print(f"   Total orders: {history.total_orders}")
        print(f"   Total amount: ${history.total_amount:,.2f}")
        print(f"   Average order: ${history.average_order_amount:,.2f}")
        print(f"   Max order: ${history.max_order_amount:,.2f}")
        print(f"   Min order: ${history.min_order_amount:,.2f}")
        print(f"   Std dev: ${history.std_dev_amount:,.2f}")

        # Product order history
        print("\n4. Product Order History (for anomaly detection):")
        product_history = await ops.get_product_order_history("ITEM-5001", months=12)
        print(f"   Product: {product_history.product_number}")
        print(f"   Description: {product_history.product_description}")
        print(f"   Total orders: {product_history.total_orders}")
        print(f"   Total quantity: {product_history.total_quantity}")
        print(f"   Average quantity: {product_history.average_quantity:.2f}")
        print(f"   Average price: ${product_history.average_price:,.2f}")


async def demo_anomaly_detection_usage():
    """Demonstrate how anomaly detection would use this mock."""
    print("\n" + "=" * 60)
    print("Anomaly Detection Usage Example")
    print("=" * 60)

    async with SalesOrderMockOperations() as ops:
        # Simulate checking if an order is anomalous
        order = await ops.get_order("100100574829001")
        history = await ops.get_customer_order_history(order.customer_id, months=12)

        print(f"\nChecking order {order.order_number}:")
        print(f"  Order amount: ${order.total_amount:,.2f}")
        print(f"  Customer average: ${history.average_order_amount:,.2f}")
        print(f"  Customer std dev: ${history.std_dev_amount:,.2f}")

        # Simple anomaly detection: >2 standard deviations from mean
        if history.std_dev_amount > 0:
            z_score = abs(float(order.total_amount - history.average_order_amount) / float(history.std_dev_amount))
            print(f"  Z-score: {z_score:.2f}")
            if z_score > 2:
                print("  ALERT: Order amount is anomalous!")
            else:
                print("  OK: Order amount is within normal range")


async def main():
    """Run all demos."""
    await demo_client()
    await demo_operations()
    await demo_anomaly_detection_usage()

    print("\n" + "=" * 60)
    print("Demo complete!")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
