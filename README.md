# SnippetDB

SnippetDB is a simple cross-platform code snippet manager.

- Snippets are stored as plain text files under `snippets/<language>`.
- Titles and optional descriptions are extracted from the first comment lines.
- A SQLite database indexes snippet titles for fast searching.
- Includes a minimal Tkinter GUI for searching and adding snippets.

## Usage

Initialize the snippet storage:

```bash
python snippet_manager.py init
```

Add a snippet from a file:

```bash
python snippet_manager.py add --language SQL --file path/to/snippet.sql
```

Search snippets by title:

```bash
python snippet_manager.py search --language SQL --query "join"
```

Launch the GUI:

```bash
python snippet_manager.py gui
```

## Snippet Format

The first comment line is the title. The next comment line (optional) is the description.

```bash
# My Snippet Title
# Optional description of the snippet
SELECT * FROM table;
```
