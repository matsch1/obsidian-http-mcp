from fastmcp import FastMCP
from pathlib import Path
from dotenv import load_dotenv
import os
import re
import datetime
import shutil

# ------------------------
# Load environment
# ------------------------
load_dotenv()


# ------------------------
# Vault interface
# ------------------------
class Vault:
    def __init__(self, path: str):
        self.path = Path(path).expanduser().resolve()

    def list_files_in_vault(self):
        return [str(f.relative_to(self.path)) for f in self.path.rglob("*.md")]

    def list_files_in_dir(self, dir: str):
        dir_path = Path(self.path) / dir
        return [str(f.relative_to(dir_path)) for f in dir_path.rglob("*.md")]

    def get_file_contents(self, filename: str, debug=False):
        # normalize filename
        if not filename.endswith(".md"):
            filename += ".md"

        dbg = []
        for file in self.path.rglob("*.md"):
            if debug:
                dbg.append(f"Checking {file.name}")
            if file.name == filename:
                content = file.read_text(encoding="utf-8")
                if debug:
                    return content, dbg
                return content

        raise FileNotFoundError(f"No note named {filename} in vault")

    def append_content(self, filename: str, content: str):
        # append content to an existing or new note
        # normalize filename
        if not filename.endswith(".md"):
            filename += ".md"

        file_path = self.path / filename

        # ensure parent directories exist
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # append the content with a newline before it
        with file_path.open("a", encoding="utf-8") as f:
            if not content.endswith("\n"):
                content += "\n"
            f.write(content)

        return file_path
        
    def patch_content(self, filename: str, content: str, position: dict):
        if not filename.endswith(".md"):
            filename += ".md"

        file_path = self.path / filename
        if not file_path.exists():
            raise FileNotFoundError(f"{filename} does not exist")

        text = file_path.read_text(encoding="utf-8")
        lines = text.splitlines()

        if position["type"] == "heading":
            anchor = position["value"].lstrip("#").strip().lower()
            for i, line in enumerate(lines):
                if line.strip().startswith("#"):
                    heading_text = line.lstrip("#").strip().lower()
                    if heading_text == anchor:
                        if position.get("mode") == "before":
                            lines.insert(i, content)
                        else:  # default = after
                            lines.insert(i + 1, content)
                        break

        elif position["type"] == "block":
            # block references look like ^block-id
            anchor = "^" + position["value"].lstrip("^")
            for i, line in enumerate(lines):
                if anchor in line:
                    if position.get("mode") == "before":
                        lines.insert(i, content)
                    else:
                        lines.insert(i + 1, content)
                    break

        elif position["type"] == "frontmatter":
            if lines[0].strip() == "---":
                end = next(i for i, l in enumerate(lines[1:], 1) if l.strip() == "---")
                frontmatter = "\n".join(lines[1:end])
                data = yaml.safe_load(frontmatter) or {}
                key = position["value"]
                if position.get("mode") == "replace":
                    data[key] = content
                else:
                    old = data.get(key, "")
                    data[key] = str(old) + ("\n" if old else "") + content
                new_frontmatter = yaml.safe_dump(data, sort_keys=False).strip()
                lines = ["---", new_frontmatter, "---"] + lines[end+1:]

        new_text = "\n".join(lines) + "\n"
        file_path.write_text(new_text, encoding="utf-8")

        return file_path

    # def add_tag(self, filename: str, tag: str):
    #     text = self.get_note(filename)
    #     updated = text.rstrip() + f"\n#{tag}\n"
    #     return self.write_note(filename, updated)
    #
    # def get_daily_note(self, date: datetime.date | None = None):
    #     if date is None:
    #         date = datetime.date.today()
    #     filename = f"{date.isoformat()}.md"
    #     file = self.path / filename
    #     if not file.exists():
    #         file.write_text(f"# {date.isoformat()}\n\n## Tasks\n", encoding="utf-8")
    #     return filename
