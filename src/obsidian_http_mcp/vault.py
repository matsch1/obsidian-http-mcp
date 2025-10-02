from rapidfuzz import fuzz
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
        # Ensure .md extension
        if not filename.endswith(".md"):
            filename += ".md"

        candidate = Path(filename)

        # Case 1: provided filename is absolute path
        if candidate.exists():
            return candidate.read_text(encoding="utf-8")

        # Case 2: provided filename is relative path
        absolute_path = Path(self.path) / candidate
        if absolute_path.exists():
            return absolute_path.read_text(encoding="utf-8")

        # Case 3: provided filename is only the name of the file
        for file in self.path.rglob("*.md"):
            if file.name == filename:
                content = file.read_text(encoding="utf-8")
                return content

        raise FileNotFoundError(f"No note found for {filename}")

    def create_note(self, filepath: str):
        # normalize filename
        if not filepath.endswith(".md"):
            filepath += ".md"

        absolute_path = self.path / filepath

        # ensure parent directories exist
        absolute_path.parent.mkdir(parents=True, exist_ok=True)

        # actually create the file if it doesn't exist
        absolute_path.touch(exist_ok=True)

        return absolute_path

    def append_content_to_note(self, filepath: str, content: str):
        absolute_path = self.path / filepath

        # append the content with a newline before it
        with absolute_path.open("a", encoding="utf-8") as f:
            if not content.startswith("\n"):
                content = "\n" + content
            if not content.endswith("\n"):
                content += "\n"
            f.write(content)

        return absolute_path

    def delete_lines_from_note(self, filepath: str, line_numbers: list[int]):
        if not filepath.endswith(".md"):
            filepath += ".md"

        absolute_path = self.path / filepath
        if not absolute_path.exists():
            raise FileNotFoundError(f"{absolute_path} does not exist")

        lines = absolute_path.read_text(encoding="utf-8").splitlines()

        # Filter out the lines that should be deleted
        new_lines = [
            line for i, line in enumerate(lines, start=1) if i not in line_numbers
        ]

        absolute_path.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        return absolute_path

    def patch_content_into_note(
        self, filepath: str, operation: str, target_type: str, target: str, content: str
    ):
        if not filepath.endswith(".md"):
            filepath += ".md"

        absolute_path = self.path / filepath
        if not absolute_path.exists():
            raise FileNotFoundError(f"{absolute_path} does not exist")

        lines = absolute_path.read_text(encoding="utf-8").splitlines()

        handlers = {
            "heading": self._patch_heading,
            "frontmatter": self._patch_frontmatter,
            "text": self._patch_text,
        }

        if target_type not in handlers:
            raise ValueError(f"Unknown target_type: {target_type}")

        lines = handlers[target_type](lines, operation, target, content)

        absolute_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return absolute_path

    def _patch_heading(self, lines, operation, target, content):
        anchor = target.lstrip("#").strip().lower()
        matches = [
            i
            for i, line in enumerate(lines)
            if line.strip().startswith("#")
            and line.lstrip("#").strip().lower() == anchor
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
            lines[i : i + 1] = new_lines
        return lines

    def _patch_frontmatter(self, lines, operation, target, content):
        # If no frontmatter exists, create a new one
        if not (lines and lines[0].strip() == "---"):
            data = {}
            if operation == "replace":
                data[target] = content
            elif operation == "append":
                data[target] = content
            elif operation == "prepend":
                data[target] = content
            new_frontmatter = yaml.safe_dump(data, sort_keys=False).strip()
            return ["---", new_frontmatter, "---"] + lines

        # Otherwise, modify existing frontmatter
        end = next(
            (i for i, line in enumerate(lines[1:], 1) if line.strip() == "---"),
            None,
        )
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

    def _patch_text(self, lines, operation, target, content):
        text = "\n".join(lines)

        matches = text.count(target)
        if matches == 0:
            raise ValueError(f"No text '{target}' found")
        if matches > 1:
            raise ValueError(
                f"Multiple matches for text '{target}' found. Must be unique."
            )

        if operation == "replace":
            text = text.replace(target, content, 1)
        elif operation == "prepend":
            text = text.replace(target, content + target, 1)
        elif operation == "append":
            text = text.replace(target, target + content, 1)

        return text.splitlines()

    def find_note_in_vault(
        self,
        directory: str,
        query: str,
        extensions: tuple[str, ...] = (".md",),
        threshold: int = 80,
    ) -> list[dict]:
        """
        Search for files in a directory (including subdirectories) whose names
        are similar to `query` using fuzzy matching.

        Args:
            directory: Relative path inside the vault to search.
            query: Filename or part of filename to search.
            extensions: Tuple of file extensions to include (default: ('.md',)).
            threshold: Minimum similarity score (0-100) to include a file.

        Returns:
            List of dicts {"path": file_path, "score": similarity_score},
            sorted by descending similarity.
        """
        # Resolve absolute path inside vault
        root = (self.path / directory).resolve()
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Directory '{directory}' does not exist in vault")

        query_lower = query.lower()
        results: list[dict] = []

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if extensions and file_path.suffix not in extensions:
                continue

            score = fuzz.partial_ratio(query_lower, file_path.name.lower())
            if score >= threshold:
                results.append({"path": str(file_path), "score": score})

        # Sort by score descending
        return sorted(results, key=lambda x: x["score"], reverse=True)

    def search_text_in_notes(
        self,
        directory: str,
        query: str,
        extensions: tuple[str, ...] = (".md",),
        threshold: int = 80,
    ) -> list[dict]:
        """
        Fuzzy search for a query in all files under a directory.

        Args:
            directory: Relative path inside the vault to search.
            query: Text to search for in file contents.
            extensions: Tuple of file extensions to include (default: ('.md',)).
            threshold: Minimum similarity score (0–100) to include a match.

        Returns:
            List of dicts with keys: 'path', 'line', 'text', 'score',
            sorted by descending similarity score.
        """
        root = (self.path / directory).resolve()
        if not root.exists() or not root.is_dir():
            raise FileNotFoundError(f"Directory '{directory}' does not exist in vault")

        results = []
        query_lower = query.lower()

        for file_path in root.rglob("*"):
            if not file_path.is_file():
                continue
            if extensions and file_path.suffix not in extensions:
                continue

            try:
                with file_path.open("r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        text = line.strip()
                        if not text:
                            continue
                        score = fuzz.partial_ratio(query_lower, line.lower())
                        if score >= threshold:
                            results.append(
                                {
                                    "path": str(file_path),
                                    "line": i,
                                    "text": line.strip(),
                                    "score": score,
                                }
                            )
            except Exception:
                continue  # skip unreadable files

        # Sort by score descending
        return sorted(results, key=lambda x: x["score"], reverse=True)
