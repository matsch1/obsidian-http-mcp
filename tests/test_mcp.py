import subprocess
import time
import tempfile
import shutil
import json
import os
import stat
from pathlib import Path
import pytest
from fastmcp import Client
from dotenv import load_dotenv

#
#
# ------------------------
# Load environment
# ------------------------
load_dotenv()

MCP_API_KEY = os.getenv("MCP_API_KEY")
MCP_USER = os.getenv("MCP_USER")


# Global variables for the temporary vault
VAULT_DIR = None
sample_filename = "test.md"


def on_rm_error(func, path, exc_info):
    # make file writable and retry
    try:
        os.chmod(path, stat.S_IWUSR)
        func(path)
    except Exception:
        pass


@pytest.fixture(scope="module")
def mcp_docker():
    global VAULT_DIR

    VAULT_DIR = tempfile.mkdtemp()
    testdir = Path(VAULT_DIR) / "testdir"
    testdir.mkdir(parents=True, exist_ok=True)

    sample_note = Path(VAULT_DIR) / sample_filename
    sample_note2 = Path(VAULT_DIR) / "file2.md"
    sample_note3 = Path(VAULT_DIR) / "file3.md"
    sample_note4 = Path(VAULT_DIR) / "testdir" / "file4.md"
    sample_note5 = Path(VAULT_DIR) / "testdir" / "file5.md"

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
            "-e",
            f"MCP_API_KEY={MCP_API_KEY}",
            "-e",
            f"MCP_USER={MCP_USER}",
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
        shutil.rmtree(VAULT_DIR, onerror=on_rm_error)


@pytest.fixture
async def mcp_client(mcp_docker):
    """Provide an MCP client connected to the test server"""
    # Load client config
    with open("client_config.json") as f:
        json_data = f.read()

    config = json.loads(json_data)

    # start client
    client = Client(config)
    async with client:
        yield client


# ============== TESTS ==============


@pytest.mark.asyncio
async def test_list_files_in_vault(mcp_client):
    result = await mcp_client.call_tool("list_files_in_vault", {})
    file_list = json.loads(result.content[0].text)
    print(sorted(file_list))

    assert len(file_list) == 5
    assert sorted(file_list) == [
        "file2.md",
        "file3.md",
        "test.md",
        "testdir/file4.md",
        "testdir/file5.md",
    ]


@pytest.mark.asyncio
async def test_list_files_in_dir(mcp_client):
    result = await mcp_client.call_tool("list_files_in_dir", {"dir": "testdir"})
    file_list = json.loads(result.content[0].text)
    print(file_list)

    assert len(file_list) == 2
    assert sorted(file_list) == ["file4.md", "file5.md"]


@pytest.mark.asyncio
async def test_list_files_in_root_dir(mcp_client):
    result = await mcp_client.call_tool("list_files_in_dir", {"dir": "/"})
    file_list = json.loads(result.content[0].text)
    print(file_list)

    vault_result = await mcp_client.call_tool("list_files_in_vault", {})
    vault_file_list = json.loads(vault_result.content[0].text)
    assert len(file_list) == len(vault_file_list)
    assert sorted(file_list) == [
        "file2.md",
        "file3.md",
        "test.md",
        "testdir/file4.md",
        "testdir/file5.md",
    ]


@pytest.mark.asyncio
async def test_list_files_in_subroot_dir(mcp_client):
    result = await mcp_client.call_tool("list_files_in_dir", {"dir": "/testdir"})
    file_list = json.loads(result.content[0].text)
    print(file_list)

    ref_result = await mcp_client.call_tool("list_files_in_dir", {"dir": "testdir"})
    ref_file_list = json.loads(ref_result.content[0].text)
    assert len(file_list) == len(ref_file_list)
    assert sorted(file_list) == ["file4.md", "file5.md"]


@pytest.mark.asyncio
async def test_get_note(mcp_client):
    result = await mcp_client.call_tool(
        "get_file_contents", {"filename": sample_filename}
    )
    assert "test_content" in result.content[0].text


@pytest.mark.asyncio
async def test_create_note_in_rootdir(mcp_client):
    new_note = "test_note.md"

    # Create the note
    path = await mcp_client.call_tool("create_note", {"filepath": new_note})
    print("Created:", path.content[0].text)

    # List files properly
    files = await mcp_client.call_tool("list_files_in_vault", {})
    file_list = json.loads(files.content[0].text)

    # Assert against the actual list
    assert new_note in file_list


@pytest.mark.asyncio
async def test_create_note_in_subdir(mcp_client):
    new_note = "test/testitest/test_note.md"

    # Create the note
    path = await mcp_client.call_tool("create_note", {"filepath": new_note})
    print("Created:", path.content[0].text)

    # List files properly
    files = await mcp_client.call_tool("list_files_in_vault", {})
    file_list = json.loads(files.content[0].text)

    # Assert against the actual list
    assert new_note in file_list


@pytest.mark.asyncio
async def test_append_content_to_empty_note(mcp_client):
    new_note = "test_note.md"
    new_content = "afdasdf asdff;aen"

    # Create the note
    path = await mcp_client.call_tool("create_note", {"filepath": new_note})
    print("Created:", path.content[0].text)

    # Append content
    path = await mcp_client.call_tool(
        "append_content_to_note", {"filepath": new_note, "content": new_content}
    )

    # Get content
    result = await mcp_client.call_tool("get_file_contents", {"filename": new_note})

    # Assert
    assert new_content in result.content[0].text


@pytest.mark.asyncio
async def test_append_content_to_nonempty_note(mcp_client):
    new_content = "afdasdf asdff;aen"

    # Append content
    path = await mcp_client.call_tool(
        "append_content_to_note", {"filepath": sample_filename, "content": new_content}
    )

    # Patch: append after heading "Tasks" (ignoring heading level)
    result = await mcp_client.call_tool(
        "patch_content",
        {
            "filepath": filepath,
            "operation": "append",
            "target_type": "heading",
            "target": "Tasks",
            "content": "- [ ] new task",
        },
    )
    assert filepath in result.content[0].text

    # Verify the updated note contains new task under Tasks
    result = await mcp_client.call_tool("get_file_contents", {"filename": filepath})
    content = result.content[0].text
    assert "- [ ] new task" in content

    # And it should appear before "### Urgent"
    tasks_index = content.index("## Tasks")
    urgent_index = content.index("### Urgent")
    new_task_index = content.index("- [ ] new task")
    assert tasks_index < new_task_index < urgent_index
