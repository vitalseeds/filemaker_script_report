#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = []
# ///
"""
Extract FileMaker scripts from DDR XML report and create individual script files.
Also create symlinks for scripts used in layouts and triggers.
Handles UTF-16 encoded XML files.

Usage:
    python3 extract_scripts.py [xml_file]
    uv run extract_scripts.py [xml_file]

    If xml_file is provided, use that file.
    Otherwise, auto-detect from ddr/ directory.
"""

import xml.etree.ElementTree as ET
import os
import re
import sys
import platform
from pathlib import Path
from collections import defaultdict

# Import utility modules
sys.path.insert(0, str(Path(__file__).parent / "includes"))
from find_unused import find_and_link_unused_scripts, _create_link
from generate_index import generate_markdown_index

# Get the directory where this script is located
SCRIPT_DIR = Path(__file__).parent.resolve()

# Paths relative to script location
DDR_DIR = SCRIPT_DIR / "ddr"
SCRIPTS_DIR = SCRIPT_DIR / "scripts"
LAYOUTS_DIR = SCRIPTS_DIR / "layouts"
TRIGGERS_DIR = SCRIPTS_DIR / "triggers"

# File extension for extracted scripts
SCRIPT_EXTENSION = ".fm"

# Find XML files in DDR directory
def find_xml_file():
    """Find and select XML file from DDR directory."""
    # Check if XML file was provided as command-line argument
    if len(sys.argv) > 1:
        xml_file = Path(sys.argv[1])
        if not xml_file.is_absolute():
            # Resolve relative to DDR directory or current directory
            if (DDR_DIR / xml_file).exists():
                xml_file = DDR_DIR / xml_file
            else:
                xml_file = Path.cwd() / xml_file

        if not xml_file.exists():
            print(f"Error: XML file not found: {xml_file}")
            exit(1)

        print(f"Using XML file: {xml_file.name}")
        return xml_file

    # Auto-detect XML files in DDR directory
    if not DDR_DIR.exists():
        print(f"Error: DDR directory not found: {DDR_DIR}")
        exit(1)

    xml_files = sorted(DDR_DIR.glob("*.xml"))

    if not xml_files:
        print(f"Error: No XML files found in {DDR_DIR}")
        exit(1)

    if len(xml_files) == 1:
        xml_file = xml_files[0]
        print(f"Found XML file: {xml_file.name}")
        return xml_file

    # Multiple files found - prompt user to choose
    print(f"\nFound {len(xml_files)} XML files in {DDR_DIR}:")
    print()
    for i, xml_file in enumerate(xml_files, 1):
        size = xml_file.stat().st_size / (1024 * 1024)  # Size in MB
        print(f"  {i}. {xml_file.name} ({size:.1f} MB)")

    print()
    while True:
        try:
            choice = input(f"Select XML file (1-{len(xml_files)}): ").strip()
            index = int(choice) - 1
            if 0 <= index < len(xml_files):
                selected = xml_files[index]
                print(f"Selected: {selected.name}")
                return selected
            else:
                print(f"Please enter a number between 1 and {len(xml_files)}")
        except (ValueError, KeyboardInterrupt):
            print("\nCancelled by user")
            exit(0)

XML_FILE = find_xml_file()

# Create directories
SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
LAYOUTS_DIR.mkdir(parents=True, exist_ok=True)
TRIGGERS_DIR.mkdir(parents=True, exist_ok=True)

# Track script to layout/trigger associations
script_layouts = defaultdict(set)  # script_name -> set of layout names
script_triggers = set()  # set of script names used as triggers
all_scripts = {}  # script_name -> safe_file_name

print(f"Parsing {XML_FILE}...")
print("This may take a while for large files...")

# Parse XML - Python's ET handles UTF-16 automatically
tree = ET.parse(XML_FILE)
root = tree.getroot()

# Extract all scripts
scripts = root.findall(".//Script")
print(f"Found {len(scripts)} scripts")

scripts_written = 0
for script_elem in scripts:
    scripts_written += 1
    script_name = script_elem.get("name", f"unnamed_script_{scripts_written}")

    # Sanitize filename
    safe_name = re.sub(r'[^\w\s-]', '_', script_name)
    safe_name = re.sub(r'[-\s]+', '_', safe_name)

    # Store mapping
    all_scripts[script_name] = safe_name

    # Get script content
    script_content = []
    script_content.append(f"Script: {script_name}\n")
    script_content.append("=" * 80 + "\n\n")

    # Get script attributes
    if script_elem.get("id"):
        script_content.append(f"ID: {script_elem.get('id')}\n")
    if script_elem.get("isFolder"):
        script_content.append(f"Is Folder: {script_elem.get('isFolder')}\n")
    if script_elem.get("includeInMenu"):
        script_content.append(f"Include in Menu: {script_elem.get('includeInMenu')}\n")

    script_content.append("\n")

    # Get script steps
    for step in script_elem.findall(".//StepList/*"):
        step_name = step.tag
        step_enable = step.get("enable", "True")
        script_content.append(f"[{'✓' if step_enable == 'True' else '✗'}] {step_name}")

        # Get step text if available
        step_text = step.find("StepText")
        if step_text is not None and step_text.text:
            script_content.append(f"    {step_text.text.strip()}\n")
        else:
            script_content.append("\n")

        # Get other parameters
        for param in step:
            if param.tag != "StepText" and param.text:
                script_content.append(f"    {param.tag}: {param.text.strip()}\n")

    # Write script file
    script_file = SCRIPTS_DIR / f"{safe_name}{SCRIPT_EXTENSION}"
    with open(script_file, "w", encoding="utf-8") as f:
        f.writelines(script_content)

    if scripts_written % 50 == 0:
        print(f"  Extracted {scripts_written} scripts...")

