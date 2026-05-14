---
name: system-inconsistencies-revision
description: Use when the user asks to review, refresh, reconcile, or clean up the notes system, TOC.md, tags, or structure after manual changes, deletions, moves, or other inconsistencies.
---

# System Inconsistencies Revision

Use this skill to audit and reconcile the notes system when it may have drifted out of sync.

Typical triggers:

- The user asks to refresh, review, clean up, or reconcile the notes system.
- The user says they changed, moved, renamed, or deleted notes manually.
- `TOC.md` appears stale.
- Tags listed in `TOC.md` no longer match the current notes.
- Notes or folders exist but are missing from the documented structure.
- Notes were deleted but still appear in `TOC.md`.
- Tags are missing, inconsistent, duplicated, or obviously outdated.

This skill may be used proactively when such inconsistencies are noticed during other work.

## Goal

Bring the note system back into a consistent state after manual edits or drift, while preserving the user's actual files 
as the source of truth.

## Source of Truth

- The current files and folders in the notes workspace are the source of truth.
- `TOC.md` is a maintained index and summary, not the authority when it conflicts with the real files.
- Existing note content should be preserved unless there is a clear reason to normalize or fix it.

## What To Check

Review the system for these classes of issues:

1. Structure mismatches.
2. `TOC.md` entries that point to removed, renamed, or moved notes.
3. Notes and folders that exist but are missing from `TOC.md`.
4. Tag drift between notes and the tag list recorded in `TOC.md`.
5. Obsolete tags that are no longer used anywhere.
6. Weak or inconsistent tags on notes that were manually edited outside the assistant.
7. Stale links from aggregating files such as tables, indexes, lists, dashboards, or category overviews that still 
reference removed, renamed, or moved notes.
8. Empty folders left behind after moves or deletions.
9. Obvious naming or placement inconsistencies that make the note system harder to navigate.

## Workflow

1. Read `TOC.md` and inspect the current note tree.
2. Compare the documented structure against the actual files and folders.
3. Collect the tags currently used across notes.
4. Check aggregating files inside categories for references to notes that no longer exist or have moved.
5. Identify stale entries, missing entries, unused tags, broken references, and obvious classification problems.
6. Update or remove broken references in aggregating files when the fix is clear.
7. Update `TOC.md` so it reflects the real current structure.
8. Remove tags from `TOC.md` that are no longer used.
9. If some notes clearly need better tags, fix them conservatively.
10. Remove empty folders when they are clearly leftovers and not intentional.
11. Summarize what was reconciled.

If the tag section in `TOC.md` is still technically correct but has become flat, noisy, or hard to navigate, use `toc-tag-grouping`.

If `TOC.md` is structurally accurate but still hard to navigate because it is too verbose, weakly linked, or not 
hierarchical enough, use `toc-navigation-structure`.

## Editing Rules

- Prefer small corrective edits over broad reorganization.
- Do not invent new structure unless the current inconsistency clearly requires it.
- Do not rewrite note content just to make it prettier.
- Be conservative with retagging. Fix obvious problems, but do not overclassify.
- Treat aggregating files as secondary indexes: keep them aligned with the real notes they reference.
- If a note could reasonably belong in more than one place, keep the current placement unless there is a strong reason to move it.
- If a mismatch is ambiguous, ask the user instead of guessing.

## When To Ask The User

Ask a short clarifying question if:

- A deleted or moved note may have been intentionally excluded from `TOC.md`.
- A folder looks empty but may be a reserved category.
- A note seems misclassified, but the intended taxonomy is unclear.
- Two possible tag schemes both look reasonable.
- An aggregating file references a missing note, but it is unclear whether the reference should be removed, replaced, or 
converted into a standalone entry without a note.
- A larger restructuring is needed beyond simple reconciliation.

## Expected Outcomes

After running this skill, the system should have:

- A `TOC.md` that matches the actual note tree.
- A current tag list in `TOC.md`.
- Stale references removed from `TOC.md`.
- Missing notes or folders reflected in `TOC.md`.
- Obsolete tags removed.
- Obviously inconsistent tags corrected where safe.
- Broken references from aggregating files fixed where the intended correction is clear.

## Response Style

When reporting results, mention:

- What inconsistencies were found.
- Whether `TOC.md` was updated.
- Whether obsolete tags were removed.
- Whether any notes were retagged or moved.
- Any remaining ambiguities that still need user input.
