import os
import shutil
from pathlib import Path

# Configuration
DRY_RUN = False
ROOT_DIR = Path(os.getcwd())
OLD_BRAND_NAME = "Q-DNA"
NEW_BRAND_NAME = "QoreLogic"
OLD_BRAND_SLUG = "qdna"
NEW_BRAND_SLUG = "qorelogic"

# Files to exclude from content replacement
EXCLUDES = [
    ".git",
    "__pycache__",
    ".pytest_cache",
    "node_modules",
    "venv",
    ".venv",
    "migrate_brand.py",
    # We generally want to touch everything else
]

def should_process(path: Path) -> bool:
    for exclude in EXCLUDES:
        if exclude in path.parts:
            return False
    return True

def replace_in_file(file_path: Path):
    try:
        # Read as text, ignore errors for binary files
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            print(f"Skipping binary file: {file_path}")
            return

        new_content = content.replace(OLD_BRAND_NAME, NEW_BRAND_NAME)
        new_content = new_content.replace(OLD_BRAND_SLUG, NEW_BRAND_SLUG)
        new_content = new_content.replace(OLD_BRAND_SLUG.upper(), NEW_BRAND_SLUG.upper())

        if content != new_content:
            print(f"Updating content: {file_path}")
            if not DRY_RUN:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def rename_item(path: Path) -> Path:
    if OLD_BRAND_SLUG in path.name:
        new_name = path.name.replace(OLD_BRAND_SLUG, NEW_BRAND_SLUG)
        new_path = path.with_name(new_name)
        print(f"Renaming: {path} -> {new_path}")
        if not DRY_RUN:
            path.rename(new_path)
        return new_path
    
    # Check for uppercase or mixed case if file system is case-sensitive (Windows usually not, but good to be explicit)
    # Actually Q-DNA might be in filename? "verify_qdna.md" -> "verify_qorelogic.md"
    # "Q-DNA_SPECIFICATION.md" -> "QoreLogic_SPECIFICATION.md"
    if OLD_BRAND_NAME in path.name:
         new_name = path.name.replace(OLD_BRAND_NAME, NEW_BRAND_NAME)
         new_path = path.with_name(new_name)
         print(f"Renaming: {path} -> {new_path}")
         if not DRY_RUN:
             path.rename(new_path)
         return new_path

    return path

def main():
    print(f"Starting migration: {OLD_BRAND_NAME} -> {NEW_BRAND_NAME}")
    
    # 1. Content Replacements (Downwards walk to handle files first)
    for root, dirs, files in os.walk(ROOT_DIR):
        root_path = Path(root)
        if not should_process(root_path):
            continue
            
        for file in files:
            file_path = root_path / file
            if should_process(file_path):
                replace_in_file(file_path)

    # 2. File Renaming (Need to be careful about iteration if we verify during loop)
    # We'll collect all paths first, then sort by depth (deepest first) to avoid renaming parents before children
    all_paths = []
    for root, dirs, files in os.walk(ROOT_DIR):
        root_path = Path(root)
        if not should_process(root_path):
            continue
        for d in dirs:
            all_paths.append(root_path / d)
        for f in files:
            all_paths.append(root_path / f)
            
    # Sort by path length descending (deepest first)
    all_paths.sort(key=lambda p: len(p.parts), reverse=True)
    
    for path in all_paths:
        if path.exists(): # Might have been moved if it was a child of a renamed dir (though we sorted deep first)
             rename_item(path)

    print("Migration complete.")

if __name__ == "__main__":
    main()
