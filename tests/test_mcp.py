import subprocess
import time
import tempfile
import shutil
import json
from pathlib import Path
import pytest
from fastmcp import Client


# Global variables for the temporary vault
VAULT_DIR = None
sample_filename = "test.md"


@pytest.fixture(scope="module")
def mcp_docker():
    global VAULT_DIR

    # Create temporary vault
    VAULT_DIR = tempfile.mkdtemp()
    testdir = Path(VAULT_DIR) / "testdir"
    testdir.mkdir(parents=True, exist_ok=True)


    sample_note = Path(VAULT_DIR) / sample_filename
    sample_note2 = Path(VAULT_DIR) / "file2.md"
    sample_note3 = Path(VAULT_DIR) / "file3.md"
    sample_note4 = Path(VAULT_DIR) /"testdir"/"file4.md" 
    sample_note5 = Path(VAULT_DIR) /"testdir"/"file5.md"

    # Actually write all files
    sample_note.write_text("test_content", encoding="utf-8")
    sample_note2.write_text("content of file 2", encoding="utf-8")
    sample_note3.write_text("content of file 3", encoding="utf-8")
    sample_note4.write_text("content of file 4", encoding="utf-8")
    sample_note5.write_text("content of file 5", encoding="utf-8")


    # Remove old Docker container and image if it exists
    subprocess.run(["docker", "rm", "-f", "mcp_test", "."], check=True)
    subprocess.run(["docker", "rmi", "-f", "mcp_test", "."], check=True)

    # Build Docker image
    subprocess.run(["docker", "build", "-t", "mcp_test:latest", "."], check=True)

    # Run Docker container
    container = subprocess.run(
        [
            "docker",
            "run",
            "-d",
            "--name",
            "mcp_test",
            "-v",
            f"{VAULT_DIR}:/vault",
            "-p",
            "9001:9001",
            "mcp_test:latest",
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    container_id = container.stdout.strip()

    # Wait for MCP server to start (consider implementing a proper health check)
    time.sleep(5)  # Increased wait time

    yield  # tests run here

    # Teardown: stop and remove container
    subprocess.run(["docker", "rm", "-f", container_id], check=True)

    # Remove temp vault
    if VAULT_DIR:
        shutil.rmtree(VAULT_DIR)


@pytest.fixture
async def mcp_client(mcp_docker):
    """Provide an MCP client connected to the test server"""
    client = Client("http://localhost:9001/mcp")
    async with client:
        yield client


# ============== TESTS ==============


@pytest.mark.asyncio
async def test_list_files_in_vault(mcp_client):
    result = await mcp_client.call_tool("list_files_in_vault", {})
    file_list = json.loads(result.content[0].text)
    print(sorted(file_list))

    assert len(file_list) == 5
    assert sorted(file_list) == ["file2.md", "file3.md", "test.md", "testdir/file4.md", "testdir/file5.md"]

@pytest.mark.asyncio
async def test_list_files_in_dir(mcp_client):
    result = await mcp_client.call_tool("list_files_in_dir", {"dir": "testdir"})
    file_list = json.loads(result.content[0].text)
    print(file_list)

    assert len(file_list) == 2
    assert sorted(file_list) == ["file4.md", "file5.md"]


@pytest.mark.asyncio
async def test_get_note(mcp_client):
    result = await mcp_client.call_tool("get_file_contents", {"filename": sample_filename})
    assert "test_content" in result.content[0].text

async def test_append_to_existing_note(mcp_client):
    # Append content to the existing sample note
    result = await mcp_client.call_tool(
        "append_content",
        {"filename": sample_filename, "content": "extra line"}
    )
    assert "test.md" in result.content[0].text  # returns the path

    # Fetch the updated note and verify new content
    result = await mcp_client.call_tool("get_file_contents", {"filename": sample_filename})
    content = result.content[0].text
    assert "test_content" in content
    assert "extra line" in content


@pytest.mark.asyncio
async def test_append_creates_new_note(mcp_client):
    new_filename = "new_note.md"
    new_content = "this is a brand new note"

    # Append to a note that doesn’t exist yet (should create it)
    result = await mcp_client.call_tool(
        "append_content",
        {"filename": new_filename, "content": new_content}
    )
    assert "new_note.md" in result.content[0].text

    # Fetch and check contents
    result = await mcp_client.call_tool("get_file_contents", {"filename": new_filename})
    content = result.content[0].text
    assert new_content in content
