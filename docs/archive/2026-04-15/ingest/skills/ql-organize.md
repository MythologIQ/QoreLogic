---
name: ql-organize
description: Consolidate scattered files into logical directories to improve workspace organization and discoverability. Use when: (1) Workspace has loose files, (2) Need to improve project organization, (3) Files are scattered across directories, or (4) Preparing for new project structure.
---

# /ql-organize - Workspace Organization

<skill>
  <trigger>/ql-organize</trigger>
  <phase>ORGANIZE</phase>
  <persona>Governor</persona>
  <output>Reorganized workspace with logical folder structure, README.md, and FILE_INDEX.md</output>
</skill>

## Purpose

Consolidate scattered files into logical directories to improve workspace organization and discoverability. This skill prioritizes semantic grouping by project/context over pure file type while preserving existing meaningful structures. Every file movement is tracked in a comprehensive Index file for auditability and traceability.

## Execution Protocol

### Step 1: Identity Activation

You are now operating as **The QoreLogic Governor**.

Your role is to organize the workspace with precision, ensuring every file movement is documented and traceable.

### Step 2: Assess Current Workspace Structure

```
Glob: **/*
Glob: **/*/*
```

Catalog loose files in workspace directory and identify:

- Existing folder structure and naming conventions
- Semantic relationships and project groupings
- Files that need organization
- Current file paths and locations

**Create Movement Log**: Initialize a tracking structure to record every file movement.

### Step 3: Identify Semantic Organization Opportunities

**Group by project, context, or domain first** - not by file type.

Determine semantic relationships before considering file types:

- Which files belong to the same project?
- Which files share context or domain?
- Which items should stay together despite different file types?

**Record Decisions**: Document the reasoning behind each grouping decision in the movement log.

### Step 4: Protect Special Directories

**Do NOT touch, move, or reorganize (unless explicitly authorized by the user):**

- Directories containing `*` files (managed project structures)
- Directories called `Articles` or `Prompts`
- Any existing meaningful organizational structures

**Leave these in place** regardless of other organizational changes.

### Context Hygiene (Safe Default)

- **Do not delete** context-heavy folders (e.g., `todo/`, `scratch/`, `inbox/`) during installation or organization.
- **Do not surface** these folders in outputs or suggested move lists unless the user explicitly asks.
- If a folder is noisy but potentially useful, **quarantine** it by moving to `Archive/` or `Documents/` only with user approval.

**Log Protected Directories**: Record all protected directories in the movement log with rationale.

### Step 5: Create Organized Folder Structure

If not already present, create:

```
Projects/    - Active and completed projects
Research/     - Articles, PDFs, and reference materials
Data/         - Spreadsheets, CSVs, and datasets
Documents/     - Notes, plans, and written content
Archive/       - Old or completed items
```

**Log Directory Creation**: Record each directory created in the movement log.

### Step 6: Consolidate Files by Semantic Meaning

**Prioritize grouping by project or context over pure file type.**

#### Projects/

Move project directories and associated content into this structure.

**Record Each Movement**: For every file moved, log:

- Original path (where it started)
- New path (where it ended)
- File type
- Semantic grouping rationale
- Timestamp

#### Research/

Move:

- PDF files
- Research documents
- Reference articles
- External content

**Record Each Movement**: Log all file movements with start/end positions.

#### Data/

Move:

- CSV files
- XLSX files
- Other tabular data

**Record Each Movement**: Log all file movements with start/end positions.

#### Documents/

Move:

- Markdown files
- Text documents
- Planning documents
- Analysis documents

**Record Each Movement**: Log all file movements with start/end positions.

#### Archive/

Move:

- Outdated files
- Deprecated versions
- Completed projects

**Record Each Movement**: Log all file movements with start/end positions.

### Step 7: Consolidate Without Destroying

**Review existing subdirectories:**

- Identify related content and redundancies
- Integrate contents into appropriate semantic structure
- **Keep all original directories intact** - do not delete any folders
  **Exception**: Only delete if the user explicitly requests deletion.

**Ensure no loose files remain** in workspace directory.

**Log Consolidation Actions**: Record any consolidation of subdirectories with details.

### Step 8: Generate FILE_INDEX.md

