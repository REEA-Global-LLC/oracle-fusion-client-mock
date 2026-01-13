#!/usr/bin/env python3
"""Ejemplo interactivo del cliente mock de Oracle Fusion."""

import asyncio
from oracle_fusion_mock import OracleFusionMockClient


async def main():
    print("=" * 60)
    print("Oracle Fusion Mock Client - Demo")
    print("=" * 60)

    async with OracleFusionMockClient() as client:
        # 1. Listar Purchase Orders
        print("\n1. PURCHASE ORDERS")
        print("-" * 40)
        orders = await client.purchase_orders.list()
        print(f"Total POs: {orders.count}")
        for po in orders.items:
            print(f"  - {po.order_number}: {po.supplier} | ${po.total_amount:,.2f} | {po.status}")

        # 2. Detalle de una PO específica
        print("\n2. DETALLE PO-2024-0001")
        print("-" * 40)
        po = await client.purchase_orders.get_by_id("300100574829561")
        print(f"Número: {po.order_number}")
        print(f"Proveedor: {po.supplier}")
        print(f"Total: ${po.total_amount:,.2f} {po.currency}")
        print(f"Estado: {po.status}")
        print(f"Líneas: {len(po.lines)}")
        for line in po.lines:
            print(f"  L{line.line_number}: {line.item_description} - {line.quantity} x ${line.unit_price}")

        # 3. Listar Suppliers
        print("\n3. SUPPLIERS")
        print("-" * 40)
        suppliers = await client.suppliers.list()
        for s in suppliers.items:
            print(f"  - {s.supplier} ({s.supplier_number}) | Sites: {len(s.sites)} | Contacts: {len(s.contacts)}")

        # 4. Detalle de un Supplier
        print("\n4. DETALLE SUPPLIER 1001")
        print("-" * 40)
        supplier = await client.suppliers.get_by_id(1001)
        print(f"Nombre: {supplier.supplier}")
        print(f"Número: {supplier.supplier_number}")
        print(f"Tax ID: {supplier.tax_registration_number}")
        print("Sites:")
        for site in supplier.sites:
            print(f"  - {site.supplier_site}: {site.city}, {site.state}")
        print("Contacts:")
        for contact in supplier.contacts:
            print(f"  - {contact.contact_name}: {contact.email}")

        # 5. Filtrar POs abiertas
        print("\n5. POs ABIERTAS (StatusCode='OPEN')")
        print("-" * 40)
        open_orders = await client.purchase_orders.list(query="StatusCode='OPEN'")
        for po in open_orders.items:
            print(f"  - {po.order_number}: {po.supplier}")

        # 6. Requisiciones
        print("\n6. REQUISICIONES")
        print("-" * 40)
        reqs = await client.requisitions.list()
        for req in reqs.items:
            print(f"  - {req.requisition}: {req.description} | {req.status} | ${req.total_amount:,.2f}")

        # 7. Agreements
        print("\n7. PURCHASE AGREEMENTS")
        print("-" * 40)
        agreements = await client.agreements.list()
        for agr in agreements.items:
            print(f"  - {agr.agreement}: {agr.description}")
            print(f"    Proveedor: {agr.supplier} | Monto: ${agr.agreed_amount:,.2f}")

        # 8. Simular acción (cancel)
        print("\n8. SIMULAR ACCIÓN: CANCEL PO")
        print("-" * 40)
        result = await client.purchase_orders.cancel("300100574829561", reason="Testing mock")
        print(f"Resultado: {result.result}")
        print(f"Mensaje: {result.message}")
        print(f"Acción: {result.action}")

        print("\n" + "=" * 60)
        print("Demo completada!")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