print(f"\nExtracted {scripts_written} scripts to {SCRIPTS_DIR}")

# Find layouts and their script references
print(f"\nSearching for layout-script associations...")
layouts = root.findall(".//Layout")
print(f"Found {len(layouts)} layouts")

for layout_elem in layouts:
    layout_name = layout_elem.get("name")
    if not layout_name:
        continue

    # Find all script references in this layout (buttons, triggers, etc.)
    # Look for any element with a "script" or "Script" attribute or child
    for elem in layout_elem.iter():
        # Check for script attribute
        script_name = elem.get("script") or elem.get("Script")
        if script_name:
            script_layouts[script_name].add(layout_name)

        # Check for Script child element
        script_child = elem.find("Script")
        if script_child is not None:
            script_name = script_child.get("name") or script_child.text
            if script_name:
                script_layouts[script_name].add(layout_name)

    # Look for triggers specifically
    trigger_tags = ["OnObjectEnter", "OnObjectExit", "OnObjectKeystroke",
                   "OnObjectModify", "OnObjectSave", "OnLayoutEnter",
                   "OnLayoutExit", "OnLayoutKeystroke", "OnLayoutLoad",
                   "OnRecordCommit", "OnRecordLoad", "OnRecordRevert",
                   "OnModeEnter", "OnModeExit", "OnViewChange",
                   "OnPanelSwitch", "OnTabSwitch", "OnGestureTap"]

    for trigger_tag in trigger_tags:
        for trigger_elem in layout_elem.findall(f".//{trigger_tag}"):
            # Find script reference in trigger
            script_ref = trigger_elem.find(".//Script")
            if script_ref is not None:
                script_name = script_ref.get("name") or script_ref.text
                if script_name:
                    script_triggers.add(script_name)
                    script_layouts[script_name].add(layout_name)

print(f"Found {len(script_layouts)} scripts associated with layouts")
print(f"Found {len(script_triggers)} scripts associated with triggers")

# Create symlinks for scripts used in layouts
print(f"\nCreating layout symlinks...")
layout_links_created = 0
for script_name, layouts in script_layouts.items():
    if script_name not in all_scripts:
        continue

    safe_script_name = all_scripts[script_name]
    script_file = SCRIPTS_DIR / f"{safe_script_name}{SCRIPT_EXTENSION}"

    if script_file.exists():
        for layout_name in layouts:
            safe_layout_name = re.sub(r'[^\w\s-]', '_', layout_name)
            safe_layout_name = re.sub(r'[-\s]+', '_', safe_layout_name)

            layout_dir = LAYOUTS_DIR / safe_layout_name
            layout_dir.mkdir(exist_ok=True)

            link_path = layout_dir / f"{safe_script_name}{SCRIPT_EXTENSION}"
            if not link_path.exists():
                success, _ = _create_link(script_file, link_path)
                if success:
                    layout_links_created += 1

link_type = 'hardlinks' if platform.system() == 'Windows' else 'symlinks'
print(f"Created {layout_links_created} layout {link_type} in {len(script_layouts)} layout folders")

# Create symlinks for scripts used as triggers
print(f"\nCreating trigger symlinks...")
trigger_links_created = 0
for script_name in script_triggers:
    if script_name not in all_scripts:
        continue

    safe_script_name = all_scripts[script_name]
    script_file = SCRIPTS_DIR / f"{safe_script_name}{SCRIPT_EXTENSION}"

    if script_file.exists():
        link_path = TRIGGERS_DIR / f"{safe_script_name}{SCRIPT_EXTENSION}"
        if not link_path.exists():
            success, _ = _create_link(script_file, link_path)
            if success:
                trigger_links_created += 1

print(f"Created {trigger_links_created} trigger {link_type}")

# Find and link unused scripts
print(f"\nFinding unused scripts...")
UNUSED_DIR = SCRIPTS_DIR / "unused"
used_scripts = set(script_layouts.keys()) | script_triggers
unused_scripts = set(all_scripts.keys()) - used_scripts
print(f"Found {len(unused_scripts)} unused scripts (not in any layout or trigger)")

print(f"Creating unused script links...")
unused_links_created, link_method = find_and_link_unused_scripts(
    unused_scripts=unused_scripts,
    all_scripts=all_scripts,
    scripts_dir=SCRIPTS_DIR,
    unused_dir=UNUSED_DIR,
    script_extension=SCRIPT_EXTENSION
)
print(f"Created {unused_links_created} unused script {link_method}s")

# Generate markdown index
print(f"\nGenerating markdown index...")
OUTPUT_FILE = SCRIPT_DIR / "scripts_index.md"
generate_markdown_index(
    output_file=OUTPUT_FILE,
    scripts_dir=SCRIPTS_DIR,
    all_scripts=all_scripts,
    script_layouts=script_layouts,
    script_triggers=script_triggers,
    unused_scripts=unused_scripts,
    script_extension=SCRIPT_EXTENSION
)
print(f"Generated index: {OUTPUT_FILE}")

print("\nDone!")
print(f"\nSummary:")
print(f"  Scripts: {scripts_written}")
print(f"  Layout associations: {len(script_layouts)}")
print(f"  Trigger associations: {len(script_triggers)}")
print(f"  Unused scripts: {len(unused_scripts)}")
print(f"  Layout symlinks: {layout_links_created}")
print(f"  Trigger symlinks: {trigger_links_created}")
print(f"  Unused symlinks: {unused_links_created}")
print(f"  Index file: {OUTPUT_FILE}")
