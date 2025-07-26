import json
from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.utilities.logging import get_logger

from app.database import db
from app.storefront.models import StockItem, OrderItem


logger = get_logger(__name__)
# store_service = StoreService()

# Create an MCP server
mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)


@mcp.tool(
    name="add_to_cart",
    description="Add a part to the cart given the part id",
)
def add_to_cart(item_id: str | int, quantity: int, cart: list) -> list:
    """Add a part to the cart
    Args:
        part_id (str | int): The part id to add to the cart

    Returns:
        str: A message indicating the part was added to the cart
    """
    if not cart:
        return [{"msg": "Cart is empty"}]
    if not item_id:
        return [{"msg": "Item id is required"}]
    try:
        item = StockItem.query.get(item_id)
        if item:
            try:
                new_order_item = OrderItem(
                    stock_item_id=item.id,
                    quantity=quantity,
                    unit_cost=item.cost,
                    unit_price=item.list_price,
                )
                db.session.add(new_order_item)
                db.session.commit()
            except Exception as e:
                return [{"msg": f"creating new item: {e}"}]

    except Exception as e:
        return [{"msg": f"Item not found {e}"}]
    return [{"msg": "Item added to cart"}]


@mcp.tool(name="find_inventory", description="Search the database inventory for a part")
def remove_from_cart(item_id: int | str, cart: list) -> str:
    """
    Search the database inventory for a part using a keryword
    Args:
        keyword: The keyword to search for in the inventory database

    Returns:
        str: A message indicating the part was found in the inventory
    """
    if not cart:
        return [{"msg": "Cart is empty"}]
    if not item_id:
        return [{"msg": "Item id is required"}]
    for i in range(len(cart)):
        order_item = cart[i]
        order_item.id
        if item_id == order_item.id:
            del cart[i]
            return [{"msg": f"Item {item_id} removed from cart"}]

    return [{"msg": f"Item {item_id} not found in cart"}]


@mcp.tool(name="find_inventory", description="Search the database inventory for a part")
def find_inventory(keyword: str, limit: int = 10) -> str:
    """
    Search the database inventory for a part using a keryword
    Args:
        keyword: The keyword to search for in the inventory database

    Returns:
        str: A message indicating the part was found in the inventory
    """

    if not keyword:
        return [["error", "Keyword is required"]]

    try:
        items = (
            StockItem.query.filter(StockItem.content.ilike(f"%{keyword}%"))
            .limit(limit)
            .all()
        )
    except Exception as e:
        logger.error(f"Error in vector_search_code: {e}")
        return json.dumps({"error": f"Search failed: {str(e)}"})

    if not items:
        return [["error", "Keyword is required"]]

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


@mcp.tool(name="checkout_cart", description="Check out the cart")
def checkout_cart(cart: list) -> str:
    """ """
    if not cart:
        return [{"msg": "Cart is empty"}]
    for i in range(len(cart)):
        item = cart[i]


# TODO: checkout cart
# TODO: rag search (parnum qwuery) and also natural language query

# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
