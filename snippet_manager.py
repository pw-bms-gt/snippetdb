import argparse
import os
import sqlite3
import datetime
import webbrowser
import tempfile
from tkinter import (
    Tk,
    Frame,
    Label,
    Entry,
    Listbox,
    Scrollbar,
    Button,
    StringVar,
    END,
    SINGLE,
    Toplevel,
    Text,
)

DB_NAME = "snippets.db"
SNIPPETS_DIR = "snippets"

# Comment prefixes used to detect titles and descriptions for each language.
# Languages not listed here fall back to "#".
COMMENT_PREFIXES = {
    "SQL": ["--"],
    "C#": ["//"],
    "M68K": [";", "*"],
}


def init_db():
    os.makedirs(SNIPPETS_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """CREATE TABLE IF NOT EXISTS snippets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT,
            title TEXT,
            description TEXT,
            file_path TEXT,
            created_at TEXT
        )"""
    )
    conn.commit()
    conn.close()


def ensure_language_dir(language: str) -> str:
    path = os.path.join(SNIPPETS_DIR, language)
    os.makedirs(path, exist_ok=True)
    return path


def parse_snippet_text(text: str, comment_markers):
    """Extract the title and optional description from a snippet."""

    title = ""
    description = ""
    lines = text.splitlines()
    for i, line in enumerate(lines[:2]):
        stripped = line.lstrip()
        marker = next((m for m in comment_markers if stripped.startswith(m)), None)
        if marker:
            content = stripped[len(marker) :].lstrip()
            if i == 0:
                title = content
            else:
                description = content
        else:
            break
    return title, description


def add_snippet(language: str, file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    markers = COMMENT_PREFIXES.get(language, ["#"])
    title, description = parse_snippet_text(text, markers)
    if not title:
        raise ValueError("Snippet must start with a commented title")
    lang_dir = ensure_language_dir(language)
    name = "_".join(title.split())
    dest_path = os.path.join(lang_dir, f"{name}.txt")
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(text)
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO snippets (language, title, description, file_path, created_at) VALUES (?, ?, ?, ?, ?)",
        (language, title, description, dest_path, datetime.datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()
    return dest_path


def search_snippets(language: str, query: str):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT title, description, file_path FROM snippets WHERE language=? AND title LIKE ? ORDER BY title",
        (language, f"%{query}%"),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


class SnippetGUI(Tk):
    def __init__(self):
        super().__init__()
        self.title("SnippetDB")
        self.geometry("600x400")
        self.language_var = StringVar()
        self.query_var = StringVar()
        self.create_widgets()
        self.refresh_languages()

    def create_widgets(self):
        top = Frame(self)
        top.pack(fill="x")
        Label(top, text="Language:").pack(side="left")
        self.lang_entry = Entry(top, textvariable=self.language_var)
        self.lang_entry.pack(side="left", padx=5)
        Label(top, text="Search:").pack(side="left")
        Entry(top, textvariable=self.query_var).pack(side="left", fill="x", expand=True)
        Button(top, text="Search", command=self.on_search).pack(side="left", padx=5)
        Button(top, text="Add", command=self.open_add_window).pack(side="left")

        frame = Frame(self)
        frame.pack(fill="both", expand=True)
        scrollbar = Scrollbar(frame)
        scrollbar.pack(side="right", fill="y")
        self.listbox = Listbox(frame, selectmode=SINGLE)
        self.listbox.pack(fill="both", expand=True)
        self.listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listbox.yview)
        self.listbox.bind("<Double-Button-1>", self.open_selected)

    def refresh_languages(self):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT language FROM snippets ORDER BY language")
        languages = [row[0] for row in cur.fetchall()]
        conn.close()
        if languages:
            self.language_var.set(languages[0])

    def on_search(self):
        lang = self.language_var.get()
        query = self.query_var.get()
        self.listbox.delete(0, END)
        for title, desc, path in search_snippets(lang, query):
            display = title if not desc else f"{title} - {desc}"
            self.listbox.insert(END, f"{display}||{path}")

    def open_selected(self, event=None):
        selection = self.listbox.curselection()
        if not selection:
            return
        item = self.listbox.get(selection[0])
        _, path = item.split("||", 1)
        webbrowser.open(f"file://{os.path.abspath(path)}")

    def open_add_window(self):
        win = Toplevel(self)
        win.title("Add Snippet")
        Label(win, text="Language:").pack(anchor="w")
        lang_var = StringVar(value=self.language_var.get())
        Entry(win, textvariable=lang_var).pack(fill="x")
        txt = Text(win, height=10)
        txt.pack(fill="both", expand=True)
        Button(win, text="Save", command=lambda: self.save_snippet(lang_var.get(), txt.get("1.0", END), win)).pack()

    def save_snippet(self, lang, text, window):
        with tempfile.NamedTemporaryFile("w", delete=False, suffix=".txt", encoding="utf-8") as tmp:
            tmp.write(text)
            temp_path = tmp.name
        try:
            add_snippet(lang, temp_path)
            window.destroy()
        except Exception as e:
            window.title(str(e))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


def main():
    parser = argparse.ArgumentParser(description="SnippetDB manager")
    sub = parser.add_subparsers(dest="cmd")

    sub.add_parser("init")

    add_p = sub.add_parser("add")
    add_p.add_argument("--language", required=True)
    add_p.add_argument("--file", required=True)

    search_p = sub.add_parser("search")
    search_p.add_argument("--language", required=True)
    search_p.add_argument("--query", default="")

    sub.add_parser("gui")

    args = parser.parse_args()

    if args.cmd == "init":
        init_db()
        print("Initialized database and snippet folder")
    elif args.cmd == "add":
        init_db()
        path = add_snippet(args.language, args.file)
        print(f"Snippet saved to {path}")
    elif args.cmd == "search":
        init_db()
        results = search_snippets(args.language, args.query)
        for title, desc, path in results:
            if desc:
                print(f"{title} - {desc} -> {path}")
            else:
                print(f"{title} -> {path}")
    elif args.cmd == "gui":
        init_db()
        app = SnippetGUI()
        app.mainloop()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
