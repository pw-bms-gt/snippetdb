# SnippetDB

SnippetDB is a simple cross-platform code snippet manager.

- Snippets are stored as plain text files under `snippets/<language>`.
 - Titles and optional descriptions are extracted from the first comment lines using language-specific comment symbols.
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

### GUI Features

The search results list shows each snippet's language and title. Every row also
includes **Open**, **Copy**, and **Explore** buttons:

- **Open** opens the snippet inside the application where it can be edited.
- **Copy** copies the snippet text to your clipboard.
- **Explore** opens the folder containing the snippet file in your system's file explorer.

When a snippet is opened, a text area allows editing. Use **Save** to persist
changes or **Copy to clipboard** and **Close** to exit.

## Snippet Format

The first comment line is the title and the second (optional) line is the description. Comment prefixes depend on the language. For example, SQL snippets start lines with `--` while C# uses `//`.

```SQL
-- My Snippet Title
-- Optional description of the snippet
SELECT * FROM table;
```

### Supported Comment Prefixes

| Language | Prefixes |
|----------|----------|
| SQL      | `--`     |
| C#       | `//`     |
| M68K     | `;`, `*` |
