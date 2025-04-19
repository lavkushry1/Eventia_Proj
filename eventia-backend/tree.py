import os

def print_tree(directory, prefix="", is_last=True, ignore_dirs=["__pycache__", ".git", "venv"]):
    """Print directory structure in tree format."""
    files = []
    dirs = []
    
    # Sort items into files and directories
    for item in sorted(os.listdir(directory)):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path) and item not in ignore_dirs:
            dirs.append(item)
        elif os.path.isfile(item_path):
            files.append(item)
    
    # Process directories
    for i, d in enumerate(dirs):
        is_last_dir = (i == len(dirs) - 1 and len(files) == 0)
        new_prefix = prefix + ("└── " if is_last_dir else "├── ")
        print(f"{new_prefix}{d}/")
        
        next_prefix = prefix + ("    " if is_last_dir else "│   ")
        dir_path = os.path.join(directory, d)
        print_tree(dir_path, next_prefix, is_last_dir, ignore_dirs)
    
    # Process files
    for i, f in enumerate(files):
        is_last_file = (i == len(files) - 1)
        new_prefix = prefix + ("└── " if is_last_file else "├── ")
        print(f"{new_prefix}{f}")

print("Eventia Backend Project Structure:")
print_tree(".")