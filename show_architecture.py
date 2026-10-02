from pathlib import Path

ROOT = Path(".")
IGNORE = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "env",
    "node_modules",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
}

def print_tree(path: Path, prefix: str = ""):
    items = sorted(
        [x for x in path.iterdir() if x.name not in IGNORE],
        key=lambda x: (x.is_file(), x.name.lower())
    )

    for index, item in enumerate(items):
        is_last = index == len(items) - 1

        connector = "└── " if is_last else "├── "
        print(f"{prefix}{connector}{item.name}")

        if item.is_dir():
            extension = "    " if is_last else "│   "
            print_tree(item, prefix + extension)


print()
print("=" * 70)
print("                 INDIA AI GRID ARCHITECTURE")
print("=" * 70)
print()

print(ROOT.resolve())
print_tree(ROOT)

print()
print("=" * 70)