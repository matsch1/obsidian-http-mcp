from fastmcp import FastMCP
from pathlib import Path
from dotenv import load_dotenv
import os
import re
import datetime
import shutil

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
def greet(name: str) -> str:
    return f"Hello, {name}!"


@mcp.tool
def list_files_in_vault() -> list[str]:
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
    return VAULT.append_content(filename,content)

# @mcp.tool
# def write_note(filename: str, content: str) -> dict:
#     """Overwrite a note with new content."""
#     return VAULT.write_note(filename, content)
#
#
# @mcp.tool
# def add_task(filename: str, task: str) -> dict:
#     """Add a new task to a note."""
#     return VAULT.add_task(filename, task)
#
#
# @mcp.tool
# def toggle_task(filename: str, task: str, done: bool = True) -> dict:
#     """Check or uncheck a task in a note."""
#     return VAULT.toggle_task(filename, task, done)
#
#
# @mcp.tool
# def add_tag(filename: str, tag: str) -> dict:
#     """Append a tag to a note."""
#     return VAULT.add_tag(filename, tag)
#
#
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
