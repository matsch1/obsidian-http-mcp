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

    # def write_note(self, filename: str, content: str):
    #     file = self.path / filename
    #     file.parent.mkdir(parents=True, exist_ok=True)
    #     tmp = file.with_suffix(".tmp")
    #     tmp.write_text(content, encoding="utf-8")
    #     shutil.move(tmp, file)
    #     return {"status": "ok"}
    #
    # def add_task(self, filename: str, task: str):
    #     text = self.get_note(filename)
    #     lines = text.splitlines()
    #     inserted = False
    #     for i, line in enumerate(lines):
    #         if line.strip().lower() == "## tasks":
    #             lines.insert(i + 1, f"- [ ] {task}")
    #             inserted = True
    #             break
    #     if not inserted:
    #         lines.append("## Tasks")
    #         lines.append(f"- [ ] {task}")
    #     return self.write_note(filename, "\n".join(lines))
    #
    # def toggle_task(self, filename: str, task_text: str, done=True):
    #     text = self.get_note(filename)
    #     pattern = r"- \[( |x)\] " + re.escape(task_text)
    #     repl = f"- [{'x' if done else ' '}] {task_text}"
    #     updated = re.sub(pattern, repl, text)
    #     return self.write_note(filename, updated)
    #
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
