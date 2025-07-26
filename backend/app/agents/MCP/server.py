from mcp.server.fastmcp import FastMCP
from pathlib import Path

from .db_connection import StoreService

SQLLITE_DB = Path(__file__).parent.parent.parent.parent.parent.parent / "store.db"

store_service = StoreService()

# Create an MCP server
mcp = FastMCP(
    name="Knowledge Base",
    host="0.0.0.0",  # only used for SSE transport (localhost)
    port=8050,  # only used for SSE transport (set this to any port)
)


@mcp.tool(
    name="search",
    description="Search inside a json file",
)
def write_db(query: str) -> str:
    pass


@mcp.tool(
    name="add_to_cart",
    description="Add a part to the cart given the part id",
)
def add_to_cart(part_id: str | int) -> str:
    """Add a part to the cart
    Args:
        part_id (str | int): The part id to add to the cart

    Returns:
        str: A message indicating the part was added to the cart
    """
    message = ""

    return message


@mcp.tool(
    name="remove_from_cart",
    description="Remove a part to the cart given the part id",
)
def remove_from_cart(part_id: str | int) -> str:
    """Remove a part from the cart
    Args:
        part_id (str | int): The part id to remove from the cart

    Returns:
        str: A message indicating the part was removed from the cart
    """
    message = ""

    return message


@mcp.tool(name="checkout_cart", description="Checkout the cart")
def checkout_cart(cart_id: str | int) -> str:
    """
    Checkout the cart
    Args:
        cart_id (str | int): The cart id to checkout

    Returns:
        str: A message indicating the cart was checked out
    """
    message = ""

    return message


@mcp.tool(name="find_inventory", description="Search the database inventory for a part")
def find_inventory(keyword: str) -> str:
    """
    Search the database inventory for a part using a keryword
    Args:
        keyword: The keyword to search for in the inventory database

    Returns:
        str: A message indicating the part was found in the inventory
    """
    message = ""

    return message


# TODO: add tools to read from dummy database (store)
# TODO: add tools to update database after exectuion
# TODO: add to user car cart (partNum), remove from cart, checkout cart
# TODO: find inventory queryword serch or rag search (parnum qwuery) and also natural language query

# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
