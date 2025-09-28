from fastmcp import FastMCP
from dotenv import load_dotenv
import os
from typing import Annotated
from pydantic import Field

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
def list_files_in_dir(
    dir: Annotated[
        str,
        Field(description="direcotry path in vault. Path is relative to vault path"),
    ],
) -> list[str]:
    """List all notes in a specific directory of the vault."""
    return VAULT.list_files_in_dir(dir)


@mcp.tool
def get_file_contents(
    filename: Annotated[
        str,
        Field(
            description="filename of note (without path)",
        ),
    ],
):
    """Return the full text of a note by filename (searches vault)."""
    result = VAULT.get_file_contents(filename)
    return result


@mcp.tool
def append_content(
    filepath: Annotated[
        str,
        Field(
            description="filepath (relative to vault path) of file which should be changed",
        ),
    ],
    content: Annotated[
        str,
        Field(
            description="new content",
        ),
    ],
) -> str:
    """Append given content to a specific file. Create file if it does not exist"""
    return VAULT.append_content(filepath, content)


@mcp.tool
def patch_content(
    filepath: Annotated[
        str,
        Field(
            description="filepath (relative to vault path) of file which should be changed",
        ),
    ],
    operation: Annotated[
        str,
        Field(
            description="operation how to insert new content: append, prepend",
        ),
    ],
    target_type: Annotated[
        str,
        Field(
            description="type where the new content should be added: heading, block, frontmatter",
        ),
    ],
    target: Annotated[
        str,
        Field(
            description="name of the target where the new content should be added: heading name e.g. Tasks",
        ),
    ],
    content: Annotated[
        str,
        Field(
            description="new content",
        ),
    ],
) -> str:
    """
    Insert or update content in an Obsidian note relative to a heading, block reference, or frontmatter field.
    """
    VAULT.patch_content(filepath, operation, target_type, target, content)
    return f"Successfully patched content in {filepath}"


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
