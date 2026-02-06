#!/usr/bin/env python3
"""
Find scripts that are not associated with any layout or trigger and create links to them.
Uses symlinks on Unix-like systems and hard links on Windows.
"""

import os
import platform
from pathlib import Path


def _create_link(source, destination):
    """
    Create a symlink (Unix) or hard link (Windows) depending on platform.

    Args:
        source: Source file path
        destination: Destination link path

    Returns:
        tuple: (success: bool, method: str) - method is 'symlink' or 'hardlink'
    """
    # On Windows, use hard links (work without admin privileges)
    # On Unix-like systems, use symbolic links
    is_windows = platform.system() == 'Windows'

    try:
        if is_windows:
            # Hard link for Windows (no admin rights required for files)
            os.link(source, destination)
            return True, 'hardlink'
        else:
            # Symbolic link for Unix-like systems
            os.symlink(source, destination)
            return True, 'symlink'
    except (OSError, FileExistsError):
        return False, None


def find_and_link_unused_scripts(
    unused_scripts,
    all_scripts,
    scripts_dir,
    unused_dir,
    script_extension=".fm"
):
    """
    Create links for unused scripts (symlinks on Unix, hard links on Windows).

    Args:
        unused_scripts: Set of unused script names
        all_scripts: Dict mapping script names to safe filenames
        scripts_dir: Path to scripts directory
        unused_dir: Path to unused scripts directory
        script_extension: File extension for scripts (default: ".fm")

    Returns:
        tuple: (links_created: int, method: str) - method is 'symlink' or 'hardlink'
    """
    # Create unused directory
    unused_dir.mkdir(parents=True, exist_ok=True)

    # Create links for unused scripts
    links_created = 0
    link_method = None

    for script_name in sorted(unused_scripts):
        if script_name not in all_scripts:
            continue

        safe_name = all_scripts[script_name]
        script_file = scripts_dir / f"{safe_name}{script_extension}"

        if script_file.exists():
            link_path = unused_dir / f"{safe_name}{script_extension}"
            if not link_path.exists():
                success, method = _create_link(script_file, link_path)
                if success:
                    links_created += 1
                    if link_method is None:
                        link_method = method

    return links_created, link_method or ('hardlink' if platform.system() == 'Windows' else 'symlink')
