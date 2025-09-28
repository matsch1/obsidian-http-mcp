from fastmcp import FastMCP
from dotenv import load_dotenv
import os

from vault import Vault
from authentication import UserAuthMiddleware

# ------------------------
# Load environment
# ------------------------
load_dotenv()

vault_path = os.getenv("VAULT_PATH")

# ------------------------
# MCP server
# ------------------------
mcp = FastMCP(
    name="obsidian-http-mcp",
    instructions="""
        Headless Obsidian MCP server.
        Provides tools to read, edit, and search notes directly in the vault.
    """,
)

mcp.add_middleware(UserAuthMiddleware())

# ------------------------
# MCP tools
# ------------------------
VAULT = Vault(vault_path)


@mcp.tool
def list_files_in_vault() -> list[str]:
    """List all notes in the vault."""
    return VAULT.list_files_in_vault()


@mcp.tool
def list_files_in_dir(dir: str) -> list[str]:
    """List all notes in a specific directory of the vault."""
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
    """Append given content to a specific file. Create file if it does not exist"""
    return VAULT.append_content(filename, content)


@mcp.tool
def patch_content(filename: str, content: str, position: dict) -> str:
    """
    Patch given content to a specific file at a specific position.
    The postiont could be a heading, block or frontmatter.
    "filename": filename,
    "content": "new content",
    "position": {"type": "heading/block", "value": "Tasks", "mode": "before/after"},
    "position": {"type": "frontmatter", "value": "Tasks", "mode": "add/replace"},
    """
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
