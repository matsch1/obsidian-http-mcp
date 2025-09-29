from pathlib import Path
from dotenv import load_dotenv
import yaml

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

    def get_file_contents(self, filename: str):
        # normalize filename
        if not filename.endswith(".md"):
            filename += ".md"

        for file in self.path.rglob("*.md"):
            if file.name == filename:
                content = file.read_text(encoding="utf-8")
                return content

        raise FileNotFoundError(f"No note named {filename} in vault")

    def append_content(self, filepath: str, content: str):
        # append content to an existing or new note
        # normalize filename
        if not filepath.endswith(".md"):
            filepath += ".md"

        absolute_path = self.path / filepath

        # ensure parent directories exist
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        # append the content with a newline before it
        with absolute_path.open("a", encoding="utf-8") as f:
            if not content.endswith("\n"):
                content += "\n"
            f.write(content)

        return absolute_path

    def patch_content(self, filepath: str, operation: str, target_type: str, target: str, content: str):
        if not filepath.endswith(".md"):
            filepath += ".md"

        absolute_path = self.path / filepath
        if not absolute_path.exists():
            raise FileNotFoundError(f"{absolute_path} does not exist")

        lines = absolute_path.read_text(encoding="utf-8").splitlines()

        handlers = {
            "heading": self._patch_heading,
            "block": self._patch_block,
            "frontmatter": self._patch_frontmatter,
        }

        if target_type not in handlers:
            raise ValueError(f"Unknown target_type: {target_type}")

        lines = handlers[target_type](lines, operation, target, content)

        absolute_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return absolute_path


def _patch_heading(self, lines, operation, target, content):
    anchor = target.lstrip("#").strip().lower()
    matches = [
        i for i, line in enumerate(lines)
        if line.strip().startswith("#") and line.lstrip("#").strip().lower() == anchor
    ]

    if not matches:
        raise ValueError(f"No heading '{target}' found")
    if len(matches) > 1:
        raise ValueError(f"Multiple headings '{target}' found. Must be unique.")

    i = matches[0]

    if operation == "prepend":
        lines.insert(i + 1, content)
    elif operation == "append":
        lines.insert(i + 1, content)
    elif operation == "replace":
        new_lines = content.splitlines()
        lines[i:i+1] = new_lines
    return lines

def _patch_block(self, lines, operation, target, content):
    anchor = "^" + target.lstrip("^")
    matches = [i for i, line in enumerate(lines) if anchor in line]

    if not matches:
        raise ValueError(f"No block '{target}' found")
    if len(matches) > 1:
        raise ValueError(f"Multiple blocks '{target}' found. Must be unique.")

    i = matches[0]

    if operation == "prepend":
        lines.insert(i, content)
    elif operation == "append":
        lines.insert(i + 1, content)
    elif operation == "replace":
        new_lines = content.splitlines()
        lines[i:i+1] = new_lines
    return lines

def _patch_frontmatter(self, lines, operation, target, content):
    if not (lines and lines[0].strip() == "---"):
        raise ValueError("No frontmatter found")

    end = next((i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"), None)
    if end is None:
        raise ValueError("Frontmatter not properly closed with '---'")

    frontmatter = "\n".join(lines[1:end])
    data = yaml.safe_load(frontmatter) or {}

    old = data.get(target, "")
    if operation == "replace":
        data[target] = content
    elif operation == "append":
        data[target] = str(old) + ("\n" if old else "") + content
    elif operation == "prepend":
        data[target] = content + ("\n" if old else "") + str(old)

    new_frontmatter = yaml.safe_dump(data, sort_keys=False).strip()
    return ["---", new_frontmatter, "---"] + lines[end + 1 :]

