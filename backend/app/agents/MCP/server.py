from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger
from app.storefront.services.order import OrderService
from app.storefront.services.inventory import InventoryService


logger = get_logger(__name__)
# store_service = StoreService()

# Create an MCP server
mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)

inventory_service = InventoryService()
order_service = OrderService()


@mcp.tool(
    name="add_to_cart",
    description="Add a part to the cart given the part id",
)
def add_to_cart(stock_item_id: str | int, quantity: int, cart) -> list:
    """Add a part to the cart
    Args:
        part_id (str | int): The part id to add to the cart

    Returns:
        str: A message indicating the part was added to the cart
    """
    if not cart:
        return [{"msg": "Cart is empty"}]
    if not stock_item_id:
        return [{"msg": "Item id is required"}]
    if order_service:
        try:
            order_service.add_item_to_cart(
                order_id=cart[0].id, stock_item_id=stock_item_id, quantity=quantity
            )
            return [{"msg": f"Item {stock_item_id} added to cart"}]
        except Exception as e:
            return [{"msg": f"Error adding item to cart: {str(e)}"}]


@mcp.tool(name="remove_from_cart", description="Remove a item from the cart")
def remove_from_cart(stock_item_id: int | str, cart: list) -> str:
    """
    Search remove an item from the cart

    Args:
        keyword: The keyword to search for in the inventory database

    Returns:
        str: A message indicating the part was found in the inventory
    """
    if not cart:
        return [{"msg": "Cart is empty"}]
    if not stock_item_id:
        return [{"msg": "Item id is required"}]
    if order_service:
        try:
            order_service.remove_item_from_cart(
                order_id=cart[0].id, item_id=stock_item_id
            )
            return [{"msg": f"Item {stock_item_id} has been removed from     cart"}]
        except Exception as e:
            return [{"msg": f"Error removing item to cart: {str(e)}"}]


@mcp.tool(name="find_inventory", description="Search the database inventory for a part")
def find_inventory(keyword: str, min_price: float, max_price: float) -> str:
    """
    Search the database inventory for a part using a keryword
    Args:
        keyword: The keyword to search for in the inventory database

    Returns:
        str: A message indicating the part was found in the inventory
    """

    if not keyword:
        return [["error", "Keyword is required"]]
    if inventory_service:
        try:
            items = inventory_service.list_stock_items(
                search=keyword, min_price=min_price, max_price=max_price
            )
        except Exception as e:
            return [["error", f"Error searching inventory: {str(e)}"]]

    results = []
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

    return results


# make install
# make run


@mcp.tool(name="checkout_cart", description="Check out the cart")
def checkout_cart(cart_id: str) -> str:
    """ """
    if not cart_id:
        return [{"msg": "Cart id is required"}]
    if order_service:
        try:
            order = order_service.place_order(order_id=cart_id)
            return [
                {
                    "order_id": order.id,
                    "status": order.status,
                    "placed_at": order.submitted_at.isoformat(),
                }
            ]
        except Exception as e:
            return [{"msg": f"Error placing order: {str(e)}"}]


# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
