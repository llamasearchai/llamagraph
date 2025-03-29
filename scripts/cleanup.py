#!/usr/bin/env python3
"""
Repository cleanup script for LlamaGraph.

This script removes duplicate and unnecessary files from the LlamaGraph repository.
Run it from the root of the repository.
"""
import os
import re
import shutil
from pathlib import Path
import argparse

# Files to remove (regexp patterns)
FILES_TO_REMOVE = [
    r'llamagraph-project.*\.py$',
    r'llamagraph-project.*\.txt$',
    r'.*\.pyc$',
    r'.*\.pyo$',
    r'.*~$',
    r'\.DS_Store$',
    r'.*\.bak$',
    r'.*\.swp$',
    r'.*\.swo$',
]

# Directories to remove
DIRS_TO_REMOVE = [
    '__pycache__',
    '.mypy_cache',
    '.pytest_cache',
    '.coverage',
    'htmlcov',
    'dist',
    'build',
    '*.egg-info',
]

def is_match(path, patterns):
    """Check if path matches any of the given patterns."""
    for pattern in patterns:
        if re.match(pattern, path.name):
            return True
    return False

def cleanup_files(directory, dry_run=False):
    """Remove unnecessary files."""
    count = 0
    directory = Path(directory)
    
    for path in directory.glob('**/*'):
        if path.is_file() and is_match(path, FILES_TO_REMOVE):
            print(f"Removing file: {path}")
            count += 1
            if not dry_run:
                path.unlink()
    
    return count

def cleanup_dirs(directory, dry_run=False):
    """Remove unnecessary directories."""
    count = 0
    directory = Path(directory)
    
    for pattern in DIRS_TO_REMOVE:
        for path in directory.glob(f'**/{pattern}'):
            if path.is_dir():
                print(f"Removing directory: {path}")
                count += 1
                if not dry_run:
                    shutil.rmtree(path)
    
    return count

def main():
    parser = argparse.ArgumentParser(description='Clean up unnecessary files in the LlamaGraph repository.')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be deleted without actually deleting')
    args = parser.parse_args()
    
    repo_root = Path(__file__).parent.parent
    
    print(f"Cleaning up repository: {repo_root}")
    print(f"Dry run: {args.dry_run}")
    
    files_count = cleanup_files(repo_root, args.dry_run)
    dirs_count = cleanup_dirs(repo_root, args.dry_run)
    
    print(f"\nCleanup completed:")
    print(f"- {files_count} files {'would be ' if args.dry_run else ''}removed")
    print(f"- {dirs_count} directories {'would be ' if args.dry_run else ''}removed")
    
    if args.dry_run:
        print("\nThis was a dry run. No files were actually deleted.")
        print("Run without --dry-run to perform the actual cleanup.")

if __name__ == "__main__":
    main() 