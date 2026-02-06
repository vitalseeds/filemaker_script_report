# FileMaker Script Extraction Tool

Extract and organize FileMaker Pro scripts from Database Design Reports (DDR) into individual, searchable files.

## Overview

This tool parses FileMaker DDR XML exports and creates:
- Individual `.fm` files for each script
- Organized symlinks by layout usage
- A comprehensive markdown index
- Easy navigation of unused scripts

## Quick Start

### 1. Export FileMaker Design Report

In FileMaker Pro:

1. Open your database file
2. Go to **Tools** → **Database Design Report...**
3. In the DDR dialog:
   - Select your database from the list
   - Check **Available Tables** (select all or specific tables)
   - Under **Include in Report**, check at least:
     - ☑ Fields
     - ☑ Relationships
     - ☑ Scripts
     - ☑ Layouts
   - Choose **Format**: XML
   - Click **Create...**
4. Save the DDR to: `reports/ddr/`
   - The XML files will be created in this folder

### 2. Run the Extraction Script

```bash
cd reports
python3 extract_scripts.py
```

**Or with uv (recommended):**

```bash
cd reports
uv run extract_scripts.py
```

**Options:**

```bash
# Auto-detect XML file (prompts if multiple found)
python3 extract_scripts.py
# or
uv run extract_scripts.py

# Specify XML file by name
python3 extract_scripts.py vs_db_fmp12.xml
# or
uv run extract_scripts.py vs_db_fmp12.xml

# Specify full or relative path
python3 extract_scripts.py ddr/vs_db_fmp12.xml
```

### 3. View Results

- **Individual scripts**: `scripts/*.fm`
- **Scripts by layout**: `scripts/layouts/{layout_name}/`
- **Unused scripts**: `scripts/unused/`
- **Index**: `scripts_index.md`

## What You Get

### Directory Structure

```
reports/
├── extract_scripts.py          # Main extraction tool
├── scripts_index.md            # Searchable script index
├── ddr/                        # Place your DDR XML files here
│   └── *.xml
└── scripts/
    ├── *.fm                    # Individual script files
    ├── layouts/                # Scripts organized by layout
    │   └── {layout_name}/
    │       └── {script}.fm → (symlink to script)
    ├── unused/                 # Scripts not used in layouts
    │   └── {script}.fm → (symlink to script)
    └── triggers/               # Scripts used as triggers
        └── {script}.fm → (symlink to script)
```

### Script File Format

Each `.fm` file contains:
```
Script: Back up monthly
================================================================================

ID: 525
Include in Menu: False

[✓] Show Custom Dialog [ Title: "Make monthly back up?"; ... ]
[✓] If [ Get ( LastMessageChoice )=2 ]
[✓] Halt Script
[✓] End If
...
```

## Features

### Automatic XML Detection

- **1 XML file**: Auto-selects and proceeds
- **Multiple XML files**: Shows interactive menu with file sizes
- **No XML files**: Displays helpful error message

### Smart Organization

- **Layouts**: Scripts linked by which layouts use them
- **Unused**: Quickly identify scripts not associated with any layout
- **Triggers**: Scripts triggered automatically (if any)
- **Index**: Markdown file with all scripts categorized and searchable

### Cross-Platform Links

- **Unix/macOS/Linux**: Uses symbolic links (symlinks)
- **Windows**: Uses hard links (work like shortcuts without admin privileges)
- Both provide multiple paths to the same script file
- Changes to one location reflect in all linked locations

### Duplicate Handling

FileMaker DDRs often contain duplicate script names. The tool:
- Identifies duplicates
- Keeps only unique script names
- Documents duplicate counts in the index

## Requirements

- **Python 3.8+** (uses only standard library)
- **FileMaker Pro** (to generate DDR)
- **macOS/Linux/Windows** (cross-platform)
- **uv** (optional but recommended) - Install with: `curl -LsSf https://astral.sh/uv/install.sh | sh`

### Why uv?

[uv](https://github.com/astral-sh/uv) is a fast Python package installer. When you run `uv run extract_scripts.py`, it:
- Automatically ensures Python 3.8+ is available
- Runs in an isolated environment
- No need to manually manage dependencies (script uses only standard library)

## Troubleshooting

### "No XML files found in ddr/"

**Solution**: Export a DDR from FileMaker (see step 1 above)

### "Error parsing XML"

**Possible causes**:
- Incomplete DDR export
- Corrupted XML file
- Wrong file format

**Solution**: Re-export DDR with all options checked

### "Module not found" errors

**Solution**: Run from the `reports/` directory:
```bash
cd reports
python3 extract_scripts.py
```

### Scripts appear multiple times

This is normal! FileMaker DDRs include script references from multiple contexts. The tool extracts unique script names only.

## Advanced Usage

### Portable Paths

The script uses relative paths - you can move the entire `reports/` folder to a different location or system without changes.

### Custom File Extension

Edit `extract_scripts.py` and change:
```python
SCRIPT_EXTENSION = ".fm"  # Change to any extension
```

### Re-extraction

Safe to run multiple times. The script will:
- Overwrite existing `.fm` files
- Recreate symlinks
- Regenerate the index

## Tips

1. **Search scripts**: Use your editor's search across the `scripts/` directory
2. **Find by layout**: Check `scripts/layouts/{layout_name}/`
3. **Review unused**: Check `scripts/unused/` for potentially obsolete scripts
4. **Use the index**: `scripts_index.md` provides a comprehensive overview

## Getting Help

- See [CLAUDE.md](CLAUDE.md) for detailed technical documentation
- Check the generated `scripts_index.md` for script statistics
- Review extraction output for warnings or errors

## License

This tool is part of the Vital Seeds database documentation system.

---

**Last Updated**: 2026-02-06
**Script Version**: 1.0
**Compatible**: FileMaker Pro 18+
