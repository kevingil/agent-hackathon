from mcp.server.fastmcp import FastMCP
from pathlib import Path
from mcp.server.fastmcp.utilities.logging import get_logger
from .db_connection import StoreService
import json
import asyncio

SQLLITE_DB = Path(__file__).parent.parent.parent.parent.parent.parent / "store.db"
logger = get_logger(__name__)
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
def find_inventory(keyword: str, limit: int = 10) -> str:
    """
    Search the database inventory for a part using a keryword
    Args:
        keyword: The keyword to search for in the inventory database

    Returns:
        str: A message indicating the part was found in the inventory
    """
    logger.info(
        f"🚨 MCP TOOL CALLED: find_inventory with  keyword='{keyword}' session_id={...}"
    )
    try:
        # Check if vector search service is available
        if not store_service:
            error_msg = "Store service not available. Please configure database connection with POSTGRES_USER, POSTGRES_PASSWORD, and POSTGRES_DB environment variables."
            logger.error(f"🚨 Vector search service not available: {error_msg}")
            return json.dumps({"error": error_msg})

        # Validate inputs
        limit = min(max(1, limit), 50)  # Clamp between 1 and 50

        # Generate embedding for the query
        # Perform the search
        try:
            # Try to run in existing event loop context
            results = asyncio.run(
                store_service.search_keyword(
                    keyword=keyword,
                    session_id=...,
                    limit=limit,
                )
            )
        except RuntimeError:
            # If there's already a loop running, use asyncio.create_task() approach
            import concurrent.futures

            def run_async():
                return asyncio.run(
                    store_service.search_keyword(
                        keyword=keyword,
                        session_id=...,
                        limit=limit,
                    )
                )

            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async)
                results = future.result()

        # Format results
        response = {
            "keyword": keyword,
            "total_results": len(results),
            "results": results,
        }

        return json.dumps(response, indent=2)

    except Exception as e:
        logger.error(f"Error in vector_search_code: {e}")
        return json.dumps({"error": f"Search failed: {str(e)}"})


# TODO: add tools to read from dummy database (store)
# TODO: add tools to update database after exectuion
# TODO: add to user car cart (partNum), remove from cart, checkout cart
# TODO: find inventory queryword serch or rag search (parnum qwuery) and also natural language query

# Run the server
if __name__ == "__main__":
    mcp.run(transport="sse")
