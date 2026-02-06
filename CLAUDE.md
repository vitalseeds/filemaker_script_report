# FileMaker Script Extraction

This directory contains extracted scripts and documentation from the FileMaker database design report (DDR).

## Directory Structure

```
reports/
├── extract_scripts.py - Main extraction script
├── CLAUDE.md - This documentation file
├── scripts_index.md - Generated markdown index
├── includes/ - Utility modules
│   ├── find_unused.py - Module to identify and link unused scripts
│   └── generate_index.py - Module to generate markdown index
├── ddr/
│   └── vs_db_fmp12.xml - Source DDR XML file
└── scripts/
    ├── *.fm - Individual script files (177 unique scripts)
    ├── layouts/ - Symlinks to scripts organized by layout
    ├── triggers/ - Symlinks to scripts used as triggers
    └── unused/ - Symlinks to unused scripts (50 scripts)
```

## How to Re-extract Scripts

If you need to re-run the extraction (e.g., after updating the database):

```bash
cd reports
python3 extract_scripts.py [xml_file]
```

### XML File Selection

The script intelligently handles XML file selection:

1. **Specify a file** (optional):
   ```bash
   python3 extract_scripts.py vs_db_fmp12.xml
   python3 extract_scripts.py ddr/vs_db_fmp12.xml
   ```

2. **Auto-detect** (no argument):
   - If **one XML file** exists in `ddr/`: automatically uses it
   - If **multiple XML files** exist: prompts you to choose from a numbered list
   - If **no XML files** found: displays an error

### What the Script Does

The script will:
1. Detect or select the DDR XML file from the `ddr/` directory
2. Parse the FileMaker DDR XML file (handles UTF-16 encoding)
3. Extract all scripts into individual `.fm` files in `scripts/`
4. Create symlinks in `scripts/layouts/` for scripts used in layouts
5. Create symlinks in `scripts/triggers/` for scripts used as triggers
6. Import and run `includes/find_unused.py` to create symlinks in `scripts/unused/`
7. Import and run `includes/generate_index.py` to create `scripts_index.md`

## Modular Architecture

The extraction script uses a modular architecture with utility modules in `includes/`:

- **`find_unused.py`** - Identifies scripts not associated with any layout or trigger and creates symlinks
- **`generate_index.py`** - Generates a comprehensive markdown index of all scripts

These modules are automatically imported and executed by `extract_scripts.py` during the extraction process.

## DDR XML Location

The source DDR XML file is located at:
```
reports/ddr/vs_db_fmp12.xml
```

## Script File Format

Each `.fm` file contains:
- Script name and ID
- Script attributes (include in menu, etc.)
- Script steps with parameters
- Enable/disable status for each step

**Note**: The script file extension is configurable via the `SCRIPT_EXTENSION` constant in the extraction script (default: `.fm`).

## Database Statistics

- **Total Script Elements in XML**: 634
- **Unique Script Names**: 177
- **Duplicate Script Names**: 133 (some scripts appear multiple times in DDR)
  - Examples: "Print front self seal" (23 times), "Print back self seal and mark printed" (11 times)
- **Layouts**: 269
- **Scripts with Layout Associations**: 127
- **Unused Scripts** (no layout/trigger association): 50
- **Layout Symlinks Created**: 367
- **Unused Symlinks Created**: 50

**Note**: The DDR contains duplicate script names. When multiple scripts share the same name, only the last occurrence is saved. This is normal for FileMaker DDRs which may include scripts from different contexts or references.

## Notes

- The DDR XML file is UTF-16 encoded with CRLF line endings
- Script names are sanitized for filesystem compatibility (special characters replaced with underscores)
- Symlinks allow easy navigation from layouts to their associated scripts
- The original XML file is ~38MB in size

## Trigger Associations

Currently, no trigger associations were found in the database. This could mean:
- The database doesn't use script triggers
- Triggers are stored in a different format in the DDR
- Triggers may be embedded within other elements

If triggers need to be identified, search the DDR XML for these trigger types:
- OnObjectEnter, OnObjectExit, OnObjectKeystroke
- OnObjectModify, OnObjectSave
- OnLayoutEnter, OnLayoutExit, OnLayoutKeystroke, OnLayoutLoad
- OnRecordCommit, OnRecordLoad, OnRecordRevert
- OnModeEnter, OnModeExit, OnViewChange
- OnPanelSwitch, OnTabSwitch, OnGestureTap

## Future Enhancements

Possible improvements to the extraction script:
1. Extract script parameters and return values
2. Generate a script dependency graph
3. Identify unused scripts
4. Extract custom functions
5. Map table occurrences to scripts
6. Generate documentation in Markdown format
