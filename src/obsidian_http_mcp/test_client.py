import asyncio
import json
from fastmcp import Client
import google_auth_oauthlib.flow
import google.auth.transport.requests


# ----------------------------
# Step 1. Run OAuth flow
# ----------------------------
def get_google_token():
    # Load client secrets
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        scopes=[
            "openid",
            "https://www.googleapis.com/auth/userinfo.email",
            "https://www.googleapis.com/auth/userinfo.profile",
        ],
    )

    # This opens a local server and launches your browser
    creds = flow.run_local_server(port=9006)

    # Return the ID token (JWT) for authentication with FastMCP
    request = google.auth.transport.requests.Request()
    creds.refresh(request)
    return creds.id_token


# ----------------------------
# Step 2. Call MCP server
# ----------------------------
async def main():
    token = get_google_token()

    client = Client(
        "http://localhost:9001/mcp",
        auth={"Authorization": f"Bearer {token}"},
    )
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
