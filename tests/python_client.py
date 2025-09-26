"""
Manual test client for interacting with a local FastMCP server.

This script demonstrates how to:
- Connect to a FastMCP server running at http://localhost:9001/mcp
- Call the `list_files_in_vault` tool to retrieve available notes
- Call the `get_file_contents` tool to fetch and print the content of a note

Intended for manual testing and development only, not for production use.
"""

import asyncio
import json
from fastmcp import Client

client = Client("http://localhost:9001/mcp")


async def main():
    async with client:
        # Call list_notes tool
        print("Notes in vault:")
        notes_result = await client.call_tool("list_files_in_vault", {})

        # unwrap the content
        notes = notes_result.content[0].text if notes_result.content else "[]"
        # fastmcp usually encodes lists as JSON inside a text block
        notes = json.loads(notes)

        for note in notes:
            print(" -", note)

        # Call get_note tool on the first note (if any exist)
        note2get = "Obsidian"
        note_result = await client.call_tool("get_file_contents", {"filename": note2get})
        print(note_result.content[0].text)  # actual note

if __name__ == "__main__":
    asyncio.run(main())
