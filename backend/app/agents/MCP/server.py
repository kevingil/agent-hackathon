import json
from flask import has_app_context, current_app
from app import create_app
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from app.storefront.services.order import OrderService
from app.storefront.services.inventory import InventoryService
from typing import Optional

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
        description="Add a part to the cart given the part id. Requires an existing order/cart (create one first if needed). Use this as the primary way to fulfill an order. Only use find_inventory if add_to_cart fails for a specific item.",
    )
    def add_to_cart(stock_item_id: str | int, quantity: int, cart) -> str:
        print(f"[add_to_cart] Received cart argument: {cart}")
        print(f"[add_to_cart] Received stock_item_id argument: {stock_item_id}")
        if not cart:
            result = {"msg": "Cart is empty"}
            print("[add_to_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        if not stock_item_id:
            result = {"msg": "Item id is required"}
            print("[add_to_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        try:
            # Robustly extract order_id from cart
            order_id = None
            if isinstance(cart, list):
                if cart and isinstance(cart[0], dict) and 'id' in cart[0]:
                    order_id = cart[0]['id']
                elif cart and isinstance(cart[0], int):
                    order_id = cart[0]
            elif isinstance(cart, dict) and 'id' in cart:
                order_id = cart['id']
            elif isinstance(cart, int):
                order_id = cart
            print(f"[add_to_cart] Using order_id: {order_id}")
            if not order_id:
                raise ValueError("Could not extract order_id from cart argument")
            # If stock_item_id is not an int, look up by name
            from app.storefront.models import StockItem
            from app.storefront.services.inventory import InventoryService
            stock_id = stock_item_id
            if isinstance(stock_item_id, str):
                print(f"[add_to_cart] Looking up StockItem by name: {stock_item_id}")
                item = StockItem.query.filter_by(name=stock_item_id).first()
                if not item:
                    print(f"[add_to_cart] No exact match for '{stock_item_id}', trying fuzzy/keyword search...")
                    matches = InventoryService.list_stock_items(search=stock_item_id)
                    if matches:
                        item = matches[0]
                        print(f"[add_to_cart] Fuzzy match found: {item.name} (id={item.id})")
                    else:
                        raise ValueError(f"Stock item with name or keyword '{stock_item_id}' not found")
                stock_id = item.id
                print(f"[add_to_cart] Found StockItem id: {stock_id}")
            order_service.add_item_to_cart(
                order_id=order_id, stock_item_id=stock_id, quantity=quantity
            )
            result = {"msg": f"Item {stock_item_id} added to cart"}
            print("[add_to_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        except Exception as e:
            print(f"[add_to_cart] Exception: {e}")
            result = {"msg": f"Error adding item to cart: {str(e)}"}
            print("[add_to_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        result = {"msg": "Unknown error"}
        print("[add_to_cart] Result:", json.dumps(result, indent=2))
        return json.dumps(result)

    @mcp.tool(name="remove_from_cart", description="Remove a item from the cart")
    def remove_from_cart(stock_item_id: int | str, cart: list) -> str:
        if not cart:
            result = {"msg": "Cart is empty"}
            print("[remove_from_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        if not stock_item_id:
            result = {"msg": "Item id is required"}
            print("[remove_from_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        try:
            order_service.remove_item_from_cart(
                order_id=cart[0].id, item_id=stock_item_id
            )
            result = {"msg": f"Item {stock_item_id} has been removed from cart"}
            print("[remove_from_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        except Exception as e:
            print(f"[remove_from_cart] Exception: {e}")
            result = {"msg": f"Error removing item from cart: {str(e)}"}
            print("[remove_from_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        result = {"msg": "Unknown error"}
        print("[remove_from_cart] Result:", json.dumps(result, indent=2))
        return json.dumps(result)

    @mcp.tool(name="find_inventory", description="Search the database inventory for a part")
    def find_inventory(keyword: str, min_price: float, max_price: float) -> str:
        """
        Only use this tool if add_to_cart fails for a specific item (e.g., item not found or unavailable). Do NOT call this for every item up front.
        """
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
        # Always return a JSON string of a list (may be empty)
        result = json.dumps(results)
        print("[find_inventory] Result:", json.dumps(results, indent=2))
        return result

    @mcp.tool(name="checkout_cart", description="Check out the cart")
    def checkout_cart(cart_id: str) -> str:
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
            print("[checkout_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        except Exception as e:
            print(f"[checkout_cart] Exception: {e}")
            result = {"msg": f"Error placing order: {str(e)}"}
            print("[checkout_cart] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        result = {"msg": "Unknown error"}
        print("[checkout_cart] Result:", json.dumps(result, indent=2))
        return json.dumps(result)

    @mcp.tool(name="create_order", description="Create a new order (cart) and return its id and status")
    def create_order() -> str:
        """
        Create a new order (cart). Returns a JSON string with order id and status.
        """
        try:
            order = order_service.create_order()
            # Access fields while still in session/app context
            order_id = order.id
            order_status = order.status
            result = {"order_id": order_id, "status": order_status}
            print("[create_order] Result:", json.dumps(result, indent=2))
            return json.dumps(result)
        except Exception as e:
            print(f"[create_order] Exception: {e}")
            result = {"msg": f"Error creating order: {str(e)}"}
            print("[create_order] Result:", json.dumps(result, indent=2))
            return json.dumps(result)

    # Run the server
    if __name__ == "__main__":
        mcp.run(transport="sse")
