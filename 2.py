#!/usr/bin/env python3
"""
Directory Tree Viewer
Displays the structure of directories and files in a tree-like format.
"""

import os
import sys
from pathlib import Path


def generate_tree(directory, prefix="", is_last=True, max_depth=None, current_depth=0, show_hidden=False):
    """
    Generate a tree structure of the directory.
    
    Args:
        directory: Path to the directory
        prefix: Prefix for the current line
        is_last: Whether this is the last item in its parent directory
        max_depth: Maximum depth to traverse (None for unlimited)
        current_depth: Current depth in the tree
        show_hidden: Whether to show hidden files/folders (starting with .)
    """
    # Check if max depth is reached
    if max_depth is not None and current_depth >= max_depth:
        return
    
    # Get the directory path
    path = Path(directory)
    
    # Print the current directory/file name
    if current_depth == 0:
        print(f"📁 {path.name}/")
    else:
        connector = "└── " if is_last else "├── "
        icon = "📁 " if path.is_dir() else "📄 "
        print(f"{prefix}{connector}{icon}{path.name}{'/' if path.is_dir() else ''}")
    
    # If it's a file, return
    if not path.is_dir():
        return
    
    # Get all items in the directory
    try:
        items = list(path.iterdir())
        
        # Filter hidden files if requested
        if not show_hidden:
            items = [item for item in items if not item.name.startswith('.')]
        
        # Sort items: directories first, then files
        items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
        
    except PermissionError:
        print(f"{prefix}{'    ' if is_last else '│   '}⚠️  [Permission Denied]")
        return
    
    # Process each item
    for index, item in enumerate(items):
        is_last_item = index == len(items) - 1
        extension = "    " if is_last else "│   "
        new_prefix = prefix + extension
        
        # Recursively process subdirectories
        generate_tree(
            item,
            new_prefix,
            is_last_item,
            max_depth,
            current_depth + 1,
            show_hidden
        )


def count_items(directory, show_hidden=False):
    """Count the number of files and directories."""
    path = Path(directory)
    file_count = 0
    dir_count = 0
    
    for root, dirs, files in os.walk(path):
        if not show_hidden:
            # Filter hidden directories
            dirs[:] = [d for d in dirs if not d.startswith('.')]
            # Filter hidden files
            files = [f for f in files if not f.startswith('.')]
        
        dir_count += len(dirs)
        file_count += len(files)
    
    return dir_count, file_count


def main():
    """Main function to run the directory tree viewer."""
    print("\n" + "="*50)
    print("       DIRECTORY TREE VIEWER")
    print("="*50 + "\n")
    
    # Get folder path from user
    folder_path = input("Enter the folder path (or press Enter for current directory): ").strip()
    
    # Use current directory if no path provided
    if not folder_path:
        folder_path = os.getcwd()
    
    # Convert to Path object
    path = Path(folder_path)
    
    # Check if path exists
    if not path.exists():
        print(f"\n❌ Error: Path '{folder_path}' does not exist!")
        sys.exit(1)
    
    # Check if it's a directory
    if not path.is_dir():
        print(f"\n❌ Error: '{folder_path}' is not a directory!")
        sys.exit(1)
    
    # Ask for options
    print("\nOptions:")
    print("1. Show all files and folders")
    print("2. Show only up to certain depth")
    print("3. Include hidden files/folders")
    print("4. Both depth limit and hidden files")
    
    choice = input("\nSelect option (1-4, default is 1): ").strip()
    
    max_depth = None
    show_hidden = False
    
    if choice in ['2', '4']:
        depth_input = input("Enter maximum depth (default is unlimited): ").strip()
        if depth_input.isdigit():
            max_depth = int(depth_input)
    
    if choice in ['3', '4']:
        show_hidden = True
    
    # Display the tree
    print(f"\n📂 Directory Tree for: {path.absolute()}")
    print("-" * 50)
    
    try:
        generate_tree(path, max_depth=max_depth, show_hidden=show_hidden)
        
        # Count and display statistics
        dir_count, file_count = count_items(path, show_hidden)
        print("\n" + "-" * 50)
        print(f"📊 Summary: {dir_count} directories, {file_count} files")
        
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Program interrupted by user. Goodbye!")
        sys.exit(0)