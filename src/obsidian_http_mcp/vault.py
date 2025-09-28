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

        absolut_path = self.path / filepath

        # ensure parent directories exist
        absolut_path.parent.mkdir(parents=True, exist_ok=True)

        # append the content with a newline before it
        with absolut_path.open("a", encoding="utf-8") as f:
            if not content.endswith("\n"):
                content += "\n"
            f.write(content)

        return absolut_path

    def patch_content(
        self, filepath: str, operation: str, target_type: str, target: str, content: str
    ):
        if not filepath.endswith(".md"):
            filepath += ".md"

        file_path = self.path / filepath
        if not file_path.exists():
            raise FileNotFoundError(f"{filepath} does not exist")

        text = file_path.read_text(encoding="utf-8")
        lines = text.splitlines()

        if target_type == "heading":
            anchor = target.lstrip("#").strip().lower()
            for i, line in enumerate(lines):
                if line.strip().startswith("##"):
                    heading_text = line.lstrip("#").strip().lower()
                    if heading_text == anchor:
                        if operation == "prepend":
                            lines.insert(i + 1, content + "\n" + lines[i + 1])
                        elif operation == "append":
                            lines.insert(i + 1, content)
                        break

        elif target_type == "block":
            # block references look like ^block-id
            anchor = "^" + target.lstrip("^")
            for i, line in enumerate(lines):
                if anchor in line:
                    if operation == "prepend":
                        lines.insert(i, content)
                    elif operation == "append":
                        lines.insert(i + 1, content)
                    elif operation == "replace":
                        lines[i] = content
                    break

        elif target_type == "frontmatter":
            if lines and lines[0].strip() == "---":
                end = next(
                    i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"
                )
                frontmatter = "\n".join(lines[1:end])
                data = yaml.safe_load(frontmatter) or {}
                if operation == "replace":
                    data[target] = content
                elif operation == "append":
                    old = data.get(target, "")
                    data[target] = str(old) + ("\n" if old else "") + content
                elif operation == "prepend":
                    old = data.get(target, "")
                    data[target] = content + ("\n" if old else "") + str(old)
                new_frontmatter = yaml.safe_dump(data, sort_keys=False).strip()
                lines = ["---", new_frontmatter, "---"] + lines[end + 1 :]

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