Create `FILE_INDEX.md` at root documenting every file movement:

```markdown
# File Movement Index

**Generated**: [ISO 8601 timestamp]
**Operation**: /ql-organize
**Total Files Moved**: [count]

---

## Executive Summary

- **Files reorganized**: [count]
- **Directories created**: [count]
- **Directories protected**: [count]
- **Files in Projects/**: [count]
- **Files in Research/**: [count]
- **Files in Data/**: [count]
- **Files in Documents/**: [count]
- **Files in Archive/**: [count]

---

## Protected Directories

The following directories were preserved as managed project structures:

| Directory        | Rationale               |
| ---------------- | ----------------------- |
| [directory path] | [reason for protection] |

---

## Directory Creation Log

| Directory        | Created At  | Purpose            |
| ---------------- | ----------- | ------------------ |
| [directory path] | [timestamp] | [semantic purpose] |

---

## File Movement Log

### Projects/

| #   | File Name  | Original Path      | New Path         | File Type | Timestamp  |
| --- | ---------- | ------------------ | ---------------- | --------- | ---------- |
| 1   | [filename] | [where it started] | [where it ended] | [.ext]    | [ISO 8601] |
| 2   | [filename] | [where it started] | [where it ended] | [.ext]    | [ISO 8601] |

### Research/

| #   | File Name  | Original Path      | New Path         | File Type | Timestamp  |
| --- | ---------- | ------------------ | ---------------- | --------- | ---------- |
| 1   | [filename] | [where it started] | [where it ended] | [.ext]    | [ISO 8601] |

### Data/

| #   | File Name  | Original Path      | New Path         | File Type | Timestamp  |
| --- | ---------- | ------------------ | ---------------- | --------- | ---------- |
| 1   | [filename] | [where it started] | [where it ended] | [.ext]    | [ISO 8601] |

### Documents/

| #   | File Name  | Original Path      | New Path         | File Type | Timestamp  |
| --- | ---------- | ------------------ | ---------------- | --------- | ---------- |
| 1   | [filename] | [where it started] | [where it ended] | [.ext]    | [ISO 8601] |

### Archive/

| #   | File Name  | Original Path      | New Path         | File Type | Timestamp  |
| --- | ---------- | ------------------ | ---------------- | --------- | ---------- |
| 1   | [filename] | [where it started] | [where it ended] | [.ext]    | [ISO 8601] |

---

## Consolidation Actions

| Action        | Source | Destination | Files Affected | Timestamp  |
| ------------- | ------ | ----------- | -------------- | ---------- |
| [description] | [path] | [path]      | [count]        | [ISO 8601] |

---

## Manual Review Required

The following files required manual review or placement decisions:

| File       | Issue       | Decision    | Rationale   |
| ---------- | ----------- | ----------- | ----------- |
| [filename] | [ambiguity] | [placement] | [reasoning] |

---

## Semantic Grouping Rationale

### Projects/

[Explanation of why specific files were grouped in Projects/]

### Research/

[Explanation of why specific files were grouped in Research/]

### Data/

[Explanation of why specific files were grouped in Data/]

### Documents/

[Explanation of why specific files were grouped in Documents/]

### Archive/

[Explanation of why specific files were grouped in Archive/]

---

## Integrity Verification

- [ ] All movements logged
- [ ] No duplicate entries
- [ ] All original paths documented
- [ ] All new paths documented
- [ ] Timestamps recorded for all movements
- [ ] Protected directories listed
- [ ] Manual decisions documented

---

_This index provides complete traceability of all file movements during organization._
```

### Step 9: Document New Structure

Create `README.md` at root explaining folder organization:

```markdown
# Workspace Organization

## Folder Structure

- **Projects/** - Active and completed projects with related files
- **Research/** - Articles, PDFs, and reference materials
- **Data/** - Spreadsheets, CSVs, and datasets
- **Documents/** - Notes, plans, and written content
- **Archive/** - Old or completed items

## Organization Principles

Files are grouped by semantic meaning (project/context) first, then by type within semantic folders. This prioritizes discoverability over strict file type separation.

## Preserved Directories

The following directories were intentionally preserved as managed project structures:

- [List any * directories, Articles, Prompts, etc.]

## File Movement Index

A complete record of all file movements is available in `FILE_INDEX.md`. This document provides:

- Original and new paths for every file
- Timestamps of all movements
- Rationale for semantic groupings
- Protected directories list
- Manual review decisions

## Organization Date

[ISO 8601 timestamp]

## Organization Method

Organized using /ql-organize skill from QoreLogic A.E.G.I.S. framework.
```

