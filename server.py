from fastmcp import FastMCP

# MCP server with instruction
mcp = FastMCP(
    name="medium-article",
    instructions="""
        Demo MCP server for medium article
    """,
)


@mcp.tool
def add_numbers(num1: int, num2: int) -> int:
    """
    Add two numbers

    :param num1: Path to the Excel file.
    :param num2: Name of the sheet to read from the Excel file.
    :return: sum of both the input numbers
    """
    return num1 + num2


@mcp.tool
def key_value_flatten(input_dict: dict) -> dict:
    """
    Flatten out a dictionary

    :param input_dict: dictionary as input
    :return: dictionary containing both keys and values as list
    """
    return {
        "all_keys": list(input_dict.keys()),
        "all_values": list(input_dict.values()),
    }


@mcp.tool
def greet(name: str) -> str:
    return f"Hello, {name}!"


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9001)
    # mcp.run(transport="stdio")
