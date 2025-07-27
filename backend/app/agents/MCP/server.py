import json
from flask import has_app_context, current_app
from app import create_app
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from app.storefront.services.order import OrderService
from app.storefront.services.inventory import InventoryService

logger = get_logger(__name__)

# Create the Flask app and MCP server inside the app context
app = create_app()
with app.app_context():
    print("[server] Initializing order_service...")
    order_service = OrderService()
    print("[server] Initializing inventory_service...")
    inventory_service = InventoryService()

    mcp = FastMCP(
        name="Knowledge Base",
        host="0.0.0.0",  # only used for SSE transport (localhost)
        port=8050,  # only used for SSE transport (set this to any port)
    )

    @mcp.tool(
        name="add_to_cart",
        description="Add a part to the cart given the part id",
    )
    def add_to_cart(stock_item_id: str | int, quantity: int, cart) -> str:
        print("[add_to_cart] Called. has_app_context:", has_app_context())
        print("[add_to_cart] order_service:", order_service)
        if not cart:
            result = {"msg": "Cart is empty"}
            print(f"[add_to_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        if not stock_item_id:
            result = {"msg": "Item id is required"}
            print(f"[add_to_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        try:
            order_service.add_item_to_cart(
                order_id=cart[0].id, stock_item_id=stock_item_id, quantity=quantity
            )
            result = {"msg": f"Item {stock_item_id} added to cart"}
            print(f"[add_to_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        except Exception as e:
            print(f"[add_to_cart] Exception: {e}")
            result = {"msg": f"Error adding item to cart: {str(e)}"}
            print(f"[add_to_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        result = {"msg": "Unknown error"}
        print(f"[add_to_cart] Returning: {type(result)} {result}")
        return json.dumps(result)

    @mcp.tool(name="remove_from_cart", description="Remove a item from the cart")
    def remove_from_cart(stock_item_id: int | str, cart: list) -> str:
        print("[remove_from_cart] Called. has_app_context:", has_app_context())
        print("[remove_from_cart] order_service:", order_service)
        if not cart:
            result = {"msg": "Cart is empty"}
            print(f"[remove_from_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        if not stock_item_id:
            result = {"msg": "Item id is required"}
            print(f"[remove_from_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        try:
            order_service.remove_item_from_cart(
                order_id=cart[0].id, item_id=stock_item_id
            )
            result = {"msg": f"Item {stock_item_id} has been removed from cart"}
            print(f"[remove_from_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        except Exception as e:
            print(f"[remove_from_cart] Exception: {e}")
            result = {"msg": f"Error removing item from cart: {str(e)}"}
            print(f"[remove_from_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        result = {"msg": "Unknown error"}
        print(f"[remove_from_cart] Returning: {type(result)} {result}")
        return json.dumps(result)

    @mcp.tool(name="find_inventory", description="Search the database inventory for a part")
    def find_inventory(keyword: str, min_price: float, max_price: float) -> str:
        print("[find_inventory] Called. has_app_context:", has_app_context())
        print("[find_inventory] inventory_service:", inventory_service)
        if not keyword:
            result = json.dumps([{"error": "Keyword is required"}])
            print(f"[find_inventory] Returning: {type(result)} {result}")
            return result
        try:
            items = inventory_service.list_stock_items(
                search=keyword, min_price=min_price, max_price=max_price
            )
        except Exception as e:
            print(f"[find_inventory] Exception: {e}")
            result = json.dumps([{"error": f"Error searching inventory: {str(e)}"}])
            print(f"[find_inventory] Returning: {type(result)} {result}")
            return result
        results = []
        if items:
            for item in items:
                results.append(
                    {
                        "id": str(item.id),
                        "session_id": str(item.name),
                        "session_name": str(item.description),
                        "cost": str(item.cost),
                        "list_price": str(item.list_price),
                        "quantity": str(item.quantity),
                    }
                )
        result = json.dumps(results)
        print(f"[find_inventory] Returning: {type(result)} {result}")
        return result

    @mcp.tool(name="checkout_cart", description="Check out the cart")
    def checkout_cart(cart_id: str) -> str:
        print("[checkout_cart] Called. has_app_context:", has_app_context())
        print("[checkout_cart] order_service:", order_service)
        if not cart_id:
            result = {"msg": "Cart id is required"}
            print(f"[checkout_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        try:
            order = order_service.place_order(order_id=cart_id)
            result = {
                "order_id": order.id,
                "status": order.status,
                "placed_at": order.submitted_at.isoformat(),
            }
            print(f"[checkout_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        except Exception as e:
            print(f"[checkout_cart] Exception: {e}")
            result = {"msg": f"Error placing order: {str(e)}"}
            print(f"[checkout_cart] Returning: {type(result)} {result}")
            return json.dumps(result)
        result = {"msg": "Unknown error"}
        print(f"[checkout_cart] Returning: {type(result)} {result}")
        return json.dumps(result)

    # Run the server
    if __name__ == "__main__":
        mcp.run(transport="sse")
