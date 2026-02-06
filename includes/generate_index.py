#!/usr/bin/env python3
"""
Generate a markdown index of all FileMaker scripts organized by category.
"""

from pathlib import Path
from datetime import datetime


def generate_markdown_index(
    output_file,
    scripts_dir,
    all_scripts,
    script_layouts,
    script_triggers,
    unused_scripts,
    script_extension=".fm"
):
    """
    Generate a markdown index of all scripts.

    Args:
        output_file: Path to output markdown file
        scripts_dir: Path to scripts directory
        all_scripts: Dict mapping script names to safe filenames
        script_layouts: Dict mapping script names to sets of layout names
        script_triggers: Set of script names used as triggers
        unused_scripts: Set of unused script names
        script_extension: File extension for scripts (default: ".fm")

    Returns:
        Path: The output file path
    """
    # Collect all script files
    all_script_files = sorted([f.name for f in scripts_dir.glob(f"*{script_extension}")])

    # Generate markdown
    lines = []
    lines.append("# FileMaker Scripts Index")
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Table of Contents
    lines.append("## Table of Contents")
    lines.append("")
    lines.append("- [Overview](#overview)")
    lines.append("- [All Scripts](#all-scripts)")
    lines.append("- [Scripts by Layout](#scripts-by-layout)")
    lines.append("- [Unused Scripts](#unused-scripts)")
    if script_triggers:
        lines.append("- [Trigger Scripts](#trigger-scripts)")
    lines.append("")
    lines.append("---")
    lines.append("")

    # Overview
    lines.append("## Overview")
    lines.append("")
    lines.append(f"- **Total Scripts**: {len(all_script_files)}")
    lines.append(f"- **Scripts Used in Layouts**: {len(script_layouts)}")
    lines.append(f"- **Unused Scripts**: {len(unused_scripts)}")
    lines.append(f"- **Trigger Scripts**: {len(script_triggers)}")
    lines.append(f"- **Layouts with Scripts**: {len(set(layout for scripts_set in script_layouts.values() for layout in scripts_set))}")
    lines.append("")
    lines.append("---")
    lines.append("")

    # All Scripts
    lines.append("## All Scripts")
    lines.append("")
    lines.append(f"Complete list of all {len(all_script_files)} scripts in alphabetical order:")
    lines.append("")

    # Get used script filenames
    used_script_files = set()
    for script_name in script_layouts.keys():
        if script_name in all_scripts:
            used_script_files.add(f"{all_scripts[script_name]}{script_extension}")

    unused_script_files = set(unused_scripts)
    if unused_script_files:
        for script_name in unused_scripts:
            if script_name in all_scripts:
                unused_script_files.add(f"{all_scripts[script_name]}{script_extension}")

    trigger_script_files = set()
    for script_name in script_triggers:
        if script_name in all_scripts:
            trigger_script_files.add(f"{all_scripts[script_name]}{script_extension}")

    for i, script in enumerate(all_script_files, 1):
        script_name = script.replace(script_extension, '')
        status = []
        if script in used_script_files:
            status.append("📍 Used in layouts")
        if script in unused_script_files or script_name in [s.replace(script_extension, '') for s in unused_script_files]:
            status.append("⚠️ Unused")
        if script in trigger_script_files:
            status.append("⚡ Trigger")

        status_str = f" — {', '.join(status)}" if status else ""
        lines.append(f"{i}. `{script_name}`{status_str}")

    lines.append("")
    lines.append("---")
    lines.append("")

    # Scripts by Layout
    lines.append("## Scripts by Layout")
    lines.append("")

    # Group by layout
    layout_scripts = {}
    for script_name, layout_names in script_layouts.items():
        for layout_name in layout_names:
            if layout_name not in layout_scripts:
                layout_scripts[layout_name] = []
            if script_name in all_scripts:
                layout_scripts[layout_name].append(all_scripts[script_name])

    lines.append(f"Scripts organized by the {len(layout_scripts)} layouts that use them:")
    lines.append("")

    for layout_name in sorted(layout_scripts.keys()):
        scripts = sorted(layout_scripts[layout_name])
        lines.append(f"### {layout_name}")
        lines.append("")
        lines.append(f"**{len(scripts)} script(s):**")
        lines.append("")
        for script in scripts:
            lines.append(f"- `{script}`")
        lines.append("")

    lines.append("---")
    lines.append("")

    # Unused Scripts
    lines.append("## Unused Scripts")
    lines.append("")
    if unused_scripts:
        unused_list = sorted([all_scripts.get(s, s) for s in unused_scripts if s in all_scripts])
        lines.append(f"These {len(unused_list)} scripts are not associated with any layout or trigger:")
        lines.append("")
        for i, script in enumerate(unused_list, 1):
            lines.append(f"{i}. `{script}`")
    else:
        lines.append("*No unused scripts found. All scripts are associated with layouts or triggers.*")
    lines.append("")

    # Trigger Scripts (if any)
    if script_triggers:
        lines.append("---")
        lines.append("")
        lines.append("## Trigger Scripts")
        lines.append("")
        trigger_list = sorted([all_scripts.get(s, s) for s in script_triggers if s in all_scripts])
        lines.append(f"These {len(trigger_list)} scripts are triggered automatically:")
        lines.append("")
        for i, script in enumerate(trigger_list, 1):
            lines.append(f"{i}. `{script}`")
        lines.append("")

    # Footer
    lines.append("---")
    lines.append("")
    lines.append("## File Locations")
    lines.append("")
    lines.append(f"- **Script files**: `{scripts_dir}/`")
    lines.append(f"- **Layout associations**: `{scripts_dir / 'layouts'}/`")
    lines.append(f"- **Trigger associations**: `{scripts_dir / 'triggers'}/`")
    lines.append(f"- **Unused scripts**: `{scripts_dir / 'unused'}/`")
    lines.append("")
    lines.append("Generated by `extract_scripts.py` from the FileMaker DDR XML export.")
    lines.append("")

    # Write file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return output_file
