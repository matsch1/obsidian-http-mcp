import asyncio
import json
from fastmcp import Client

client = Client("http://localhost:9001/mcp")


async def main():
    async with client:
        # Call greet tool
        greet_result = await client.call_tool("greet", {"name": "Ford"})
        print("Greet result:", greet_result)

        # Call list_notes tool
        print("Notes in vault:")
        notes_result = await client.call_tool("list_notes", {})

        # unwrap the content
        notes = notes_result.content[0].text if notes_result.content else "[]"
        # fastmcp usually encodes lists as JSON inside a text block
        notes = json.loads(notes)

        for note in notes:
            print(" -", note)

        # Call get_note tool on the first note (if any exist)
        note2get = "Obsidian"
        note_result = await client.call_tool("get_note", {"filename": note2get})
        print(note_result.content[0].text)  # actual note

if __name__ == "__main__":
    asyncio.run(main())
