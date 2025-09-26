from fastmcp import FastMCP
from pathlib import Path
from dotenv import load_dotenv
import os

from vault import Vault

# ------------------------
# Load environment
# ------------------------
load_dotenv()

# ------------------------
# MCP server
# ------------------------
mcp = FastMCP(
    name="obsidian-fast",
    instructions="""
        Headless Obsidian MCP server.
        Provides tools to read, edit, and search notes directly in the vault.
    """,
)

vault_path = os.getenv("VAULT_PATH")
VAULT = Vault(vault_path)


# ------------------------
# MCP tools
# ------------------------


@mcp.tool
def list_files_in_vault(
    name="list_files_in_vault",
    description="List all note paths in the obsidian vault.",
) -> list[str]:
    """List all notes in the vault."""
    return VAULT.list_files_in_vault()


@mcp.tool
def list_files_in_dir(dir: str) -> list[str]:
    """List all notes in the vault."""
    return VAULT.list_files_in_dir(dir)


@mcp.tool
def get_file_contents(filename: str, debug: bool = False):
    """Return the full text of a note by filename (searches vault)."""
    result = VAULT.get_file_contents(filename, debug=debug)
    if debug:
        content, dbg = result
        return {"content": content, "debug": dbg}
    return result


@mcp.tool
def append_content(filename: str, content: str) -> str:
    """List all notes in the vault."""
    return VAULT.append_content(filename, content)


@mcp.tool
def patch_content(filename: str, content: str, position: dict) -> str:
    """List all notes in the vault."""
    return VAULT.patch_content(filename, content, position)


# @mcp.tool
# def get_daily_note(date: str | None = None) -> str:
#     """Return today's (or given ISO date) daily note filename, creating it if necessary."""
#     if date:
#         d = datetime.date.fromisoformat(date)
#     else:
#         d = None
#     return VAULT.get_daily_note(d)


# ------------------------
# Run server
# ------------------------
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=9001)
    # mcp.run(transport="stdio")
