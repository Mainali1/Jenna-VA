#!/usr/bin/env python3
"""
Jenna Voice Assistant - Deep Clean Utility

This script performs a deep clean of the Jenna Voice Assistant codebase,
removing redundant files, development artifacts, and temporary files.

Usage:
    python cleanup.py [--dry-run] [--all] [--cache] [--build] [--temp] [--node]

Options:
    --dry-run   Show what would be deleted without actually deleting
    --all       Remove all types of redundant files (default)
    --cache     Remove only Python cache files (__pycache__, .pyc)
    --build     Remove only build artifacts (dist, build directories)
    --temp      Remove only temporary files
    --node      Remove only Node.js artifacts (node_modules)
"""

import os
import sys
import shutil
import argparse
from pathlib import Path
import re

# Define the project root directory
PROJECT_ROOT = Path(__file__).resolve().parent

# Define patterns for different types of files to clean
CACHE_PATTERNS = [
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".pytest_cache",
    ".coverage",
    "htmlcov",
]

BUILD_PATTERNS = [
    "dist",
    "build",
    "*.egg-info",
    "frontend/dist",
    ".venv",
]

TEMP_PATTERNS = [
    "*.tmp",
    "*.bak",
    "*.swp",
    "*.swo",
    "*~",
    ".DS_Store",
    "Thumbs.db",
]

NODE_PATTERNS = [
    "node_modules",
    "package-lock.json",
    "yarn.lock",
    ".npm",
]


def match_pattern(path, patterns):
    """Check if a path matches any of the given patterns."""
    path_str = str(path)
    for pattern in patterns:
        # Handle directory patterns (no wildcards)
        if "*" not in pattern and path.name == pattern:
            return True
        # Handle wildcard patterns for files
        elif "*" in pattern:
            if re.match(pattern.replace("*", ".*"), path.name):
                return True
    return False


def find_matches(root_dir, patterns):
    """Find all paths that match the given patterns."""
    matches = []
    for path in root_dir.glob("**/*"):
        if match_pattern(path, patterns):
            matches.append(path)
    return matches


def remove_paths(paths, dry_run=False):
    """Remove the given paths, handling both files and directories."""
    for path in sorted(paths, key=lambda p: len(str(p)), reverse=True):
        if path.exists():
            if dry_run:
                print(f"Would remove: {path}")
            else:
                try:
                    if path.is_dir():
                        shutil.rmtree(path)
                        print(f"Removed directory: {path}")
                    else:
                        path.unlink()
                        print(f"Removed file: {path}")
                except Exception as e:
                    print(f"Error removing {path}: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Deep clean the Jenna Voice Assistant codebase"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be deleted without actually deleting"
    )
    parser.add_argument(
        "--all", action="store_true", help="Remove all types of redundant files (default)"
    )
    parser.add_argument(
        "--cache", action="store_true", help="Remove only Python cache files"
    )
    parser.add_argument(
        "--build", action="store_true", help="Remove only build artifacts"
    )
    parser.add_argument(
        "--temp", action="store_true", help="Remove only temporary files"
    )
    parser.add_argument(
        "--node", action="store_true", help="Remove only Node.js artifacts"
    )

    args = parser.parse_args()

    # If no specific category is selected, default to --all
    if not (args.cache or args.build or args.temp or args.node):
        args.all = True

    # Collect all paths to remove
    paths_to_remove = []

    if args.all or args.cache:
        cache_matches = find_matches(PROJECT_ROOT, CACHE_PATTERNS)
        paths_to_remove.extend(cache_matches)
        print(f"Found {len(cache_matches)} Python cache files/directories")

    if args.all or args.build:
        build_matches = find_matches(PROJECT_ROOT, BUILD_PATTERNS)
        paths_to_remove.extend(build_matches)
        print(f"Found {len(build_matches)} build artifacts")

    if args.all or args.temp:
        temp_matches = find_matches(PROJECT_ROOT, TEMP_PATTERNS)
        paths_to_remove.extend(temp_matches)
        print(f"Found {len(temp_matches)} temporary files")

    if args.all or args.node:
        node_matches = find_matches(PROJECT_ROOT, NODE_PATTERNS)
        paths_to_remove.extend(node_matches)
        print(f"Found {len(node_matches)} Node.js artifacts")

    # Remove duplicates while preserving order
    unique_paths = []
    for path in paths_to_remove:
        if path not in unique_paths:
            unique_paths.append(path)

    # Remove the paths
    if unique_paths:
        print(f"\nTotal files/directories to remove: {len(unique_paths)}")
        if args.dry_run:
            print("\nDRY RUN - No files will be deleted\n")
        remove_paths(unique_paths, args.dry_run)
        if not args.dry_run:
            print("\n✅ Cleanup completed successfully!")
    else:
        print("\nNo files found to remove.")


if __name__ == "__main__":
    main()