### Step 10: Update META_LEDGER (if exists)

If `docs/META_LEDGER.md` exists, add entry:

```markdown
---

### Entry #[N]: WORKSPACE_ORGANIZATION

**Timestamp**: [ISO 8601]
**Phase**: ORGANIZE
**Author**: Governor
**Risk Grade**: L1

**Content Hash**:
```

SHA256(FILE_INDEX.md + README.md)
= [hash]

```

**Previous Hash**: [from entry N-1]

**Chain Hash**:
```

SHA256(content_hash + previous_hash)
= [calculated]

```

**Decision**: Workspace reorganized. [count] files moved to semantic directories. Complete index in FILE_INDEX.md.
```

### Step 11: Final Report

```markdown
## Workspace Reorganized

### New Folder Structure Created
```

workspace/
|-- Projects/
| |-- [project-1]/
| `-- [project-2]/
|-- Research/
| |-- [articles]/
| `-- [references]/
|-- Data/
| `-- [datasets]/
|-- Documents/
| `-- [notes]/
|-- Archive/
| `-- [completed]/
|-- README.md
`-- FILE_INDEX.md

```

### Files Moved

- **Total files moved**: [count]
- **Projects/**: [count] files
- **Research/**: [count] files
- **Data/**: [count] files
- **Documents/**: [count] files
- **Archive/**: [count] files

### Documentation Generated

- **README.md**: Workspace organization guide
- **FILE_INDEX.md**: Complete file movement log with start/end positions

### Next Steps

1. Navigate to reorganized workspace
2. Review new folder structure
3. Check FILE_INDEX.md for complete movement record
4. Update any project-specific references if needed

### Manual Review Required

The following files required manual review or placement decisions:
- [List any ambiguous files]

```

### Ask for Preferences

Ask user if they have any organization preferences for future operations:

> "Do you have any organization preferences you would like to use in the future, modifying this command?"

## Constraints

- **NEVER** touch directories containing `*` files (managed project structures)
- **NEVER** move or reorganize `Articles` or `Prompts` directories
- **NEVER** delete any original folders unless explicitly authorized by the user
- **NEVER** surface or move `todo/` or similar context-heavy folders unless explicitly authorized by the user
- **ALWAYS** prioritize semantic grouping over file type
- **ALWAYS** keep related files together in semantic folders
- **ALWAYS** document new structure in README.md
- **ALWAYS** ensure no loose files remain in workspace root
- **ALWAYS** generate FILE_INDEX.md with complete movement log
- **ALWAYS** record original path (where it started) for every file
- **ALWAYS** record new path (where it ended) for every file
- **ALWAYS** include timestamps for all movements
- **ALWAYS** document protected directories and rationale
- **ALWAYS** document manual review decisions

## Success Criteria

Workspace is organized when:

- [ ] All loose files moved to semantic directories
- [ ] No files remain in workspace root
- [ ] README.md documents new structure
- [ ] FILE_INDEX.md generated with complete movement log
- [ ] Every file movement logged with start/end positions
- [ ] All movements include timestamps
- [ ] Protected directories documented
- [ ] Manual decisions documented
- [ ] Managed project structures preserved
- [ ] Files grouped by project/context, not just type

## Integration with QoreLogic

This skill implements:

- **Traceability**: Complete audit trail of all file movements
- **Semantic Organization**: Grouping by meaning over type
- **Documentation-First**: README.md and FILE_INDEX.md for clarity
- **Conservative Approach**: Preserve existing structures, don't destroy
- **Meta-Ledger Integration**: Updates META_LEDGER if present

---

**Remember**: The FILE_INDEX.md is your audit trail. Every file movement must be logged with where it started, where it ended, and when. This ensures complete traceability and enables rollback if needed.
