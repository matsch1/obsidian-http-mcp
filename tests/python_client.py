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
import os
from fastmcp import Client
from dotenv import load_dotenv

#
# ------------------------
# Load environment
# ------------------------
load_dotenv()

MCP_API_KEY = os.getenv("MCP_API_KEY")
MCP_USER = os.getenv("MCP_USER")


#
# ------------------------
# Client
# ------------------------
# Load client config
with open("client_config.json") as f:
    json_data = f.read()

config = json.loads(json_data)

# start client
client = Client(config)


async def main():
    async with client:
        ################ Call list_notes tool
        # print("Notes in vault:")
        # notes_result = await client.call_tool("list_files_in_vault", {})
        #
        # # unwrap the content
        # notes = notes_result.content[0].text if notes_result.content else "[]"
        # # fastmcp usually encodes lists as JSON inside a text block
        # notes = json.loads(notes)
        #
        # for note in notes:
        #     print(" -", note)

        ############################ Call get_note tool on the first note (if any exist)
        # note2get = "Obsidian"
        # note_result = await client.call_tool(
        #     "get_file_contents", {"filename": note2get}
        # )
        # print(note_result.content[0].text)  # actual note

        ############################# patch content with test file
        # note_result = await client.call_tool(
        #     "get_file_contents", {"filename": "test folder/test mcp 1.md"}
        # )
        # print(note_result.content[0].text)  # actual note
        # note_content = await client.call_tool(
        #     "patch_content_into_note",
        #     {
        #         "filepath": "test folder/test mcp 1.md",
        #         "operation": "append",
        #         "target_type": "text",
        #         "target": "dko diggidi diggidiasdf\ntest",
        #         "content": "\nDubsidu",
        #     },
        # )
        # note_result = await client.call_tool(
        #     "get_file_contents", {"filename": "test folder/test mcp 1.md"}
        # )
        # print(note_result.content[0].text)  # actual note

        ####################### find file
        # found_notes = await client.call_tool(
        #     "find_note_in_vault",
        #     {
        #         "directory": ".",
        #         "query": "MCP",
        #         "extensions": [".md"],
        #         "threshold": 80,
        #     },
        # )
        # print(found_notes.content[0].text)

        ####################### search text
        # found_notes = await client.call_tool(
        #     "search_text_in_notes",
        #     {
        #         "directory": ".",
        #         "query": "new content",
        #         "extensions": [".md"],
        #         "threshold": 90,
        #     },
        # )
        # print(found_notes.content[0].text)
        #

        ############################# patch content with test file
        note_result = await client.call_tool(
            "get_file_contents", {"filename": "test folder/test mcp 1.md"}
        )
        print(note_result.content[0].text)  # actual note
        note_content = await client.call_tool(
            "delete_lines_from_note",
            {
                "filepath": "test folder/test mcp 1.md",
                "line_numbers": [2, 4],
            },
        )
        note_result = await client.call_tool(
            "get_file_contents", {"filename": "test folder/test mcp 1.md"}
        )
        print(note_result.content[0].text)  # actual note


if __name__ == "__main__":
    asyncio.run(main())
